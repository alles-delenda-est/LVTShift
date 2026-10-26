"""Yields to replace in the equal-yield scenarios of spec 0005.

One table, one place: every tax a land value tax would replace, with its
annual yield by year (M€), the source it was read from, its scope and how
sure we are of it. The site displays this table as it is (``export_json``),
so a figure changed here changes the published page.

Reference value per tax (spec 0005, decision D1): the average of the last five
available years for cyclical taxes (DMTO, taxes on gains), the latest year for
the others.

Scenarios (spec 0005 §1):
    S1  taxe foncière (TFPB + TFPNB) + DMTO
    S2  S1 + taxes on real-estate capital gains, with IFI as an optional toggle
    S3  S2 + taxes on rental income

Indicative rates divide the yield by INSEE's built-land value net of public
land. They are national averages, for orientation: the model sets the local
tier commune by commune (spec 0005 §4.1).

All figures were re-read from the sources on 2026-10-26; see
docs/research/yields-2026.md for each reconciliation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Literal, Optional

Tier = Literal["local", "departmental", "national"]
Budget = Literal["bloc communal", "départements", "État", "Sécurité sociale"]
Basis = Literal["average", "latest"]
Status = Literal["verified", "derived", "reported"]

AVERAGE_YEARS = 5


@dataclass(frozen=True)
class TaxYield:
    """One tax line: annual yields by year, in millions of euros.

    Parameters
    ----------
    key : str
        Stable identifier used by the site.
    label_fr : str
        Display label.
    scenario : str
        First scenario that replaces it: "S1", "S2", "S2_IFI" (the optional
        IFI toggle) or "S3".
    tier, budget : str
        Which rate raises it (spec 0005 §2) and whose budget it funds today.
    values : dict[int, float]
        Yield by year, M€.
    basis : str
        "average" (last ``AVERAGE_YEARS`` years) or "latest".
    status : str
        "verified": read from the primary source; "derived": computed from
        primary figures (method in ``note``); "reported": a secondary source
        quoting the primary, not yet checked against it.
    """

    key: str
    label_fr: str
    scenario: str
    tier: Tier
    budget: Budget
    values: Dict[int, float]
    basis: Basis
    status: Status
    source: str
    url: str
    scope: str
    note: str = ""

    def reference_years(self) -> List[int]:
        years = sorted(self.values)
        return years[-AVERAGE_YEARS:] if self.basis == "average" else years[-1:]

    def reference(self) -> float:
        """Reference yield, M€ (D1: 5-year average for cyclical taxes)."""
        years = self.reference_years()
        return sum(self.values[y] for y in years) / len(years)


# Departmental DMTO "avant péréquation", OFGL comptes des départements
# (agrégat « DMTO avant péreq. », budget principal), M€.
_DMTO_DEP = {2021: 16511, 2022: 16776, 2023: 13044, 2024: 11297, 2025: 13669}

# State collection fee on departmental DMTO (frais d'assiette et de
# recouvrement, 2,37 % of the departmental duty, paid on top by the buyer).
_FRAIS_ASSIETTE_RATE = 0.0237

YIELDS: List[TaxYield] = [
    TaxYield(
        key="tfpb", label_fr="Taxe foncière sur les propriétés bâties",
        scenario="S1", tier="local", budget="bloc communal",
        values={2024: 39113 + 2519, 2025: 40157 + 2619},
        basis="latest", status="verified",
        source="DGFiP, REI 2024–2025, via OFGL (« MONTANT RÉEL », commune + intercommunalité)",
        url="https://data.ofgl.fr/explore/dataset/rei/",
        scope="Toutes les propriétés bâties ; parts commune et intercommunalité (périmètre du modèle). "
              "Hors syndicats (184 M€), taxes spéciales d'équipement, GEMAPI et TASA (≈ 0,7 Md€, à confirmer) et TEOM.",
    ),
    TaxYield(
        key="tfpnb", label_fr="Taxe foncière sur les propriétés non bâties",
        scenario="S1", tier="local", budget="bloc communal",
        values={2024: 1008 + 189 + 4 + 91 + 4, 2025: 916 + 172 + 4 + 91 + 5},
        basis="latest", status="verified",
        source="DGFiP, REI 2024–2025, via OFGL (FNB et taxe additionnelle, « MONTANT RÉEL »)",
        url="https://data.ofgl.fr/explore/dataset/rei/",
        scope="Commune, intercommunalité et taxe additionnelle (TAFNB) ; hors syndicats et chambres d'agriculture.",
    ),
    TaxYield(
        key="dmto_communes", label_fr="Droits de mutation — part communale",
        scenario="S1", tier="local", budget="bloc communal",
        values={2021: 3643, 2022: 3978, 2023: 3356, 2024: 2882, 2025: 3155},
        basis="average", status="derived",
        source="Comptes de gestion des communes, via OFGL (grand livre, tous budgets)",
        url="https://data.ofgl.fr/explore/dataset/grand-livre/",
        scope="Taxe additionnelle (c/7381 en M14, c/73123 en M57, c/7332) et fonds départemental "
              "pour les communes de moins de 5 000 habitants (c/73223, c/73224).",
        note="Somme des comptes par exercice. Les prélèvements et attributions de péréquation "
             "(c/739225, c/73225) sont des transferts entre collectivités et ne sont pas comptés.",
    ),
    TaxYield(
        key="dmto_departements", label_fr="Droits de mutation — part départementale",
        scenario="S1", tier="departmental", budget="départements",
        values=dict(_DMTO_DEP),
        basis="average", status="verified",
        source="Comptes des départements, via OFGL (agrégat « DMTO avant péreq. », budget principal)",
        url="https://data.ofgl.fr/explore/dataset/ofgl-base-departements/",
        scope="Droits départementaux avant péréquation, y compris Paris et la métropole de Lyon.",
    ),
    TaxYield(
        key="dmto_etat", label_fr="Droits de mutation — frais d'assiette (État)",
        scenario="S1", tier="national", budget="État",
        values={y: round(v * _FRAIS_ASSIETTE_RATE) for y, v in _DMTO_DEP.items()},
        basis="average", status="derived",
        source="CGI art. 1647 V : 2,37 % en sus des droits départementaux (2,14 % là où le taux départemental est réduit à 0,70 %)",
        url="https://www.legifrance.gouv.fr/codes/id/LEGITEXT000006069577/",
        scope="Prélèvement de l'État pour frais d'assiette et de recouvrement, payé par l'acquéreur.",
        note="Calculé au taux de 2,37 % sur l'ensemble des droits départementaux ; légère surestimation pour la part taxée au taux réduit.",
    ),
    TaxYield(
        key="gains_ir", label_fr="Plus-values immobilières — impôt sur le revenu",
        scenario="S2", tier="national", budget="État",
        # IR + surtaxe on large gains + taxes on land made constructible
        values={2020: 944 + 78.7 + 2.0 + 24.7, 2021: 1285 + 102.0 + 2.4 + 32.7,
                2022: 1501 + 138.2 + 2.2 + 36.2, 2023: 1145 + 105.9 + 2.6 + 24.6,
                2024: 907.6 + 70.0 + 1.5 + 15.9},
        basis="average", status="verified",
        source="Cour des comptes, L'imposition des plus-values immobilières des particuliers (25 nov. 2025), données ouvertes, graphiques 9-10 (2020–2023) et tableau 7 (2024)",
        url="https://www.ccomptes.fr/fr/publications/limposition-des-plus-values-immobilieres-des-particuliers",
        scope="Particuliers : IR à 19 %, surtaxe sur les plus-values élevées, taxes sur les terrains devenus constructibles. "
              "Hors impôt sur les sociétés (non publié, décision D3).",
        note="Rupture de série en 2024 : le tableau 7 donne pour 2023 un montant supérieur de ~10 % à celui des graphiques 9-10.",
    ),
    TaxYield(
        key="gains_ps", label_fr="Plus-values immobilières — prélèvements sociaux",
        scenario="S2", tier="national", budget="Sécurité sociale",
        values={2020: 2061, 2021: 2702, 2022: 3014, 2023: 2347, 2024: 1924.5},
        basis="average", status="verified",
        source="Cour des comptes (25 nov. 2025), données ouvertes, graphiques 9-10 (2020–2023) et tableau 7 (2024)",
        url="https://www.ccomptes.fr/fr/publications/limposition-des-plus-values-immobilieres-des-particuliers",
        scope="Prélèvements sociaux (17,2 %) sur les plus-values des particuliers.",
        note="Même rupture de série en 2024 que la ligne IR.",
    ),
    TaxYield(
        key="ifi", label_fr="Impôt sur la fortune immobilière (IFI)",
        scenario="S2_IFI", tier="national", budget="État",
        values={2022: 2100, 2023: 1900, 2024: 2200, 2025: 2300},
        basis="latest", status="reported",
        source="DGFiP Statistiques n° 23 (2023) ; CPO 2023 (2022) ; DGFiP cité par la presse (2024, 2025)",
        url="https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-la-fortune-immobiliere-en-2023",
        scope="Produit de l'IFI, tous redevables.",
        note="2024 et 2025 à vérifier sur la publication DGFiP elle-même.",
    ),
    TaxYield(
        key="rents_ir", label_fr="Revenus locatifs — impôt sur le revenu",
        scenario="S3", tier="national", budget="État",
        values={2022: 4200},
        basis="latest", status="reported",
        source="CPO, Pour une fiscalité du logement plus cohérente (déc. 2023), p. 23",
        url="https://www.vie-publique.fr/files/rapport/pdf/292676.pdf",
        scope="IR lié aux revenus locatifs des particuliers. Locations meublées (BIC) non isolées (D7) ; hors IS (D3).",
        note="CPO p. 23 (année 2022). Le CPO cite aussi la CSG sur revenus fonciers (1,1 Md€) et la contribution sur les revenus locatifs (0,1 Md€), "
             "et un total de 8,3 Md€ que ses lignes n'atteignent pas (7,8 Md€) ; le compte du logement 2024 donne 8,9 Md€. Périmètre à réconcilier.",
    ),
    TaxYield(
        key="rents_ps", label_fr="Revenus locatifs — prélèvements sociaux",
        scenario="S3", tier="national", budget="Sécurité sociale",
        values={2022: 2400},
        basis="latest", status="reported",
        source="CPO, Pour une fiscalité du logement plus cohérente (déc. 2023), p. 23",
        url="https://www.vie-publique.fr/files/rapport/pdf/292676.pdf",
        scope="Prélèvements sociaux (17,2 %) sur les revenus fonciers.",
    ),
]

SCENARIOS: Dict[str, List[str]] = {
    "S1": ["S1"],
    "S2": ["S1", "S2"],
    "S3": ["S1", "S2", "S3"],
}


@dataclass(frozen=True)
class LandBase:
    """Taxable land value used for indicative national rates, M€."""

    built_land_total: float = 6_346_000
    built_land_public: float = 916_000
    year: int = 2023
    source: str = "INSEE, Insee Première n° 2028 (déc. 2024), figure 2, comptes nationaux base 2020"
    url: str = "https://www.insee.fr/fr/statistiques/8305990"
    note: str = ("Terrains bâtis hors administrations publiques (foncier public exonéré). "
                 "Terres agricoles et naturelles (décision D6) pas encore incluses : l'INSEE ne les "
                 "isole pas dans cette publication. Valeur fin 2023, après une baisse de 13,7 % sur un an.")

    @property
    def taxable(self) -> float:
        return self.built_land_total - self.built_land_public


LAND_BASE = LandBase()


def lines_for(scenario: str, include_ifi: bool = False) -> List[TaxYield]:
    """Tax lines replaced in a scenario (cumulative), optionally with the IFI."""
    wanted = set(SCENARIOS[scenario])
    if include_ifi and scenario in ("S2", "S3"):
        wanted.add("S2_IFI")
    return [t for t in YIELDS if t.scenario in wanted]


def scenario_total(scenario: str, include_ifi: bool = False) -> float:
    """Total reference yield to replace, M€."""
    return sum(t.reference() for t in lines_for(scenario, include_ifi))


def tier_totals(scenario: str, include_ifi: bool = False) -> Dict[str, float]:
    out: Dict[str, float] = {"local": 0.0, "departmental": 0.0, "national": 0.0}
    for t in lines_for(scenario, include_ifi):
        out[t.tier] += t.reference()
    return out


def indicative_rate_pct(scenario: str, include_ifi: bool = False,
                        base: Optional[LandBase] = None) -> float:
    """Average LVT rate, % of taxable land value a year (orientation only)."""
    b = base or LAND_BASE
    return 100.0 * scenario_total(scenario, include_ifi) / b.taxable


def export_json(path: str | Path = "site/public/data/yields.json") -> dict:
    """Write the yield table and scenario totals for the site."""
    variants = []
    for sc in SCENARIOS:
        for ifi in ((False, True) if sc != "S1" else (False,)):
            variants.append({
                "scenario": sc, "include_ifi": ifi,
                "total_meur": round(scenario_total(sc, ifi)),
                "tiers_meur": {k: round(v) for k, v in tier_totals(sc, ifi).items()},
                "rate_pct": round(indicative_rate_pct(sc, ifi), 2),
                "lines": [t.key for t in lines_for(sc, ifi)],
            })
    payload = {
        "as_of": "2026-10-26",
        "average_years": AVERAGE_YEARS,
        "taxes": [{
            "key": t.key, "label_fr": t.label_fr, "scenario": t.scenario,
            "tier": t.tier, "budget": t.budget, "basis": t.basis, "status": t.status,
            "values_meur": {str(y): round(v, 1) for y, v in sorted(t.values.items())},
            "reference_years": t.reference_years(),
            "reference_meur": round(t.reference()),
            "source": t.source, "url": t.url, "scope": t.scope, "note": t.note,
        } for t in YIELDS],
        "land_base": {
            "taxable_meur": LAND_BASE.taxable, "total_meur": LAND_BASE.built_land_total,
            "public_meur": LAND_BASE.built_land_public, "year": LAND_BASE.year,
            "source": LAND_BASE.source, "url": LAND_BASE.url, "note": LAND_BASE.note,
        },
        "variants": variants,
    }
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    data = export_json(Path(__file__).resolve().parent / "site/public/data/yields.json")
    for v in data["variants"]:
        print(f"{v['scenario']}{' + IFI' if v['include_ifi'] else ''}: "
              f"{v['total_meur']:,} M€  ({v['rate_pct']} % of taxable land)")
