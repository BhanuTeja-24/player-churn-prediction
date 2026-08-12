"""Cohort construction and churn labelling.

Implements the Observation Period / Churn Prediction Period definition of
Perianez et al. (PLOS ONE 2017) with two additions that the original write-up
leaves implicit but which matter for a defensible evaluation:

1. **Right-censoring guard.** A player is only admitted to the cohort if their
   entire OP+CP window falls inside the observed data range. Otherwise "no
   sessions during CP" merely means the log ended, not that the player left.

2. **Left-censoring guard.** A player whose first observed event sits at the
   very start of the log may have been playing before logging began, so they
   are not genuinely "new". Players are therefore required to first appear at
   least `burn_in_days` after the log starts.

Both guards shrink the cohort but remove label noise that would otherwise
inflate measured performance.
"""

from __future__ import annotations

import pandas as pd

from . import config

DAY = 86_400


def build_cohort(
    events: pd.DataFrame,
    op_days: int = config.OBSERVATION_PERIOD_DAYS,
    cp_days: int = config.CHURN_PREDICTION_PERIOD_DAYS,
    burn_in_days: int | None = None,
    authed_only: bool = True,
) -> pd.DataFrame:
    """Return one labelled row per eligible player.

    Columns: player_id, first_ts, op_end, cp_end, n_events_op, n_events_cp, churn
    """
    if burn_in_days is None:
        burn_in_days = op_days

    if authed_only and "authed" in events.columns:
        events = events[events["authed"].fillna(True)]

    if events.empty:
        raise ValueError("No events left after filtering; cannot build a cohort.")

    log_start = int(events["ts"].min())
    log_end = int(events["ts"].max())

    first_ts = events.groupby("player_id", sort=False)["ts"].min().rename("first_ts")
    cohort = first_ts.reset_index()

    op_secs = op_days * DAY
    cp_secs = cp_days * DAY
    cohort["op_end"] = cohort["first_ts"] + op_secs
    cohort["cp_end"] = cohort["op_end"] + cp_secs

    n_all = len(cohort)
    # Left guard: must appear after the burn-in so they are plausibly new.
    cohort = cohort[cohort["first_ts"] >= log_start + burn_in_days * DAY]
    n_left = len(cohort)
    # Right guard: the full OP+CP window must be observable.
    cohort = cohort[cohort["cp_end"] <= log_end]
    n_right = len(cohort)

    if cohort.empty:
        raise ValueError(
            f"No players survive censoring guards for OP={op_days}, CP={cp_days}. "
            f"Log spans only {(log_end - log_start) / DAY:.1f} days."
        )

    # Count activity in each window for the surviving cohort.
    ev = events.merge(cohort[["player_id", "first_ts", "op_end", "cp_end"]],
                      on="player_id", how="inner")

    in_op = ev["ts"] < ev["op_end"]
    in_cp = (ev["ts"] >= ev["op_end"]) & (ev["ts"] < ev["cp_end"])

    n_op = (ev[in_op].groupby("player_id", sort=False).size()
            .rename("n_events_op"))
    n_cp = (ev[in_cp].groupby("player_id", sort=False).size()
            .rename("n_events_cp"))

    cohort = (cohort.merge(n_op, on="player_id", how="left")
                    .merge(n_cp, on="player_id", how="left"))
    cohort["n_events_op"] = cohort["n_events_op"].fillna(0).astype(int)
    cohort["n_events_cp"] = cohort["n_events_cp"].fillna(0).astype(int)

    cohort = cohort[cohort["n_events_op"] >= config.MIN_SESSIONS_IN_OP]
    cohort["churn"] = (cohort["n_events_cp"] == 0).astype(int)

    cohort = cohort.reset_index(drop=True)

    print(
        f"  cohort: {n_all:,} players -> {n_left:,} after left guard "
        f"-> {n_right:,} after right guard -> {len(cohort):,} with OP activity | "
        f"churn rate {cohort['churn'].mean():.1%}"
    )
    return cohort


def cohort_summary(cohort: pd.DataFrame, game: str, op_days: int, cp_days: int) -> dict:
    return {
        "game": game,
        "op_days": op_days,
        "cp_days": cp_days,
        "players": len(cohort),
        "churners": int(cohort["churn"].sum()),
        "churn_rate": float(cohort["churn"].mean()),
        "median_events_op": float(cohort["n_events_op"].median()),
    }
