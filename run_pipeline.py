"""End-to-end experiment runner.

    python run_pipeline.py                     # all games, full analysis
    python run_pipeline.py --games game1       # one game
    python run_pipeline.py --skip-lstm --skip-sensitivity
    python run_pipeline.py --max-players 50000 # subsample large cohorts

Stages per game:
  1. load the tidy event table produced by src.etl
  2. build the OP/CP labelled cohort
  3. engineer Observation-Period features
  4. train Logistic Regression / Random Forest / XGBoost, evaluate on a held-out set
  5. explain the best model with SHAP
  6. audit subgroup performance
  7. train an LSTM on daily sequences using the same split
  8. repeat labelling across several OP/CP windows as a sensitivity check

All tables land in outputs/tables and all figures in outputs/figures.
"""

from __future__ import annotations

import argparse
import json
import time
import warnings

import pandas as pd

from src import config, explainability, fairness, features, labeling, modeling
from src import sequence, visualisation

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def load_events(game: str) -> pd.DataFrame:
    path = config.INTERIM_DIR / f"{game}_events.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing. Run: python -m src.etl --game {game}")
    return pd.read_parquet(path)


def window_sensitivity(events: pd.DataFrame, game: str,
                       max_players: int | None) -> pd.DataFrame:
    """Re-label and re-fit XGBoost across several OP/CP settings."""
    rows = []
    for op, cp in config.WINDOW_GRID:
        try:
            cohort = labeling.build_cohort(events, op, cp)
        except ValueError as exc:
            print(f"  OP{op}/CP{cp}: skipped ({exc})")
            continue

        if max_players and len(cohort) > max_players:
            cohort = cohort.sample(max_players, random_state=config.RANDOM_STATE)

        feats = features.prune_features(features.build_features(events, cohort, op))
        split = modeling.make_split(feats)
        model = modeling.build_models(split.y_train)["xgboost"]
        model.fit(split.X_train, split.y_train)
        proba = model.predict_proba(split.X_test)[:, 1]
        metrics = modeling.evaluate(split.y_test, proba)

        rows.append({"game": game, "op_days": op, "cp_days": cp,
                     "players": len(cohort),
                     "churn_rate": float(cohort["churn"].mean()),
                     "roc_auc": metrics["roc_auc"],
                     "pr_auc_retained": metrics["pr_auc_retained"]})
        print(f"  OP{op}/CP{cp}: {len(cohort):,} players | "
              f"churn {cohort['churn'].mean():.1%} | ROC-AUC {metrics['roc_auc']:.4f}")

    df = pd.DataFrame(rows)
    if not df.empty:
        df.to_csv(config.TABLE_DIR / f"{game}_window_sensitivity.csv", index=False)
        visualisation.plot_window_sensitivity(df, game)
    return df


def run_game(game: str, args) -> dict:
    print(f"\n{'=' * 70}\n{game.upper()}\n{'=' * 70}")
    t0 = time.time()

    events = load_events(game)
    print(f"  {len(events):,} events / {events['player_id'].nunique():,} players")

    cohort = labeling.build_cohort(
        events, config.OBSERVATION_PERIOD_DAYS, config.CHURN_PREDICTION_PERIOD_DAYS)

    if args.max_players and len(cohort) > args.max_players:
        cohort = cohort.sample(args.max_players, random_state=config.RANDOM_STATE)
        print(f"  subsampled cohort to {len(cohort):,} players")

    feats = features.prune_features(
        features.build_features(events, cohort, config.OBSERVATION_PERIOD_DAYS))
    feats.to_parquet(config.PROCESSED_DIR / f"{game}_features.parquet", index=False)
    print(f"  feature matrix {feats.shape[0]:,} x {feats.shape[1]}")

    visualisation.plot_cohort_overview(feats, game)

    results, art = modeling.train_all(feats, game, temporal=args.temporal,
                                      do_cv=not args.skip_cv)
    split, curves, best = art["split"], art["curves"], art["best"]
    visualisation.plot_model_curves(curves, split.y_test, game)

    # ---- SHAP on the best model ----------------------------------------
    importance = pd.DataFrame()
    if not args.skip_shap:
        print("  computing SHAP values...")
        importance = explainability.explain(
            art["fitted"][best], split.X_test, game, best)

    # ---- fairness audit -------------------------------------------------
    fair_report = pd.DataFrame()
    if not args.skip_fairness:
        test_ctx = feats.iloc[split.test_idx].reset_index(drop=True)
        thr = float(results.loc[results["model"] == best, "best_threshold"].iat[0])
        fair_report, _ = fairness.run_audit(
            test_ctx, split.y_test.to_numpy(), curves[best]["proba"], thr, game)
        visualisation.plot_fairness(fair_report, game)

    # ---- LSTM on the same split ----------------------------------------
    if not args.skip_lstm:
        print("  training LSTM on daily sequences...")
        X, y, _ = sequence.build_sequences(events, cohort,
                                           config.OBSERVATION_PERIOD_DAYS)
        _, proba, y_test = sequence.train_lstm(
            X, y, split.train_idx, split.test_idx, epochs=args.epochs)
        lstm_metrics = modeling.evaluate(pd.Series(y_test), proba)
        lstm_metrics.update({"model": "lstm", "game": game})
        print(f"    {'lstm':22s} ROC-AUC {lstm_metrics['roc_auc']:.4f} | "
              f"PR-AUC(retained) {lstm_metrics['pr_auc_retained']:.4f} | "
              f"balanced acc {lstm_metrics['balanced_accuracy']:.4f}")

        results = pd.concat([results, pd.DataFrame([lstm_metrics])],
                            ignore_index=True)
        curves["lstm"] = {"proba": proba}
        results.to_csv(config.TABLE_DIR / f"{game}_model_results.csv", index=False)

    # ---- OP/CP sensitivity ---------------------------------------------
    sens = pd.DataFrame()
    if not args.skip_sensitivity:
        print("  OP/CP window sensitivity:")
        sens = window_sensitivity(events, game, args.max_players)

    print(f"  {game} finished in {time.time() - t0:.0f}s")

    return {"game": game, "results": results, "importance": importance,
            "fairness": fair_report, "sensitivity": sens,
            "cohort_summary": labeling.cohort_summary(
                cohort, game, config.OBSERVATION_PERIOD_DAYS,
                config.CHURN_PREDICTION_PERIOD_DAYS)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--games", nargs="+", default=list(config.GAMES),
                    choices=list(config.GAMES))
    ap.add_argument("--max-players", type=int, default=None,
                    help="subsample cohorts larger than this")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--temporal", action="store_true",
                    help="split by cohort entry date instead of at random")
    ap.add_argument("--skip-cv", action="store_true")
    ap.add_argument("--skip-shap", action="store_true")
    ap.add_argument("--skip-fairness", action="store_true")
    ap.add_argument("--skip-lstm", action="store_true")
    ap.add_argument("--skip-sensitivity", action="store_true")
    args = ap.parse_args()

    started = time.time()
    all_results, all_cohorts = [], []

    for game in args.games:
        try:
            out = run_game(game, args)
        except Exception as exc:  # keep going so one game cannot sink the run
            print(f"  !! {game} failed: {type(exc).__name__}: {exc}")
            import traceback
            traceback.print_exc()
            continue
        all_results.append(out["results"])
        all_cohorts.append(out["cohort_summary"])

    if all_results:
        combined = pd.concat(all_results, ignore_index=True)
        combined.to_csv(config.TABLE_DIR / "all_model_results.csv", index=False)
        visualisation.plot_cross_game_summary(combined)

        cohorts = pd.DataFrame(all_cohorts)
        cohorts.to_csv(config.TABLE_DIR / "cohort_summary.csv", index=False)

        print(f"\n{'=' * 70}\nSUMMARY\n{'=' * 70}")
        print(cohorts.to_string(index=False))
        print()
        cols = ["game", "model", "roc_auc", "pr_auc_retained",
                "baseline_pr_retained", "balanced_accuracy"]
        print(combined[cols].round(4).to_string(index=False))

        with open(config.TABLE_DIR / "run_metadata.json", "w") as fh:
            json.dump({"games": args.games,
                       "op_days": config.OBSERVATION_PERIOD_DAYS,
                       "cp_days": config.CHURN_PREDICTION_PERIOD_DAYS,
                       "runtime_seconds": round(time.time() - started, 1)},
                      fh, indent=2)

    print(f"\nTotal runtime {time.time() - started:.0f}s")
    print(f"Tables  -> {config.TABLE_DIR}")
    print(f"Figures -> {config.FIGURE_DIR}")


if __name__ == "__main__":
    main()
