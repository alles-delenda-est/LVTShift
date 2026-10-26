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

All figures were re-read from the sources on 2026-10-26 and checked again by an
independent verification pass; see docs/research/yields-2026.md.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Literal, Optional

Tier = Literal["local", "departmental", "national"]
Budget = Literal["bloc communal", "départements", "État", "Sécurité sociale et État"]
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


# Departmental DMTO, M€. OFGL's departmental aggregate « DMTO avant péreq. »
# includes, for Paris, the communal additional tax, which dmto_communes already
# counts (grand livre, M57 c/73123); it is removed here (OFGL Paris aggregate
# minus Paris's departmental account c/73121; DGCL BIS 190 gives 289 M€ for
# 2023). The single authorities of Corse, Martinique and Guyane levy the
# departmental duty but sit in OFGL's regions dataset; they are added.
_DMTO_DEP_OFGL = {2021: 16511, 2022: 16776, 2023: 13044, 2024: 11297, 2025: 13669}
_PARIS_COMMUNAL = {2021: 397, 2022: 392, 2023: 301, 2024: 268, 2025: 320}
_DMTO_CTU = {2021: 145, 2022: 154, 2023: 139, 2024: 116, 2025: 135}
_DMTO_DEP = {y: _DMTO_DEP_OFGL[y] - _PARIS_COMMUNAL[y] + _DMTO_CTU[y] for y in _DMTO_DEP_OFGL}

# State fees added on top of the local taxes and paid by the taxpayer:
# 2,37 % on the departmental DMTO (CGI art. 1647 V) and 3 % on the taxe
# foncière of communes and intercommunalities (CGI art. 1641).
_FRAIS_ASSIETTE_RATE = 0.0237
_FRAIS_TF_RATE = 0.03
_TFPB = {2024: 39113 + 2519, 2025: 40157 + 2619}
_TFPNB = {2024: 1008 + 189 + 4 + 91 + 4, 2025: 916 + 172 + 4 + 91 + 5}

YIELDS: List[TaxYield] = [
    TaxYield(
        key="tfpb", label_fr="Taxe foncière sur les propriétés bâties",
        scenario="S1", tier="local", budget="bloc communal",
        values=dict(_TFPB),
        basis="latest", status="verified",
        source="DGFiP, REI 2024–2025, via OFGL (« MONTANT RÉEL », commune + intercommunalité)",
        url="https://data.ofgl.fr/explore/dataset/rei/",
        scope="Toutes les propriétés bâties ; parts commune et intercommunalité (périmètre du modèle). "
              "Hors syndicats (184 M€), taxes spéciales d'équipement, GEMAPI et TASA (710 M€ en 2025) et TEOM.",
    ),
    TaxYield(
        key="tfpnb", label_fr="Taxe foncière sur les propriétés non bâties",
        scenario="S1", tier="local", budget="bloc communal",
        values=dict(_TFPNB),
        basis="latest", status="verified",
        source="DGFiP, REI 2024–2025, via OFGL (FNB et taxe additionnelle, « MONTANT RÉEL »)",
        url="https://data.ofgl.fr/explore/dataset/rei/",
        scope="Commune, intercommunalité et taxe additionnelle (TAFNB) ; hors syndicats et chambres d'agriculture.",
    ),
    TaxYield(
        key="tf_etat", label_fr="Taxe foncière — frais de gestion (État)",
        scenario="S1", tier="national", budget="État",
        values={y: round(_FRAIS_TF_RATE * (_TFPB[y] + _TFPNB[y])) for y in _TFPB},
        basis="latest", status="derived",
        source="CGI art. 1641 : 3 % en sus de la taxe foncière des communes et intercommunalités",
        url="https://www.legifrance.gouv.fr/codes/id/LEGITEXT000006069577/",
        scope="Frais d'assiette, de dégrèvement et de non-valeurs ajoutés par l'État à l'avis de taxe foncière.",
        note="Ordre de grandeur cohérent avec le REI 2025 (2 068 M€ de frais sur l'ensemble de l'avis, TEOM comprise).",
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
        scope="Droits départementaux avant péréquation, y compris la métropole de Lyon et les collectivités "
              "uniques de Corse, Martinique et Guyane ; hors part communale de Paris (comptée avec les communes).",
        note="OFGL comptes des départements moins la part communale de Paris (≈ 335 M€ par an), "
             "plus les collectivités uniques (OFGL comptes des régions, ≈ 138 M€ par an).",
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
        # 2020-2023 (graphiques 9-10): IR + surtax + the two taxes on land made
        # constructible, listed separately. 2024 (tableau 7): its IR column
        # already includes them (in 2023 it equals the 9-10 sum to 0,5 M€).
        values={2020: 944 + 78.7 + 2.0 + 24.7, 2021: 1285 + 102.0 + 2.4 + 32.7,
                2022: 1501 + 138.2 + 2.2 + 36.2, 2023: 1145 + 105.9 + 2.6 + 24.6,
                2024: 907.6},
        basis="average", status="verified",
        source="Cour des comptes, L'imposition des plus-values immobilières des particuliers (25 nov. 2025), données ouvertes, graphiques 9-10 (2020–2023) et tableau 7 (2024)",
        url="https://www.ccomptes.fr/fr/publications/limposition-des-plus-values-immobilieres-des-particuliers",
        scope="Particuliers : IR à 19 %, surtaxe sur les plus-values élevées, taxes sur les terrains devenus constructibles. "
              "Hors impôt sur les sociétés (non publié, décision D3).",
        note="2024 provisoire (tableau 7), dont la colonne IR inclut déjà la surtaxe et les taxes sur les terrains.",
    ),
    TaxYield(
        key="gains_ps", label_fr="Plus-values immobilières — prélèvements sociaux",
        scenario="S2", tier="national", budget="Sécurité sociale et État",
        values={2020: 2061, 2021: 2702, 2022: 3014, 2023: 2347, 2024: 1924.5},
        basis="average", status="verified",
        source="Cour des comptes (25 nov. 2025), données ouvertes, graphiques 9-10 (2020–2023) et tableau 7 (2024)",
        url="https://www.ccomptes.fr/fr/publications/limposition-des-plus-values-immobilieres-des-particuliers",
        scope="Prélèvements sociaux (17,2 %, dont 7,5 points de prélèvement de solidarité versés à l'État) sur les plus-values des particuliers.",
        note="Rupture de série : pour 2023, le tableau 7 donne 2 583 M€ contre 2 347 dans les graphiques 9-10 (+10 %), écart non expliqué. "
             "Sensibilité de la moyenne : −54 à +317 M€ selon la série retenue.",
    ),
    TaxYield(
        key="ifi", label_fr="Impôt sur la fortune immobilière (IFI)",
        scenario="S2_IFI", tier="national", budget="État",
        values={2022: 1800, 2023: 1900, 2024: 2200, 2025: 2300},
        basis="latest", status="verified",
        source="DGFiP Statistiques n° 15 (2022), n° 23 (2023), n° 33 (2024), n° 45 (2025)",
        url="https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-la-fortune-immobiliere-en-2025",
        scope="Montant des avis d'IFI, tous redevables.",
        note="Les recettes budgétaires sont plus élevées (2 739 M€ en 2024, 2 965 M€ prévus pour 2025, "
             "PLF 2026, Voies et moyens, ligne 1406) : écart entre avis et encaissements, non expliqué par la source.",
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
        scenario="S3", tier="national", budget="Sécurité sociale et État",
        values={2022: 2400},
        basis="latest", status="reported",
        source="CPO, Pour une fiscalité du logement plus cohérente (déc. 2023), p. 23",
        url="https://www.vie-publique.fr/files/rapport/pdf/292676.pdf",
        scope="Prélèvements sociaux (17,2 %, dont 7,5 points versés à l'État) sur les revenus fonciers.",
        note="Le CPO cite séparément 1,1 Md€ de CSG sur les revenus fonciers ; aucune hypothèse (CSG incluse ou non) "
             "ne cadre avec un taux de 17,2 %. Ligne CSG non ajoutée tant que le partage n'est pas connu.",
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

    built_land_total: float = 7_032_000
    built_land_public: float = 941_000
    year: int = 2025
    source: str = ("INSEE, Chiffres-clés « Patrimoine national par secteur institutionnel et grand type "
                   "d'actif », données 2025 provisoires (30 juillet 2026)")
    url: str = "https://www.insee.fr/fr/statistiques/2830290"
    note: str = ("Terrains bâtis hors administrations publiques (foncier public exonéré). "
                 "Terres agricoles et naturelles (décision D6) pas encore incluses : l'INSEE ne les "
                 "isole pas. Fin 2024 définitif : 6 729 Md€ dont 903 publics (Insee Première n° 2081).")

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
