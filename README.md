# Player Churn Prediction and Engagement Optimisation in Online Gaming Platforms

Machine learning pipeline for predicting player churn from raw behavioural
logs, explaining the drivers of disengagement with SHAP, and auditing whether
the resulting model performs equally well for different kinds of player.

## V5 evaluation notebooks

The eleven notebooks under [notebooks](notebooks) contain saved outputs. The
original random-split results remain available in the earlier notebooks and
[outputs/tables](outputs/tables). The V5 outputs are grouped separately in
[outputs/v5](outputs/v5).

| Notebook | Evaluation | Saved results |
|---|---|---|
| [08](notebooks/08_game1_temporal_validation.ipynb) | Game 1 model comparison on later players | [Game 1 metrics](outputs/v5/game1_temporal_results.json) |
| [09](notebooks/09_cross_game_temporal_validation.ipynb) | Later-player comparison across all three games | [Cross-game metrics](outputs/v5/three_game_temporal_results.json) |
| [10](notebooks/10_game3_filter_impact.ipynb) | Matched comparison of Game 3 account filters | [Filter comparison](outputs/v5/game3_filter_impact_results.json) |

On the same 4,826 Game 3 test players, applying the account filter consistently
raised overall ROC-AUC from 0.8026 to 0.8114. The confidence interval for the
change among one-event players includes zero. The
[full random-split rerun](outputs/v5/three_game_rerun) includes the environment
and a comparison with the originally published metrics.

To reproduce the notebooks, open them with `notebooks/` as the working
directory. Run [Notebook 00](notebooks/00_setup.ipynb) to download the pinned
pipeline and verify the data. Install the pinned checkout's dependencies with
`python -m pip install -r .pipeline/requirements.txt`, then use
[Notebook 01](notebooks/01_data_preparation.ipynb) to extract the data. The
notebooks use the same local `.pipeline` checkout for imports and outputs.

## Data

Raw play logs from three commercial games, released under CC-BY 4.0 alongside
Kim, Choi, Lee and Rhee, *Churn prediction of mobile and online casual games using play
log data*, PLOS ONE 12(7), 2017.

- Dataset: <https://zenodo.org/record/166035>
- Paper: <https://doi.org/10.1371/journal.pone.0180735>

| Game | Description | Events | Players | Span |
|------|-------------|--------|---------|------|
| game1 | *Dodge the Mud* — Android casual action | 153,929 | 25,956 | 496 days |
| game2 | Casual racing (iOS + Android), with purchases | 7,620,167 | 79,436 | 107 days |
| game3 | *TagPro* — web capture-the-flag, with match outcomes | 3,516,753 | 91,094 | 213 days |

Totals (11.29M events, 196,486 players) reproduce the figures reported in the
source paper (10.87M records, 193,443 players) to within 4%, which serves as an
independent check on the ETL.

### Two data defects handled in code

1. **Deflate64.** Seven of game2's eight archive parts use compression method 9,
   which CPython's `zipfile` cannot open. `src/zip64_reader.py` streams them
   directly (no 7-Zip dependency, flat memory use).
2. **Truncated JSON.** `bulkplayers.json` in game3 is delivered without its
   closing brace, so strict parsers abort after ~411k records. `src/etl.py`
   supplies the missing brace at EOF; no record content is fabricated.

## Churn definition

Following the source paper, churn is defined over two windows:

- **Observation Period (OP)** — the first *n* days after a player's first ever
  session. All features are computed here.
- **Churn Prediction Period (CP)** — the following *m* days. A player is a
  churner if they record **zero** sessions in this window.

Defaults are OP=5, CP=10 days, with a sensitivity grid over
(3,7), (5,10), (7,14) and (5,30) to confirm conclusions are not an artefact of
one threshold.

Two censoring guards are applied that the source paper leaves implicit:

- **Right guard** — the full OP+CP window must fall inside the observed log,
  otherwise "no sessions in CP" only means the data ended.
- **Left guard** — players first seen at the very start of the log may have been
  active earlier, so they are not genuinely new and are excluded.

## Setup

```bash
pip install -r requirements.txt
```

Download the three raw files from <https://zenodo.org/record/166035> into
`data/raw/`, then build the tidy event tables:

```bash
python -m src.etl --game all
```

## Running the analysis

```bash
python run_pipeline.py
```

Useful flags:

```bash
python run_pipeline.py --games game1 --skip-lstm --skip-sensitivity
python run_pipeline.py --max-players 50000 --temporal
```

| Flag | Effect |
|------|--------|
| `--games` | restrict to specific games |
| `--max-players` | subsample large cohorts |
| `--temporal` | split by cohort entry date instead of at random |
| `--epochs` | LSTM training epochs |
| `--skip-cv` / `--skip-shap` / `--skip-fairness` / `--skip-lstm` / `--skip-sensitivity` | skip stages |

## Layout

```
src/
  config.py           paths, window parameters, random seeds
  zip64_reader.py     Deflate64 streaming ZIP reader
  etl.py              raw archives -> tidy event Parquet
  labeling.py         OP/CP cohort construction and churn labels
  features.py         Observation-Period behavioural features
  modeling.py         LR / RF / XGBoost training and evaluation
  sequence.py         LSTM over daily behaviour sequences
  explainability.py   SHAP global and local explanations
  fairness.py         subgroup performance audit
  visualisation.py    result figures
run_pipeline.py       end-to-end runner
outputs/tables        metrics, SHAP rankings, fairness reports (CSV/JSON)
outputs/figures       ROC/PR/calibration, SHAP plots, fairness charts
```

## Evaluation notes

These cohorts are heavily churn-dominated (>90% churn in game1), so accuracy
and churn-class precision are close to meaningless — predicting "everyone
churns" already scores above 0.90. Results therefore lead with **ROC-AUC**,
**retained-class PR-AUC against its base rate**, and **balanced accuracy**,
since the operationally useful question is which players will *stay*.

## Licence and attribution

The data is CC-BY 4.0 and must be attributed to Kim, Choi, Lee and Rhee (2017). This
code is coursework built on top of that release.
