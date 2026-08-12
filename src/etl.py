"""Streaming ETL: raw Zenodo archives -> tidy per-game event tables (Parquet).

The raw archives do not fit comfortably in memory once decompressed
(game2 is ~4.3 GB of NDJSON across 8 parts; game3's bulkplayers.json is
~933 MB of nested JSON), so every game is parsed as a stream and flushed to
Parquet in row-group batches rather than being materialised as one DataFrame.

Output schema (one row per in-game event), written to data/interim/<game>_events.parquet:

    player_id  str     anonymised player identity
    ts         int64   unix epoch SECONDS
    event      str     raw event name from the source log
    action     str     outcome of a gameplay attempt (complete/fail/quit/start)
    fail_state str     reason an attempt failed, when the game records one
    score      float64 points scored in the event
    price      float64 in-game currency spent in the event
    currency   str     which currency was spent (soft / gacha / real)
    duration   float64 event duration in SECONDS
    won        float64 1.0 win, 0.0 loss, NaN when not applicable
    platform   str     iOS / Android / web
    device     str     device model string, when recorded
    authed     bool    whether the identity is a registered account

Run:  python -m src.etl --game all
"""

from __future__ import annotations

import argparse
import time
import zipfile
from pathlib import Path

import ijson
import orjson
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from . import config
from .zip64_reader import iter_member_lines

SCHEMA = pa.schema([
    ("player_id", pa.string()),
    ("ts", pa.int64()),
    ("event", pa.string()),
    ("action", pa.string()),
    ("fail_state", pa.string()),
    ("score", pa.float64()),
    ("price", pa.float64()),
    ("currency", pa.string()),
    ("duration", pa.float64()),
    ("won", pa.float64()),
    ("platform", pa.string()),
    ("device", pa.string()),
    ("authed", pa.bool_()),
])

BATCH_ROWS = 500_000


class _ParquetSink:
    """Accumulate row dicts and flush them to Parquet in fixed-size batches."""

    def __init__(self, path: Path, schema: pa.Schema = SCHEMA):
        self.path = path
        self.schema = schema
        self._rows: list[dict] = []
        self._writer: pq.ParquetWriter | None = None
        self.total = 0

    def add(self, row: dict) -> None:
        self._rows.append(row)
        if len(self._rows) >= BATCH_ROWS:
            self.flush()

    def flush(self) -> None:
        if not self._rows:
            return
        table = pa.Table.from_pylist(self._rows, schema=self.schema)
        if self._writer is None:
            self._writer = pq.ParquetWriter(self.path, self.schema, compression="zstd")
        self._writer.write_table(table)
        self.total += len(self._rows)
        self._rows.clear()

    def close(self) -> int:
        self.flush()
        if self._writer is not None:
            self._writer.close()
        return self.total

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def _blank() -> dict:
    return {name: None for name in SCHEMA.names}


# --------------------------------------------------------------------------
# game1 - "Dodge the Mud": flat CSV, one score submission per row.
# --------------------------------------------------------------------------

def etl_game1() -> Path:
    src = config.RAW_DIR / "rawdata_game1.csv"
    out = config.INTERIM_DIR / "game1_events.parquet"

    df = pd.read_csv(src)
    tidy = pd.DataFrame({
        "player_id": df["device"].astype(str),
        "ts": pd.to_numeric(df["time"], errors="coerce"),
        "event": "play",
        "action": None,
        "fail_state": None,
        "score": pd.to_numeric(df["score"], errors="coerce"),
        "price": float("nan"),
        "currency": None,
        "duration": float("nan"),
        "won": float("nan"),
        "platform": "Android",
        "device": None,
        "authed": True,
    })
    tidy = tidy.dropna(subset=["ts"])
    tidy["ts"] = tidy["ts"].astype("int64")
    tidy = tidy.sort_values(["player_id", "ts"], ignore_index=True)

    pq.write_table(pa.Table.from_pandas(tidy, schema=SCHEMA, preserve_index=False),
                   out, compression="zstd")
    print(f"[game1] {len(tidy):,} events -> {out.name}")
    return out


# --------------------------------------------------------------------------
# game2 - casual racing game: NDJSON event stream across 8 archive parts.
# --------------------------------------------------------------------------

# Purchases are recorded in in-game currencies. 'gacha' bought via the paid
# loot-box path is the closest available proxy for real monetisation; 'soft'
# currency is earned through play. They are kept distinct rather than summed.
_PAID_TYPES = {"gacha_paid"}


def etl_game2() -> Path:
    src = config.RAW_DIR / "rawdata_game2.zip"
    out = config.INTERIM_DIR / "game2_events.parquet"
    started = time.time()
    skipped = 0

    with zipfile.ZipFile(src) as zf:
        parts = sorted(n for n in zf.namelist()
                       if n.startswith("part-") and not n.endswith("/"))

    # 7 of the 8 parts are Deflate64, which stdlib zipfile cannot open, so
    # every part is streamed through the local reader instead.
    with _ParquetSink(out) as sink:
        for part in parts:
            for line in iter_member_lines(src, part):
                line = line.strip()
                if not line:
                    continue
                try:
                    d = orjson.loads(line)
                except orjson.JSONDecodeError:
                    skipped += 1
                    continue

                uid = d.get("uid")
                raw_ts = d.get("time")
                if not uid or raw_ts is None:
                    skipped += 1
                    continue

                props = d.get("properties") or {}
                ev = d.get("event")
                ptype = props.get("type")

                row = _blank()
                row["player_id"] = str(uid)
                row["ts"] = int(raw_ts) // 1000  # source is epoch milliseconds
                row["event"] = ev
                row["action"] = props.get("action")
                row["fail_state"] = props.get("fail_state")
                row["platform"] = d.get("platform")
                row["device"] = d.get("device")
                row["authed"] = True

                reward = props.get("reward")
                if isinstance(reward, (int, float)):
                    row["score"] = float(reward)

                price = props.get("price")
                if isinstance(price, (int, float)):
                    row["price"] = float(price)
                    cur = props.get("currency")
                    if ptype in _PAID_TYPES:
                        row["currency"] = "real"
                    elif isinstance(cur, str):
                        row["currency"] = cur
                    elif ev == "softSale":
                        row["currency"] = "soft"

                # A completed race is the game's notion of a successful attempt.
                if ev == "progress" and ptype == "race":
                    act = props.get("action")
                    if act == "complete":
                        row["won"] = 1.0
                    elif act in ("fail", "quit"):
                        row["won"] = 0.0

                sink.add(row)

            print(f"[game2]   {part}: running total "
                  f"{sink.total + len(sink._rows):,}", flush=True)

        total = sink.total + len(sink._rows)

    print(f"[game2] {total:,} events ({skipped:,} skipped) "
          f"in {time.time() - started:.0f}s -> {out.name}")
    return out


# --------------------------------------------------------------------------
# game3 - TagPro: two match-keyed JSON objects that must be joined.
# --------------------------------------------------------------------------

class _ClosingBraceStream:
    """Wrap a byte stream and close a dangling top-level JSON object at EOF.

    The published bulkplayers.json is truncated: it ends with the final player
    list's "}]" and never emits the outer object's closing brace, so a strict
    streaming parser reports a premature EOF after ~1.4M valid records. Rather
    than discarding the file, the missing brace is supplied at EOF. Only a
    closing brace is ever added; no record content is fabricated.
    """

    def __init__(self, fh):
        self._fh = fh
        self._last = b""
        self._patched = False
        self.repaired = False

    def read(self, size: int = -1) -> bytes:
        # A zero-length request is a probe, not end-of-stream; answering it
        # with the patch would consume the one-shot repair before EOF.
        if size == 0:
            return b""

        data = self._fh.read(size)
        if data:
            self._last = data[-8:]
            return data
        if not self._patched:
            self._patched = True
            if self._last.rstrip().endswith(b"]"):
                self.repaired = True
                return b"}"
        return b""


def _stream_matches(zf: zipfile.ZipFile) -> dict[str, tuple[int, float, list]]:
    """match_id -> (epoch_seconds, duration_seconds, [team_scores])."""
    matches: dict[str, tuple[int, float, list]] = {}
    with zf.open("bulkmatches.json") as raw:
        fh = _ClosingBraceStream(raw)
        for match_id, meta in ijson.kvitems(fh, ""):
            if not isinstance(meta, dict):
                continue
            date = meta.get("date")
            if date is None:
                continue
            duration = meta.get("duration")
            scores = [t.get("score") for t in (meta.get("teams") or [])
                      if isinstance(t, dict)]
            matches[str(match_id)] = (
                int(date),
                float(duration) / 1000.0 if duration is not None else float("nan"),
                scores,
            )
    return matches


def etl_game3() -> Path:
    src = config.RAW_DIR / "rawdata_game3.zip"
    out = config.INTERIM_DIR / "game3_events.parquet"
    started = time.time()

    with zipfile.ZipFile(src) as zf:
        print("[game3] indexing matches...")
        matches = _stream_matches(zf)
        print(f"[game3] {len(matches):,} matches indexed "
              f"({time.time() - started:.0f}s); streaming players...")

        unmatched = 0
        with _ParquetSink(out) as sink, zf.open("bulkplayers.json") as raw:
            fh = _ClosingBraceStream(raw)
            for match_id, players in ijson.kvitems(fh, ""):
                meta = matches.get(str(match_id))
                if meta is None or not isinstance(players, list):
                    unmatched += 1
                    continue
                ts, duration, scores = meta

                for p in players:
                    if not isinstance(p, dict):
                        continue
                    name = p.get("name")
                    if not name:
                        continue

                    # team is 1-indexed into the match's team list
                    won = float("nan")
                    team = p.get("team")
                    if isinstance(team, int) and len(scores) == 2 and all(
                        isinstance(s, (int, float)) for s in scores
                    ):
                        idx = team - 1
                        if idx in (0, 1):
                            mine, theirs = scores[idx], scores[1 - idx]
                            won = float(mine > theirs) if mine != theirs else 0.5

                    row = _blank()
                    row["player_id"] = str(name)
                    row["ts"] = int(ts)
                    row["event"] = "match"
                    row["action"] = None
                    row["fail_state"] = None
                    row["score"] = (float(p["score"])
                                    if isinstance(p.get("score"), (int, float))
                                    else float("nan"))
                    row["price"] = float("nan")
                    row["currency"] = None
                    row["duration"] = duration
                    row["won"] = won
                    row["platform"] = "web"
                    row["device"] = None
                    # Guest players share reusable display names, so only
                    # authenticated accounts are stable identities.
                    row["authed"] = bool(p.get("auth", False))

                    sink.add(row)

            total = sink.total + len(sink._rows)

    print(f"[game3] {total:,} player-match events ({unmatched:,} unmatched) "
          f"in {time.time() - started:.0f}s -> {out.name}")
    return out


ETL = {"game1": etl_game1, "game2": etl_game2, "game3": etl_game3}


def main() -> None:
    ap = argparse.ArgumentParser(description="Convert raw archives to event Parquet.")
    ap.add_argument("--game", default="all", choices=["all", *config.GAMES])
    args = ap.parse_args()

    games = config.GAMES if args.game == "all" else (args.game,)
    for g in games:
        print(f"\n=== ETL {g} ===")
        ETL[g]()


if __name__ == "__main__":
    main()
