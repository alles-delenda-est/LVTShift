"""Offline tests for Paris/Lyon (arrondissement data codes) and the
extra-muros territories (per-commune neutrality, aggregation, ingest helpers).

Run: python -m pytest -q test_territories.py
"""

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402
import export_web as ew  # noqa: E402
import ingest  # noqa: E402


# ------------------------------------------------------------------ #
# configuration
# ------------------------------------------------------------------ #

def test_paris_lyon_data_codes():
    assert config.PARIS.insee_code == "75056"            # REI / fiscal code
    assert config.PARIS.data_codes == tuple(f"751{n:02d}" for n in range(1, 21))
    assert config.LYON.insee_code == "69123"
    assert config.LYON.data_codes == tuple(f"6938{n}" for n in range(1, 10))
    # ordinary communes: data code == fiscal code
    assert config.CAHORS.data_codes == ("46042",)


def test_territory_membership():
    t = config.TERRITORIES
    paris = t["paris-extra-muros"]["members"]
    lyon = t["lyon-extra-muros"]["members"]
    assert len(paris) == 122 and len(lyon) == 57
    assert len(set(paris)) == 122 and len(set(lyon)) == 57
    # existing panel configs are reused, not duplicated
    assert "montreuil" in paris and "villeurbanne" in lyon
    assert "lyon" not in lyon and "paris" not in paris
    for key in paris:
        assert config.COMMUNES[key].departement in ("92", "93", "94")
    for key in lyon:
        assert config.COMMUNES[key].departement == "69"
    # site keys must satisfy the site's loader guard /^[a-z0-9_-]+$/
    for key in list(config.COMMUNES) + list(t):
        assert re.fullmatch(r"[a-z0-9_-]+", key), key


def test_commune_key_ascii():
    assert config.commune_key("L'Haÿ-les-Roses") == "l-hay-les-roses"
    assert config.commune_key("Saint-Denis") == "saint-denis"


def test_slug_keeps_legacy_stems():
    # legacy panel output names must not move (existing CSVs / site JSON)
    assert config.slug_of(config.SETE) == "sète"
    assert config.slug_of(config.PARIS) == "paris"
    assert config.slug_of(config.COMMUNES["l-hay-les-roses"]) == "l-hay-les-roses"


# ------------------------------------------------------------------ #
# ingest helpers (no network)
# ------------------------------------------------------------------ #

def test_per_code_splits_by_arrondissement():
    parcels = pd.DataFrame({"idpar": ["75101000AB0001", "75101000AB0002",
                                      "75102000AC0001"]})
    seen = []

    def fake(cfg, sub):
        seen.append((cfg.insee_code, len(sub)))
        return pd.DataFrame({"idpar": sub["idpar"], "code": cfg.insee_code})

    out = ingest._per_code(fake, config.PARIS, parcels)
    assert seen == [("75101", 2), ("75102", 1)]
    assert len(out) == 3
    # the sub-config must not leak back into the shared config
    assert config.PARIS.insee_code == "75056"


def test_wfs_unkeyed_layer_splits_instead_of_truncating(monkeypatch):
    """A full first page on an unkeyed layer must tile the bbox, never STARTINDEX."""
    calls = []

    def fake_get(url, *a, **k):
        calls.append(url)
        assert "STARTINDEX" not in url
        if len(calls) == 1:   # whole bbox: page full
            feats = [{"geometry": {"type": "Point", "coordinates": [i, 0]},
                      "properties": {"i": i}} for i in range(3)]
        else:                 # each quadrant: the same shared feature + one own
            feats = [{"geometry": {"type": "Point", "coordinates": [0, 0]},
                      "properties": {"i": 0}},
                     {"geometry": {"type": "Point", "coordinates": [len(calls), 1]},
                      "properties": {"i": len(calls)}}]
        return json.dumps({"features": feats}).encode()

    monkeypatch.setattr(ingest, "_get", fake_get)
    feats = ingest._wfs_features("wfs_du:zone_urba", (0, 0, 1000, 1000), page=3,
                                 paginate=False)
    assert len(calls) == 5                    # 1 full page + 4 quadrants
    assert len(feats) == 1 + 4                # shared feature de-duplicated


def test_get_cache_roundtrip(monkeypatch, tmp_path):
    hits = []

    class Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            hits.append(1)
            return b"payload"

    monkeypatch.setattr(ingest.urllib.request, "urlopen", lambda *a, **k: Resp())
    monkeypatch.setattr(ingest, "CACHE_DIR", str(tmp_path))
    assert ingest._get("https://example.org/x") == b"payload"
    assert ingest._get("https://example.org/x") == b"payload"
    assert len(hits) == 1                     # second call served from disk
    assert not list(tmp_path.glob("*.part"))  # no torn temp files left behind


def test_get_does_not_retry_404(monkeypatch):
    import urllib.error
    n = []

    def boom(*a, **k):
        n.append(1)
        raise urllib.error.HTTPError("u", 404, "nf", {}, None)

    monkeypatch.setattr(ingest.urllib.request, "urlopen", boom)
    monkeypatch.setattr(ingest, "CACHE_DIR", None)
    with pytest.raises(urllib.error.HTTPError):
        ingest._get("https://example.org/missing")
    assert len(n) == 1


# ------------------------------------------------------------------ #
# territory aggregation
# ------------------------------------------------------------------ #

def _member_frame(seed: int, n: int, levy: float, land_bias: float) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    land = rng.uniform(50_000, 400_000, n) * land_bias
    imp = rng.uniform(50_000, 300_000, n)
    cur = rng.uniform(0.5, 1.5, n)
    cur = levy * cur / cur.sum()
    cats = rng.choice(["Single Family Residential", "Condominium", "Commercial"], n)
    return pd.DataFrame({
        "taxable_land_value": land, "taxable_improvement_value": imp,
        "current_tax": cur, "property_category": cats,
    })


def test_territory_sensitivity_is_neutral_per_commune():
    """Base leg must keep EACH commune's own revenue (no cross-commune shift)."""
    a = _member_frame(1, 300, 1_000_000.0, 1.0).assign(_commune="a")
    b = _member_frame(2, 200, 5_000_000.0, 3.0).assign(_commune="b")
    df = pd.concat([a, b], ignore_index=True)
    for key, sub in df.groupby("_commune"):
        s = sub["taxable_land_value"].sum() / (
            sub["taxable_land_value"].sum() + sub["taxable_improvement_value"].sum())
        chg = ew._tilted_change(sub, s, 4.0, float(sub["current_tax"].sum()))
        assert abs(chg.sum()) < 1e-6 * sub["current_tax"].sum(), key
    band = ew.build_territory_sensitivity(df, 4.0)
    assert set(band) == {"delta_pt", "base", "low", "high"}
    # more land weight -> more redistribution, monotone across the band
    assert band["low"]["gross_pct_of_levy"] <= band["high"]["gross_pct_of_levy"] + 1e-9


def test_territory_payload_shape(tmp_path, monkeypatch):
    """Payload aggregates members, reports missing ones, passes the leak guard."""
    t = {"name": "Test ring", "departement": "99", "members": ["ma", "mb", "mc"]}
    monkeypatch.setitem(config.TERRITORIES, "test-ring", t)
    for k in ("ma", "mb", "mc"):
        monkeypatch.setitem(config.COMMUNES, k, config.CommuneConfig(
            f"990{len(k):02d}", k.upper(), "99", key=k))
    for k, seed in (("ma", 3), ("mb", 4)):      # mc deliberately has no output
        f = _member_frame(seed, 120, 2e6, 1.5)
        f["new_tax"] = f["current_tax"] * 1.0
        f["tax_change"] = 0.0
        f.loc[f.index[:40], "tax_change"] = 10.0
        f.loc[f.index[40:80], "tax_change"] = -10.0
        f["tax_change_pct"] = 100 * f["tax_change"] / f["current_tax"]
        f.to_csv(tmp_path / f"{k}.csv", index=False)
    p = ew.build_territory_payload("test-ring", out_dir=str(tmp_path))
    ew.assert_aggregate_only(p)
    assert p["kind"] == "territory"
    assert p["coverage"] == {"members_total": 3, "members_modeled": 2,
                             "members_missing": ["mc"]}
    assert p["headline"]["parcels_modeled"] == 240
    assert {m["commune_key"] for m in p["members"]} == {"ma", "mb"}


def test_within_commune_quintiles_reverse_a_pooling_artefact():
    """Two communes, each progressive inside; pooled ranking looks regressive."""
    rows = []
    # poor commune: everyone pays more, richer IRIS slightly more
    for i, inc in enumerate(np.repeat(np.arange(10, 15, 0.5), 10)):
        rows.append(("poor", inc * 1000.0, 5.0 + inc / 10))
    # rich commune: everyone pays less, richer IRIS slightly less negative
    for i, inc in enumerate(np.repeat(np.arange(30, 35, 0.5), 10)):
        rows.append(("rich", inc * 1000.0, -5.0 + inc / 100))
    df = pd.DataFrame(rows, columns=["_commune", "median_income", "tax_change_pct"])
    df["property_category"] = "Condominium"
    within, cov = ew.build_by_income_quintile_within(df)
    assert cov == 100.0
    meds = [q["median_change_pct"] for q in within]
    assert meds == sorted(meds), "within-commune gradient must be increasing"
    pooled = [q["median_change_pct"] for q in ew.build_by_income_quintile(df)]
    assert pooled[0] > pooled[-1], "pooled ranking shows the (spurious) regressive tilt"


def test_dvf_rate_limit_is_not_mistaken_for_a_missing_year(monkeypatch):
    import urllib.error

    def fake_get(url, *a, **k):
        if "/2023/" in url:
            raise urllib.error.HTTPError(url, 429, "too many", {}, None)
        raise urllib.error.HTTPError(url, 404, "nf", {}, None)

    monkeypatch.setattr(ingest, "_get", fake_get)
    with pytest.raises(urllib.error.HTTPError):
        ingest.fetch_dvf(config.CAHORS)


def test_cache_refuses_error_bodies_served_as_200():
    import gzip as _gz
    assert ingest._cacheable(_gz.compress(b'{"features": []}'))
    assert ingest._cacheable(b'{"results": []}')
    assert ingest._cacheable(b"id_mutation,date\n1,2024-01-01\n")
    assert not ingest._cacheable(b"")
    assert not ingest._cacheable(
        b'<?xml version="1.0"?><ows:ExceptionReport><ows:Exception/></ows:ExceptionReport>')
    assert not ingest._cacheable(b"<!DOCTYPE html><html>maintenance</html>")
    assert not ingest._cacheable(b"\x1f\x8b" + b"truncated")       # torn gzip
    assert not ingest._cacheable(b'{"results": [1, 2')            # torn JSON


def test_leak_guard_rejects_parcel_ids_and_iris_codes_by_value():
    base = {"commune_key": "x", "name": "X", "by_category": [], "by_improvement_ratio": []}
    ew.assert_aggregate_only(base)
    with pytest.raises(AssertionError, match="parcel id"):
        ew.assert_aggregate_only({**base, "name": "see 75101000AB0002"})
    with pytest.raises(AssertionError, match="IRIS"):
        ew.assert_aggregate_only({**base, "name": "751010101"})
    # ordinary 5-digit INSEE codes and euro amounts stay allowed
    ew.assert_aggregate_only({**base, "name": "75056",
                              "headline": {"neutral_levy_eur": 1840896539}})
    # nested headline keys are whitelisted too
    with pytest.raises(AssertionError, match="headline keys"):
        ew.assert_aggregate_only({**base, "headline": {"parcel_value": 1.0}})


def test_built_at_cap_pct_counts_only_built_parcels_at_the_bound():
    import export_web as ew
    df = pd.DataFrame({
        "taxable_land_value": [85.0] * 20 + [50.0] * 10 + [10.0],
        "taxable_improvement_value": [15.0] * 20 + [50.0] * 10 + [0.0],  # last: vacant
    })
    assert ew.built_at_cap_pct(df) == round(100 * 20 / 30, 1)
    # under 30 built parcels the % would describe individual parcels: withheld
    assert ew.built_at_cap_pct(df.iloc[:29]) is None
    assert ew.built_at_cap_pct(df.iloc[[30]]) is None
