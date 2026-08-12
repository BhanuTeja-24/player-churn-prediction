"""Central configuration: paths and churn-labelling parameters.

Churn is defined following Perianez et al. (PLOS ONE 2017, doi:10.1371/journal.pone.0180735),
who released the raw logs used here (Zenodo doi:10.5281/zenodo.166035):

    A churner is a player whose first ever session falls inside the Observation
    Period (OP) and who then records zero sessions during the following Churn
    Prediction Period (CP).

All predictive features are computed *only* from the OP window, so no
information from the CP label window can leak into the model.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = ROOT / "data" / "raw"
INTERIM_DIR = ROOT / "data" / "interim"
PROCESSED_DIR = ROOT / "data" / "processed"

OUTPUT_DIR = ROOT / "outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"
MODEL_DIR = OUTPUT_DIR / "models"
TABLE_DIR = OUTPUT_DIR / "tables"

for _d in (INTERIM_DIR, PROCESSED_DIR, FIGURE_DIR, MODEL_DIR, TABLE_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# Labelling windows, in days.
OBSERVATION_PERIOD_DAYS = 5
CHURN_PREDICTION_PERIOD_DAYS = 10

# Sensitivity analysis grid: (OP, CP) pairs re-run to show the results are not
# an artefact of one arbitrary threshold choice.
WINDOW_GRID = [(3, 7), (5, 10), (7, 14), (5, 30)]

# A player is only usable if the full OP+CP window fits inside the observed
# data range; otherwise "no sessions in CP" is censoring, not churn.
MIN_SESSIONS_IN_OP = 1

RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5

GAMES = ("game1", "game2", "game3")
