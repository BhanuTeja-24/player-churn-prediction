"""Execute the analysis notebooks top-to-bottom and save them with outputs.

    python run_notebooks.py                # run all, in order
    python run_notebooks.py 01 04          # run only notebooks starting 01 and 04
    python run_notebooks.py --check        # execute without saving (validation only)

Executed copies keep their filenames, so committing them gives a submittable
record of every result. A failure reports the offending cell and stops that
notebook, but the remaining notebooks still run.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

ROOT = Path(__file__).resolve().parent
NOTEBOOK_DIR = ROOT / "notebooks"
TIMEOUT_SECONDS = 3600


def run_one(path: Path, save: bool) -> bool:
    print(f"\n=== {path.name} ===")
    started = time.time()

    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(
        nb,
        timeout=TIMEOUT_SECONDS,
        kernel_name="python3",
        # Run from the project root so `from src import ...` resolves and
        # relative output paths land in outputs/.
        resources={"metadata": {"path": str(ROOT)}},
        allow_errors=False,
    )

    try:
        client.execute()
    except CellExecutionError as exc:
        print(f"  FAILED after {time.time() - started:.0f}s")
        # Surface the traceback tail; the last lines carry the actual error.
        lines = [ln for ln in str(exc).splitlines() if ln.strip()]
        for ln in lines[-12:]:
            print(f"    {ln[:200]}")
        if save:
            nbformat.write(nb, path)
        return False
    except Exception as exc:
        print(f"  FAILED: {type(exc).__name__}: {exc}")
        return False

    if save:
        nbformat.write(nb, path)
    print(f"  OK ({time.time() - started:.0f}s)")
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prefixes", nargs="*",
                    help="only run notebooks whose filename starts with these")
    ap.add_argument("--check", action="store_true",
                    help="execute but do not write outputs back")
    args = ap.parse_args()

    notebooks = sorted(NOTEBOOK_DIR.glob("*.ipynb"))
    if args.prefixes:
        notebooks = [n for n in notebooks
                     if any(n.name.startswith(p) for p in args.prefixes)]

    if not notebooks:
        print("No notebooks matched.")
        sys.exit(1)

    started = time.time()
    results = {n.name: run_one(n, save=not args.check) for n in notebooks}

    passed = sum(results.values())
    print(f"\n{'=' * 60}")
    for name, ok in results.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    print(f"{passed}/{len(results)} notebooks executed cleanly "
          f"in {time.time() - started:.0f}s")

    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
