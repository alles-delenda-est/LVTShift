"""Offline tests for the exempt-public-property flag (exemptions.py, spec 0003).

Run: python -m pytest -q test_exemptions.py
"""

import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import estimate  # noqa: E402
import exemptions as ex  # noqa: E402
import ingest  # noqa: E402

VDP = ex.VILLE_DE_PARIS_SIREN


def _row(idpar, src, droit, forme, siren="130000000", den="ETAT", prefixe=""):
    return {"dep": idpar[:2], "com": idpar[2:5], "prefixe": prefixe,
            "section": idpar[8:10], "plan": idpar[10:], "code_droit": droit,
            "siren": siren, "forme": forme, "denomination": den, "src": src,
            "idpar": idpar}


def _flags(rows, lyon=frozenset()):
    f = ex.classify(pd.DataFrame(rows), lyon)
    return dict(zip(f["idpar"], f["tier"]))


def test_idpar_padding():
    df = pd.DataFrame({"dep": ["75"], "com": ["107"], "prefixe": ["   "],
                       "section": [" E"], "plan": ["25"]})
    assert ex.idpar_of(df).iloc[0] == "751070000E0025"
    df = pd.DataFrame({"dep": ["93"], "com": ["66"], "prefixe": ["059"],
                       "section": ["AB"], "plan": ["0001"]})
    assert ex.idpar_of(df).iloc[0] == "93066059AB0001"
    df = pd.DataFrame({"dep": ["2a"], "com": ["004"], "prefixe": [""],
                       "section": ["b"], "plan": ["12"]})
    assert ex.idpar_of(df).iloc[0] == "2A0040000B0012"


def test_public_full_owner_with_units_is_a1_and_land_only_is_a2():
    p1, p2 = "75107000BO0025", "75112000AA0001"
    rows = [_row(p1, "NB", "P", "7113"), _row(p1, "B", "P", "7113"),
            _row(p2, "NB", "P", "7229", siren=VDP, den="VILLE DE PARIS")]
    assert _flags(rows) == {p1: "A1", p2: "A2"}


def test_condominium_lease_private_and_housing_manager_block_the_flag():
    base = "75105000AX00"
    cases = {
        base + "01": [_row(base + "01", "NB", "P", "7113"),
                      _row(base + "01", "NB", "S", "5499", den="SYNDIC X")],        # copro
        base + "02": [_row(base + "02", "NB", "P", "7113"),
                      _row(base + "02", "B", "E", "5710", den="SAS CAFE")],          # lease
        base + "03": [_row(base + "03", "NB", "P", "7113"),
                      _row(base + "03", "B", "P", "6540", den="SCI X")],             # private unit
        base + "04": [_row(base + "04", "NB", "P", "7364", den="AP-HP"),
                      _row(base + "04", "B", "G", "7364", den="SERVICE LOGEMENT AP-HP")],
        base + "05": [_row(base + "05", "NB", "P", "4110", den="SNCF")],             # EPIC
    }
    rows = [r for rs in cases.values() for r in rs]
    assert _flags(rows) == {}


def test_state_property_managed_by_a_public_agency():
    # domaine national: the State owns, the Centre des monuments nationaux (an
    # EPA, not itself a qualifying form) manages under droit Z -> still exempt
    p, q = "92064000AB0001", "92064000AB0002"
    rows = [_row(p, "NB", "P", "7113"), _row(p, "NB", "Z", "7389", den="CMN"),
            # a private company managing State land under Z still blocks
            _row(q, "NB", "P", "7113"), _row(q, "NB", "Z", "5710", den="SAS X")]
    f = ex.classify(pd.DataFrame(rows))
    assert dict(zip(f["idpar"], f["tier"])) == {p: "A2"}
    assert f["owner_type"].tolist() == ["etat"]


def test_utility_units_are_ignored():
    p = "75105000AX0010"
    rows = [_row(p, "NB", "P", "7383", den="SORBONNE UNIVERSITE"),
            _row(p, "B", "P", "7383", den="SORBONNE UNIVERSITE"),
            _row(p, "B", "P", "5710", den="ENEDIS")]
    assert _flags(rows) == {p: "A1"}
    # a lessee whose name merely resembles a utility still blocks the flag,
    # and so does a utility holding anything but full ownership
    for den, droit in (("SARL ORANGE CONSEIL", "P"), ("ENEDIS", "E")):
        rows = [_row(p, "NB", "P", "7113"), _row(p, "B", "P", "7113"),
                _row(p, "B", droit, "5710", den=den)]
        assert _flags(rows) == {}, den


def test_commune_and_departement_only_on_their_own_territory():
    own, away = "93048000AB0001", "93066000AB0001"
    montreuil = "219300480"                       # 21 93 0 048 0 -> 93048
    rows = [_row(own, "NB", "P", "7210", siren=montreuil),
            _row(away, "NB", "P", "7210", siren=montreuil)]
    assert _flags(rows) == {own: "A2"}
    # Ville de Paris: exempt in Paris, not in Montreuil; arrondissements -> 75056
    rows = [_row("75120000CD0001", "NB", "P", "7229", siren=VDP),
            _row("93048000CD0001", "NB", "P", "7229", siren=VDP)]
    assert _flags(rows) == {"75120000CD0001": "A2"}
    # département 93 property in 93 only
    d93 = "229300015"
    rows = [_row("93048000EF0001", "NB", "P", "7220", siren=d93),
            _row("94028000EF0001", "NB", "P", "7220", siren=d93)]
    assert _flags(rows) == {"93048000EF0001": "A2"}
    # Métropole de Lyon on its territory
    rows = [_row("69381000GH0001", "NB", "P", "7229", siren=ex.METROPOLE_LYON_SIREN),
            _row("69290000GH0001", "NB", "P", "7229", siren=ex.METROPOLE_LYON_SIREN)]
    assert _flags(rows, lyon={"69123", "69290"}) == {"69381000GH0001": "A2",
                                                      "69290000GH0001": "A2"}
    assert _flags(rows, lyon={"69123"}) == {"69381000GH0001": "A2"}


def test_a2_exempt_only_where_the_model_sees_no_building(monkeypatch):
    flags = pd.DataFrame({"idpar": ["P1", "P2", "P3"], "tier": ["A1", "A2", "A2"],
                          "owner_type": ["etat"] * 3})
    monkeypatch.setattr(ex, "flags_for_departement", lambda dep, year=ex.PM_YEAR: flags)

    class Cfg:
        departement = "75"
    parcels = pd.DataFrame({"idpar": ["P1", "P2", "P3", "P4"]})
    built = pd.Series([True, True, False, True])
    out = ex.exempt_public(Cfg, parcels, built)
    assert list(out["is_exempt_public"]) == [True, False, True, False]
    assert list(out["exempt_tier"].fillna("-")) == ["A1", "-", "A2", "-"]


def test_current_tax_skips_exempt_parcels():
    p = pd.DataFrame({"floor_area_m2": [100.0, 100.0, 200.0],
                      "is_exempt_public": [False, True, False]})
    out = estimate.current_tax(p, 900.0)
    assert list(out["current_tax"]) == [300.0, 0.0, 600.0]


def test_fetch_rows_reads_the_departement_member(monkeypatch):
    label = {"dep": "Département", "code_droit": "Code droit", "siren": "N° SIREN",
             "forme": "Forme juridique", "denomination": "Dénomination"}
    b_csv = (";".join(label.get(c, c) for c in ex.B_COLS) + "\n" + ";".join(
        ["75", "0", "107", "PARIS 07", "", "BO", "0025"] + [""] * 10
        + ["P", "X", "130000000", "1", "7113", "MIN", "MINISTERE"]) + "\n").encode()
    nb_csv = (";".join(label.get(c, c) for c in ex.NB_COLS) + "\n" + ";".join(
        ["75", "0", "107", "PARIS 07", "", "BO", "0025"] + [""] * 6
        + ["1000", "", "S", "1000", "P", "X", "130000000", "1", "7113", "MIN",
           "MINISTERE"]) + "\n").encode()

    def zipped(members):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            for name, body in members.items():
                z.writestr(name, body)
        return buf.getvalue()
    h = "https://data.economie.gouv.fr/api/attachments/"
    catalog = {"attachments": [
        {"href": h + "B", "metas": {"id": "fichier_des_locaux_situation_2025_zip"}},
        {"href": h + "NB1", "metas": {"id": "fichier_des_parcelles_situation_2025_dpts_01_a_56_zip"}},
        {"href": h + "NB2", "metas": {"id": "fichier_des_parcelles_situation_2025_dpts_57_a_976_zip"}},
        {"href": h + "old", "metas": {"id": "fichier_des_locaux_situation_2024_zip"}},
    ]}
    bodies = {
        h + "B": zipped({"l/PB_25_B_750 (1 a12).csv": b_csv, "l/PM_25_B_7501.csv": b"x"}),
        h + "NB2": zipped({"p/PM_25_NB_750.csv": nb_csv}),
    }
    fetched = []

    def fake_get(url, *a, **k):
        fetched.append(url)
        return json.dumps(catalog).encode() if url == ex.SRC["pm_catalog"] else bodies[url]
    monkeypatch.setattr(ingest, "_get", fake_get)
    rows = ex.fetch_rows("75")
    assert h + "NB1" not in fetched and h + "old" not in fetched  # only 57-976 for dept 75
    assert sorted(rows["src"]) == ["B", "NB"]
    assert set(rows["idpar"]) == {"75107000BO0025"}
    assert "denomination" in rows.columns            # needed by classify, never cached
    f = ex.classify(rows)
    assert list(f.columns) == ["idpar", "tier", "owner_type"]   # no names, no siren
    # a tampered catalog pointing elsewhere is refused
    catalog["attachments"][0]["href"] = "file:///etc/passwd"
    with pytest.raises(ingest.IngestUnavailable):
        ex.fetch_rows("75")
    catalog["attachments"][0]["href"] = h + "B"
    # a renamed column (schema drift) fails loudly
    bodies[h + "B"] = zipped({"l/PB_25_B_750.csv": b_csv.replace(
        "Forme juridique".encode(), b"Categorie")})
    with pytest.raises(ingest.IngestUnavailable):
        ex.fetch_rows("75")


def test_pipeline_exempts_and_stays_revenue_neutral():
    from lvt.lvt_utils import model_split_rate_tax
    rng = np.random.default_rng(3)
    n = 50
    p = pd.DataFrame({"land_value": rng.uniform(1e5, 5e5, n),
                      "improvement_value": rng.uniform(1e5, 5e5, n),
                      "floor_area_m2": rng.uniform(50, 300, n),
                      "is_exempt_public": [i < 5 for i in range(n)]})
    p = estimate.current_tax(p, 100_000.0)
    p["is_exempt_public"] = p["is_exempt_public"].astype(int)
    _l, _i, rev, out = model_split_rate_tax(
        df=p, land_value_col="land_value", improvement_value_col="improvement_value",
        current_revenue=100_000.0, land_improvement_ratio=4.0,
        exemption_flag_col="is_exempt_public")
    assert abs(out["new_tax"].sum() - 100_000.0) < 1.0
    assert (out.loc[:4, "new_tax"] == 0).all() and (out.loc[:4, "current_tax"] == 0).all()
    assert (out.loc[:4, "taxable_land_value"] == 0).all()


def test_export_counts_exempt_parcels_without_listing_them(tmp_path, monkeypatch):
    import config
    import export_web as ew
    monkeypatch.setitem(config.COMMUNES, "zz", config.CommuneConfig("99001", "ZZ", "99", key="zz"))
    pd.DataFrame({"taxable_land_value": [1.0, 2.0, 3.0],
                  "is_fully_exempt": [True, False, False]}).to_csv(tmp_path / "zz.csv", index=False)
    df = ew.load_parcels("zz", out_dir=str(tmp_path))
    assert len(df) == 2 and df.attrs["exempt_parcels"] == 1


def test_rural_buildings_need_agricultural_use_and_a_rural_signal():
    b = pd.DataFrame({
        "idpar": ["U1", "U2", "A1", "N1", "U3", "A2", "X"],
        "usage": ["Agricole", "Agricole", "Agricole", "Agricole", "Commercial et services",
                  "Résidentiel", "Agricole"],
        "nature": ["Serre", "Indifférenciée", "Indifférenciée", "Silo", "Serre",
                   "Indifférenciée", None],
    })
    zoning = pd.DataFrame({"idpar": ["U1", "U2", "A1", "N1", "U3", "A2", "A2"],
                           "zone_typ": ["U", "U", "A", "N", "U", "A", "A"]})
    got = ex.rural_buildings(b, zoning)
    # greenhouse anywhere, any farm building in A/N; not an urban farm shed
    # (possibly a converted workshop), not a garden centre, not a farmhouse,
    # not an unzoned shed with no greenhouse/silo signal
    assert list(got) == [True, False, True, True, False, False, False]
    assert got.dtype == bool
    # older frames without `nature` rely on zoning alone
    assert list(ex.rural_buildings(b.drop(columns="nature"), zoning)) == \
        [False, False, True, True, False, False, False]
    # an unlabelled shed is a farm building in A/N, not in an urban zone
    iac = "Industriel, agricole ou commercial"
    s = pd.DataFrame({"idpar": ["A1", "U1", "A1", "A1"],
                      "usage": [None, "Indifférencié", "Industriel", None],
                      "nature": [iac, iac, iac, "Indifférenciée"]})
    assert list(ex.rural_buildings(s, zoning)) == [True, False, False, False]
    assert not ex.rural_buildings(s.drop(columns="usage"), zoning).iloc[1]
