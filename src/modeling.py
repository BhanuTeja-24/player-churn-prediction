"""Model training and evaluation for churn classification.

Three classifiers are compared on identical splits:

  * Logistic Regression - interpretable linear baseline (scaled + imputed)
  * Random Forest       - bagged trees, robust to feature scaling
  * XGBoost             - gradient boosting, the strongest performer in the
                          source literature for this data

Evaluation deliberately reports metrics for BOTH classes. The cohorts here are
heavily churn-dominated (>90% churn in game1), so a model that predicts "churn"
for everyone already scores >0.90 accuracy and ~0.93 average precision on the
churn class. The operationally interesting question - "which players will
stay?" - is the minority class, so retained-class average precision and
balanced accuracy are the headline numbers alongside ROC-AUC.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from . import config, features as feat_mod


@dataclass
class SplitData:
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    train_idx: np.ndarray
    test_idx: np.ndarray
    columns: list[str] = field(default_factory=list)


def make_split(df: pd.DataFrame, temporal: bool = False,
               test_size: float = config.TEST_SIZE) -> SplitData:
    """Stratified random split, or a time-ordered split on cohort entry date.

    The temporal option trains on players who joined earlier and tests on later
    arrivals, which mirrors how such a model is actually deployed.
    """
    cols = feat_mod.feature_columns(df)
    X, y = df[cols], df[feat_mod.LABEL_COL]

    if temporal and "first_ts" in df.columns:
        order = np.argsort(df["first_ts"].to_numpy(), kind="stable")
        cut = int(len(order) * (1 - test_size))
        train_idx, test_idx = order[:cut], order[cut:]
    else:
        idx = np.arange(len(df))
        train_idx, test_idx = train_test_split(
            idx, test_size=test_size, stratify=y,
            random_state=config.RANDOM_STATE)

    return SplitData(
        X_train=X.iloc[train_idx], X_test=X.iloc[test_idx],
        y_train=y.iloc[train_idx], y_test=y.iloc[test_idx],
        train_idx=train_idx, test_idx=test_idx, columns=cols,
    )


def build_models(y_train: pd.Series) -> dict[str, Pipeline | XGBClassifier]:
    """Instantiate the three classifiers with imbalance handling."""
    pos = int(y_train.sum())
    neg = int(len(y_train) - pos)
    # Ratio of retained to churned; caps runaway weights on extreme splits.
    scale_pos_weight = float(neg) / max(pos, 1)

    return {
        "logistic_regression": Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("clf", LogisticRegression(max_iter=2000, class_weight="balanced",
                                       random_state=config.RANDOM_STATE)),
        ]),
        "random_forest": Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("clf", RandomForestClassifier(
                n_estimators=400, min_samples_leaf=5, n_jobs=-1,
                class_weight="balanced_subsample",
                random_state=config.RANDOM_STATE)),
        ]),
        "xgboost": XGBClassifier(
            n_estimators=600, learning_rate=0.05, max_depth=6,
            subsample=0.8, colsample_bytree=0.8,
            min_child_weight=5, reg_lambda=1.0,
            scale_pos_weight=scale_pos_weight,
            tree_method="hist", eval_metric="logloss",
            n_jobs=-1, random_state=config.RANDOM_STATE,
        ),
    }


def evaluate(y_true: pd.Series, proba: np.ndarray) -> dict:
    """Metrics for both classes plus a decision-threshold summary."""
    y = np.asarray(y_true)
    churn_rate = float(y.mean())

    # Threshold that maximises F1 on the churn class.
    prec, rec, thr = precision_recall_curve(y, proba)
    f1s = np.divide(2 * prec * rec, prec + rec,
                    out=np.zeros_like(prec), where=(prec + rec) > 0)
    best = int(np.argmax(f1s[:-1])) if len(thr) else 0
    best_thr = float(thr[best]) if len(thr) else 0.5
    pred = (proba >= best_thr).astype(int)

    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()

    return {
        "roc_auc": float(roc_auc_score(y, proba)),
        "pr_auc_churn": float(average_precision_score(y, proba)),
        "pr_auc_retained": float(average_precision_score(1 - y, 1 - proba)),
        "baseline_pr_churn": churn_rate,
        "baseline_pr_retained": 1 - churn_rate,
        "lift_retained": float(average_precision_score(1 - y, 1 - proba) /
                               max(1 - churn_rate, 1e-9)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "f1_churn": float(f1_score(y, pred, zero_division=0)),
        "f1_retained": float(f1_score(1 - y, 1 - pred, zero_division=0)),
        "brier": float(brier_score_loss(y, proba)),
        "best_threshold": best_thr,
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def cross_validate(model, X: pd.DataFrame, y: pd.Series,
                   folds: int = config.CV_FOLDS) -> dict:
    cv = StratifiedKFold(n_splits=folds, shuffle=True,
                         random_state=config.RANDOM_STATE)
    scores = cross_val_score(model, X, y, cv=cv, scoring="roc_auc", n_jobs=1)
    return {"cv_roc_auc_mean": float(scores.mean()),
            "cv_roc_auc_std": float(scores.std())}


def train_all(df: pd.DataFrame, game: str, temporal: bool = False,
              do_cv: bool = True) -> tuple[pd.DataFrame, dict]:
    """Train every model, evaluate on the held-out test set, persist artefacts."""
    split = make_split(df, temporal=temporal)
    print(f"  train {len(split.X_train):,} / test {len(split.X_test):,} | "
          f"{len(split.columns)} features | "
          f"churn rate train {split.y_train.mean():.1%}")

    rows, fitted, curves = [], {}, {}

    for name, model in build_models(split.y_train).items():
        t0 = time.time()
        model.fit(split.X_train, split.y_train)
        proba = model.predict_proba(split.X_test)[:, 1]

        metrics = evaluate(split.y_test, proba)
        metrics["model"] = name
        metrics["game"] = game
        metrics["fit_seconds"] = round(time.time() - t0, 1)

        if do_cv:
            metrics.update(cross_validate(model, split.X_train, split.y_train))

        rows.append(metrics)
        fitted[name] = model
        fpr, tpr, _ = roc_curve(split.y_test, proba)
        prec, rec, _ = precision_recall_curve(split.y_test, proba)
        frac_pos, mean_pred = calibration_curve(split.y_test, proba, n_bins=10,
                                                strategy="quantile")
        curves[name] = {"fpr": fpr, "tpr": tpr, "precision": prec, "recall": rec,
                        "cal_true": frac_pos, "cal_pred": mean_pred, "proba": proba}

        print(f"    {name:22s} ROC-AUC {metrics['roc_auc']:.4f} | "
              f"PR-AUC(retained) {metrics['pr_auc_retained']:.4f} "
              f"(base {metrics['baseline_pr_retained']:.4f}) | "
              f"balanced acc {metrics['balanced_accuracy']:.4f} | "
              f"{metrics['fit_seconds']}s")

        joblib.dump(model, config.MODEL_DIR / f"{game}_{name}.joblib")

    results = pd.DataFrame(rows)
    lead = ["game", "model", "roc_auc", "pr_auc_retained", "baseline_pr_retained",
            "lift_retained", "balanced_accuracy", "f1_churn", "f1_retained", "brier"]
    results = results[lead + [c for c in results.columns if c not in lead]]
    results.to_csv(config.TABLE_DIR / f"{game}_model_results.csv", index=False)

    best = results.sort_values("roc_auc", ascending=False)["model"].iat[0]
    artefacts = {"split": split, "fitted": fitted, "curves": curves, "best": best}

    with open(config.TABLE_DIR / f"{game}_model_results.json", "w") as fh:
        json.dump(rows, fh, indent=2)

    print(f"  best model by ROC-AUC: {best}")
    return results, artefacts
