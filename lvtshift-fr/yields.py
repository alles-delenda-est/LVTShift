"""Yields to replace in the equal-yield scenarios of spec 0005.

One table, one place: every tax a land value tax would replace, with its
annual yield by year (M€), the source it was read from, its scope and how
sure we are of it. The site displays this table as it is (``export_json``),
so a figure changed here changes the published page.

Reference value per tax (spec 0005, decision D1): the average of the last five
available years for cyclical taxes (DMTO, taxes on gains), the latest year for
the others.

Scenarios (spec 0005 §1):
    S1  taxe foncière (TFPB + TFPNB) + taxe d'habitation on second homes + DMTO
    S2  S1 + taxes on real-estate capital gains, with IFI as an optional toggle
    S3  S2 + taxes on rental income

Indicative rates divide the yield by the taxable land value: INSEE's built land
net of public land. Agricultural and natural land is outside the reform (D6,
revised 2026-10-29): it keeps today's TFPNB, so neither its value nor its TFPNB
enters the totals. Its SAFER value is kept as a sensitivity. The rates are
national averages, for orientation: the model sets the local tier commune by
commune (spec 0005 §4.1).

All figures were re-read from the sources on 2026-10-26 and checked again by an
independent verification pass, then reviewed by Gemini (gemini-4-argon) on
2026-10-27 with each of its claims checked against primary sources; see
docs/research/yields-2026.md.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Literal, Optional

Tier = Literal["local", "departmental", "national"]
Budget = Literal["bloc communal", "bloc communal et établissements publics", "départements",
                 "État", "Sécurité sociale", "Sécurité sociale et État"]
Basis = Literal["average", "latest"]
Status = Literal["verified", "derived", "reported"]

AVERAGE_YEARS = 5

# Sensitivity to D1 (not the headline): yields restated in 2025 euros with the
# consumer price index, INSEE annual average, base 2015, all households, France
# (BDM idbank 001764363, « séries arrêtées »; do not mix with base 2025).
CPI = {2020: 104.73, 2021: 106.45, 2022: 112.01, 2023: 117.47, 2024: 119.82, 2025: 120.95}
CPI_YEAR = 2025
CPI_SOURCE = ("INSEE, indice annuel des prix à la consommation, base 2015, ensemble des ménages, "
              "France (idbank 001764363)")
CPI_URL = "https://www.insee.fr/fr/statistiques/serie/001764363"


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

    def reference_constant(self) -> float:
        """Reference yield with each year restated in CPI_YEAR euros, M€ (D1 sensitivity)."""
        years = self.reference_years()
        return sum(self.values[y] * CPI[CPI_YEAR] / CPI[y] for y in years) / len(years)


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

# State fees added on top of the local taxes and paid by the taxpayer, read on
# Légifrance on 2026-10-27: 2,37 % on the departmental DMTO (CGI art. 1647 V);
# on the taxe foncière bill (CGI art. 1641), 3 % on the TF of communes,
# intercommunalities and syndicates and on GEMAPI, 8 % on TASA, 9 % on TSE.
_FRAIS_ASSIETTE_RATE = 0.0237
_FRAIS_TF_RATE = 0.03
_FRAIS_TASA_RATE = 0.08
_FRAIS_TSE_RATE = 0.09
_TFPB = {2024: 39113 + 2519, 2025: 40157 + 2619}
_TFPNB_ALL = {2024: 1008 + 189 + 4 + 91 + 4, 2025: 916 + 172 + 4 + 91 + 5}
# Part of it on agricultural and natural land (cadastral groups 1-6, 8, 9), which
# stays on today's TFPNB (D6). Not published as such: rebuilt commune by commune
# from the REI. The TAFNB base (B11/B31/B31MGP TAFNB) covers exactly the other
# groups (BOI-IF-AUT-80, BOI-IF-TFNB-10-40-50), so base TAFNB ÷ base TFPNB is
# each commune's non-agricultural share; the whole TAFNB is non-agricultural.
# Check: the 20 % agricultural exemption base (D21, 2024) implies the same
# agricultural base within 0,6 % (docs/research/tfpnb_farm_split.py). Syndicates excluded, as in _TFPNB_ALL.
_TFPNB_FARM = {2024: 1032.9, 2025: 922.2}
_FARM_SHARE = {y: _TFPNB_FARM[y] / _TFPNB_ALL[y] for y in _TFPNB_ALL}
_TFPNB = {y: _TFPNB_ALL[y] - _TFPNB_FARM[y] for y in _TFPNB_ALL}
# Other levies on the taxe foncière bill, REI « MONTANT RÉEL », built + non-built:
# TSE (E53, E53A, B53, B53A), TASA (E53TASA), GEMAPI (E53gGEMAPI, B53gGEMAPI),
# syndicates (E23, B23).
# The non-built parts (B53 + B53A, B53gGEMAPI, B23) lose their farmland share
# like the TFPNB itself (same base, same exemptions).
_TSE_NB = {2024: 1.3 + 0.4, 2025: 1.2 + 0.3}
_GEMAPI_NB = {2024: 18.9, 2025: 20.5}
_SYNDICATS_NB = {2024: 7.3, 2025: 6.7}
_TSE = {y: b + _TSE_NB[y] * (1 - _FARM_SHARE[y]) for y, b in {2024: 191.2 + 75.4, 2025: 202.7 + 72.4}.items()}
_TASA = {2024: 57.7, 2025: 57.9}
_GEMAPI = {y: b + _GEMAPI_NB[y] * (1 - _FARM_SHARE[y]) for y, b in {2024: 340.1, 2025: 376.6}.items()}
_SYNDICATS = {y: b + _SYNDICATS_NB[y] * (1 - _FARM_SHARE[y]) for y, b in {2024: 174.8, 2025: 184.3}.items()}
_TF_ANNEXES = {y: _TSE[y] + _TASA[y] + _GEMAPI[y] + _SYNDICATS[y] for y in _TSE}
_FRAIS_TF = {y: _FRAIS_TF_RATE * (_TFPB[y] + _TFPNB[y] + _GEMAPI[y] + _SYNDICATS[y])
             + _FRAIS_TASA_RATE * _TASA[y] + _FRAIS_TSE_RATE * _TSE[y] for y in _TFPB}

# Taxe d'habitation on second homes, REI « MONTANT RÉEL »: commune, intercommunality
# and syndicates (H13THS, H33THS, H23THS), plus the surcharge in high-demand areas
# (MTMAJOTHRS, CGI art. 1407 ter), which H13THS does not include. The State's fee
# is 3 % (CGI art. 1641 I-A c + II), as on the taxe foncière.
_THRS = {2024: 2208.5 + 1031.6 + 15.0 + 436.3, 2025: 1727.42 + 843.14 + 12.10 + 390.92}
_FRAIS_THRS_RATE = 0.03

YIELDS: List[TaxYield] = [
    TaxYield(
        key="tfpb", label_fr="Taxe foncière sur les propriétés bâties",
        scenario="S1", tier="local", budget="bloc communal",
        values=dict(_TFPB),
        basis="latest", status="verified",
        source="DGFiP, REI 2024–2025, via OFGL (« MONTANT RÉEL », commune + intercommunalité)",
        url="https://data.ofgl.fr/explore/dataset/rei/",
        scope="Toutes les propriétés bâties ; parts commune et intercommunalité (périmètre du modèle). "
              "Syndicats, taxes spéciales d'équipement, GEMAPI et TASA : ligne « tf_annexes ». Hors TEOM.",
    ),
    TaxYield(
        key="tfpnb", label_fr="Taxe foncière sur les propriétés non bâties",
        scenario="S1", tier="local", budget="bloc communal",
        values={y: round(v, 1) for y, v in _TFPNB.items()},
        basis="latest", status="derived",
        source="DGFiP, REI 2024–2025, via OFGL (FNB et taxe additionnelle, « MONTANT RÉEL » et bases "
               "TAFNB, commune par commune)",
        url="https://data.ofgl.fr/explore/dataset/rei/",
        scope="Terrains non bâtis hors terres agricoles et naturelles (carrières, terrains à bâtir, "
              "terrains d'agrément, voies ferrées, sols) : commune, intercommunalité et taxe additionnelle "
              "(TAFNB) ; syndicats dans « tf_annexes » ; hors chambres d'agriculture. Les terres agricoles "
              "et naturelles, hors de la réforme, gardent leur TFPNB (922 M€ en 2025 sur 1 188 M€).",
        note="Part agricole et naturelle reconstituée commune par commune : la base de la TAFNB couvre "
             "exactement les groupes non agricoles (BOI-IF-AUT-80), d'où la part non agricole de chaque "
             "commune ; contrôle par la base de l'exonération agricole de 20 % (écart 0,6 %). "
             "La compensation par l'État de cette exonération (environ 131 M€) reste hors du calcul.",
    ),
    TaxYield(
        key="tf_annexes", label_fr="Taxe foncière — syndicats, TSE, GEMAPI et TASA",
        scenario="S1", tier="local", budget="bloc communal et établissements publics",
        values={y: round(v, 1) for y, v in _TF_ANNEXES.items()},
        basis="latest", status="derived",
        source="DGFiP, REI 2024–2025, via OFGL (« MONTANT RÉEL », bâti et non bâti)",
        url="https://data.ofgl.fr/explore/dataset/rei/",
        scope="Prélevés sur l'avis de taxe foncière, sur la même base : syndicats (191 M€ en 2025), "
              "taxes spéciales d'équipement (277 M€, établissements publics fonciers), GEMAPI (397 M€) "
              "et taxe additionnelle spéciale annuelle d'Île-de-France (58 M€).",
        note="Ajoutée après la revue Gemini du 27 octobre 2026 : même base et même avis que la taxe foncière ; "
             "la spec 0005 (§ 2) range déjà les syndicats dans le niveau local. Parts non bâties diminuées "
             "de la part des terres agricoles et naturelles, qui gardent leur TFPNB (D6).",
    ),
    TaxYield(
        key="tf_etat", label_fr="Taxe foncière — frais de gestion (État)",
        scenario="S1", tier="national", budget="État",
        values={y: round(v) for y, v in _FRAIS_TF.items()},
        basis="latest", status="derived",
        source="CGI art. 1641 (lu sur Légifrance le 27 oct. 2026) : 3 % (2 % de dégrèvement et non-valeurs, I-A, "
               "+ 1 % d'assiette et recouvrement, II) sur la taxe foncière, les syndicats et la GEMAPI ; "
               "8 % sur la TASA ; 9 % sur les TSE",
        url="https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000053546093",
        scope="Frais d'assiette, de dégrèvement et de non-valeurs ajoutés par l'État à l'avis de taxe foncière, "
              "sur les lignes « tfpb », « tfpnb » et « tf_annexes ».",
        note="Ordre de grandeur cohérent avec le REI 2025 (2 068 M€ de frais sur l'ensemble de l'avis, TEOM comprise à 8 %).",
    ),
    TaxYield(
        key="thrs", label_fr="Taxe d'habitation sur les résidences secondaires",
        scenario="S1", tier="local", budget="bloc communal",
        values={y: round(v, 1) for y, v in _THRS.items()},
        basis="latest", status="verified",
        source="DGFiP, REI 2024–2025, via OFGL (« MONTANT RÉEL » THS et majoration MTMAJOTHRS)",
        url="https://data.ofgl.fr/explore/dataset/rei/",
        scope="Résidences secondaires et autres logements meublés non affectés à l'habitation principale : "
              "parts commune, intercommunalité et syndicats (2 583 M€ en 2025) et majoration en zone tendue "
              "(391 M€, CGI art. 1407 ter). Hors taxe sur les logements vacants.",
        note="Ajoutée par décision du 27 octobre 2026 : c'est un impôt local sur la propriété résidentielle, "
             "payé dans la plupart des cas par le propriétaire. Baisse de 19 % entre 2024 (3 691 M€) et 2025, "
             "dans presque tous les départements, non expliquée (correction probable des déclarations d'occupation) ; "
             "2025 est retenu, conformément à D1.",
    ),
    TaxYield(
        key="thrs_etat", label_fr="Taxe d'habitation (résidences secondaires) — frais de gestion (État)",
        scenario="S1", tier="national", budget="État",
        values={y: round(_FRAIS_THRS_RATE * v) for y, v in _THRS.items()},
        basis="latest", status="derived",
        source="CGI art. 1641 (lu sur Légifrance le 27 oct. 2026) : 2 % de dégrèvement et non-valeurs (I-A c) "
               "+ 1 % d'assiette et recouvrement (II)",
        url="https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000053546093",
        scope="Frais ajoutés par l'État à l'avis de taxe d'habitation sur les résidences secondaires, majoration comprise.",
        note="Le REI 2025 donne 93 M€ de frais sur la taxe d'habitation (variable H01), proche des 89 M€ calculés ici.",
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
        source="CGI art. 1647 V (lu sur Légifrance le 27 oct. 2026) : 2,37 % en sus des droits départementaux "
               "(2,14 % là où le taux départemental est réduit à 0,70 %)",
        url="https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000054373998",
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
        values={2022: 1800, 2023: 1900, 2024: 2159, 2025: 2332},
        basis="latest", status="verified",
        source="DGFiP Statistiques n° 15 (2022), n° 23 (2023) ; n° 45 (avril 2026), tableau 1 (2024–2025)",
        url="https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-la-fortune-immobiliere-en-2025",
        scope="Montant des avis d'IFI, tous redevables.",
        note="Les recettes budgétaires sont plus élevées (ligne 1406 : 2 739 M€ en 2024, 2 771 M€ encaissés en 2025). "
             "Selon la DGFiP (Statistiques n° 45), elles incluent les restes d'avis antérieurs et le produit du contrôle "
             "fiscal ; la ligne comprend aussi les reliquats d'ISF.",
    ),
    TaxYield(
        key="rents_ir", label_fr="Revenus locatifs — impôt sur le revenu",
        scenario="S3", tier="national", budget="État",
        values={2022: 4198},
        basis="latest", status="verified",
        source="CPO, Pour une fiscalité du logement plus cohérente (déc. 2023), p. 23, et rapport particulier n° 1, p. 47 ; "
               "compte du logement 2022, partie 6, tableau 1",
        url="https://www.vie-publique.fr/files/rapport/pdf/292676.pdf",
        scope="IR sur les revenus locatifs de logements des particuliers, net des réductions d'impôt (Pinel, etc.). "
              "Locations meublées (BIC) non isolées (D7) ; locaux non résidentiels exclus ; hors IS (D3).",
        note="Le total de 8,3 Md€ du CPO (8 264 M€) est la ligne « impositions sur les revenus immobiliers » du compte "
             "du logement : IR 4 198 + PS 2 399 + CSG 1 093 + CRL 107 + IS 467. La CRL et l'IS, payés par des sociétés, "
             "sont exclus (D3). Le compte du logement 2024 donne 8 895 M€ pour 2024, sans détail.",
    ),
    TaxYield(
        key="rents_ps", label_fr="Revenus locatifs — prélèvements sociaux",
        scenario="S3", tier="national", budget="Sécurité sociale et État",
        values={2022: 2399},
        basis="latest", status="verified",
        source="CPO (déc. 2023), rapport particulier n° 1, p. 47 et tableau 28 ; compte du logement 2022, partie 6, tableau 1",
        url="https://www.vie-publique.fr/files/rapport/pdf/292676.pdf",
        scope="Prélèvements sociaux sur les revenus locatifs de logements des particuliers, hors CSG (ligne « rents_csg »).",
        note="Le partage entre « PS » et « CSG » du compte du logement suit une convention comptable (la CSG passe de "
             "87 M€ en 2017 à 1 016 M€ en 2018) : seule la somme des deux lignes (3 492 M€) est fiable.",
    ),
    TaxYield(
        key="rents_csg", label_fr="Revenus locatifs — CSG",
        scenario="S3", tier="national", budget="Sécurité sociale",
        values={2022: 1093},
        basis="latest", status="verified",
        source="CPO (déc. 2023), p. 23, et rapport particulier n° 1, p. 47 et tableau 28 ; "
               "compte du logement 2022, partie 6, tableau 1",
        url="https://www.vie-publique.fr/files/rapport/pdf/292676.pdf",
        scope="CSG sur les revenus locatifs de logements des particuliers, en plus de la ligne « rents_ps ».",
        note="Ajoutée après la revue Gemini du 27 octobre 2026 : le rapport particulier du CPO présente la CSG et les PS "
             "comme deux lignes qui s'additionnent.",
    ),
]

SCENARIOS: Dict[str, List[str]] = {
    "S1": ["S1"],
    "S2": ["S1", "S2"],
    "S3": ["S1", "S2", "S3"],
}


@dataclass(frozen=True)
class Farmland:
    """Farmland at market prices: SAFER price per hectare × area (decision D6).

    Arable land and grassland (orchards and other permanent crops included) are
    valued at the midpoint of the prices of vacant and let land; the range uses
    each price alone. Vineyards are valued at the AOP price excluding Champagne,
    which undervalues Champagne and overvalues non-AOP vines.
    """

    area_ha: float = 26_638_633 - 747_976
    vine_area_ha: float = 747_976
    price_free_eur_ha: float = 6_460
    price_let_eur_ha: float = 5_350
    vine_price_eur_ha: float = 87_400
    year: int = 2025
    source: str = ("Groupe Safer, Le prix des terres 2025 (mai 2026), et Agreste, Statistique agricole "
                   "annuelle 2025 provisoire (SAU des exploitations, France hors DROM)")
    url: str = "https://www.le-prix-des-terres.fr/app/uploads/2026/05/2026-LPDT-synthese.pdf"

    def _value(self, price: float) -> float:
        return (self.area_ha * price + self.vine_area_ha * self.vine_price_eur_ha) / 1e6

    @property
    def value(self) -> float:
        """Central value, M€."""
        return self._value((self.price_free_eur_ha + self.price_let_eur_ha) / 2)

    @property
    def low(self) -> float:
        return self._value(self.price_let_eur_ha)

    @property
    def high(self) -> float:
        return self._value(self.price_free_eur_ha)


FARMLAND = Farmland()

# Not in the base (D6 sensitivity): forests, 17,5 Mha (IGN, Mémento 2024) at the
# SAFER price of 4 950 €/ha, which includes standing timber, so an upper bound.
FOREST_UPPER_MEUR = 17_500_000 * 4_950 / 1e6
# INSEE's own value of cultivated land (AN.2112), end-2025, not used: about five
# times the market price per hectare, with no published method.
INSEE_FARMLAND_MEUR = 902_100


@dataclass(frozen=True)
class UnbuiltLand:
    """Unbuilt building land at market prices, an estimate (open point of #48).

    INSEE values the buildable part of unbuilt land at housing prices, but in
    its unbuilt-land lines (AN.2119, partly AN.2112), which it does not split;
    it is therefore missing from built land (AN.2111), the rest of the base.
    Rebuilt as area × price, in two parts, each with a low / central / high case:

    * AU zones (to be urbanised): 144 976 ha unbuilt in the 12 051 communes
      studied by Cerema, an under-count (no AU zone or no plan online elsewhere),
      so 145 000-250 000 ha; raw unserviced land at 10-40 €/m².
    * Vacant plots in U zones: no national stock is published. Assumed
      100 000-250 000 ha at 50-150 €/m², against 102 €/m² for serviced plots
      bought for a house in 2024 (SDES, EPTB). The weakest step.

    A share of 85 % (80-90 %) is taken as privately held, since public land is
    exempt.

    Only the AU part enters the base. The U part is a sensitivity: no stock is
    published, and a vacant plot in a U zone is often a garden sold with its
    house, already priced in built land (AN.2111) through house prices
    (Gemini review, 29 October), so adding it risks double counting.
    """

    au_ha: tuple = (145_000, 185_000, 250_000)
    au_eur_m2: tuple = (10, 20, 40)
    u_ha: tuple = (100_000, 150_000, 250_000)
    u_eur_m2: tuple = (50, 100, 150)
    private_share: tuple = (0.90, 0.85, 0.80)
    source: str = ("Cerema, Consommation d'espaces et documents d'urbanisme (nov. 2023) ; SDES, Le prix "
                   "des terrains et du bâti pour les maisons individuelles en 2024 (nov. 2025) ; INSEE, "
                   "fiche méthodologique 24, base 2020 (juil. 2026)")
    url: str = ("https://artificialisation.developpement-durable.gouv.fr/sites/artificialisation/files/"
                "inline-files/conso_enaf_docurba.pdf")

    def _au(self, i: int) -> float:
        return self.au_ha[i] * 1e4 * self.au_eur_m2[i] / 1e6 * self.private_share[i]

    def _u(self, i: int) -> float:
        return self.u_ha[i] * 1e4 * self.u_eur_m2[i] / 1e6 * self.private_share[i]

    @property
    def low(self) -> float:
        return self._au(0)

    @property
    def value(self) -> float:
        """Central value of AU land, M€ (in the base)."""
        return self._au(1)

    @property
    def high(self) -> float:
        return self._au(2)

    @property
    def u_value(self) -> float:
        """Central value of vacant U plots, M€ (sensitivity only)."""
        return self._u(1)

    @property
    def u_high(self) -> float:
        return self._u(2)


UNBUILT_LAND = UnbuiltLand()


@dataclass(frozen=True)
class LandBase:
    """Taxable land value used for indicative national rates, M€."""

    built_land_total: float = 7_032_000
    built_land_public: float = 941_000
    # Non-financial (S11, 1 700,7 Md€) and financial (S12, 200,3 Md€) companies,
    # INSEE T_8200_2025, row N2111.
    built_land_companies: float = 1_701_000 + 200_000
    # Unbuilt AU land: in the reform, so in the base (U plots: sensitivity)
    unbuilt: float = UNBUILT_LAND.value
    # D6 sensitivity only: farmland is outside the reform, so not in `taxable`
    farmland: float = FARMLAND.value
    year: int = 2025
    source: str = ("INSEE, Chiffres-clés « Patrimoine national par secteur institutionnel et grand type "
                   "d'actif », données 2025 provisoires (30 juillet 2026)")
    url: str = "https://www.insee.fr/fr/statistiques/2830290"
    note: str = ("Terrains bâtis hors administrations publiques (foncier public exonéré), plus une "
                 "estimation des terrains à bâtir non bâtis, que l'INSEE range avec les terrains non bâtis "
                 "sans les isoler. Terres agricoles et naturelles hors de la réforme (D6).")

    @property
    def taxable_built(self) -> float:
        return self.built_land_total - self.built_land_public

    @property
    def taxable(self) -> float:
        return self.taxable_built + self.unbuilt

    @property
    def taxable_with_farmland(self) -> float:
        """D6 sensitivity: the base if farmland entered at SAFER prices."""
        return self.taxable + self.farmland

    @property
    def companies_share(self) -> float:
        """Companies' share of taxable built land, applied to the whole base."""
        return self.built_land_companies / self.taxable_built


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


def scenario_total_constant(scenario: str, include_ifi: bool = False) -> float:
    """Total reference yield in CPI_YEAR euros, M€ (D1 sensitivity)."""
    return sum(t.reference_constant() for t in lines_for(scenario, include_ifi))


def companies_shift(scenario: str, include_ifi: bool = False,
                    base: Optional[LandBase] = None) -> float:
    """Yield moved onto companies' land by S2–S3, M€ a year (D3).

    S2 and S3 replace taxes that only individuals pay (IR and social levies on
    gains and rents, IFI); companies' corporate tax on the same income stays.
    The national rate that replaces them falls on all land, so companies pay
    their share of the base on these lines without any tax of theirs being cut.
    S1 lines are paid by companies and individuals alike and are left out.
    """
    b = base or LAND_BASE
    added = sum(t.reference() for t in lines_for(scenario, include_ifi) if t.scenario != "S1")
    return b.companies_share * added


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


def farmland_sensitivity(scenario: str = "S1", base: Optional[LandBase] = None) -> Dict[str, float]:
    """D6 sensitivity: farmland in the reform at SAFER prices, its TFPNB replaced too.

    Returns the rate, % of land value, and what farmland would pay, M€ a year.
    """
    b = base or LAND_BASE
    y = max(_TFPNB_FARM)
    sh = _FARM_SHARE[y]
    farm_tf = ((_TFPNB_FARM[y] + sh * (_GEMAPI_NB[y] + _SYNDICATS_NB[y])) * (1 + _FRAIS_TF_RATE)
               + sh * _TSE_NB[y] * (1 + _FRAIS_TSE_RATE))      # with the State's fees
    total = scenario_total(scenario) + farm_tf
    rate = 100.0 * total / b.taxable_with_farmland
    return {"rate_pct": rate, "farmland_pays_meur": rate / 100 * b.farmland,
            "farmland_tfpnb_meur": _TFPNB_FARM[y]}


def export_json(path: str | Path = "site/public/data/yields.json") -> dict:
    """Write the yield table and scenario totals for the site."""
    variants = []
    for sc in SCENARIOS:
        for ifi in ((False, True) if sc != "S1" else (False,)):
            variants.append({
                "scenario": sc, "include_ifi": ifi,
                "total_meur": round(scenario_total(sc, ifi)),
                "total_constant_meur": round(scenario_total_constant(sc, ifi)),
                "tiers_meur": {k: round(v) for k, v in tier_totals(sc, ifi).items()},
                "rate_pct": round(indicative_rate_pct(sc, ifi), 2),
                "companies_shift_meur": round(companies_shift(sc, ifi)),
                "lines": [t.key for t in lines_for(sc, ifi)],
            })
    farm = farmland_sensitivity()
    payload = {
        "as_of": "2026-10-29",
        "average_years": AVERAGE_YEARS,
        "constant_euros": {"year": CPI_YEAR, "source": CPI_SOURCE, "url": CPI_URL},
        "taxes": [{
            "key": t.key, "label_fr": t.label_fr, "scenario": t.scenario,
            "tier": t.tier, "budget": t.budget, "basis": t.basis, "status": t.status,
            "values_meur": {str(y): round(v, 1) for y, v in sorted(t.values.items())},
            "reference_years": t.reference_years(),
            "reference_meur": round(t.reference()),
            "source": t.source, "url": t.url, "scope": t.scope, "note": t.note,
        } for t in YIELDS],
        "land_base": {
            "taxable_meur": round(LAND_BASE.taxable), "total_meur": LAND_BASE.built_land_total,
            "public_meur": LAND_BASE.built_land_public, "year": LAND_BASE.year,
            "companies_meur": LAND_BASE.built_land_companies,
            "companies_share": round(LAND_BASE.companies_share, 4),
            "source": LAND_BASE.source, "url": LAND_BASE.url, "note": LAND_BASE.note,
            "built_taxable_meur": round(LAND_BASE.taxable_built),
            "unbuilt": {
                "value_meur": round(UNBUILT_LAND.value), "low_meur": round(UNBUILT_LAND.low),
                "high_meur": round(UNBUILT_LAND.high),
                "u_value_meur": round(UNBUILT_LAND.u_value), "u_high_meur": round(UNBUILT_LAND.u_high),
                # S1 rate if the vacant U plots were in the base too (central, high)
                "s1_rate_with_u_pct": round(100 * scenario_total("S1")
                                            / (LAND_BASE.taxable + UNBUILT_LAND.u_value), 2),
                "s1_rate_with_u_high_pct": round(100 * scenario_total("S1")
                                                 / (LAND_BASE.taxable_built + UNBUILT_LAND.high
                                                    + UNBUILT_LAND.u_high), 2),
                "source": UNBUILT_LAND.source, "url": UNBUILT_LAND.url,
            },
            "farmland": {
                "value_meur": round(FARMLAND.value), "low_meur": round(FARMLAND.low),
                "high_meur": round(FARMLAND.high), "area_ha": FARMLAND.area_ha,
                "vine_area_ha": FARMLAND.vine_area_ha, "price_free_eur_ha": FARMLAND.price_free_eur_ha,
                "price_let_eur_ha": FARMLAND.price_let_eur_ha, "vine_price_eur_ha": FARMLAND.vine_price_eur_ha,
                "year": FARMLAND.year, "source": FARMLAND.source, "url": FARMLAND.url,
                "insee_meur": INSEE_FARMLAND_MEUR, "forest_upper_meur": round(FOREST_UPPER_MEUR),
                "included": False,
                "tfpnb_meur": round(farm["farmland_tfpnb_meur"]),
                "tfpnb_all_meur": round(_TFPNB_ALL[max(_TFPNB_ALL)]),
                "s1_rate_if_included_pct": round(farm["rate_pct"], 2),
                "pays_if_included_meur": round(farm["farmland_pays_meur"]),
            },
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
