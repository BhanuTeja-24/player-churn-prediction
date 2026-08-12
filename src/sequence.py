"""LSTM churn model over daily behaviour sequences.

The tabular models see the Observation Period collapsed into summary statistics.
A recurrent model instead sees the window as an ordered sequence of days, so it
can in principle pick up *shape* - a player whose activity decays across the
window differs from one with the same total spread evenly, even though many
aggregate features are identical.

Sequences are (op_days x channels) tensors built from the same OP-restricted
events as the tabular features, and the model is trained and evaluated on the
identical train/test split so the comparison is like-for-like.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from . import config

DAY = 86_400

CHANNELS = ["plays", "active", "session_count", "playtime_min",
            "mean_score", "spend", "win_rate"]


def build_sequences(events: pd.DataFrame, cohort: pd.DataFrame,
                    op_days: int) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Return (X of shape [n_players, op_days, n_channels], y, player_ids)."""
    ev = events.merge(cohort[["player_id", "first_ts", "op_end"]],
                      on="player_id", how="inner")
    ev = ev[ev["ts"] < ev["op_end"]].copy()
    ev["day_index"] = ((ev["ts"] - ev["first_ts"]) // DAY).astype(int)
    ev = ev[(ev["day_index"] >= 0) & (ev["day_index"] < op_days)]

    ev["gap"] = ev.sort_values(["player_id", "ts"]).groupby("player_id", sort=False)["ts"].diff()
    ev["new_session"] = ev["gap"].isna() | (ev["gap"] > 1800)

    grp = ev.groupby(["player_id", "day_index"], sort=False)
    daily = grp.agg(
        plays=("ts", "size"),
        session_count=("new_session", "sum"),
        playtime_min=("ts", lambda s: (s.max() - s.min()) / 60.0),
        mean_score=("score", "mean"),
        spend=("price", lambda s: s[s > 0].sum()),
        win_rate=("won", "mean"),
    ).reset_index()
    daily["active"] = 1.0

    order = {p: i for i, p in enumerate(cohort["player_id"].to_numpy())}
    n = len(order)
    X = np.zeros((n, op_days, len(CHANNELS)), dtype=np.float32)

    rows = daily["player_id"].map(order).to_numpy()
    cols = daily["day_index"].to_numpy()
    keep = ~pd.isna(rows)
    rows = rows[keep].astype(int)
    cols = cols[keep].astype(int)

    for ci, ch in enumerate(CHANNELS):
        vals = pd.to_numeric(daily.loc[keep, ch], errors="coerce").fillna(0.0).to_numpy()
        X[rows, cols, ci] = vals.astype(np.float32)

    y = cohort["churn"].to_numpy().astype(np.float32)
    return X, y, cohort["player_id"].tolist()


class ChurnLSTM(nn.Module):
    def __init__(self, n_channels: int, hidden: int = 64, layers: int = 1,
                 dropout: float = 0.2):
        super().__init__()
        self.lstm = nn.LSTM(n_channels, hidden, num_layers=layers,
                            batch_first=True,
                            dropout=dropout if layers > 1 else 0.0)
        self.head = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden, 32), nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.head(out[:, -1, :]).squeeze(-1)


def _standardise(X_train: np.ndarray, *others: np.ndarray):
    """Per-channel z-scoring using training statistics only."""
    mu = X_train.reshape(-1, X_train.shape[-1]).mean(axis=0)
    sd = X_train.reshape(-1, X_train.shape[-1]).std(axis=0)
    sd[sd == 0] = 1.0
    return [(A - mu) / sd for A in (X_train, *others)]


def train_lstm(X: np.ndarray, y: np.ndarray, train_idx: np.ndarray,
               test_idx: np.ndarray, epochs: int = 30, batch_size: int = 512,
               lr: float = 1e-3, patience: int = 5, verbose: bool = True):
    """Train on train_idx, early-stop on a validation slice, score test_idx."""
    from sklearn.metrics import roc_auc_score

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(config.RANDOM_STATE)

    # Carve a validation set out of the training indices only.
    rng = np.random.default_rng(config.RANDOM_STATE)
    perm = rng.permutation(len(train_idx))
    n_val = max(1, int(0.15 * len(train_idx)))
    val_idx = train_idx[perm[:n_val]]
    fit_idx = train_idx[perm[n_val:]]

    Xf, Xv, Xt = _standardise(X[fit_idx], X[val_idx], X[test_idx])
    yf, yv, yt = y[fit_idx], y[val_idx], y[test_idx]

    model = ChurnLSTM(X.shape[-1]).to(device)
    pos = float(yf.sum())
    neg = float(len(yf) - pos)
    pos_weight = torch.tensor([neg / max(pos, 1.0)], device=device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    opt = torch.optim.Adam(model.parameters(), lr=lr)

    loader = DataLoader(
        TensorDataset(torch.from_numpy(Xf).float(), torch.from_numpy(yf).float()),
        batch_size=batch_size, shuffle=True)

    Xv_t = torch.from_numpy(Xv).float().to(device)
    Xt_t = torch.from_numpy(Xt).float().to(device)

    best_auc, best_state, stale = -np.inf, None, 0

    for epoch in range(1, epochs + 1):
        model.train()
        total = 0.0
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            loss = criterion(model(xb), yb)
            loss.backward()
            opt.step()
            total += loss.item() * len(xb)

        model.eval()
        with torch.no_grad():
            val_proba = torch.sigmoid(model(Xv_t)).cpu().numpy()
        auc = roc_auc_score(yv, val_proba) if len(np.unique(yv)) > 1 else np.nan

        if auc > best_auc:
            best_auc, stale = auc, 0
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        else:
            stale += 1

        if verbose and (epoch % 5 == 0 or epoch == 1):
            print(f"    epoch {epoch:3d} | loss {total / len(fit_idx):.4f} | "
                  f"val ROC-AUC {auc:.4f}")

        if stale >= patience:
            if verbose:
                print(f"    early stop at epoch {epoch} (best val AUC {best_auc:.4f})")
            break

    if best_state is not None:
        model.load_state_dict(best_state)

    model.eval()
    with torch.no_grad():
        proba = torch.sigmoid(model(Xt_t)).cpu().numpy()

    return model, proba, yt
