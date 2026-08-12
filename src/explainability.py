"""SHAP explainability for the churn classifiers.

The source study for this data (Perianez et al. 2017) ranked features only by
single-feature predictive power, which cannot show the *direction* of an
effect, interactions, or why an individual player was flagged. SHAP supplies
all three, which is what turns a churn score into an actionable retention
decision.

Produces, per game:
  <game>_shap_beeswarm.png      global effect direction and magnitude
  <game>_shap_bar.png           mean |SHAP| feature ranking
  <game>_shap_dependence_*.png  effect shape for the top features
  <game>_shap_waterfall_*.png   individual explanations (high/low risk players)
  <game>_shap_importance.csv    ranked mean |SHAP| values
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from sklearn.pipeline import Pipeline

from . import config

MAX_SHAP_SAMPLES = 5_000


def _unwrap(model):
    """Return (estimator, transform) so pipelines can be explained too."""
    if isinstance(model, Pipeline):
        est = model.steps[-1][1]
        pre = Pipeline(model.steps[:-1]) if len(model.steps) > 1 else None
        return est, pre
    return model, None


def explain(model, X: pd.DataFrame, game: str, model_name: str,
            max_samples: int = MAX_SHAP_SAMPLES) -> pd.DataFrame:
    """Compute SHAP values and write the standard plot set. Returns the ranking."""
    est, pre = _unwrap(model)

    if len(X) > max_samples:
        X = X.sample(max_samples, random_state=config.RANDOM_STATE)

    Xt = X
    if pre is not None:
        Xt = pd.DataFrame(pre.transform(X), columns=X.columns, index=X.index)

    is_tree = est.__class__.__name__ in (
        "XGBClassifier", "RandomForestClassifier", "GradientBoostingClassifier")

    if is_tree:
        explainer = shap.TreeExplainer(est)
        sv = explainer(Xt, check_additivity=False)
    else:
        # Linear models: explain against a median background.
        background = shap.maskers.Independent(Xt, max_samples=min(500, len(Xt)))
        explainer = shap.Explainer(est, background)
        sv = explainer(Xt)

    # Random forests return one array per class; keep the churn class.
    if sv.values.ndim == 3:
        sv = sv[:, :, 1]

    stem = f"{game}_{model_name}"

    plt.figure()
    shap.plots.beeswarm(sv, max_display=18, show=False)
    plt.title(f"{game} - SHAP value by feature ({model_name})", fontsize=11)
    plt.tight_layout()
    plt.savefig(config.FIGURE_DIR / f"{stem}_shap_beeswarm.png", dpi=160)
    plt.close()

    plt.figure()
    shap.plots.bar(sv, max_display=18, show=False)
    plt.title(f"{game} - mean |SHAP| ({model_name})", fontsize=11)
    plt.tight_layout()
    plt.savefig(config.FIGURE_DIR / f"{stem}_shap_bar.png", dpi=160)
    plt.close()

    importance = (pd.DataFrame({
        "feature": X.columns,
        "mean_abs_shap": np.abs(sv.values).mean(axis=0),
        # Sign of the correlation between feature value and its SHAP value
        # tells us whether more of the feature pushes toward churn.
        "direction": [
            np.sign(np.corrcoef(Xt.iloc[:, i].fillna(Xt.iloc[:, i].median()),
                                sv.values[:, i])[0, 1])
            if np.nanstd(Xt.iloc[:, i]) > 0 else 0.0
            for i in range(X.shape[1])
        ],
    }).sort_values("mean_abs_shap", ascending=False).reset_index(drop=True))
    importance["pushes_toward"] = np.where(importance["direction"] > 0,
                                           "churn", "retention")
    importance.to_csv(config.TABLE_DIR / f"{stem}_shap_importance.csv", index=False)

    for feature in importance["feature"].head(4):
        plt.figure()
        shap.plots.scatter(sv[:, feature], show=False)
        plt.title(f"{game} - {feature}", fontsize=11)
        plt.tight_layout()
        plt.savefig(config.FIGURE_DIR / f"{stem}_shap_dependence_{feature}.png", dpi=160)
        plt.close()

    # Individual explanations: the most and least at-risk players in the sample.
    totals = sv.values.sum(axis=1)
    for label, pos in (("highest_risk", int(np.argmax(totals))),
                       ("lowest_risk", int(np.argmin(totals)))):
        plt.figure()
        shap.plots.waterfall(sv[pos], max_display=14, show=False)
        plt.title(f"{game} - {label.replace('_', ' ')} player", fontsize=11)
        plt.tight_layout()
        plt.savefig(config.FIGURE_DIR / f"{stem}_shap_waterfall_{label}.png", dpi=160)
        plt.close()

    print(f"  SHAP top features: "
          + ", ".join(f"{r.feature}({r.pushes_toward[:3]})"
                      for r in importance.head(6).itertuples()))
    return importance
