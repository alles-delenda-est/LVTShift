# Social housing (HLM) per parcel: source verification

Verified live on 3 November 2026, using Montreuil (93048) and Villeurbanne (69266) as test communes.
Everything below is an aggregate. The report contains no addresses, no parcel ids and no statistics per landlord.

## 0. Bottom line

| | Montreuil | Villeurbanne |
|---|---|---|
| Social dwellings, RPLS at 1 Jan 2025 (detailed file) | **18,755** | **21,711** |
| Same figure in the SDES commune file (parc social + HLM free-rent dwellings) | 18,708 + 47 = 18,755 (exact match) | 21,662 + 49 = 21,711 (exact match) |
| Not in the detailed file: non-conventioned SEM dwellings | 255 | 262 |
| Share of all dwellings (INSEE RP 2023: 54,472 / 93,196) | 34.4 % | 23.3 % |
| SDES density (social dwellings per 100 résidences principales) | 37.7 | 26.7 |
| of which student dwellings (TYPECONST = E) | 446 | 2,954 |
| Parcels where a social landlord holds the taxable right on built units (DGFiP PM 2025) | 410 | 722 |
| of which "estates" (the landlord also holds the land) | 289 | 395 |
| Parcels that receive RPLS dwellings (PM-anchored join) | 496 | 651 |
| Union: parcels with social presence | 591 | 830 |
| PM parcels with social units *or* social land (land-only ones include roads, green space, car parks) | 915 | 933 |
| RPLS habitable area | 1.14 M m² | 1.27 M m² |
| As a share of BD TOPO gross residential floor area (4.67 / 7.85 M m²), raw | 24 % | 16 % |
| Same after a habitable-to-gross factor of 0.75 / 0.70 (the medians observed, §4) | ≈ 32 % | ≈ 23 % |
| BD TOPO gross residential floor on social-presence parcels: an upper bound, because mixed parcels count in full | 30 % | 32 % |
| **Likely 1384 A/C-exempt in 2025, 15-year bracket** (conventioned, not PLI; new build or VEFA by CONSTRUCT ≥ 2010, acquisition by PATRIMOINE ≥ 2010) | **4,275 (22.8 %)** | **5,980 (27.5 %)** |
| same, using first-letting year (LOCAT) for new builds | 4,455 (23.8 %) | 6,067 (27.9 %) |
| **25-year bracket** (≥ 2000) | **6,139 (32.7 %)** | **7,924 (36.5 %)** |
| same, using LOCAT | 7,238 (38.6 %) | 8,106 (37.3 %) |
| Split of the 15-year bracket: new build + VEFA / acquisition | 2,543 / 1,732 | 4,342 / 1,638 |
| Parcels holding ≥ 1 bracketed-exempt dwelling, 15 y / 25 y (all exempt: 100 / 191 and 233 / 315) | 141 / 241 | 293 / 375 |
| **Dwellings in a QPV 2024** (geocoded; landlord declaration 9,627 / 4,970; SDES file 9,581 / 4,975) | **9,619 (51.3 %)** | **4,947 (22.8 %)** |
| QPV dwellings that are conventioned and outside the exempt bracket (1388 bis candidates), 15 y / 25 y | 7,518 / 7,086 | 3,870 / 3,863 |
| Parcels with social dwellings in a QPV | 143 | 75 |

The exemption counts are brackets, not rules. The tax year is 2025 and the exemption runs from year N+1 to N+15 (or N+25), so the cut-offs are 2010 and 2000. The exact duration depends on the date of the financing decision. RPLS carries **DATCONV**, the date the convention took effect, for more than 99 % of recent new builds, so the agent establishing the rules can apply a decision-date rule directly (§1).

## 1. RPLS (SDES): open, dwelling-level, with coordinates; no parcel reference and no landlord

- **Dataset:** SDES DiDo, id `6390f7cb84f0679b04942fc2`, "Données détaillées au logement du RPLS". It is mirrored on data.gouv.fr as dataset `689c42dc21932fa1640d99c3` (SDES organisation).
  - Datafile rid `f3c2f2cb-8fb1-40fd-8733-964247744c9a`.
  - Millésimes 2022-01, 2023-01, 2024-01 and **2025-01** (latest: 5,416,826 rows, published 20 Jan 2026). DiDo's `frequency_date` gives **2027-01-20** for the next millésime (1 Jan 2026).
  - Older vintages (2021 to 2024) are also available as zip attachments.
- **API (no key):**
  `https://data.statistiques.developpement-durable.gouv.fr/dido/api/v1/datafiles/f3c2f2cb-8fb1-40fd-8733-964247744c9a/csv?millesime=2025-01&withColumnName=true&withColumnDescription=false&withColumnUnit=false&DEPCOM=eq:<insee>`
  - Returns `;`-separated, quoted UTF-8, 73 columns, 12.5 MB for Montreuil and 14.1 MB for Villeurbanne.
  - The `/rows` endpoint (pageSize 10/20/50/100) returns a `total`, useful as a cheap count check.
  - **DEPCOM uses arrondissement codes for Paris, Lyon and Marseille:** `75056` and `69123` return 0 rows, while `75111` returns 10,942 and `69381` returns 2,820. This matches the pipeline's `data_codes`.
  - Filters on the extended zones `DEP`, `EPCI` and `PLG_IRIS2024` also exist.
- **Licence:**
  - DiDo and data.gouv declare `fr-lo`, which data.gouv resolves to "Licence Ouverte / Open Licence" (Etalab v1.0).
  - **Caveat:** the SDES dictionary (`.../dido/api/files/c6a10559-a936-4bee-9be0-a2fc7d36e18e`, sheet 1) restates the *décret 2009-1485* diffusion rules:
    - no public statistic may identify a landlord;
    - no public aggregate may rest on fewer than 11 dwellings, *unless it covers a whole commune*, where every crossing is allowed;
    - the detailed data "cannot be redistributed as is".
  - Our use (commune-level aggregates, no file redistribution, nothing per landlord) is compatible with these rules. Treat them as binding, and **do not republish the RPLS rows or any parcel-level derivative**.
- **Scope (SDES methodology note, `.../media/2281/download`):**
  - Covered: HLM bodies, SEMs (L.481-1), agreed MOI bodies (L.365-2), Foncière Logement and a few others. Their "logements ordinaires" held in full ownership, usufruct, emphyteusis, building lease or rehabilitation lease.
  - **Excluded: logements-foyers, foyers de travailleurs and résidences sociales**. These can also be TFPB-exempt.
  - The open file also excludes **non-conventioned SEM dwellings**.
  - The landlord's identity is not supplied.
- **Field names** (2025-01; codes from the dictionary):

| Need | Field(s) | Fill rate, Montreuil / Villeurbanne |
|---|---|---|
| Commune | `DEPCOM` (+ `LIBCOM`, `CODEPOSTAL`) | 100 % |
| Address | `NUMVOIE`, `INDREP`, `TYPVOIE`, `NOMVOIE`, `COMPLGEO` (programme), `LIEUDIT`, `ETAGE`, `PLG_VOIE` | NUMVOIE 95 % / **38 %**, NOMVOIE 100 % |
| Coordinates | `X`, `Y`, `EPSG` (2154 in mainland France), quality `QUALITE_XY` (11 = street sure and number found; 12, 21, 22, 33 = random within the street or commune), `DISTANCE_PRECISION` | X/Y 99.3 % / 96.7 %; QUALITE_XY = 11: 98.7 % / 96.0 % |
| **Cadastral parcel** | **none** | 0 % |
| Construction year | `CONSTRUCT` (year the construction was completed) | 100 % |
| First letting year | `LOCAT` | 100 % |
| Year entered the landlord's stock, and how | `PATRIMOINE`; `ORIGINE` (1 built by the body, 2 acquired with works, 3 acquired without works, 4 VEFA) | 100 % |
| Financing | `FINAN_CODE` / `FINAN_LIBELLE` (10 PLA-I/LLTS, 11 PLA-LM/PLATS/PLAI, 12 PLA ordinaire, 13 PLUS, 14 PLS/PPLS/PLA-CFF, 16 PLI, 17 PCL, 49 other ≥ 1977, 50–55 HBM/PLR/PSR/HLM-O/ILM/ILN/CFF, 99 other < 1977), `FINANAUTRE`, `CUS` | 100 % |
| Conventionnement | `CONV` (1 yes, 2 no), `NUMCONV`, **`DATCONV`** (ISO date), `SRU_EXPIR`, `SRU_ALINEA` | CONV 100 %; DATCONV 96 % / 91 % overall and > 99 % for new builds since 2000 |
| QPV | `QPV_CODE` (landlord's declaration, 1/2), `PLG_QP24` (INSEE geocoding: QPV 2024 code `QNxxxxx`, `HZ` outside, `CSZ` commune without zoning), `QUALITE_QP24`, `PLG_QP15`, `COMAQP` | 100 % / 99.3 % (96.7 %) |
| Number of dwellings | one row = one dwelling (no count field); `SURFHAB`, `NBPIECE`, `TYPECONST` (C / I / E for students) | |
| Landlord's right | `DROIT_CODE` (1 full ownership, 2 rehabilitation lease, 3 emphyteusis, 4 usufruct, 5 building lease, 6 BRS, 7 BRI) | Villeurbanne: 1,793 emphyteusis, 814 building lease, 255 usufruct |
| Landlord identity (SIREN or name) | **none** (the dictionary mentions `ident_int` / `ident_rep`, but they are not in the open file) | |
| Other | DPE, PMR, IRIS 2024, UU/AAV/ZE 2020 | |

- **Other RPLS products** (aggregated, not usable per parcel):
  - SDES "données nationales régions/départements/EPCI/communes – RPLS au 1er janvier 2025": a 20 MB zip at `https://www.statistiques.developpement-durable.gouv.fr/media/8938/download`, one xlsx with a commune sheet. Used above for the cross-check.
  - INSEE RPLS by IRIS (`insee.fr/fr/statistiques/9057420`) and by QPV 2024 (`/9054633`).
  - Regional and departmental re-publications on data.gouv (Géo2France, DREAL Bretagne, DDT 82…). These are older or partial.

## 2. QPV 2024 contours (ANCT)

- **Source:** data.gouv.fr dataset `5a561801c751df42d7fca9b6`, "Quartiers prioritaires de la politique de la ville (QPV)", ANCT. Licence `fr-lo` (Licence Ouverte), updated 6 Oct 2026.
  - It describes the **decree 2023-1314 of 28 Dec 2023** (in force from 1 Jan 2024).
  - The decree of 14 July 2024 corrected names and commune attachments only.
  - Overseas territories: decree 2024-1212 (from 1 Jan 2025). Mayotte became a QPV in full under decree 2025-1435 of 30 Dec 2025.
- **Files:**
  - `qpv-2024-geojson.zip` (8.4 MB): `https://static.data.gouv.fr/resources/quartiers-prioritaires-de-la-politique-de-la-ville-qpv/20260115-204323/qpv-2024-geojson.zip`.
    - `GEOJSON/QP2024_France_hexagonale_LB93.geojson`: **1,362 MultiPolygons in EPSG:2154**.
    - `QP2024_France_Hexagonale_Outre_Mer_WGS84.geojson`: 1,584 features.
    - Plus one file per overseas territory in its local CRS.
  - The same layers exist as GPKG / SHP (`qpv-2024-gpkg.zip`, `qpv-2024-shp.zip`, `qpv-2024.zip` with all formats).
  - List as CSV: `listeqp2024-cog2025.csv` (1,618 rows, COG 2025).
  - Correspondence table QP 2015 → QP 2024.
- **Fields:** `fid`, `code_qp` (e.g. `QN09318M`), `lib_qp`, `insee_reg`, `lib_reg`, `insee_dep`, `lib_dep`, `insee_com`, `lib_com`, `siren_epci`.
  - **`insee_com` lists every commune of a multi-commune QPV**, joined by `", "` in the GeoJSON. Three of Montreuil's five QPVs straddle the commune boundary.
  - The CSV writes `insee_com` as an Excel formula (`"=""93006;93048"""`), so parse it with care.
  - `siren_epci` differs between the GeoJSON (the EPT) and the CSV (the MGP).
- **Pitfalls:**
  - The Géoplateforme WFS (`data.geopf.fr/wfs`) only exposes the **2015** QP layers (`AREAMANAGEMENT.QP.VECTOR:qp_decretmodif_2015…`). Do not use it.
  - `sig.ville.gouv.fr` offers atlases and a geocoding service, but no bulk download.
- **Check:** Montreuil has 5 QPVs and Villeurbanne 5. A point-in-polygon of the RPLS points against these contours reproduces RPLS `PLG_QP24` **for 100 % of dwellings** (9,619 / 4,947). Parcel-level QPV can therefore be taken from the polygons directly; 1,748 / 444 cadastre parcels have their representative point inside a QPV.

## 3. DGFiP "locaux et parcelles des personnes morales" (already in the pipeline)

- **Source and files:**
  - Catalogue: `https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/fichiers-des-locaux-et-des-parcelles-des-personnes-morales/attachments`. Licence Ouverte 2.0, as in `exemptions.py`.
  - The 2025 zips were read **from the pipeline cache**, with no re-download:
    - locaux: sha `0751f0c2c923…`, 204 MB;
    - parcelles 57–976: `2d1ab0c53b5b…`;
    - parcelles 01–56: `36a840600e60…`.
  - Members `PM_25_B_930.csv`, `PM_25_B_690.csv`, `PM_25_NB_930.csv`, `PM_25_NB_690.csv`. The schema matches `B_COLS` / `NB_COLS`.
- **Side finding: the 2026 vintage is published, and `exemptions._attachments` would not read it.** The attachment ids changed (`fichiers_des_locaux_situation_2026zip`, `fichiers_des_parcelles_dpts_1_a_30_situation_2026zip`, `fichier_des_parcelles_31_a_60_situation_2026zip`, `fichiers_des_parcelles_dpts_61_a_976_situation_2026zip`).
  - They have no `_zip` suffix, and one parcelles id has no `dpts_` prefix.
  - Bumping `PM_YEAR` to 2026 would therefore raise `IngestUnavailable`. It fails loudly, not silently, but it needs a fix whenever the year is bumped.
- **Identification fields** (definitions from DGFiP's 2025/2026 descriptif):
  - `Groupe personne` codes: 0 not notable, 1 State, 2 region, 3 department, 4 commune, **5 "office HLM"**, **6 SEM**, 7 co-owners, 8 partners, 9 public bodies.
  - `Forme juridique`: INSEE codes, with labels confirmed in the descriptif:
    - 4140 local EPIC (the legal form of OPHs);
    - 7371 OPHLM;
    - **5546 / 5646 SA de HLM**;
    - **5547 / 5647 coopérative de production d'HLM**;
    - **5515 / 5615 SEM**;
    - 5560 other cooperative SA (some HLM coops);
    - 5599 / 5699 generic SA ("s.a.i."): **many large ESH are registered this way**.
  - Also `N° SIREN`, `Dénomination` and `Code droit`. On the code: P owner; U/N usufruct / bare ownership; B/R building lessor / lessee; V/W rehabilitation lessor / lessee; E emphyteuta; G manager; S syndic; O AOT; Z State manager.
- **Reliability findings:**
  1. **Groupe 5 is the best single flag, but it is not sufficient:**
     - It is recorded per row, not per SIREN. Among the SIRENs that have any groupe-5 row, 4.6 % (dep. 93) and 5.3 % (dep. 69) of their rows carry another code (0 or 9).
     - **One OPH (the Métropole de Lyon's) is never coded 5 (it is coded 9)**, and it is a major landlord in Villeurbanne.
     - Three HLM-form SIRENs per département are never coded 5.
     - Groupe 5 also contains an intermediate-rent (LLI) company (IN'LI), which is not social, and a few SCI/SC.
  2. **Recommended rule (SIREN-level, built over the whole département or nation, not the commune):**
     - *HLM* = SIREN with any groupe-5 row, ∪ legal form 5546/5646/5547/5647/7371, ∪ (4140 and a name matching OFFICE PUBLIC|OPH|OPAC|HABITAT|HLM);
     - minus a short deny-list of LLI companies;
     - *SEM* = groupe 6 or 5515/5615, kept as a separate class: SEMs are partly non-social (developers, lessors), so they need RPLS corroboration.
     - A social landlord is the taxable holder of a unit when it holds **E/R/W/U**, or **P with no other E/R/W/U holder**. B (building lessor) and G/S (managers) are not holders.
     - This gives 31 HLM + 4 SEM SIRENs in Montreuil and 23 + 14 in Villeurbanne.
  3. **The PM files do not give dwelling counts:**
     - `N° Majic` is the *owner's* MAJIC person number, not a unit id. There is no invariant, and **no nature-of-unit field**: units are keyed by (parcel, bâtiment, entrée, niveau, porte), which is near-unique.
     - Social units number 37,489 in Montreuil and 47,029 in Villeurbanne, i.e. **2.0× and 2.2× the RPLS dwellings**: parking spaces, cellars and shops are separate units.
     - Only units held by legal persons are listed, so on mixed parcels (VEFA in co-ownership) there is no denominator.
     - **Use PM for *which parcels* and *whose*, and RPLS for *how many* and *which regime*.**
  4. **Parcel typology:**
     - Of the 410 / 722 parcels with social units, the landlord also holds the land on **289 / 395** ("estates"). These carry 77 % / 69 % of the social units.
     - On 119 / 324 parcels it does not: there the land is held by natural persons or a co-ownership, i.e. mostly VEFA in mixed buildings, which is frequent in Villeurbanne (RPLS ORIGINE 4: 3,181 dwellings).
     - 9 / 39 social parcels have a syndic.
     - These mixed parcels need a *fractional* social share, not a whole-parcel flag.
  5. **Interaction with the existing public-exemption rule:** `HOUSING_RE` already stops public parcels with housing managers from being flagged as exempt. On public land under a building lease or emphyteusis with an OPH (B or P by the commune, R or E by the OPH), the new rule makes the parcel "social" (taxable holder = the OPH), which is consistent.

## 4. Joining RPLS to cadastre parcels (pipeline fetchers, read from cache)

- **Setup:** `ingest.fetch_parcels` and `ingest.fetch_buildings` / `_wfs_features` from the `results-wording` worktree. `_get` was replaced by a read-only reader of `lvtshift-fr/output/cache`; all 19 / 15 requests were cache hits and there were 0 live fetches.
  - Parcels: 14,218 / 10,782.
  - BD TOPO buildings in the bbox: 42,222 / 30,030.
- **RPLS geometry:**
  - 1,199 / 1,321 distinct address points carry 18,629 / 20,985 geolocated dwellings.
  - 68 % / 70 % of the points fall inside a parcel. The rest lie on the street, and **all but 2 / 3 dwellings are within 15 m of a parcel**.
- **Three joins were tested:**
  - **A, point in parcel (nearest within 15 m):** matches 99.99 % of dwellings.
  - **B, nearest dwelling building within 30 m, then that building's main parcel:**
    - Matches 86.9 % / 94.1 % of dwellings.
    - Median distance 5.9 / 0.9 m; 90th percentile 18.8 / 15.1 m.
    - A and B agree on the parcel for only **52 % / 72 %** of dwellings: within an estate, the address point often sits on a neighbouring parcel of the same estate.
  - **C, PM-anchored (recommended): nearest parcel where a social landlord holds units or land, within 30 m, otherwise A:**
    - **96.0 % / 94.1 %** of geolocated RPLS dwellings are within 30 m of a PM-social parcel.
    - 89 % / 86 % are within 10 m, and 53 % / 53 % inside one.
    - The rest are 30–60 m away (interquartile range).
    - Conversely, **77 % / 75 %** of PM-social parcels (81 % / 82 % of their units) receive RPLS dwellings.
    - The PM parcels left over carry only 811 / 3,585 BD TOPO dwellings: foyers and résidences sociales (excluded from RPLS), non-conventioned SEM or LLI stock, shops and car parks, or estate parcels whose address point fell next door.
- **RPLS dwellings compared with BD TOPO `nombre_de_logements` on matched parcels:**

| Test | Result |
|---|---|
| Join A, totals on matched parcels | RPLS 18,627 vs BD TOPO 10,098; 20,982 vs 17,321 |
| Matched parcels with 0 BD TOPO dwellings | 220 / 238 parcels, carrying 5,978 / 3,639 RPLS dwellings |
| Per parcel, within ±25 % (joins A/B/C) | only 27–34 % of parcels and 25–30 % of dwellings, both communes |
| Estate clusters (contiguous social parcels), within ±25 % | 24 % / 27 % of dwellings |
| Estate clusters, dwelling-weighted median ratio RPLS/BD TOPO | **1.8 / 1.7** |
| **Floor area per cluster:** RPLS habitable m² vs BD TOPO gross residential m², area-weighted median (IQR) | **0.75 (0.65–1.30) / 0.70 (0.53–1.07)**, a plausible habitable/gross ratio |
| Floor area over all join-C parcels | 1.13 M vs 1.33 M m² (Montreuil) |

  - **BD TOPO dwelling counts are the weak side:**
    - In Montreuil, 27 % of the residential footprint on social parcels (30 % commune-wide) has no `nombre_de_logements`. In Villeurbanne the figure is 3 % (2 % commune-wide).
    - Commune totals are 39,570 / 65,431 against **54,472 / 93,196 INSEE 2023 dwellings** (−27 % / −30 %).
  - **Use RPLS (and floor area) to quantify social housing. Do not validate against BD TOPO dwelling counts.**

## 5. Recommended identification method

1. **Ownership (which parcels):**
   - Use the DGFiP PM 2025 file (already cached). Apply the SIREN-level rule of §3.2, computed per département before filtering to the commune, and keep the HLM and SEM classes separate.
   - A parcel is "social" when a social landlord is the taxable holder of at least one unit. Mark it as an **estate** when the landlord also holds the land, and as **mixed** otherwise.
2. **Dwellings and regime (how many, exempt or not, QPV):**
   - Use RPLS 2025 via the DiDo API (`DEPCOM=eq:` on the data codes; same 1 January situation as the PM file and the 2025 tax year).
   - Assign points with join C.
   - Exempt bracket: `ORIGINE`, plus `CONSTRUCT` / `LOCAT` / `PATRIMOINE`, plus **`DATCONV`** (financing-decision proxy), restricted to `CONV`=1 and not PLI. The duration rule comes from the rules agent.
   - QPV: from the ANCT 2024 polygons (identical to `PLG_QP24`).
3. **Shares rather than per-parcel counts:**
   - Compute the exempt share and the QPV share **per estate cluster**, weighted by `SURFHAB`, then apply them to the parcels' housing baseline. Cluster level absorbs the point-on-the-wrong-parcel noise.
   - TFPB on the social part ≈ baseline × (1 − exempt share − 0.30 × non-exempt QPV share), i.e. 0 for exempt dwellings and 70 % for QPV-abated ones.
   - On mixed parcels: social fraction = RPLS habitable area / (0.72 × BD TOPO gross residential), capped at 1.
4. **Landlord category for charts:**
   - Estates (and mixed parcels with a social fraction of 0.5 or more) form a "Bailleur social" category outside the household-income charts.
   - The remaining mixed parcels keep their household category with the social fraction removed.
5. **Disclosure:**
   - Publish commune-level figures only. Never publish anything by landlord, and that includes figures drawn from PM names.
   - Never publish an RPLS-derived figure below 11 dwellings below commune level.
   - Never redistribute RPLS rows or parcel-level flags.

**Expected accuracy:**
- Commune totals of social dwellings, QPV dwellings and bracketed-exempt dwellings: **exact up to the rule** (they come straight from RPLS).
- Which parcels are social: high. Ownership is legal fact in MAJIC, and 94–96 % of RPLS dwellings sit within 30 m of a PM-social parcel.
- How the social share splits across parcels within an estate: moderate. The floor-area check puts 40–47 % of the area within a 0.6–1.1 ratio.
- Exempt or QPV shares at estate level: good. Exemption is homogeneous by programme, and QPV contours are exact.

**Blockers and limits:**
- No parcel reference and no landlord in RPLS, so the join is spatial.
- RPLS excludes foyers and résidences sociales, which PM sees as social property but without dwelling attributes. Treat them by default as not exempt, or mark them explicitly as unknown.
- About 1 year of MAJIC lag for new builds: under the point-in-parcel join, 490 / 798 RPLS dwellings built since 2020 sit on parcels with no PM social right.
- SEM stock is only partly social.
- The diffusion rules in the dictionary are stricter than the "fr-lo" label suggests.
- The PM 2026 attachment naming breaks `_attachments` (§3).
- No open, authoritative SIREN list of HLM bodies was found on data.gouv, so the DGFiP groupe code plus legal form is the practical classifier.

## 6. Working files

The scripts, downloads and per-parcel working files behind this note were kept outside the repository and are not published.
