"""Fairness audit: does churn prediction work equally well for every player?

The raw logs carry no protected demographic attributes (no age, gender or
ethnicity), so a conventional demographic fairness audit is not possible on
this data and is not claimed. Two substitutes are used instead:

1. **Contextual attributes that are actually present** - platform (iOS vs
   Android) and device family. These are not protected characteristics, but
   they correlate with device cost and therefore act as a coarse, openly
   acknowledged proxy for economic access.

2. **Behavioural segments** - engagement, spend and skill tiers derived from
   the observation window. A retention model that is accurate for core players
   but unreliable for casual ones will systematically misdirect interventions,
   which is an equity problem in the operational sense even though no protected
   attribute is involved.

Reported per subgroup: size, base churn rate, ROC-AUC, retained-class PR-AUC,
and error rates at a single shared decision threshold. Using one global
threshold is essential - per-group thresholds would hide exactly the disparity
being measured.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from . import config

MIN_GROUP = 100  # subgroups smaller than this are not reported


def _rates(y: np.ndarray, pred: np.ndarray) -> dict:
    pos, neg = y == 1, y == 0
    return {
        "fnr": float((pred[pos] == 0).mean()) if pos.any() else np.nan,
        "fpr": float((pred[neg] == 1).mean()) if neg.any() else np.nan,
        "selection_rate": float(pred.mean()),
    }


def audit(df: pd.DataFrame, y: np.ndarray, proba: np.ndarray,
          threshold: float, attributes: list[str]) -> pd.DataFrame:
    """Per-subgroup performance for each attribute in `attributes`."""
    pred = (proba >= threshold).astype(int)
    rows = []

    for attr in attributes:
        if attr not in df.columns:
            continue
        for value, idx in df.groupby(attr, dropna=False).groups.items():
            mask = df.index.isin(idx)
            n = int(mask.sum())
            if n < MIN_GROUP:
                continue
            yg, pg, dg = y[mask], proba[mask], pred[mask]
            if len(np.unique(yg)) < 2:
                continue

            row = {
                "attribute": attr,
                "group": str(value),
                "n": n,
                "churn_rate": float(yg.mean()),
                "roc_auc": float(roc_auc_score(yg, pg)),
                "pr_auc_retained": float(average_precision_score(1 - yg, 1 - pg)),
                "baseline_pr_retained": float(1 - yg.mean()),
            }
            row.update(_rates(yg, dg))
            rows.append(row)

    return pd.DataFrame(rows)


def add_behavioural_segments(df: pd.DataFrame) -> pd.DataFrame:
    """Attach engagement / spend / skill tiers used as audit attributes."""
    out = df.copy()

    if "play_count" in out.columns:
        out["engagement_tier"] = pd.qcut(
            out["play_count"].rank(method="first"), 3,
            labels=["light", "medium", "heavy"]).astype(str)

    if "purchase_total" in out.columns and (out["purchase_total"] > 0).any():
        spender = out["purchase_total"] > 0
        tier = pd.Series("non_spender", index=out.index, dtype=object)
        if spender.sum() >= 2 * MIN_GROUP:
            paying = out.loc[spender, "purchase_total"]
            med = paying.median()
            tier[spender & (out["purchase_total"] <= med)] = "low_spender"
            tier[spender & (out["purchase_total"] > med)] = "high_spender"
        else:
            tier[spender] = "spender"
        out["spend_tier"] = tier

    skill_col = next((c for c in ("win_ratio", "score_mean") if c in out.columns), None)
    if skill_col is not None and out[skill_col].notna().sum() >= 3 * MIN_GROUP:
        out["skill_tier"] = pd.qcut(
            out[skill_col].rank(method="first"), 3,
            labels=["low", "mid", "high"]).astype(str)

    return out


def disparity_summary(report: pd.DataFrame) -> pd.DataFrame:
    """Max-min gap per attribute - the headline disparity numbers."""
    rows = []
    for attr, grp in report.groupby("attribute"):
        if len(grp) < 2:
            continue
        worst = grp.loc[grp["roc_auc"].idxmin()]
        best = grp.loc[grp["roc_auc"].idxmax()]
        rows.append({
            "attribute": attr,
            "groups": len(grp),
            "auc_gap": float(best["roc_auc"] - worst["roc_auc"]),
            "worst_group": worst["group"],
            "worst_auc": float(worst["roc_auc"]),
            "best_group": best["group"],
            "best_auc": float(best["roc_auc"]),
            "fnr_gap": float(grp["fnr"].max() - grp["fnr"].min()),
            "fpr_gap": float(grp["fpr"].max() - grp["fpr"].min()),
            "selection_rate_gap": float(grp["selection_rate"].max()
                                        - grp["selection_rate"].min()),
        })
    return pd.DataFrame(rows).sort_values("auc_gap", ascending=False)


def run_audit(test_df: pd.DataFrame, y: np.ndarray, proba: np.ndarray,
              threshold: float, game: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = add_behavioural_segments(test_df).reset_index(drop=True)
    attrs = [a for a in ("platform", "device_family", "engagement_tier",
                         "spend_tier", "skill_tier") if a in df.columns]

    report = audit(df, y, proba, threshold, attrs)
    if report.empty:
        print("  fairness: no subgroup met the minimum size threshold")
        return report, pd.DataFrame()

    summary = disparity_summary(report)
    report.to_csv(config.TABLE_DIR / f"{game}_fairness_report.csv", index=False)
    summary.to_csv(config.TABLE_DIR / f"{game}_fairness_summary.csv", index=False)

    for r in summary.itertuples():
        print(f"  fairness [{r.attribute}]: AUC gap {r.auc_gap:.3f} "
              f"(worst {r.worst_group} {r.worst_auc:.3f} vs "
              f"best {r.best_group} {r.best_auc:.3f}), FNR gap {r.fnr_gap:.3f}")

    return report, summary
