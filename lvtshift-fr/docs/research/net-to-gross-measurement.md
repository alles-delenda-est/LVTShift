# Net-to-gross ratio r: empirical measurement (DPE x BD TOPO)

> **Archived research report** (October 2026), kept as the evidence behind the
> model's parameters. Working files it mentions (downloads, scripts, intermediate
> tables) were kept outside the repository. The decisions taken from it are in
> METHODOLOGY §3.1 and §4.

Date: 2026-10-21. The machine-readable results, detailed tables, scripts and interim
pilot note behind this report were working files and are not retained in the
repository; every figure the model uses is reproduced below.

## Bottom line

| | Desk estimate | **Measured (recommend)** | Range |
|---|---|---|---|
| Appartement | 0.74 (0.70-0.79) | **0.64** | 0.59-0.68 |
| Maison | 0.80-0.85 | **0.61** | 0.58-0.66 |

The measured ratios are about 0.10 (flats) and 0.20 (houses) **below** the desk values.
That is not a contradiction. The desk value is an architectural ratio: habitable area
over the true external floor area. The measured ratio is habitable area over **the
pipeline's own gross area**. That gross area also counts levels BD TOPO records that
contain no habitable space: attics, raised basements and garage levels in houses, and
an extra storey in about a third of collective buildings. For the market-value fix, the
measured ratio is the right one, because it corrects exactly the area the pipeline
multiplies by.

**Structure:** use a single national pair. Flats show no meaningful variation by place:
Paris 0.634, rest 0.639 (pure residential). Most per-commune values sit within about
±0.05 of the mean; the outliers are Paris 3e and Lyon 2e (0.51) and Sète (0.53). Variation by era is modest (±0.03-0.04) and not monotonic. Houses show one real place
effect: Paris and the inner ring are about 0.06 higher. An optional two-way split for
houses is given below. The bigger driver of variation is the BD TOPO storey count of each
building, not the place.

## Method

1. **Join key.** DPE (ADEME, 3CL-2021, 15.8 M rows) carries `id_rnb`. BD TOPO `batiment`
   carries `identifiants_rnb` (separated by `/`). The join uses this national building ID
   (RNB) directly, so no geocoding is needed. RNB IDs and BD TOPO polygons form a graph,
   and each connected component is one unit. Habitable area and gross area are summed
   on both sides, which handles buildings split or merged differently in the two sources.
2. **Gross area** is computed exactly as `estimate.improvement_value` does it:
   footprint × `nombre_d_etages`, else round(hauteur/3) with a minimum of 1. BD TOPO and
   cadastre come from the repo's `ingest` functions and the shared cache, so the URLs and
   bounding boxes match the pipeline.
3. **Flats.** The numerator is `surface_habitable_immeuble` from building-level DPEs
   ('dpe immeuble collectif' and the flat DPEs generated from it, deduplicated to one per
   parent). If several DPEs for one RNB ID disagree by more than 15%, the RNB ID is dropped.
   Filters:
   - storeys measured (none imputed);
   - building in service, not a light construction;
   - no tertiary surface, at least 2 flats, BD TOPO `usage_1` = Résidentiel;
   - DPE `nombre_appartement` / BD TOPO `nombre_de_logements` in [0.67, 1.5], which checks
     that the DPE covers the same building.

   'Pure' means BD TOPO `usage_2` is empty. 'Mixed' means `usage_2` is set (typically
   ground-floor commerce).
4. **Houses.** The numerator is `surface_habitable_logement` from 'maison' DPEs, on BD TOPO
   components with at most 1 dwelling. Three variants:
   - building-level;
   - **parcel-level**, which follows the pipeline: habitable area / all floor area on the
     parcel, garages and annexes included, built from the same ≥5 m² intersection pieces as
     `fetch_buildings`;
   - an **RNB-free** check: DPE point in parcel, with exactly one dwelling on the parcel.
5. **Robustness.**
   - Trim to 0.3 < r < 1.2, with a sensitivity test on the trim bounds.
   - Report medians and area-weighted ratios (Σ habitable area / Σ gross area). The
     area-weighted ratio is the one that matters for aggregate value.
   - Confidence intervals: building bootstrap, plus a commune-cluster bootstrap for pooled
     groups.
   - Results are split by era band from the DPE `periode_construction`.
6. **From DPE to DVF basis.** The pipeline's €/m² is per DVF `surface_reelle_bati`, not per
   DPE habitable area. I compared the two directly:
   - houses: single-house DVF sales on parcels holding one consistent maison DPE (n = 2,330);
   - flats: parcel medians, which is a distributional comparison only (n = 5,331 parcels).
7. **Coverage.** 35 data codes, 5,713 flat buildings and 9,212 houses in the core samples:
   - Paris 3e, 7e, 8e, 11e, 15e, 16e, 17e, 18e, 20e;
   - Lyon 1er-9e;
   - Villeurbanne;
   - Paris inner ring: Boulogne, Montreuil, Saint-Denis, Vincennes, Créteil;
   - Lyon ring: Bron, Caluire, Vénissieux;
   - Grenoble, Annemasse, Roubaix, Cahors, Figeac, Sète, La Rochelle, Mulhouse.

## Results (area-weighted r_DPE, 95% bootstrap CI, n; trim 0.3-1.2)

**Collective (flats)**

| Group | Pure residential | All residential (pure + mixed) |
|---|---|---|
| All | **0.637** [0.621-0.652] n=962 (median 0.674) | 0.612 [0.606-0.617] n=5713 (median 0.631) |
| Paris | 0.634 [0.612-0.655] n=303 | 0.611 [0.603-0.619] n=2324 |
| Non-Paris | 0.639 [0.618-0.660] n=659 | 0.613 [0.605-0.620] n=3389 |
| Lyon (arr.) | 0.597 [0.548-0.644] n=63 | 0.595 [0.585-0.605] n=1165 |
| Paris inner ring | 0.647 [0.620-0.675] n=390 | 0.652 [0.632-0.670] n=594 |
| Lyon ring + Villeurbanne | 0.650 [0.558-0.727] n=33 | 0.601 [0.578-0.625] n=322 |
| Panel towns | 0.612 [0.573-0.654] n=173 | 0.614 [0.602-0.626] n=1308 |
| pre-1948 | 0.637 n=395 | 0.603 n=3036 |
| 1948-1974 | 0.673 n=247 | 0.641 n=1338 |
| 1975+ | 0.603 n=320 | 0.594 n=1339 |

- Mixed-use buildings alone: 0.607 (n = 4,751).
- Parcel-level, pure residential: 0.649 (n = 413).
- Per-commune range (all residential): 0.51 (Paris 3e, Lyon 2e) to 0.68 (Créteil).
- The Haussmann case (pre-1948 Paris) is in line with the rest. Paris pre-1948 is
  0.60-0.64, not the ≈0.67 feared, nor anything lower.

**Houses**

| Group | Building | Parcel-level (pipeline-faithful) |
|---|---|---|
| All | **0.672** [0.668-0.676] n=9212 (median 0.701) | **0.659** [0.654-0.665] n=4941 (median 0.682) |
| Paris (n small, selective) | 0.745 n=242 | 0.742 n=151 |
| Paris inner ring | 0.717 n=1056 | 0.715 n=575 |
| Lyon arr. / ring | 0.671 / 0.673 | 0.645 / 0.655 |
| Panel towns | 0.660 n=6636 | 0.646 n=3419 |
| pre-1948 / 1948-74 / 1975+ | 0.677 / 0.683 / 0.643 | 0.663 / 0.668 / 0.635 |
| BD TOPO 1 / 2 / 3+ storeys | 0.808 / 0.672 / 0.604 | |

- RNB-free check (point in parcel): 0.667 (n = 4,406). It agrees with the RNB-matched
  result, so the RNB matching does not bias the sample.
- Annex floor area is on average only 1.5% of parcel floor area in the parcel sample.

**Diagnostics**
- **Storeys.** In 28-42% of flat buildings, BD TOPO counts more storeys than the DPE
  `nombre_niveau_immeuble` (mean excess +0.2 to +0.45 levels). Using DPE storeys instead
  raises r from 0.61 to 0.64-0.65. For flats with height/levels < 2.4 m, r is 0.53. For
  houses, r is 0.56 when height/levels < 2.4 m and 0.76 when it is > 3.4 m. Storey
  miscounting is the main source of scatter.
- **DVF vs DPE surface.**
  - Houses: DVF/DPE has a median of 0.93 and an area-weighted value of 0.90. DVF
    under-records converted attics and extensions.
  - Flats: median 1.03, area-weighted 1.06. This comparison is distributional, not
    matched sale by sale, and may reflect which flats get sold. I treat flats as ≈1.00.
- **Trim sensitivity.**
  - Houses: loosening or removing the trim raises r (parcel-level 0.659 → 0.671 → 0.68).
  - Flats: loosening the trim lowers r (pure 0.637 → 0.624-0.631; all residential
    0.612 → 0.59).

## Recommendation and how the numbers were built

```python
# DVF-basis net-to-gross, applied as market_value *= r[type_local]
NET_TO_GROSS = {"Appartement": 0.64,   # range 0.59-0.68
                "Maison":      0.61}   # range 0.58-0.66
# optional (houses only): {"Maison": 0.66} for Paris + petite couronne, 0.60 elsewhere
```

- **Appartement 0.64.** This is the pure-residential r (0.637) with DVF/DPE = 1.00.
  - I use the pure ratio rather than the all-residential one (0.61) because mixed
    buildings score lower: their commercial ground floor counts in gross area but not in
    habitable area. Applying 0.61 would in effect value shop floors at zero. Applying 0.64
    to every building values commercial floors at the residential net €/m², which is a
    reasonable stand-in.
  - The range runs from 0.59 (all-residential, untrimmed) to 0.68 (DVF/DPE of 1.06, or
    counting storeys the DPE way).
  - No Paris/era split: the differences are inside the noise.
- **Maison 0.61.** This is the parcel-level r_DPE (0.659 trimmed, 0.68 untrimmed) ×
  DVF/DPE (0.90-0.93): 0.59-0.63, central 0.61.
  - Optional split, Paris + inner ring vs rest: 0.715-0.725 × 0.92 ≈ 0.66, against
    0.645-0.66 × 0.91 ≈ 0.60.

## Implication for the cost side (important)

Much of the gap from 0.74 comes from BD TOPO gross area including non-habitable levels.
That same inflated gross area is multiplied by the construction cost per m² of gross area
on the building side. So scaling only the market side with r ≈ 0.61-0.64 understates land
value compared with a consistent treatment.

Option (b) of `construction-costs-2025.md` is more consistent: put both sides on the
same habitable basis, with habitable area = r × gross and cost per habitable m². With
that, the land share becomes 1 − cost_hab × depreciation / price per m², which no longer
depends on r. r then only scales the level of value. Gemini reached the same conclusion
independently. I recommend the maintainer decide between (a) and (b) knowing this. Under (a),
the land share is highly sensitive to r: ±0.05 on r moves market value by about ±8%, and
all of that moves into land.

## Caveats

- **DPE selection.** DPEs exist only for dwellings that were sold, let or renovated since
  July 2021.
  - Building-level DPEs over-represent large copropriétés and social landlords, which are
    obliged to have collective DPEs. Pure-residential buildings are only about 17% of the
    flat sample, and mixed buildings dominate in Paris.
  - The houses sample is urban and suburban. It contains no rural communes with large farm
    outbuildings, where the parcel-level r would be lower.
- **RNB coverage.** 61% of building-level flat DPE rows and 56% of house DPE rows carry an
  RNB ID. 99% of those IDs are found in BD TOPO. 8.7% (flats) and 3.6% (houses) of RNB IDs
  had inconsistent surfaces and were dropped. Of 9,535 flat components, 5,973 passed the
  filters and 5,713 survived the trim; most losses come from the flat-count consistency
  check. The RNB-free check for houses matches the RNB result to 0.01.
- **BD TOPO storeys.** In the median commune, 38% of BD TOPO buildings have imputed
  storeys, but these are almost all non-dwellings. Matched dwellings essentially always
  have a measured `nombre_d_etages`, so the result applies to the stock the pipeline
  prices. Storey miscounts are the main source of scatter: IQR ≈ 0.54-0.71 for flats and
  0.58-0.83 for houses.
- **DVF basis.** The flat DVF/DPE factor is not matched sale by sale. The house factor is
  matched by parcel, but a parcel may have changed between the sale and the DPE.
- **Not covered.** Alsace-Moselle is included only through Mulhouse, which has DPE and
  BD TOPO but no DVF, so it adds nothing to the DVF check. Marseille, overseas departments
  and rural communes are not covered.
- **Privacy.** Outputs are aggregates only. Intermediate per-building tables (no addresses,
  no owners; RNB IDs only in raw caches) stay in the scratchpad.

## Gemini review (gemini-4-argon) and my response

- **Applying the pure-residential r to flats, and DVF/DPE ≈ 1 for flats.** Agreed and
  adopted.
- **Houses 0.60 (0.55 if rural).** Close to my 0.61. Not adopted for rural use: the panel
  includes Cahors and Figeac, whose parcel-level r (0.657 and 0.656) is no lower than
  elsewhere. Rural communes remain untested, so this is noted as a caveat.
- **"Trimming biases house r upward."** Tested, and it is wrong: loosening the trim
  *raises* house r (0.659 → 0.68). I kept the trimmed figure as the low-mid anchor.
- **Change the storey heuristic from h/3 to 3.1-3.3 m.** Not supported by this data:
  matched dwellings almost never use the imputation. This is a separate question.
- **Severe cost-side inconsistency; cost per habitable m² is the cleaner fix.** Agreed;
  see the section above. Its suggested cost scaling of 0.88 is a judgement call, and I
  have not adopted it.
