"""Batch driver: model every member commune of an extra-muros territory.

Usage:
    python run_territory.py paris-extra-muros --workers 4
    python run_territory.py lyon-extra-muros --only bron venissieux
    python run_territory.py paris-extra-muros --rerun-failed

Each member runs `run_commune.py <key> --no-report` in its OWN process, so one
commune's crash or memory spike never takes down the batch, and each is held
revenue-neutral on its own levy. Raw downloads are shared through the on-disk
cache (output/cache), which makes the batch resumable: a member whose CSV
already exists is skipped unless --force. A status file
(output/logs/<territory>.status.json) records ok/failed per commune with the
tail of the error, so a failure is a documented finding, never a silent gap.
The aggregate itself is built afterwards by `export_web.py <territory>`.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from config import COMMUNES, TERRITORIES, slug_of

HERE = Path(__file__).resolve().parent


def _run_one(key: str, out_dir: Path, cache_dir: Path, log_dir: Path,
             timeout_s: int) -> dict:
    log = log_dir / f"{key}.log"
    cmd = [sys.executable, str(HERE / "run_commune.py"), key, "--no-report",
           "--out-dir", str(out_dir), "--cache-dir", str(cache_dir)]
    env = {**os.environ, "PYTHONUTF8": "1"}
    t0 = time.time()
    try:
        with open(log, "w", encoding="utf-8") as fh:
            rc = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, cwd=HERE,
                                env=env, timeout=timeout_s).returncode
    except subprocess.TimeoutExpired:
        rc = "timeout"
    tail = log.read_text(encoding="utf-8", errors="replace").strip().splitlines()[-6:]
    return {"key": key, "status": "ok" if rc == 0 else "failed", "returncode": rc,
            "seconds": round(time.time() - t0), "log": str(log),
            "error_tail": None if rc == 0 else tail}


def _write_status(path: Path, territory: str, results: dict) -> None:
    """Atomic write, so an interrupted batch never leaves a torn status file."""
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(
        {"territory": territory,
         "results": sorted(results.values(), key=lambda r: r["key"])},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("territory", choices=sorted(TERRITORIES))
    ap.add_argument("--workers", type=int, default=4,
                    help="parallel communes (each its own process; default 4 — "
                         "be gentle with the public WFS/DPE APIs)")
    ap.add_argument("--only", nargs="+", help="restrict to these member keys")
    ap.add_argument("--force", action="store_true", help="re-run even if output exists")
    ap.add_argument("--rerun-failed", action="store_true",
                    help="only members marked failed in the last status file")
    ap.add_argument("--out-dir", default="output")
    ap.add_argument("--cache-dir", default="output/cache")
    ap.add_argument("--timeout", type=int, default=3600, help="per-commune seconds")
    a = ap.parse_args()

    # relative paths resolve against lvtshift-fr/ (where the defaults live)
    out_dir = (HERE / a.out_dir).resolve()
    cache_dir = (HERE / a.cache_dir).resolve()
    log_dir = out_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    status_path = log_dir / f"{a.territory}.status.json"
    previous = {}
    if status_path.exists():
        try:
            previous = {r["key"]: r
                        for r in json.loads(status_path.read_text("utf-8"))["results"]}
        except (ValueError, KeyError):
            print(f"warning: unreadable {status_path.name}; starting a fresh record")

    members = TERRITORIES[a.territory]["members"]
    if a.only:
        unknown = set(a.only) - set(members)
        if unknown:
            ap.error(f"not members of {a.territory}: {sorted(unknown)}")
        members = [m for m in members if m in a.only]
    if a.rerun_failed:
        members = [m for m in members if previous.get(m, {}).get("status") == "failed"]

    todo = [m for m in members
            if a.force or a.rerun_failed
            or not (out_dir / f"{slug_of(COMMUNES[m])}.csv").exists()]
    print(f"{a.territory}: {len(members)} selected, {len(todo)} to run, "
          f"{len(members) - len(todo)} already modelled")

    results = dict(previous)
    for m in members:
        if m not in todo and m not in results:
            results[m] = {"key": m, "status": "ok", "returncode": 0,
                          "note": "existing output reused"}
    # Build each département's exempt-property flags once, before the workers
    # start: otherwise every worker would download and parse the same national
    # DGFiP files at the same time (≈1 GB of memory each).
    if todo:
        import exemptions
        import ingest
        ingest.CACHE_DIR = str(cache_dir)
        for dep in sorted({COMMUNES[k].departement for k in todo}):
            print(f"preparing exempt-property flags for département {dep}", flush=True)
            exemptions.flags_for_departement(dep)
    with ThreadPoolExecutor(max_workers=max(1, a.workers)) as pool:
        futs = {pool.submit(_run_one, k, out_dir, cache_dir, log_dir, a.timeout): k
                for k in todo}
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            results[r["key"]] = r
            print(f"[{i}/{len(todo)}] {r['key']}: {r['status']} ({r.get('seconds')}s)",
                  flush=True)
            # write after every commune so an interrupted batch leaves a true record
            _write_status(status_path, a.territory, results)

    _write_status(status_path, a.territory, results)
    failed = [k for k, r in results.items() if r["status"] != "ok"]
    print(f"done: {len(results) - len(failed)} ok, {len(failed)} failed"
          + (f" -> {failed}" if failed else ""))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
