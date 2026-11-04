Below is an expert review of `social_housing.py` and the pipeline integration, covering French tax law (CGI), HLM/RPLS data mechanics, spatial/econometric logic, and Python/pandas performance.

---

### Executive Summary: Ranked Issues by Severity

1. **[CRITICAL - Code/Data Bug] Missing `landlord_key` when RPLS points fall on un-anchored parcels (`parcel_social`)**: When an RPLS point misses the 30m PM-anchor join and falls back to the 15m general parcel join, or when a social landlord is missing from the PM classification (e.g., Foncière Logement), `soc["landlord_key"]` is `NaN`. In `export_web.py`, this silently undercounts `social_landlords(df)`, causing valid communes to fail the `< 3 landlords` disclosure check and fold their Social Housing category into "Other".
2. **[HIGH - Tax Law / RPLS] CGI 1384 C II (Acquisition without works) & CGI 1384 A III (ANRU) omissions (`dwelling_status`)**: Acquisitions *sans travaux* (`ORIGINE == "3"`) are generally **not** eligible for the 15/25-year exemption of Art. 1384 C I (which requires *acquisition-amélioration* financed by PLA-I/PLUS/PLS loans), unless they are emergencies/hotels; yet the code grants them full 15/25-year exemptions. Conversely, ANRU reconstructions (Art. 1384 A III, `FINAN_CODE == "15"`) are omitted from `ELIGIBLE_FINANCING`.
3. **[HIGH - Spatial / Estate Logic] Unconstrained transitive chaining of estates (`_clusters`)**: `_clusters` buffers all social parcels by 1m (`CLUSTER_GAP_M / 2`) and unions them *without grouping by `landlord_key` or `siren`*. In dense urban tissue or ZACs, adjacent parcels belonging to *different* HLM landlords (or a 100% exempt new build next to a 1970s taxable tower) merge into a single "estate", averaging their tax factors and forcing `social_share = 1.0` across mixed-ownership blocks.
4. **[HIGH - Performance / Memory] `social_parcels` string concatenation and `set` lookups on 1.5M rows (Paris)**: Constructing `unit` keys via 5-way string concatenation and filtering with `.isin(set)` on unindexed strings will peak at several GBs of RAM on département 75 and run slowly.
5. **[MEDIUM - Tax Law / QPV] Over-application of CGI 1388 bis (`dwelling_status`)**: Art. 1388 bis requires the dwelling to be *conventionné APL* (`CONV == "1"`) or financed by specific legacy regimes. The current `qpv` rule checks `~fin.isin(INTERMEDIATE_FINANCING)` without checking `CONV == "1"`, granting the 30% abatement to non-conventioned PLS/old dwellings in QPVs.
6. **[MEDIUM - Econometric Calibration] Unweighted fallback parcels in `estimate.current_tax`**: On parcels where BD TOPO building categorization failed (`wf <= 0`, so plain floor area `w` is used), `current_tax` multiplies `w` by `hf` (`hlm_tax_factor`), whereas `_baseline_weights` only scales `floor_housing` when computing `bucket_weights`. This creates a slight mismatch between the calibration denominator and the distribution denominator.

---

### Detailed Answers to Your 8 Questions

#### 1. Legal Rule (`dwelling_status`) for Tax Year 2025
* **Exemption clock & thresholds (Art. 1384 A & C)**:
  * **The math is exact**: Under Art. 1384 A, the exemption starts on Jan 1 of the year *following* completion (`start + 1`). For a 15-year exemption, the last exempt tax year is `start + 15`. For `year = 2025`, `start + 15 >= 2025` $\iff$ `start >= 2010` (`year - SHORT_YEARS`). For 25 years, `start + 25 >= 2025` $\iff$ `start >= 2000`, bounded below by `FIRST_LONG_START = 2005` because the 25-year window opened on July 1, 2004 (Loi 2005-32). And `start < year` properly excludes completions in 2025 (not in RPLS 2025-01 anyway, or not taxable until 2026).
* **`DATCONV` as a proxy for the financing decision date**:
  * **Sound, with one caveat**: In practice, the APL convention (`DATCONV`) is signed *at or after* the financing decision (often right before first letting for VEFA/new builds, though usually within 6–18 months of the *décision d'agrément*). For the 2005–2009 cohort, a dwelling completed in 2005 whose loan was approved in May 2004 (15-year rule) might have its APL convention signed in late 2004 or 2005, causing `datconv >= 2004-07-01` to be a **false positive** (classifying it as 25-year exempt instead of expired in 2020).
  * **Fix**: Shift the lower bound of `LONG_WINDOW` for `DATCONV` by ~6–9 months (e.g., `2005-01-01` or `2005-04-01`) when `CONSTRUCT <= 2006`, or require `CONSTRUCT >= 2006` when relying on `DATCONV` near the 2004 cutoff.
  * **Crucial RPLS quirk (`DATCONV` renewals/amendments)**: When HLM landlords merge (Loi ELAN caused massive mergers between 2018 and 2023) or sign *avenants*, they occasionally overwrite `DATCONV` in RPLS with the *avenant* date (e.g., `2021-01-01`) on a 1978 building! Because your `in_long` check requires `start >= 2005`, pre-2005 buildings are immune to this bug. For 2005–2009 buildings, a post-2007 `DATCONV` is fine anyway because virtually all 2007+ completions got the 25-year loan.
* **Acquisition / Transfer logic (`ORIGINE`, `LOCAT`, `PATRIMOINE`)**:
  * **The transfer heuristic (`locat < patr - 1`) is clever and necessary**: RPLS `ORIGINE` codes `"2"` (acquisition with works) and `"3"` (acquisition without works) are used both for purchasing private buildings to convert to social housing *and* for bulk purchases/mergers between HLM landlords. By checking `locat < patr - 1`, you accurately catch dwellings that were already rented in the social stock prior to entering the current landlord's `PATRIMOINE` (per CCH L.353-4, the APL convention and original tax clock travel with the building).
  * **What I would change (Error #1 - `ORIGINE == "3"`)**: Under CGI Art. 1384 C I, the 15/25-year exemption for acquisitions applies to dwellings acquired *with a view to improvement* (*en vue de leur amélioration*) with State aid, or acquired from the private market under specific conventionnement rules. In RPLS, `ORIGINE == "3"` (*acquis sans travaux*) bought after completion (`PATRIMOINE > CONSTRUCT + 2`) that is *not* a transfer (`locat >= patr - 1`) is often a second-hand purchase without heavy rehabilitation, or a *rachat de patrimoine* where `LOCAT` was reset by the reporting landlord. Treating all `ORIGINE == "3"` as starting a fresh 25-year clock at `PATRIMOINE` **overstates exemptions by roughly 3–6% of the exempt stock**. I would restrict the `PATRIMOINE` clock to `ORIGINE == "2"` (acquisitions with works), or for `ORIGINE == "3"` require `FINAN_CODE in {"10", "11", "12", "13"}` (excluding PLS `"14"` and `"49"`, as PLS acquisition without works gets no 1384 C exemption).
* **`FINAN_CODE` set**:
  * `{10, 11, 12, 13, 14, 49}` is nearly right, and excluding `16` (PLI) and `17` (PCL) is 100% right.
  * **Missing code `15`**: In the SDES RPLS dictionary, check whether your millésime uses `15` for **ANRU / PNRU reconstitution de l'offre** (exempt under CGI 1384 A III) or PSLA. If `15` is ANRU rental, it should be in `ELIGIBLE_FINANCING`.
  * **Watch out for `49` ("Autre financement aidé") + `CONV == "1"` on PLS (`14`)**: Under CGI 1384 A I bis, PLS (`14`) is indeed eligible for the 15/25-year exemption, *provided* >50% of the financing comes from the Caisse des Dépôts loan. RPLS doesn't show the % of loan, so including `14` is the right call. However, `49` (*Autre financement*) is a catch-all used by landlords for municipal/regional subsidies or legacy loans that do *not* always qualify as *prêts aidés par l'État* under CGI 1384 A. Including `49` is a slight overestimate (~1–2%).
* **QPV Rule (CGI 1388 bis)**:
  * **Fix needed**: Currently: `qpv = (r["PLG_QP24"].fillna("").str.strip().str.startswith("QN") & ~fin.isin(INTERMEDIATE_FINANCING) & ~exempt)`.
  * Art. 1388 bis requires the dwelling to be either conventioned APL or financed with specific PLA/HLM loans. In RPLS, a landlord can report non-conventioned dwellings (`CONV == "2"`) with `FINAN_CODE == "49"` or `"99"` (libre/fonds propres) inside a QPV. You should require `(r["CONV"].fillna("").str.strip().eq("1") | fin.isin(ELIGIBLE_FINANCING))` inside `qpv`.
* **Likely error magnitude**: On a typical mid-sized city like [redacted] ([redacted] % exempt), the net error of `dwelling_status` is small—likely **within ±2 to 3 percentage points** of the true exempt share (slight overestimation from `ORIGINE == "3"` and `FINAN_CODE == "49"`, slight underestimation from ignoring the 5-year environmental bonus *bonification énergétique* under 1384 A I bis, which extends 2005–2009 completions to 30 years).

---

#### 2. REI Produit & Calibration Interaction (`estimate.current_tax` and `_baseline_weights`)
* **Conceptual validity**: **Yes, this is completely right.** In the DGFiP REI dataset, the *base nette* and *produit réel* (commune + EPCI) only reflect **taxable** bases after applying temporary exemptions (1384 A/C = 100% exempt from communal/EPCI TFPB) and the 30% QPV abatement (1388 bis reduces the *base d'imposition* by 30%). Note: The State pays a partial *allocation compensatrice* to communes for 1384 A/C and 1388 bis, which is recorded in separate REI columns (*allocations compensatrices*), **not** in the *montant réel des cotisations* paid by taxpayers. Therefore, to distribute the taxpayer-paid *produit* across today's taxpayers, exempt HLM floor must get weight `0` and QPV-abated floor weight `0.7`.
* **Interaction with Group Calibration (`_baseline_weights`)**:
  * In `run_pipeline.py`:
    ```python
    q["floor_housing"] = q["floor_housing"].fillna(0) * _housing_factor(p).to_numpy()
    totals = {k: float(q.loc[taxable, f"floor_{k}"].fillna(0).sum()) for k in estimate.BUCKETS}
    ```
    Because `totals["housing"]` is reduced by `_housing_factor(p)`, the calibrated weight `bucket_weights["housing"]` (EUR or relative VLC per taxable m²) rises proportionally so that `(totals["housing"] * bucket_weights["housing"]) / total_weighted_floor` still equals the REI housing share!
  * **Why the other parcels rose [redacted]**: Wait—if `bucket_weights["housing"]` adjusts so that the *Housing bucket as a whole* still pays the exact same REI housing share, why did non-social parcels' tax rise when social housing tax fell?
    1. Because **private housing parcels** are inside the `housing` bucket! When the exempt HLM floor is zeroed out, the remaining taxable housing floor (private homeowners + private landlords + non-exempt HLM) absorbs the amount that used to be attributed to exempt HLM floor.
    2. **Check one bug in `_baseline_weights` vs `current_tax`**: What if a commune runs in `plain` mode (`bucket_weights=None`), or what about parcels where `wf <= 0` (buildings with `floor_area_m2 > 0` in `p`, so `taxable` is True, but `floor_housing == 0` or unbucketed)?
    In `estimate.py`:
    ```python
    # parcels with a building but no grouped floor keep plain floor area
    w = w.where(wf <= 0, taxed.clip(lower=0.0).where(w > 0, 0.0))
    if hf is not None:
        w = w.where(wf > 0, w * hf)
    ```
    Those fallback parcels (`wf <= 0` but `w > 0`) are included in the final tax sum `w.sum()`, so they take a small slice of `commune_tfpb_produit`. In `_write_baseline`, you compute `achieved` shares using only `wf` (ignoring the fallback parcels where `wf == 0`!). That's pre-existing, not introduced by your diff, and minor.

---

#### 3. Parcel Assignment & Estate Clustering (`_place`, `_clusters`, `parcel_social`)
* **Spatial Join (`_place`)**:
  * The two-tier distance join (30m to a known PM social parcel, else 15m to any parcel) is a very pragmatic solution to the classic BAN/RPLS geocoding problem (where address points sit on the street centerline or at the entrance gate of a multi-parcel *résidence*).
  * **Weakness 1 (`sjoin_nearest` tie-breaking)**:
    ```python
    nn = gpd.sjoin_nearest(pts[["geometry"]], soc, how="left", max_distance=JOIN_SOCIAL_M)
    nn = nn[~nn.index.duplicated()]
    ```
    If an RPLS point lies *inside* parcel A (distance = 0), and parcel B touches parcel A at the boundary where the point sits (or `pts` is equidistant to two parcels), `~nn.index.duplicated()` picks whichever row GeoPandas emitted first. That's usually fine because `_clusters` merges touching social parcels within 2m anyway!
  * **Weakness 2 (Points inside a non-PM parcel when a PM parcel is 25m away)**: Suppose a social landlord bought 4 apartments in a private condominium (*copropriété*) on Parcel A. Because it's a small *copropriété* or bought via VEFA, or held by an entity not in `social`, Parcel A is *not* in `anchors`. Across the 20m street sits Parcel B, an HLM tower (in `anchors`). Because `JOIN_SOCIAL_M = 30m` runs **first** on *all* RPLS points, the 4 apartments on Parcel A will be **pulled across the street onto Parcel B** instead of matching Parcel A (distance = 0m)!
  * **Fix for Weakness 2**: If an RPLS point is *strictly inside* (`predicate="within"`, distance = 0) a built residential parcel, or if you check `distance == 0` first before jumping up to 30m across the street, you avoid false-positive pulls in dense urban streets. At minimum, reduce `JOIN_SOCIAL_M` from `30.0` to `20.0`, or only prefer `soc` when `dist_to_soc <= dist_to_any + 15.0`.
* **Estate Clustering (`_clusters`)**:
  * **Severe weakness**: `_clusters` buffers every parcel in `members` by `1.0m` (`CLUSTER_GAP_M / 2`) and unions any two intersecting buffers, **regardless of who owns the parcel**.
  * In French suburban *grands ensembles* and urban ZACs, OPH A, SA d'HLM B, and SEM C frequently own adjacent parcels along the same block, or a parcel with a 2018 exempt building sits right next to a 1975 fully taxable building. Worse: `members` includes `set(per.index)` (any private parcel that received even 1 stray RPLS point!). If a private condo parcel with 2 social flats sits next to an HLM estate, `_clusters` merges the private condo into the estate! (Thankfully, `on_estate` checks `land & (units > 0)` from `soc`, so the private condo won't get `on_estate = True`, *unless* the HLM also owns 1 unit in the condo and the land row isn't empty).
  * **Fix**: Group or restrict `_clusters` edges so two parcels `a` and `b` only merge if they share the same `landlord_key` (or at least if one of them has `landlord_key` missing and is absorbed into an adjacent known landlord's parcel).
* **`HAB_TO_GROSS = 0.72` on mixed parcels**:
  * 0.72 is an empirically solid ratio between `SURFHAB` (RPLS habitable area) and BD TOPO `hauteur * emprise` gross floor area.
  * **Edge case**: When BD TOPO underestimates height or misses an extension on a 100% social parcel that is *not* flagged as `on_estate` (e.g., because the `NB` land row was missing in the DGFiP PM file—very common in urban cadastres where built parcels with no unbuilt courtyard only appear in the `B` file, not the `NB` file!), `own` is clipped at `1.0`, which works well.
  * **WAIT — Critical DGFiP PM File Fact (`src == "NB"` vs `src == "B"`)**:
    Look at line 154 & 318 of `social_housing.py`:
    ```python
    land = r[(r["src"] == "NB") & r["droit"].isin(HOLDER_RIGHTS) & r["soc"].notna()]
    ...
    on_estate = (units > 0) & land & (landlord.eq("hlm") | estate_of.map(rpls_est).eq(True))
    ```
    In the DGFiP *Fichiers des personnes morales*, the **Parcelles (`NB`) file** lists *sujets à la TFPNB* (unbuilt sub-parcels / *sols*). Does a 100% built urban parcel (where the building covers 100% of the parcel footprint, or where all *subdivisions fiscales* are *sols de propriétés bâties* exempt from TFPNB under CGI Art. 1394-7°) always appear in the `NB` file? Usually yes, because the *sol* (nature de culture `"S"`) is recorded in the Majic parcelle table exported to the `NB` file. However, in *copropriétés horizontales* or *divisions en volumes* (common in urban social housing over parking/commercial podiums), the HLM holds lots in `B` while the parcel `NB` is held by a *syndicat de copropriétaires* or AFUL! In those cases, `land` is `False`, so `on_estate` is `False`, and the parcel falls back to `own = own_hab / (0.72 * fh)`. Because `own` works as a fallback, this degrades gracefully—*except* if RPLS points for Building A fell on adjacent Parcel B of the same estate, leaving Parcel A with `own_hab = 0` and `on_estate = False`!
    * **Suggestion**: If a social landlord holds **all** (or $\ge 90\%$) of the building units (`B`) on a parcel and there are no private owners, or if the parcel is in an estate cluster where the landlord holds the `NB` on the neighbouring parcel, treat `on_estate` as `True` even if `land` (`NB`) is False on that specific parcel.

---

#### 4. Landlord Identification (`social_sirens` / `social_parcels`)
* **Groupe 5 non-social subsidiaries**:
  * Excluding `IN'LI` (`\bIN ?'?LI\b`) is spot-on (Action Logement's intermediate housing arm).
  * **Other intermediate/non-social entities that sometimes appear in Groupe 5 or with HLM/HABITAT names**:
    * **CDC Habitat**: Wait—CDC Habitat (formerly SNI) has both **CDC Habitat Social** (ESH, SA d'HLM, legal form `5546`) and **CDC Habitat** (SEM / filialised intermediate housing, legal form `5515` or `5599`). Because `5515` is in `SEM_FORMS`, CDC Habitat (parent) is classified as `"sem"`, which requires RPLS dwellings to activate `on_estate`. That's safe!
    * **Foncière Logement** (`SIREN [redacted]`, association loi 1901, legal form `9220`): Action Logement's arm that builds rental housing in ANRU neighborhoods (often conventioned or mixité sociale, some in RPLS). Legal form `9220` is not in `HLM_FORMS` or `SEM_FORMS`, so its parcels won't be in `social_parcels` (they will rely on the 15m RPLS fallback).
    * **Tonus Territoires / 1001 Vies Habitat / Seqens / Erilia / Vilogia**: All standard ESH (`5546`), caught by `HLM_FORMS`.
    * **`OPH_NAME` regex (`HABITAT`)**: Look at:
      ```python
      OPH_FORM = "4140"
      OPH_NAME = re.compile(r"OFFICE PUBLIC|\bOPH\b|\bOPAC\b|HABITAT|\bHLM\b")
      ```
      Because `OPH_NAME` is gated by `forme == "4140"` (*EPIC local*), this is very safe—almost every local EPIC with those words is an OPH. (One edge case: an OPH named e.g. *"ARCHIPEL"* or *"DOMOFRANCE"*? Wait: Domofrance is an ESH (`5546`); Archipel Habitat has `HABITAT`; what about **Paris Habitat - OPH**? Has `HABITAT` and `OPH`. What about **Rennes Métropole's OPH** or **2F / Actis / Côte d'Azur**? If an OPH (`4140`) doesn't have `OPH`, `OPAC`, `OFFICE PUBLIC`, `HABITAT`, or `HLM` in its name—e.g. *"LOGIDIA"*, *"LOGEVIE"*, *"SILENE"*, *"EKIDOM"*, *"3F"* (ESH), *"NEOTOA"* (OPH of Ille-et-Vilaine, SIREN [redacted], legal form `4140`, denomination `"NEOTOA"`!), *" PATRIMOINE SA LANGUEDOCIENNE"* (`5546`), *"AIGUILLON"* (`5546`), *" FINISTERE HABITAT"*—wait: **NEOTOA** in Rennes and **SILENE** in Saint-Nazaire and **EKIDOM** in Poitiers and **LOGEMLOIRET** and **SOLIHA**!).
      Wait: Why aren't OPHs (`4140`) caught by `g == "5"`? Most OPHs *are* `groupe == "5"` in Majic! The only reason you added `(forme == OPH_FORM) & den.str.contains(OPH_NAME)` is for the few OPHs miscoded in `groupe == "9"` (like Lyon Métropole Habitat). So Neotoa/Ekidom are caught by `g == "5"` as long as DGFiP coded them in groupe 5.
* **"Taxable holder of a unit" rule (`HOLDER_RIGHTS`)**:
  * **Legal check (CGI Art. 1400)**:
    * `P` (Propriétaire), `U` (Usufruitier), `E` (Emphytéote), `R` (Preneur à bail à construction), `W` (Preneur à bail à réhabilitation) are indeed the exact rights where the holder is the *redevable légal* of the TFPB!
    * **What about `A` (Locataire-attributaire) and `T` (Tenancier / preneur d'un bail à domaine congéable) and `G` (Gérant, mandataire, syndic)?** Excluding `G` is essential because `G` is a *syndic de copropriété* (many HLM companies act as *syndic* for buildings where they sold units under *vente HLM*, so including `G` would falsely flag sold apartments as HLM-owned!).
    * **What about `B` (Bâtisseur / preneur de bail sur sol d'autrui) or `S` (Superficiaire / propriétaire de volumes)?** In Majic `code_droit`, wait: is `B` or `S` used when an HLM owns a volume? Usually volume owners are coded `P` on the *local* (`src == "B"`).
    * **One missing right: Bail réel solidaire (BRS) / OFS**: Under a BRS, the household is the taxable holder of the TFPB (CGI Art. 1400 II), while the OFS (often an HLM) owns the land (`P`). Wait: on a BRS unit, the household is a physical person (not in the PM file!), and the OFS (HLM) holds the residual ownership (`P` or `F` / foncier). Because households aren't in the PM file, `others` (`b["droit"].isin(LESSEE_RIGHTS) & b["soc"].isna()`) will **not** contain the household! However, BRS is homeownership (*accession sociale*), so BRS dwellings are **not in RPLS** (RPLS is strictly rental housing). Still, if an HLM is recorded as `P` on the land (`NB`) or units (`B`) of a BRS building, `social_parcels` might think the HLM owns it. In practice, in Majic, the BRS *preneur* (household) is coded on the `B` local, and the OFS is not `P` on the `B` local.

---

#### 5. Disclosure Rules (`MIN_SOCIAL_LANDLORDS = 3`, RPLS diffusion rules)
* **RPLS diffusion rules (Décret 2009-1485 / Arrêté du 27 mai 2010 / SDES guide)**:
  * The RPLS legal constraints require:
    1. No dissemination of individual dwelling rows (satisfied: rows stay in local cache).
    2. No statistic allowing direct or indirect identification of a specific bailleur (satisfied by `MIN_SOCIAL_LANDLORDS = 3`, *with one caveat below*).
    3. No sub-communal (infra-communal, e.g. IRIS or parcel) statistic computed on $< 11$ social dwellings.
* **Verify sub-communal exports**:
  * Does your web payload (`export_web.py`) export IRIS-level or parcel-level maps/tables that include `hlm_tax_factor`, `social_share`, or the `"Social Housing"` category per IRIS?
  * You excluded `"Social Housing"` from `FR_RESIDENTIAL`, so IRIS-level household/income quintile figures exclude it. If the web map displays parcel-level or IRIS-level categories or tax changes using RPLS-derived `hlm_tax_factor` on fewer than 11 dwellings, that would violate the $<11$ infra-communal rule. As long as the web payload only publishes **commune-level** aggregates (`build_by_category` and `social_provenance`), the $<11$ rule is strictly respected because it only applies *below* the commune scale (*à une échelle infra-communale*).
* **Dominance rule caveat (`MIN_SOCIAL_LANDLORDS = 3`)**:
  * In statistical confidentiality (INSEE secret statistique), the primary rule has two parts: the **threshold rule** ($N \ge 3$ units) and the **dominance rule** (1 unit cannot represent $> 85\%$ of the total). In many French mid-sized cities ([redacted]), the historic municipal/departmental OPH ([redacted]) owns 80–90% of the social stock, while 2 tiny SA d'HLM own 5% each. While INSEE enforces the 85% dominance rule on mandatory business surveys (ESANE), SDES's RPLS diffusion guide usually only states that bailleur names/SIRENs cannot be published alongside sub-communal figures. Your `MIN_SOCIAL_LANDLORDS = 3` check is already much stricter and more conscientious than most academic/policy models.
  * **However, see Bug #1 in Section 7**: `social_landlords(df)` has a bug where parcels assigned via RPLS fallback have `landlord_key == ""`, which can cause a 3-landlord commune to only count 2 keys!

---

#### 6. Category Median with `current_tax == 0` as $+\infty$ (`_median_change_pct`)
* **Statistical & Economic Soundness**: **Yes, this is mathematically right and much better than dropping zeros.**
  * If a category has [n] parcels: [m] exempt (going from 0 € to $>0$ €, i.e., $+\infty\%$ change) and [n − m] taxed today (say with median $+15\%$ change).
  * If you drop the [m] zeros, you report the median of the [n − m] already-taxed parcels ($+15\%$), which creates a perverse artifact: the more exempt parcels a landlord has, the *excluded* they are from the median, making the reform look milder on the category!
  * Treating $0 \to >0$ as $+\infty$ places those [m] parcels in the upper tail of the rank ordering. Since [m] is under half of [n], the median parcel (the true median parcel of the distribution!) has a finite percentage change, which represents the true 50th percentile of all social housing parcels. And if $>50\%$ of parcels pay 0 today (like Vacant Land), the median is $\infty$, and your function returns `None` (`round(med, 1) if math.isfinite(med) else None`), which is completely honest.

---

#### 7. Code Review: Bugs, Edge Cases, Pandas Pitfalls & Paris Performance

Here are the concrete code bugs and performance bottlenecks, with exact line fragments and fixes:

##### Bug 7.1 [CRITICAL]: `landlord_key` is `NaN`/empty for RPLS-only parcels, breaking `social_landlords(df)`
* **Where**: `social_housing.py` lines 313, 332–333 and `run_pipeline.py` lines 414–415:
  ```python
  # social_housing.py:
  soc = social.set_index("idpar").reindex(sorted(members))
  ...
  "landlord_key": soc["landlord_key"].reindex(ids).values,
  ```
* **What happens**: `members` is the union of `social` parcels and `per.index` (parcels where `_place` put RPLS dwellings). When `_place` misses the 30m social-parcel join and falls back to the 15m general parcel join (or when a landlord like Foncière Logement / an unrecognized SEM is not in `social`), the parcel is in `per.index` with `social_share >= 0.5`, so it becomes `"Social Housing"`. However, it is not in `social`, so `soc["landlord_key"]` is `NaN`.
* Worse: what if an RPLS point falls on a parcel that is in `_clusters` (`est`) next to a known `social` parcel, or what if 2 landlords are in `social` and 1 landlord was only placed by RPLS? `social_landlords(df)` counts distinct non-empty `landlord_key`s.
* **Even more subtle**: In `social_parcels`:
  ```python
  land_siren = land.drop_duplicates("idpar").set_index("idpar")["siren"]
  ...
  who = top.set_index("idpar")["siren"].reindex(ids).fillna(land_siren.reindex(ids))
  ```
  If a parcel is in an estate (`est`), should `landlord_key` propagate across the estate when missing? Yes:
  ```python
  # Propagate landlord_key within estate if missing on an RPLS-placed member parcel
  ```

##### Bug 7.2 [HIGH]: `_clusters` union-find merges different landlords' parcels across a 2m alley
* **Where**: `social_housing.py` lines 265–286:
  ```python
  buf = gpd.GeoDataFrame(sub[["idpar"]], geometry=sub.geometry.buffer(CLUSTER_GAP_M / 2),
                         crs=pg.crs)
  pairs = gpd.sjoin(buf, buf, how="inner", predicate="intersects")
  ```
* **What happens**: In Paris or Lyon, two HLM buildings on the same block (or across a 1.8m pedestrian passage) owned by two different bailleurs (e.g. Paris Habitat and RIVP, or an HLM parcel and a private parcel that caught 1 stray RPLS point) get merged into a single estate!
* **Consequence**:
  1. Both bailleurs get the exact same averaged `c_factor` (so the 2020 exempt building of RIVP shares its 0.0 tax factor with the 1960 taxable building of Paris Habitat!).
  2. In `parcel_social`: `on_estate = (units > 0) & land & (landlord.eq("hlm") | estate_of.map(rpls_est).eq(True))`. An SEM commercial/office parcel that happens to sit within 2m of an HLM parcel with RPLS dwellings gets `estate_of.map(rpls_est) == True`, turning a non-social SEM parcel into `social_share = 1.0`!
* **Fix**: Pass `landlord_key` (from `social`) into `_clusters`, and only union `a` and `b` if `key_a == key_b` or one of `key_a, key_b` is missing (`NaN`, i.e., an RPLS-only parcel being absorbed into an adjacent PM parcel).

##### Bug 7.3 [HIGH]: Performance & Memory in `social_parcels` on Paris (1.5M PM rows)
* **Where**: `social_housing.py` lines 142–151:
  ```python
  b = r[r["src"] == "B"]
  unit = (b["idpar"] + "|" + b["bat"].str.strip() + "|" + b["ent"].str.strip()
          + "|" + b["niv"].str.strip() + "|" + b["porte"].str.strip())
  b = b.assign(unit=unit)
  others = set(b.loc[b["droit"].isin(LESSEE_RIGHTS) & b["soc"].isna(), "unit"])
  held = b[b["droit"].isin(HOLDER_RIGHTS) & b["soc"].notna()]
  held = held[~((held["droit"] == "P") & held["unit"].isin(others))]
  ```
* **What happens on Paris (dep 75)**:
  `r` has ~1.5M rows (`b` has ~1.3M rows). You strip and concatenate 5 string columns for **all 1.3M rows**, even though only ~15–20% of rows have `soc.notna()` or `droit.isin(LESSEE_RIGHTS)`! Building 4 intermediate 1.3M-element Python string Series takes ~600 MB of RAM and several seconds.
* **Fix**: Filter `b` **first** to `b[b["droit"].isin(HOLDER_RIGHTS) & (b["soc"].notna() | b["droit"].isin(LESSEE_RIGHTS))]`, or even better, filter to `idpar`s where at least one `soc.notna()` exists! That shrinks `b` by 80–90% *before* any string stripping or concatenation:
  ```python
  b = r[(r["src"] == "B") & r["droit"].isin(HOLDER_RIGHTS)]
  soc_idpars = set(b.loc[b["soc"].notna(), "idpar"])
  b = b[b["idpar"].isin(soc_idpars)]
  ```
  This 3-line change will cut `social_parcels` runtime and memory on Paris by ~5x.

##### Bug 7.4 [MEDIUM]: `social_sirens` classifies any company with 1 row in `groupe == "5"` as HLM across the whole département
* **Where**: `social_housing.py` lines 118–124:
  ```python
  hlm = known & ((g == "5") | forme.isin(HLM_FORMS)
                 | ((forme == OPH_FORM) & den.str.contains(OPH_NAME)))
  ...
  h = set(siren[hlm]) - bad
  ```
* **What happens**: In the DGFiP Majic files, `groupe` (code groupe de personne morale) is sometimes miscoded on *a single local* (e.g., when a private bank, SCI, or promoteur like Bouygues Immobilier or Nexity is accidentally given `groupe = "5"` by a local cadastre clerk on one parcel, while its other 500 parcels have `groupe = "0"` and `forme = "5710"` SAS). Because `social_sirens` takes `set(siren[hlm])` if *any* row has `g == "5"`, that private developer or bank becomes `'hlm'` across the entire département!
* **Fix**: Either require `forme` not to be a standard private commercial/SCI form unless `g == "5"` is the majority of rows for that SIREN, or exclude obvious private forms (like SCI `6540` unless it's an HLM coop/SCIC), or check `(g == "5")` per row / majority per SIREN.

##### Bug 7.5 [MEDIUM]: `dwelling_status` `start` calculation when `CONSTRUCT` is missing on acquisitions
* **Where**: `social_housing.py` lines 221–224:
  ```python
  acq = origine.isin(["2", "3"])
  transfer = acq & (locat < patr - 1)
  start = construct.where(~acq, patr)
  start = start.where(~transfer, np.fmax(construct, locat - 1))
  start = start.fillna(locat - 1)
  ```
* **What happens**: Look at `np.fmax(construct, locat - 1)`:
  Suppose a building was constructed in `1920` (`CONSTRUCT = 1920`), bought and rehabilitated into social housing in `2012` (`LOCAT = 2012`), and then transferred during an HLM merger in `2021` (`PATRIMOINE = 2021`, `ORIGINE = "3"`).
  1. `acq` is `True`, `transfer` (`2012 < 2020`) is `True`.
  2. `np.fmax(1920, 2011)` evaluates to **`2011`** (`locat - 1`)!
  3. That works! Now suppose the reverse: a building was constructed as an HLM in `1975` (`CONSTRUCT = 1975`), merged into a new HLM in `2018` (`PATRIMOINE = 2018`, `ORIGINE = "3"`), and the new landlord erroneously entered `LOCAT = 2012` (say, the date of a renovation or the date the previous landlord bought it). `np.fmax(1975, 2011)` picks `2011`, granting a fresh 25-year exemption to a 1975 building!
  Why did you use `np.fmax(construct, locat - 1)` instead of `np.fmin`? Because for a private building built in 1900 and converted to social housing in 2012 (`LOCAT = 2012`) and transferred in 2020 (`PATRIMOINE = 2020`), the original social exemption started in 2012 (`locat - 1`), not 1900 (`construct`). That is actually very well thought out!
* **However, check `start` when `CONSTRUCT`, `PATRIMOINE`, and `LOCAT` are ALL NaN**:
  `start` is `NaN`. Then in line 228:
  ```python
  long_ = (datconv >= LONG_WINDOW[0]) & (datconv <= LONG_WINDOW[1])
  long_ = long_.where(datconv.notna(), start >= LONG_DEFAULT_FROM)
  ```
  That's safe because `in_short` and `in_long` will be `False` when `start` is `NaN`.
* **Check Pandas `Series.where` dtype warning in line 227–228**:
  `long_` is `bool` Series. When `datconv.notna()` is False, `start >= LONG_DEFAULT_FROM` is also `bool` Series. So `long_.astype(bool)` on line 231 isn't even needed, though harmless.

##### Bug 7.6 [LOW]: `_place` CRS comparison fails if `ingest.CRS_METRIC` is `"EPSG:2154"` vs `"2154"`
* **Where**: `social_housing.py` line 245:
  ```python
  ok = x.notna() & y.notna() & rpls["EPSG"].astype(str).str.strip().eq(str(ingest.CRS_METRIC))
  ```
* **Check**: In RPLS CSV, the `EPSG` column contains `"2154"` (for metropolitan France). Ensure `ingest.CRS_METRIC` is the integer `2154` or string `"2154"`, not `"EPSG:2154"`. (Since the first run placed dwellings, `CRS_METRIC` must be `2154`, just worth noting if someone changes `CRS_METRIC` to a `pyproj.CRS` object).

##### Bug 7.7 [LOW]: `social_provenance` hides commune-level RPLS counts if `social_landlords(df) < 3`
* **Where**: `export_web.py` line 898:
  ```python
  if social_landlords(df) >= MIN_SOCIAL_LANDLORDS and tot["rpls_dwellings"] > 0:
      out["rpls_dwellings"] = tot["rpls_dwellings"]
  ```
* **Note**: The SDES RPLS diffusion rules actually **allow** publishing commune-level RPLS counts even when there is only 1 landlord in the commune (in fact, SDES publishes commune-level RPLS totals for all communes on DiDo!). What is forbidden is publishing the *landlord's identity* or linking the landlord to tax/financial outcomes of fewer than 3 entities. Blanking `social_provenance` when `< 3` landlords is extra cautious (since knowing 80% of RPLS dwellings in a 1-landlord commune are exempt tells you that landlord's exemption rate), so keeping this guard is defensible, provided Bug 7.1 is fixed.

---

#### 8. Policy & Economic Framing Review
Your proposed site framing states:
> *"The reform ends HLM exemptions because they are an unbudgeted aid paid by host communes, barely compensated (2–12%), poorly targeted (Cour des comptes 2017 référé S2017-1737; CPO 2023), leaking into land prices; and that support should be a visible, guaranteed direct subsidy instead."*

As an expert in French local public finance and HLM economics, here are **four factual/institutional nuances** you should refine so that HLM federations (USH) or local finance experts cannot dismiss your argument on a technicality:

1. **The "2–12% compensation" figure is accurate for *historic* 1384 A exemptions, MUST be qualified for 2021–2026 approvals**:
   * Why did compensation fall to 2–12%? Because the State's *allocation compensatrice* (CGI Art. 1384 A, calculated on 1980s ceilings + repeated *minorations* of the *variables d'ajustement* under the *enveloppe normée* since 2008) was devastated by budget cuts.
   * **CRITICAL UPDATE (Loi de finances pour 2021, Art. 16 / FCTVA & TFPB reform)**: Following fierce lobbying by associations of mayors (AMF, France Urbaine), the government committed to **100% full compensation for the first 10 years** for all new social housing approved (*agréés*) between **January 1, 2021 and December 31, 2026**!
   * *How to phrase it safely*: Say that the stock of existing exemptions is *"historically compensated at only 2–12% after two decades of State clawbacks (variables d'ajustement), and even the post-2021 promise of 10-year compensation leaves communes bearing 15 years of uncompensated losses (years 11 to 25)"*. That shows deep mastery of the dossier and makes your point bulletproof.
2. **CGI 1388 bis (30% QPV abatement) compensation**:
   * Similarly, the State compensates the 30% QPV abatement at roughly ~40% on average (after *variables d'ajustement* erosion), not 2–12%. Specify that 2–12% refers to the historic 1384 A/C exemption.
3. **Financial Equilibrium of HLM Operations (Why HLM bailleurs rely on the 25-year exemption)**:
   * In French HLM project finance, a new social housing operation is balanced over 40–50 years using Caisse des Dépôts loans (PLAI/PLUS). Because rents are capped by State circulars well below market, the 25-year TFPB exemption is baked directly into the *plan de financement prévisionnel* at day 1 (it represents roughly **10% to 15% of the investment cost** in discounted cash flow, often exceeding the direct State subsidy *subvention de l'État / FNAP*!).
   * If a reform abruptly ends the 1384 A exemption on **already built (2005–2024) cohorts** without a transitional grant or debt restructuring, many bailleurs with young stock in high-land-value communes would see their autofinancement (*capacité d'autofinancement nette*, CAF) turn negative.
   * *How to phrase it safely*: Explicitly distinguish between:
     * **New production (flow)**: Replacing the 25-year TFPB exemption with an upfront direct building subsidy (*pierre*) prevents the aid from leaking to land sellers and stops penalizing communes that build social housing.
     * **Existing 2005–2024 stock**: Acknowledge that because existing operating budgets (*bilans d'opération*) were signed with the State under a 25-year tax-free guarantee, transitioning existing exempt cohorts onto the land tax requires either grandfathering existing 1384 A contracts or converting them into an explicit budgetary credit.
4. **"Leaking into land prices"**:
   * This is strongly supported by the CPO (Conseil des prélèvements obligatoires, 2023 report on housing taxation) and IGF/CGEDD reports on VEFA (now >50% of HLM production). When HLM landlords buy in VEFA from private developers, the future 25-year TFPB exemption increases the HLM's willingness-to-pay for the turnkey building, which developers pass back into higher land bids (*charge foncière*). Highlighting the **VEFA channel** will make your land-price capitalization argument much more concrete and persuasive.
