"""Behavioural feature engineering over the Observation Period.

Every feature is derived strictly from events with ts < op_end, so nothing from
the label window can leak into the model.

Feature families map onto the behavioural constructs in the research question:

  activity / session frequency  play_count, active_days, session_count,
                                mean_session_minutes, recency_hours, gap stats
  engagement trajectory         daily counts d0..d4, activity_slope,
                                first_vs_last_day_ratio, consecutive_play_ratio
  progression / mastery         score best/mean/worst/std, score_slope,
                                score_improvement
  difficulty / frustration      win_ratio, fail_ratio, quit_ratio,
                                max_loss_streak, fail_state_diversity,
                                dominant fail reason
  monetisation                  purchase_count, purchase_total, paid_*,
                                first_purchase_day, purchases_per_play
  context (fairness attributes) platform, device_family

Features that a game cannot supply (e.g. purchases in game1) come out as NaN
columns and are dropped by `prune_features`, so the same code runs unchanged
across all three datasets.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

DAY = 86_400
SESSION_GAP_SECONDS = 30 * 60  # inactivity gap that starts a new session

# Kept out of the model matrix but carried through for the fairness audit.
CONTEXT_COLS = ["platform", "device_family"]
ID_COLS = ["player_id"]
LABEL_COL = "churn"


def _slope(df: pd.DataFrame, key: str, x: str, y: str) -> pd.Series:
    """Least-squares slope of y on x within each group (NaN if x is constant)."""
    g = df.groupby(key, sort=False)
    xbar = g[x].transform("mean")
    ybar = g[y].transform("mean")
    dx = df[x] - xbar
    dy = df[y] - ybar
    num = (dx * dy).groupby(df[key], sort=False).sum()
    den = (dx * dx).groupby(df[key], sort=False).sum()
    return (num / den.replace(0, np.nan)).rename(f"{y}_slope")


def _device_family(s: pd.Series) -> pd.Series:
    """Collapse device strings to a coarse family to avoid tiny categories."""
    t = s.fillna("unknown").astype(str).str.lower()
    fam = pd.Series("other", index=s.index, dtype=object)
    for key, label in [("ipad", "iPad"), ("ipod", "iPod"), ("iphone", "iPhone")]:
        fam[t.str.contains(key, na=False)] = label
    fam[t.eq("unknown")] = "unknown"
    return fam


def build_features(events: pd.DataFrame, cohort: pd.DataFrame,
                   op_days: int) -> pd.DataFrame:
    """Return one feature row per player in `cohort`."""
    ev = events.merge(cohort[["player_id", "first_ts", "op_end"]],
                      on="player_id", how="inner")
    ev = ev[ev["ts"] < ev["op_end"]].copy()
    if ev.empty:
        raise ValueError("No Observation Period events for this cohort.")

    ev = ev.sort_values(["player_id", "ts"], ignore_index=True)
    ev["elapsed"] = ev["ts"] - ev["first_ts"]
    ev["day_index"] = (ev["elapsed"] // DAY).astype(int)
    dt = pd.to_datetime(ev["ts"], unit="s")
    ev["hour"] = dt.dt.hour
    ev["is_weekend"] = (dt.dt.dayofweek >= 5).astype(float)
    ev["is_night"] = ev["hour"].between(0, 5).astype(float)

    g = ev.groupby("player_id", sort=False)
    feats = pd.DataFrame(index=g.size().index)
    feats.index.name = "player_id"

    # ---- activity volume and timing -------------------------------------
    feats["play_count"] = g.size()
    feats["active_days"] = g["day_index"].nunique()
    feats["active_duration_hours"] = (g["elapsed"].max() - g["elapsed"].min()) / 3600.0
    feats["recency_hours"] = (ev["op_end"] - ev["ts"]).groupby(
        ev["player_id"], sort=False).min() / 3600.0
    feats["plays_per_active_day"] = feats["play_count"] / feats["active_days"]
    feats["weekend_ratio"] = g["is_weekend"].mean()
    feats["night_ratio"] = g["is_night"].mean()
    feats["hour_spread"] = g["hour"].std()

    # ---- inter-event gaps ------------------------------------------------
    ev["gap"] = g["ts"].diff()
    gaps = ev.dropna(subset=["gap"]).groupby("player_id", sort=False)["gap"]
    feats["mean_gap_hours"] = gaps.mean() / 3600.0
    feats["max_gap_hours"] = gaps.max() / 3600.0
    feats["std_gap_hours"] = gaps.std() / 3600.0

    # ---- sessionisation --------------------------------------------------
    ev["new_session"] = (ev["gap"].isna() | (ev["gap"] > SESSION_GAP_SECONDS))
    ev["session_id"] = ev.groupby("player_id", sort=False)["new_session"].cumsum()
    sess = ev.groupby(["player_id", "session_id"], sort=False)["ts"].agg(["min", "max", "size"])
    sess["length_min"] = (sess["max"] - sess["min"]) / 60.0
    by_player = sess.groupby(level=0)
    feats["session_count"] = by_player.size()
    feats["mean_session_minutes"] = by_player["length_min"].mean()
    feats["max_session_minutes"] = by_player["length_min"].max()
    feats["mean_plays_per_session"] = by_player["size"].mean()
    feats["total_playtime_minutes"] = by_player["length_min"].sum()

    # ---- engagement trajectory across the OP window ----------------------
    daily = (ev.groupby(["player_id", "day_index"], sort=False).size()
               .unstack(fill_value=0)
               .reindex(columns=range(op_days), fill_value=0))
    daily.columns = [f"day{c}_plays" for c in daily.columns]
    feats = feats.join(daily)

    day_cols = list(daily.columns)
    first_day = daily[day_cols[0]]
    last_day = daily[day_cols[-1]]
    feats["first_vs_last_day_ratio"] = (last_day + 1) / (first_day + 1)
    feats["activity_slope"] = _slope(
        ev.assign(one=1.0)
          .groupby(["player_id", "day_index"], sort=False)["one"].sum()
          .reset_index(name="plays"),
        "player_id", "day_index", "plays")

    # consecutivePlayRatio: share of adjacent day pairs that are both active
    active_mat = (daily.to_numpy() > 0)
    if active_mat.shape[1] > 1:
        pairs = (active_mat[:, :-1] & active_mat[:, 1:]).sum(axis=1)
        feats["consecutive_play_ratio"] = pairs / (active_mat.shape[1] - 1)
    else:
        feats["consecutive_play_ratio"] = np.nan

    # ---- score / progression --------------------------------------------
    if ev["score"].notna().any():
        sc = ev.dropna(subset=["score"])
        sg = sc.groupby("player_id", sort=False)["score"]
        feats["score_best"] = sg.max()
        feats["score_mean"] = sg.mean()
        feats["score_worst"] = sg.min()
        feats["score_std"] = sg.std()
        feats["score_median"] = sg.median()
        sc = sc.assign(order=sc.groupby("player_id", sort=False).cumcount())
        feats = feats.join(_slope(sc, "player_id", "order", "score"))
        half = sc.groupby("player_id", sort=False)["order"].transform("max") / 2.0
        early = sc[sc["order"] <= half].groupby("player_id", sort=False)["score"].mean()
        late = sc[sc["order"] > half].groupby("player_id", sort=False)["score"].mean()
        feats["score_improvement"] = late - early

    # ---- difficulty / outcomes ------------------------------------------
    if ev["won"].notna().any():
        w = ev.dropna(subset=["won"])
        wg = w.groupby("player_id", sort=False)["won"]
        feats["attempt_count"] = wg.size()
        feats["win_ratio"] = wg.mean()
        feats["mean_outcome_std"] = wg.std()

        loss = w["won"].eq(0.0)
        block = (~loss).groupby(w["player_id"], sort=False).cumsum()
        streaks = loss.groupby([w["player_id"], block], sort=False).sum()
        feats["max_loss_streak"] = streaks.groupby(level=0).max()

    if ev["action"].notna().any():
        act = ev.dropna(subset=["action"])
        counts = (act.groupby(["player_id", "action"], sort=False).size()
                     .unstack(fill_value=0))
        total = counts.sum(axis=1).replace(0, np.nan)
        for name in ("fail", "quit", "complete"):
            if name in counts.columns:
                feats[f"{name}_ratio"] = counts[name] / total
        feats["attempts_started"] = counts.get("start", pd.Series(dtype=float))

    if ev["fail_state"].notna().any():
        fs = ev.dropna(subset=["fail_state"])
        feats["fail_state_diversity"] = fs.groupby("player_id", sort=False)["fail_state"].nunique()
        feats["fail_event_count"] = fs.groupby("player_id", sort=False).size()

    if ev["duration"].notna().any():
        dg = ev.dropna(subset=["duration"]).groupby("player_id", sort=False)["duration"]
        feats["mean_match_minutes"] = dg.mean() / 60.0
        feats["total_match_minutes"] = dg.sum() / 60.0

    # ---- monetisation ----------------------------------------------------
    spend = ev[ev["price"].notna() & (ev["price"] > 0)]
    if not spend.empty:
        sp = spend.groupby("player_id", sort=False)["price"]
        feats["purchase_count"] = sp.size()
        feats["purchase_total"] = sp.sum()
        feats["purchase_mean"] = sp.mean()
        feats["purchase_max"] = sp.max()
        feats["first_purchase_day"] = spend.groupby("player_id", sort=False)["day_index"].min()

        paid = spend[spend["currency"].eq("real")]
        if not paid.empty:
            pg = paid.groupby("player_id", sort=False)["price"]
            feats["paid_purchase_count"] = pg.size()
            feats["paid_purchase_total"] = pg.sum()

    # ---- context attributes for the fairness audit -----------------------
    if ev["platform"].notna().any():
        feats["platform"] = g["platform"].agg(
            lambda s: s.dropna().mode().iat[0] if s.notna().any() else "unknown")
    if ev["device"].notna().any():
        dev = g["device"].agg(
            lambda s: s.dropna().mode().iat[0] if s.notna().any() else "unknown")
        feats["device_family"] = _device_family(dev)

    feats = feats.reset_index()

    # Counting features are legitimately zero when the player never did the thing.
    zero_fill = [c for c in feats.columns
                 if c.startswith(("purchase", "paid_", "fail_", "attempts_"))
                 or c.endswith(("_count", "_ratio", "_plays"))]
    for c in zero_fill:
        if c in feats.columns and pd.api.types.is_numeric_dtype(feats[c]):
            feats[c] = feats[c].fillna(0.0)

    out = cohort[["player_id", "churn", "first_ts"]].merge(feats, on="player_id", how="inner")
    return out


def prune_features(df: pd.DataFrame, min_fill: float = 0.5,
                   max_missing_all: bool = True) -> pd.DataFrame:
    """Drop all-NaN and near-constant columns produced by games lacking a signal."""
    drop: list[str] = []
    for c in df.columns:
        if c in ID_COLS + [LABEL_COL] + CONTEXT_COLS or c == "first_ts":
            continue
        s = df[c]
        if max_missing_all and s.isna().all():
            drop.append(c)
        elif pd.api.types.is_numeric_dtype(s) and s.nunique(dropna=True) <= 1:
            drop.append(c)
        elif s.notna().mean() < min_fill:
            drop.append(c)
    if drop:
        print(f"  dropped {len(drop)} uninformative columns: {', '.join(drop[:8])}"
              + (" ..." if len(drop) > 8 else ""))
    return df.drop(columns=drop)


def feature_columns(df: pd.DataFrame) -> list[str]:
    """Model input columns: numeric, excluding identifiers, label and context."""
    exclude = set(ID_COLS + [LABEL_COL] + CONTEXT_COLS + ["first_ts"])
    return [c for c in df.columns
            if c not in exclude and pd.api.types.is_numeric_dtype(df[c])]
