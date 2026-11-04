"""Offline tests for social housing: today's exemptions, the landlord category,
and their disclosure.

Run: python -m pytest -q test_social_housing.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import estimate  # noqa: E402
import ingest  # noqa: E402
import social_housing as sh  # noqa: E402


def _dwelling(**kw):
    row = dict(DEPCOM="99001", X="1000", Y="1000", EPSG="2154", CONSTRUCT="1970",
               LOCAT="1971", PATRIMOINE="1970", ORIGINE="1", FINAN_CODE="13", CONV="1",
               DATCONV="", PLG_QP24="HZ", SURFHAB="60")
    row.update({k: str(v) for k, v in kw.items()})
    return row


def _status(*rows):
    return list(sh.dwelling_status(pd.DataFrame(rows))["status"])


def test_new_builds_are_exempt_for_15_or_25_years():
    assert _status(_dwelling(CONSTRUCT=2015)) == ["exempt"]              # within 15 years
    # 2005–09: 25 years only for a financing decision from July 2004
    assert _status(_dwelling(CONSTRUCT=2008, DATCONV="2006-03-01"),
                   _dwelling(CONSTRUCT=2008, DATCONV="2003-05-01")) == ["exempt", "taxable"]
    # no convention date: from 2007 taken as the 25-year rule, 2005–06 as not
    assert _status(_dwelling(CONSTRUCT=2007), _dwelling(CONSTRUCT=2006)) == ["exempt", "taxable"]
    # a decision from July 2004 cannot complete before 2005
    assert _status(_dwelling(CONSTRUCT=2003, DATCONV="2005-01-01")) == ["taxable"]
    # 2005–06: a late-2004 convention may follow an earlier decision
    assert _status(_dwelling(CONSTRUCT=2006, DATCONV="2004-09-01"),
                   _dwelling(CONSTRUCT=2006, DATCONV="2005-02-01"),
                   _dwelling(CONSTRUCT=2008, DATCONV="2004-09-01")) == ["taxable", "exempt", "exempt"]
    assert _status(_dwelling(CONSTRUCT=1985)) == ["taxable"]
    assert _status(_dwelling(CONSTRUCT=2015, ORIGINE=4)) == ["exempt"]   # VEFA


def test_intermediate_and_unconventioned_dwellings_are_never_exempt():
    assert _status(_dwelling(CONSTRUCT=2015, FINAN_CODE=16),             # PLI
                   _dwelling(CONSTRUCT=2015, FINAN_CODE=17),             # PCL
                   _dwelling(CONSTRUCT=2015, CONV=2),
                   # PLA ordinaire: every decision predates July 2004
                   _dwelling(CONSTRUCT=2012, FINAN_CODE=12)) == ["taxable"] * 4


def test_acquisitions_restart_the_clock_but_transfers_do_not():
    # bought into the social stock in 2012 (first let the next year)
    assert _status(_dwelling(ORIGINE=2, CONSTRUCT=1965, PATRIMOINE=2012, LOCAT=2013)) == ["exempt"]
    # passed between landlords in 2020 (first let in 1980): no new exemption
    assert _status(_dwelling(ORIGINE=3, CONSTRUCT=1975, PATRIMOINE=2020, LOCAT=1980)) == ["taxable"]
    # a recent new build passed to another landlord keeps its own exemption
    assert _status(_dwelling(ORIGINE=3, CONSTRUCT=2011, PATRIMOINE=2021, LOCAT=2012)) == ["exempt"]
    # acquired during the tax year: not this landlord's base yet
    assert _status(_dwelling(ORIGINE=2, CONSTRUCT=1965, PATRIMOINE=2025, LOCAT=2025)) == ["taxable"]
    # the convention date decides when known: a 1930 building first let in
    # 1930 but conventioned on its purchase in 2011 is a new acquisition…
    assert _status(_dwelling(ORIGINE=2, CONSTRUCT=1930, LOCAT=1930, PATRIMOINE=2011,
                             DATCONV="2012-03-01")) == ["exempt"]
    # …and one conventioned in 2001, long before its 2015 entry, a transfer
    assert _status(_dwelling(ORIGINE=3, CONSTRUCT=1930, LOCAT=2015, PATRIMOINE=2015,
                             DATCONV="2001-05-01")) == ["taxable"]


def test_qpv_abatement_applies_to_taxable_social_dwellings_only():
    st = sh.dwelling_status(pd.DataFrame([
        _dwelling(PLG_QP24="QN09318M"),                      # old, taxable, in a QPV
        _dwelling(PLG_QP24="QN09318M", CONSTRUCT=2015),      # exempt wins
        _dwelling(PLG_QP24="QN09318M", FINAN_CODE=16),       # PLI: not abated
        _dwelling(PLG_QP24="CSZ"),                           # commune without QPV
        # unconventioned: abated only with pre-1977 HLM financing
        _dwelling(PLG_QP24="QN09318M", CONV=2, FINAN_CODE=52),
        _dwelling(PLG_QP24="QN09318M", CONV=2, FINAN_CODE=49)]))
    assert list(st["status"]) == ["qpv", "exempt", "taxable", "taxable", "qpv", "taxable"]
    assert list(st["factor"]) == [0.7, 0.0, 1.0, 1.0, 0.7, 1.0]


def _pm(**kw):
    row = dict(dep="99", com="001", prefixe="", section="A", plan="1", code_droit="P",
               siren="111111111", groupe="0 - Personnes morales non remarquables",
               forme="5499", denomination="SCI X", bat="A", ent="01", niv="00", porte="01001",
               src="B")
    row.update(kw)
    row["idpar"] = "99001000A" + row["plan"].zfill(4)[-5:]
    return row


def test_social_landlords_from_groupe_legal_form_or_office_name():
    rows = pd.DataFrame([
        _pm(siren="1", groupe="5 - Office HLM"),
        _pm(siren="2", forme="5546"),                                     # SA d'HLM
        _pm(siren="3", forme="4140", denomination="LYON METROPOLE HABITAT"),
        _pm(siren="4", forme="4140", denomination="REGIE DES EAUX"),
        _pm(siren="5", groupe="5 - Office HLM", denomination="IN'LI"),    # intermediate rents
        _pm(siren="6", groupe="6 - Personnes morales représentant des sociétés"),
        # mostly groupe 5 with an SEM form on one row: HLM wins
        _pm(siren="7", forme="5515"), _pm(siren="7", groupe="5 - Office HLM"),
        _pm(siren="7", groupe="5 - Office HLM"),
        # one stray groupe-5 row on a private developer: not social
        _pm(siren="8", groupe="5 - Office HLM"), _pm(siren="8"), _pm(siren="8")])
    assert sh.social_sirens(rows) == {"1": "hlm", "2": "hlm", "3": "hlm", "6": "sem", "7": "hlm"}


def test_a_landlord_holds_a_unit_unless_someone_else_leases_it():
    hlm = dict(groupe="5 - Office HLM", siren="900", denomination="OPH")
    rows = pd.DataFrame([
        # parcel 1: an estate, land and two units held by the office
        _pm(plan="1", src="NB", bat="", ent="", niv="", porte="", **hlm),
        _pm(plan="1", porte="1", **hlm), _pm(plan="1", porte="2", **hlm),
        # parcel 2: the office owns, a private company holds an emphyteutic lease
        _pm(plan="2", **hlm), _pm(plan="2", code_droit="E", siren="222"),
        # parcel 3: the office is the building lessee on someone else's unit
        _pm(plan="3", code_droit="R", **hlm), _pm(plan="3", code_droit="B", siren="333"),
        # parcel 4: the office only manages
        _pm(plan="4", code_droit="G", **hlm)])
    out = sh.social_parcels(rows).set_index("idpar")
    assert set(out.index) == {"99001000A0001", "99001000A0003"}
    assert out.loc["99001000A0001", "units"] == 2 and out.loc["99001000A0001", "land"]
    assert out.loc["99001000A0003", "units"] == 1 and not out.loc["99001000A0003", "land"]
    assert (out["landlord"] == "hlm").all()
    assert set(out["landlord_key"]) == {sh._landlord_key("900")}     # a label, not the SIREN


def _grid(n=4, size=20.0):
    """n square parcels in a row, touching, in Lambert-93."""
    import geopandas as gpd
    from shapely.geometry import box
    return gpd.GeoDataFrame({"idpar": [f"99001000A{i:04d}" for i in range(n)]},
                            geometry=[box(i * size, 0, (i + 1) * size, size) for i in range(n)],
                            crs=ingest.CRS_METRIC)


def test_estates_share_their_dwellings_regime_and_mixed_parcels_their_floor():
    import geopandas as gpd
    from shapely.geometry import box
    pg = _grid(3)
    far = gpd.GeoDataFrame({"idpar": ["99001000A0009"]}, geometry=[box(500, 0, 520, 20)],
                           crs=ingest.CRS_METRIC)
    pg = pd.concat([pg, far], ignore_index=True)
    ids = list(pg["idpar"])
    social = pd.DataFrame({"idpar": ids[:2], "landlord": ["hlm", "hlm"], "units": [10, 10],
                           "land": [True, True], "landlord_key": ["k1", "k1"]})
    # all six dwellings' address points fall on the first estate parcel: half
    # exempt (2015), half taxable (1970); the far parcel is a private block
    # with one social flat bought off-plan (VEFA, 2016) of 60 m²
    rpls = pd.DataFrame([_dwelling(X=10, Y=10, CONSTRUCT=2015)] * 3
                        + [_dwelling(X=10, Y=10)] * 3
                        + [_dwelling(X=510, Y=10, CONSTRUCT=2016, ORIGINE=4)])
    floor = pd.Series([500.0, 500.0, 300.0, 1000.0], index=ids)
    out, summary = sh.parcel_social(pg, floor, social, rpls)
    o = out.set_index("idpar")
    # both estate parcels: wholly social, at the estate's half-exempt regime
    assert o.loc[ids[0], "social_share"] == o.loc[ids[1], "social_share"] == 1.0
    assert o.loc[ids[0], "hlm_tax_factor"] == o.loc[ids[1], "hlm_tax_factor"] == 0.5
    # the private neighbour without social rights or dwellings is untouched
    assert ids[2] not in o.index
    # the VEFA flat: 60 m² habitable of 1,000 m² gross, exempt
    s = 60 / (sh.HAB_TO_GROSS * 1000)
    assert abs(o.loc[ids[3], "social_share"] - round(s, 4)) < 1e-4
    assert abs(o.loc[ids[3], "hlm_tax_factor"] - round(1 - s, 4)) < 1e-4
    assert summary["rpls_dwellings"] == 7 and summary["exempt_dwellings"] == 4
    assert summary["social_parcels"] == 2


def test_neighbouring_estates_of_different_landlords_keep_their_own_regime():
    pg = _grid(3)
    ids = list(pg["idpar"])
    social = pd.DataFrame({"idpar": ids, "landlord": ["hlm"] * 3, "units": [10] * 3,
                           "land": [True] * 3, "landlord_key": ["a", "b", None]})
    # landlord a's dwellings are new (exempt), b's old (taxable); the third
    # parcel's landlord is unknown and its dwellings old
    rpls = pd.DataFrame([_dwelling(X=10, Y=10, CONSTRUCT=2018)] * 2
                        + [_dwelling(X=30, Y=10)] * 2 + [_dwelling(X=50, Y=10)] * 2)
    out, summary = sh.parcel_social(pg, pd.Series(100.0, index=ids), social, rpls)
    o = out.set_index("idpar")
    assert list(o["hlm_tax_factor"]) == [0.0, 1.0, 1.0]
    # the unknown landlord joins its neighbour b's estate (never bridging a–b)
    assert summary["estates"] == 2 and o.loc[ids[2], "landlord_key"] == "b"


def test_an_sem_estate_counts_only_with_social_dwellings():
    pg = _grid(2, size=20.0)
    ids = list(pg["idpar"])
    social = pd.DataFrame({"idpar": ids, "landlord": ["sem", "sem"], "units": [5, 5],
                           "land": [True, True], "landlord_key": ["a", "a"]})
    far_rpls = pd.DataFrame([_dwelling(X=10, Y=10)])
    out, _ = sh.parcel_social(pg, pd.Series([100.0, 100.0], index=ids), social.iloc[[1]],
                              pd.DataFrame(columns=sh.RPLS_COLS))
    assert (out["social_share"] == 0).all()            # no RPLS dwelling: not social
    out, _ = sh.parcel_social(pg, pd.Series([100.0, 100.0], index=ids), social, far_rpls)
    assert (out.set_index("idpar")["social_share"] == 1.0).all()


def test_no_social_housing_returns_an_empty_frame():
    out, summary = sh.parcel_social(_grid(2), pd.Series(dtype=float),
                                    pd.DataFrame(columns=sh.SOCIAL_COLS),
                                    pd.DataFrame(columns=sh.RPLS_COLS))
    assert out.empty and list(out.columns) == sh.PARCEL_COLS
    assert summary["rpls_dwellings"] == 0


def test_rpls_fetch_checks_the_count_and_skips_empty_codes(monkeypatch):
    class Cfg:
        insee_code, data_codes = "99001", ("99001", "99002")
    header = ";".join(f'"{c}"' for c in sh.RPLS_COLS)
    line = ";".join(f'"{v}"' for v in _dwelling().values())
    calls = []

    def fake(url, timeout=180, retries=5):
        calls.append(url)
        if "/rows?" in url:
            return json.dumps({"total": 0 if "99002" in url else 2}).encode()
        return f"{header}\n{line}\n{line}\n".encode()

    monkeypatch.setattr(ingest, "_get", fake)
    df = sh.fetch_rpls(Cfg)
    assert len(df) == 2 and not any("csv?" in u and "99002" in u for u in calls)
    # a CSV shorter than the announced count is truncated: refuse it
    monkeypatch.setattr(ingest, "_get", lambda url, timeout=180, retries=5: (
        json.dumps({"total": 3}).encode() if "/rows?" in url
        else f"{header}\n{line}\n".encode()))
    with pytest.raises(ingest.IngestUnavailable):
        sh.fetch_rpls(Cfg)


def test_current_tax_shares_the_produit_over_taxable_housing_floor_only():
    p = pd.DataFrame({"idpar": ["a", "b", "c"], "floor_area_m2": [100.0, 100.0, 100.0],
                      "floor_industrial": [0.0] * 3, "floor_professional": [0.0, 0.0, 50.0],
                      "floor_housing": [100.0, 100.0, 50.0],
                      "hlm_tax_factor": [1.0, 0.0, 0.7]})     # b fully exempt, c abated
    w = {"industrial": 1.0, "professional": 2.0, "housing": 1.0}
    out = estimate.current_tax(p, 1000.0, bucket_weights=w)
    tax = out.set_index("idpar")["current_tax"]
    assert abs(tax.sum() - 1000.0) < 1e-9
    assert tax["b"] == 0.0                          # not the plain-floor fallback
    # weights: a 100, c 50×2 + 50×0.7 = 135
    assert abs(tax["a"] / tax["c"] - 100 / 135) < 1e-9
    # plain floor-area baseline: the factor on the whole parcel
    plain = estimate.current_tax(p.drop(columns=["floor_housing"]), 1000.0)
    assert plain.set_index("idpar")["current_tax"]["b"] == 0.0
    with pytest.raises(ValueError):
        estimate.current_tax(p.assign(hlm_tax_factor=[1.0, 1.5, 1.0]), 1000.0, bucket_weights=w)


def test_pipeline_puts_social_landlords_in_their_own_category(tmp_path):
    import run_pipeline as rp
    from test_farmland import _world
    parcels, buildings, dvf = _world()
    # flats outside the ten exempt public parcels of the fixture
    flats = parcels.index[(parcels["category_fr"] == "appartement")
                          & ~parcels["is_exempt_public"]][:40]
    parcels["social_share"] = 0.0
    parcels["hlm_tax_factor"] = 1.0
    parcels["landlord_key"] = None
    parcels.loc[flats[:30], ["social_share", "hlm_tax_factor"]] = [1.0, 0.0]
    parcels.loc[flats[:30], "landlord_key"] = ["k1", "k2", "k3"] * 10
    parcels.loc[flats[30:], "social_share"] = 0.25           # mixed: stays a flat
    levy = 2_000_000.0
    plain = rp.run(parcels.drop(columns=["social_share", "hlm_tax_factor", "landlord_key"]),
                   buildings, dvf, levy, out_dir=str(tmp_path / "plain"), make_report=False)
    out = rp.run(parcels, buildings, dvf, levy, out_dir=str(tmp_path), make_report=False,
                 social_summary={"tax_year": 2025, "rpls_dwellings": 900,
                                 "exempt_dwellings": 300, "qpv_abated_dwellings": 0})
    soc = out["property_category"] == rp.SOCIAL_CATEGORY
    assert soc.sum() == 30
    assert abs(out["current_tax"].sum() - levy) < 1 and abs(out["new_tax"].sum() / levy - 1) < 0.01
    assert (out.loc[soc, "current_tax"] == 0).all()           # exempt today
    assert (out.loc[soc, "new_tax"] > 0).all()                # taxed under the reform
    # the reform's bills do not depend on today's exemptions
    assert np.allclose(out["new_tax"], plain["new_tax"])
    side = pd.read_csv(tmp_path / f"{rp.slug_of(rp.CFG)}.households.csv")
    assert (side.loc[soc.values, "n_dwellings"] == 0).all()
    mixed = parcels.index.isin(flats[30:])
    assert np.allclose(side.loc[mixed, "n_dwellings"],
                       pd.read_csv(tmp_path / "plain" / f"{rp.slug_of(rp.CFG)}.households.csv")
                       .loc[mixed, "n_dwellings"] * 0.75, atol=0.01)
    assert set(side.loc[soc.values, "landlord_key"]) == {"k1", "k2", "k3"}
    assert side.loc[~soc.values, "landlord_key"].isna().all()
    meta = json.loads((tmp_path / f"{rp.slug_of(rp.CFG)}.households.meta.json").read_text())
    assert meta["social_housing"]["exempt_dwellings"] == 300


def _cat_rows(n_social, keys):
    flat = dict(property_category="Condominium", current_tax=100.0, new_tax=90.0,
                tax_change=-10.0, tax_change_pct=-10.0, landlord_key="")
    exempt = dict(property_category="Social Housing", current_tax=0.0, new_tax=50.0,
                  tax_change=50.0, tax_change_pct=np.nan)
    taxed = dict(property_category="Social Housing", current_tax=100.0, new_tax=80.0,
                 tax_change=-20.0, tax_change_pct=-20.0)
    rows = [flat] * 20 + [dict(exempt, landlord_key=keys[i % len(keys)])
                          for i in range(n_social // 2)]
    rows += [dict(taxed, landlord_key=keys[i % len(keys)]) for i in range(n_social - n_social // 2)]
    return pd.DataFrame(rows)


def test_social_category_needs_three_landlords_and_counts_rises_from_zero():
    import export_web as ew
    rows = {r["category"]: r for r in ew.build_by_category(_cat_rows(15, ["a", "b", "c"]))}
    s = rows["Social Housing"]
    assert s["label_fr"] == "Logement social (bailleurs)"
    # 7 exempt parcels go from 0 € to 50 €: counted as rises, so the median of
    # 7 rises and 8 falls of −20 % is −20 %, while 7 of 15 pay more
    assert s["median_change_pct"] == -20.0 and s["count_paying_more"] == 7
    # an even split straddling a rise from 0 has no % median (the € one shows)
    rows = {r["category"]: r for r in ew.build_by_category(_cat_rows(16, ["a", "b", "c"]))}
    assert rows["Social Housing"]["median_change_pct"] is None
    assert rows["Social Housing"]["median_change_eur"] is not None
    more = _cat_rows(15, ["a", "b", "c"])
    more.loc[more["property_category"] == "Social Housing", "current_tax"] = 0.0
    more.loc[more["property_category"] == "Social Housing", "tax_change"] = 50.0
    assert {r["category"]: r for r in ew.build_by_category(more)}[
        "Social Housing"]["median_change_pct"] is None            # median on a rise from 0
    # two landlords: the category would describe them, so it joins "Other"
    cats = {r["category"] for r in ew.build_by_category(_cat_rows(15, ["a", "b"]))}
    assert "Social Housing" not in cats and "Other" in cats
    assert ew.social_landlords(_cat_rows(15, ["a", "b", ""])) == 2
    # three landlords, but one carries over 85 % of the tax: still withheld
    dominant = _cat_rows(15, ["a", "b", "c"])
    soc = dominant["property_category"] == "Social Housing"
    dominant.loc[soc, "landlord_key"] = ["a"] * 13 + ["b", "c"]
    minor = dominant.index[soc][-2:]
    dominant.loc[minor, ["current_tax", "new_tax", "tax_change"]] = [10.0, 9.0, -1.0]
    assert ew.social_landlords(dominant) == 3 and not ew.social_disclosable(dominant)
    assert "Social Housing" not in {r["category"] for r in ew.build_by_category(dominant)}


def test_social_provenance_is_withheld_below_three_landlords():
    import export_web as ew
    counts = [{"tax_year": 2025, "rpls_dwellings": 900, "exempt_dwellings": 300,
               "qpv_abated_dwellings": 90}]
    df = _cat_rows(15, ["a", "b", "c"])
    pub = ew.social_provenance(counts, df, ew.build_by_category(df))
    assert pub == {"modelled": True, "tax_year": 2025, "category": "shown",
                   "rpls_dwellings": 900, "exempt_dwellings_pct": 33.3,
                   "qpv_abated_dwellings_pct": 10.0}
    df = _cat_rows(15, ["a", "b"])
    few = ew.social_provenance(counts, df, ew.build_by_category(df))
    assert few["category"] == "folded" and few["rpls_dwellings"] is None
    assert few["exempt_dwellings_pct"] is None
    none = _cat_rows(0, ["a"])
    assert ew.social_provenance(counts, none, ew.build_by_category(none))["category"] == "none"
    assert ew.social_provenance([None], df, []) == {"modelled": False}
    assert ew.social_provenance([], df, []) == {"modelled": False}


def test_social_counts_are_validated(tmp_path, monkeypatch):
    import config
    import export_web as ew
    monkeypatch.setitem(config.COMMUNES, "zz", config.CommuneConfig("99001", "ZZ", "99", key="zz"))
    meta = tmp_path / "zz.households.meta.json"
    assert ew.load_social_counts("zz", str(tmp_path)) is None
    good = {"tax_year": 2025, "rpls_dwellings": 10, "exempt_dwellings": 4, "qpv_abated_dwellings": 2}
    meta.write_text(json.dumps({"social_housing": good}))
    assert ew.load_social_counts("zz", str(tmp_path)) == good
    for bad in ({**good, "exempt_dwellings": 9}, {**good, "rpls_dwellings": "10"},
                {**good, "qpv_abated_dwellings": True}):
        meta.write_text(json.dumps({"social_housing": bad}))
        with pytest.raises(ValueError):
            ew.load_social_counts("zz", str(tmp_path))
