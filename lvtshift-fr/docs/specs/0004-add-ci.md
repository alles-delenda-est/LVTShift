# Spec 0004 — Add CI

**Status:** Draft · **Priority:** P1 (MEDIUM, one workflow file) ·
**Source:** external review PROPOSED_NEXT_STEPS #5 ·
**Est. effort:** ~1 hour

---

## 1. Problem

No `.github/` exists in the repo at all. Three test suites already pass but
nothing runs them: the upstream `tests/` pytest (4/4), the FR pilot unit tests
(`lvtshift-fr/test_units.py`, 21/21 after PR #14), and the FR synthetic
end-to-end (`lvtshift-fr/test_synthetic.py`, exercises the real solver). "Tests
exist" is not "tests run" — a regression in the pilot or a broken upstream merge
ships silently.

## 2. Goal

A single GitHub Actions workflow that runs all three suites on every PR and push,
so the FR synthetic end-to-end (a genuine regression net) actually executes.

## 3. Design

`.github/workflows/ci.yml`:

```yaml
name: CI
on:
  pull_request:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - name: Install deps
        run: pip install pandas numpy geopandas matplotlib seaborn pytest
      - name: Upstream unit tests
        run: python -m pytest tests/ -q
      - name: FR pilot unit tests
        run: cd lvtshift-fr && python test_units.py
      - name: FR synthetic end-to-end
        run: cd lvtshift-fr && python test_synthetic.py
```

Notes:
- `test_units.py` / `test_synthetic.py` are plain-assert runners (exit non-zero
  on failure) — they work under both `python x.py` and pytest; the plain form
  avoids pytest-collection surprises.
- geopandas pulls heavy geo deps; pin versions or use a `requirements-ci.txt` if
  install time is a concern. Cache pip.
- Network: the unit/synthetic suites are **offline** by design (no ingest), so CI
  needs no data.gouv access — keep it that way (do not add a live `run_commune`
  step to CI; that would depend on moving endpoints).

## 4. Files

| File | Change |
|---|---|
| `.github/workflows/ci.yml` | **new** — three offline suites on PR/push |
| `lvtshift-fr/requirements-ci.txt` | (optional) pinned CI deps for reproducibility |
| `README.md` / `METHODOLOGY.md` §8 | add a CI badge + note "suites run in CI" |

## 5. Acceptance criteria

- A PR that breaks any suite shows a red check.
- The three suites run offline (no network) and finish in a reasonable time.
- A CI badge is visible in the README.
- (Optional follow-up) a required status check on `main` via branch protection.

## 6. Risks

- **geopandas install flakiness** — pin GDAL-compatible versions or use a
  prebuilt wheel index; if install is slow, cache and/or split the geo-dependent
  synthetic test from the pure unit test into separate jobs.
- Do **not** put live-data `run_commune` in CI — it re-downloads from endpoints
  that "occasionally move" (config.py's own warning) and would make CI flaky and
  slow. Live runs stay manual.
