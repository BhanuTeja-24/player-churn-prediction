"""Figures for the results chapter."""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from . import config

sns.set_theme(style="whitegrid", context="paper")
PALETTE = {"logistic_regression": "#4C72B0", "random_forest": "#DD8452",
           "xgboost": "#55A868", "lstm": "#C44E52"}


def _colour(name: str) -> str:
    return PALETTE.get(name, "#8172B3")


def plot_model_curves(curves: dict, y_test, game: str) -> None:
    """ROC, precision-recall (retained class) and calibration in one figure."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    y = np.asarray(y_test)

    for name, c in curves.items():
        axes[0].plot(c["fpr"], c["tpr"], label=name, color=_colour(name), lw=1.8)
    axes[0].plot([0, 1], [0, 1], "k--", lw=1, label="chance")
    axes[0].set(xlabel="False positive rate", ylabel="True positive rate",
                title=f"{game} - ROC (churn class)")
    axes[0].legend(fontsize=8)

    from sklearn.metrics import precision_recall_curve
    for name, c in curves.items():
        prec, rec, _ = precision_recall_curve(1 - y, 1 - c["proba"])
        axes[1].plot(rec, prec, label=name, color=_colour(name), lw=1.8)
    base = 1 - y.mean()
    axes[1].axhline(base, ls="--", c="k", lw=1, label=f"baseline {base:.3f}")
    axes[1].set(xlabel="Recall", ylabel="Precision",
                title=f"{game} - PR (retained class)")
    axes[1].legend(fontsize=8)

    for name, c in curves.items():
        axes[2].plot(c["cal_pred"], c["cal_true"], "o-", label=name,
                     color=_colour(name), lw=1.5, ms=4)
    axes[2].plot([0, 1], [0, 1], "k--", lw=1)
    axes[2].set(xlabel="Mean predicted churn probability",
                ylabel="Observed churn fraction",
                title=f"{game} - calibration")
    axes[2].legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(config.FIGURE_DIR / f"{game}_model_curves.png", dpi=160)
    plt.close(fig)


def plot_cohort_overview(feats: pd.DataFrame, game: str) -> None:
    """Descriptive view of the cohort: churn balance and key distributions."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))

    counts = feats["churn"].value_counts().sort_index()
    axes[0].bar(["retained", "churned"], [counts.get(0, 0), counts.get(1, 0)],
                color=["#55A868", "#C44E52"])
    axes[0].set(title=f"{game} - class balance", ylabel="players")
    for i, v in enumerate([counts.get(0, 0), counts.get(1, 0)]):
        axes[0].text(i, v, f"{v:,}", ha="center", va="bottom", fontsize=9)

    if "play_count" in feats.columns:
        d = feats[feats["play_count"] <= feats["play_count"].quantile(0.99)]
        sns.histplot(data=d, x="play_count", hue="churn", bins=40,
                     element="step", stat="density", common_norm=False, ax=axes[1])
        axes[1].set(title=f"{game} - plays during OP (99th pct clipped)")

    day_cols = [c for c in feats.columns if c.endswith("_plays") and c.startswith("day")]
    if day_cols:
        means = feats.groupby("churn")[day_cols].mean().T
        means.index = [c.replace("_plays", "") for c in means.index]
        means.plot(ax=axes[2], marker="o")
        axes[2].set(title=f"{game} - mean daily activity", xlabel="day of OP",
                    ylabel="mean plays")
        axes[2].legend(["retained", "churned"], fontsize=8)

    fig.tight_layout()
    fig.savefig(config.FIGURE_DIR / f"{game}_cohort_overview.png", dpi=160)
    plt.close(fig)


def plot_fairness(report: pd.DataFrame, game: str) -> None:
    if report.empty:
        return
    attrs = report["attribute"].unique()
    fig, axes = plt.subplots(1, len(attrs), figsize=(4.6 * len(attrs), 4.2),
                             squeeze=False)

    for ax, attr in zip(axes[0], attrs):
        sub = report[report["attribute"] == attr].sort_values("roc_auc")
        ax.barh(sub["group"], sub["roc_auc"], color="#4C72B0")
        ax.axvline(0.5, ls="--", c="k", lw=1)
        ax.set(xlabel="ROC-AUC", title=f"{attr}", xlim=(0.4, 1.0))
        for i, (_, r) in enumerate(sub.iterrows()):
            ax.text(r["roc_auc"] + 0.005, i, f"n={int(r['n']):,}",
                    va="center", fontsize=7)

    fig.suptitle(f"{game} - subgroup discrimination at a shared threshold", fontsize=11)
    fig.tight_layout()
    fig.savefig(config.FIGURE_DIR / f"{game}_fairness.png", dpi=160)
    plt.close(fig)


def plot_window_sensitivity(df: pd.DataFrame, game: str) -> None:
    """Show that conclusions are not an artefact of one OP/CP choice."""
    if df.empty:
        return
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    labels = [f"OP{r.op_days}/CP{r.cp_days}" for r in df.itertuples()]

    axes[0].bar(labels, df["churn_rate"], color="#C44E52")
    axes[0].set(title=f"{game} - churn rate by window", ylabel="churn rate")
    axes[1].bar(labels, df["roc_auc"], color="#55A868")
    axes[1].axhline(0.5, ls="--", c="k", lw=1)
    axes[1].set(title=f"{game} - XGBoost ROC-AUC by window", ylabel="ROC-AUC",
                ylim=(0.4, 1.0))
    for ax in axes:
        ax.tick_params(axis="x", rotation=20)

    fig.tight_layout()
    fig.savefig(config.FIGURE_DIR / f"{game}_window_sensitivity.png", dpi=160)
    plt.close(fig)


def plot_cross_game_summary(results: pd.DataFrame) -> None:
    """One comparison chart across all games and models."""
    if results.empty:
        return
    fig, ax = plt.subplots(figsize=(9, 4.6))
    pivot = results.pivot_table(index="game", columns="model", values="roc_auc")
    pivot.plot(kind="bar", ax=ax, color=[_colour(c) for c in pivot.columns])
    ax.axhline(0.5, ls="--", c="k", lw=1)
    ax.set(ylabel="ROC-AUC", title="Churn prediction performance across games",
           ylim=(0.4, 1.0))
    ax.legend(fontsize=8, ncol=2)
    ax.tick_params(axis="x", rotation=0)
    fig.tight_layout()
    fig.savefig(config.FIGURE_DIR / "cross_game_summary.png", dpi=160)
    plt.close(fig)
