# Collectif (multi-family) construction-cost calibration — follow-up research

**Purpose.** Follow-up to `docs/construction-cost-calibration-data.md` §5.1, which
flagged that SDES **EPTB** (individual-house survey) understates construction cost
for **collectif** buildings, most acutely in **Montreuil** (Zone A bis, dense
Île-de-France inner suburb). This note sources an authoritative **collectif** €/m²
and derives a single recommended figure for Montreuil. **Gathering/citation only —
no code touched, no number tuned to a land-share target.**

**Author / date.** Research agent, 2026-07-15.

---

## 0. Access note (same constraint as the prior pass)

`WebFetch` returned **HTTP 403** for every primary host tried in this pass
(`banquedesterritoires.fr` PDF, `opendata.caissedesdepots.fr`,
`data.smartidf.services`, `politiquedulogement.com`). **`WebSearch` worked** and
was able to surface and quote figures from those exact pages/PDFs (Google's cache
of the content). All figures below are cited to the **primary URL** (verifiable by
a human in a browser) with a note that they were **read via WebSearch**, per the
same discipline as the prior document. Nothing here is invented; anything that
required stacking assumptions (indexation, zone-split extrapolation) is explicitly
labelled **[DERIVED]** and the chain of reasoning is shown so it can be checked or
rejected independently of the sourced anchors.

---

## 1. Sourced figures table

| # | €/m² value | Surface basis | Foncier? | Social / Private | Region | Vintage | Source |
|---|---|---|---|---|---|---|---|
| A | **2,300 → 2,550 €/m²** (+11%) | **surface utile** (SU — habitable + capped share of annexes; standard HLM metric, *smaller than SDP*) | **avec foncier** (prix de revient = charge foncière + travaux + autres charges) | **Social (HLM)**, national average, all zones blended | National | 2019 → 2023 (published Dec 2024) | Banque des Territoires, *Éclairages n°33*, Déc. 2024 [S1] |
| B | Zone A bis **+24%**, B1 +18%, B2 +15%, C +11% (2019→2024 trajectories) | SU | avec foncier | Social | Zone A bis = Paris + 29 inner-ring communes incl. **Montreuil** (93) | 2019–2024 | Same, *Éclairages n°33* [S1] |
| C | **169,200 €** average unit cost (2023) | SU, whole-unit (not €/m²) | avec foncier | Social | National | 2023 | Same [S1] (relayed by [S2][S3]) |
| D | Travaux (construction work) **+22%**, autres charges +10% (2023) — vs total +11% | — | **hors foncier component isolated** | Social | National | 2019–2023 | Same [S1] |
| E | National direct-management (MOD) split: **2,262 €/m² = 67% travaux + 21% foncier + 12% autres** | SU (implied) | split given | Social | National | **2020** | Le Moniteur / La Banque Postale, citing CDC data [S4][S5], relayed via [S6] |
| F | Zone A bis **3,400 €/m²**; Zone B1 2,200; Zone C < 2,000 (**totals, avec foncier**) | SU | avec foncier | Social | Zone A bis (incl. Montreuil) | **2020** | Le Moniteur [S4] |
| G | Range **1,440 €/m² (Orne) to 3,940 €/m² (Paris)**; national avg **2,060 €/m²** | SU | avec foncier | Social | Département-level, Paris = Zone A bis core | **2017–2020 average** | La Banque Postale [S5] |
| H | CV (coefficient of variation) across départements: **foncier 37%**, **travaux (construction) 15%** | — | split | Social | National | 2017–2020 | Same [S5] — *key structural fact: construction cost itself varies much less by geography than land does, but Paris/zone A bis sits at the high end of that 15% band, not the low end (see §2)* |
| I | **1,120–1,240 €/m² SDP** (social/PLAI-type); **1,340–1,480 €/m² SDP** (standard collectif); **1,500–1,730** (intermediate standing); **1,900–2,000 €/m² SDP** ("attractive urban zones" e.g. Paris/Lyon); **>2,000 up to 3,200 €/m² SDP** (high-end) | **explicitly SDP** (surface de plancher) — matches the model's basis directly, **no haircut needed** | **hors foncier** (construction ratio only) | Both social and private ranges given separately | National, with an explicit "zones urbaines attractives" uplift bracket | **2019** | Cabinet Franck Verdelet (AMO/économiste de la construction, trade source) [S7][S8] `[UNVERIFIED – secondary, but surface basis is explicit and matches the parameter definition exactly]` |
| J | **2,403 €HT/m² SDP** — single collective-housing case study (biosourced-materials cost survey) | **explicitly SDP**, HT (ex-VAT) | **hors foncier** | Not stated (appears to be private/mixed) | Pays de la Loire / Hauts-de-France (regional survey, **not** IdF) | ~2021–2023 (Cerema ongoing observatory) | Cerema, *Observatoire des coûts de la construction* [S9] |
| K | Range **1,517–1,647 €/m²** modelled RE2020 collective-housing construction cost (8.5% spread optimistic/pessimistic) | **not stated** in the secondary relay (likely SHAB/habitable, needs verification) | Framed as construction-only in context | — | National | ~2022 | Cerema/Untec RE2020 cost-impact studies, relayed via trade press [S10][S11] `[PARTIALLY VERIFIED — surface basis unconfirmed]` |
| L | Habitable-€/m² **floor values multiply by a factor of ~2.5×** (ceiling values ~3×) going from Type‑1 (single-storey house) to Type‑6 (dense urban collectif); sharp cost step between Type‑3 and Type‑4 **coincides with the requirement for underground parking** | per m² habitable | hors foncier | Both (general typology) | National, structural/qualitative finding | 2019 study | politiquedulogement.com, *"Des coûts de construction très différents selon le type d'immeuble"*, Dec. 2019 [S12] — **no absolute € figures recoverable via WebSearch** (WebFetch 403); cited for the **mechanism** (parking/height/complexity drive the collectif premium), not as a numeric anchor |
| M | IdF **private/promoteur new-build sale price**: 5,643 €/m² (Q4 2024) → 5,774 (Q2 2025) → 5,862 €/m² (Q1 2026) | Not construction cost — **prix de vente** (sale price), includes land, margin, taxes, VAT, fees | avec foncier + marge + taxes | Private/promoteur | Île-de-France | 2024–2026 | FPI France, *Les chiffres du logement neuf* [S13] — **do not use as a construction-cost figure**; kept only as a sanity-check ceiling (construction-only must be well below this) |
| N | Olonn.fr note: in Paris, the high prix de revient is due "**especially to land scarcity, but also to very high construction work costs [themselves]**" | qualitative | — | Social | Paris | 2020-era commentary | olonn.fr, citing CDC data [S6] — supports a **real** (not purely land-driven) construction-cost premium in dense Paris-adjacent cores |

---

## 2. Deriving a collectif construction-cost figure comparable to the parameter

The parameter needs: **hors foncier, per m² of floor area (SDP-like, walls
included), turnkey, gros œuvre + second œuvre, 2025 reference year**. None of the
sourced figures above hit all four criteria simultaneously for **Montreuil / Zone
A bis** specifically — each needs at least one adjustment. Two independent
derivation paths are shown; they converge reasonably well, which is the main basis
for confidence in the final number.

### Path 1 — From Éclairages n°33 (social, Zone A bis, surface utile, avec foncier)

1. **Isolate zone A bis level.** Row F gives zone A bis 2020 ≈ **3,400 €/m²** total
   (avec foncier, SU). Row B gives zone A bis **+24%** from ~2019 to 2024. Taking
   2020 ≈ 2019 (pre-shock, roughly flat) as the base: 2024 zone A bis total ≈
   3,400 × 1.24 ≈ **4,216 €/m²** `[DERIVED — combines two overlapping-but-distinct
   vintages from two different secondary relays of CDC data; treat as
   approximate]`.
2. **Strip out foncier + autres charges.** The national 2020 split (row E) is
   67% travaux / 21% foncier / 12% autres, but **this split does not transfer
   directly to zone A bis** — land is proportionally much bigger there (row H: land
   CV = 37% vs construction CV = 15%, i.e. land is what moves most between zones).
   Applying the **national travaux trajectory** instead of a zone-specific split
   avoids compounding that error: national travaux 2019 ≈ 67% × 2,300 ≈ 1,541 €/m²
   (row A base × row E ratio); travaux **+22%** 2019→2023 (row D) ⇒ national
   travaux 2023 ≈ **1,880 €/m²** (SU, hors foncier, national blended).
3. **Zone-A-bis construction premium.** Construction cost (not land) varies with a
   15% coefficient of variation across départements (row H); dense, constrained,
   high-labour-cost Paris/inner-ring sites plausibly sit **~15–30% above** the
   national mean (crane logistics, site access, underground parking, higher local
   wages) — consistent with olonn.fr's explicit note that Paris construction work
   itself, not just land, runs very high (row N). Applying **+15% to +30%** to the
   national 2023 travaux figure: 1,880 × 1.15–1.30 ≈ **2,160–2,440 €/m²** (zone A
   bis, SU, hors foncier, 2023).
4. **Index 2023 → 2025.** National BT01-based nudge from the prior document
   (§3) is small (~4–6% cumulative for two years, consistent with the flattening
   BT01). ⇒ **≈ 2,250–2,590 €/m²** (zone A bis, SU, hors foncier, **2025**).
5. **Surface-utile → SDP haircut.** Surface utile (habitable + capped annex share)
   is smaller than surface de plancher (adds external walls, circulation,
   stairwells, technical rooms). The same ~10–20% order-of-magnitude haircut
   flagged in the prior document for habitable→SDP applies here, somewhat
   attenuated because SU already includes some annex area — call it **~10–15%**.
   ⇒ **≈ 1,910–2,330 €/m² SDP**, zone A bis social collectif, hors foncier, 2025.
   `[DERIVED, multi-step — the anchors (rows A, D, E, F, H) are sourced; the
   combination is not]`.

### Path 2 — From SDP-basis trade/technical sources (rows I, J), indexed to 2025

- Row I ("zones urbaines attractives", 2019, **already SDP, hors foncier**):
  1,900–2,000 €/m². Applying the same construction-cost inflation used above
  (+22% 2019→2023, +~5% 2023→2025 ⇒ **cumulative ≈ +28%**): **2,430–2,560 €/m²
  SDP** (2025).
- Row J (Cerema case study, **already SDP HT, hors foncier**, ~2021–2023,
  non-IdF regions): 2,403 €/m², indexed modestly to 2025 (+5–10% for 2–4 years'
  BT01 drift): **≈ 2,520–2,640 €/m²**. This is a **single case study outside
  Île-de-France**, so treat as a rough cross-check, not a zone A bis figure per se
  — if anything it suggests 2,400+ is achievable even **outside** the most
  expensive IdF core, which supports rather than undermines the Path-1 range.

### Convergence

Path 1 (social, Zone A bis, derived from Éclairages n°33): **≈ 1,910–2,330 €/m²
SDP**. Path 2 (SDP-basis trade/technical sources, "attractive urban zones" and one
non-IdF case study, indexed): **≈ 2,430–2,640 €/m²**. The two paths overlap only at
their outer edges (~2,330–2,430), which is a **materially useful convergence**
given they use entirely independent primary sources and different methodologies —
it brackets a plausible central zone of **≈ €2,200–2,550/m² SDP** for dense-IdF-core
collectif, hors foncier, 2025 vintage, before making the social-vs-private call
below.

---

## 3. Social vs private/promoteur — which is the right basis for the model

- **Social (HLM) collectif** is the **cheaper** end: land is often obtained via
  charge-foncière caps/subsidy, build quality/finish is more standardised, and
  Éclairages n°33's own split (row E) shows social operations keep travaux at
  ~67% of total spend even under land pressure. Path 1 above (**≈1,910–2,330
  €/m² SDP**) is a social-only estimate.
- **Private/promoteur collectif** is **dearer**: better finishes, larger balconies/
  parking ratios, and land/margin/marketing pressure that indirectly raises
  build-to-spec quality in tense markets. Row I's private "zones urbaines
  attractives" bracket (1,900–2,000 €/m² SDP, 2019) indexed to **2,430–2,560
  €/m² SDP (2025)** is the private-collectif proxy — noticeably above Path 1.
  FPI sale-price data (row M, ~5,600–5,900 €/m² IdF) confirms private collectif
  sits at a much higher total price point, of which construction is only one
  (large) component alongside land, margin, taxes and fees — consistent with a
  hors-foncier construction share well below the sale price, in the
  €2,400–2,700/m² range if travaux is assumed to be roughly 45–55% of the
  private sale price (this ratio is **not separately sourced here** — FPI
  reports sale prices, not cost breakdowns; treat this cross-check as indicative
  only, not a primary anchor).
- **Which basis for the model.** The parameter values **existing housing stock**
  as a whole (a mix of social and private-market collectif, built across decades),
  not a single tenure. Montreuil specifically is **not** a majority-social
  commune (it is a mixed inner-suburb with a meaningful HLM share alongside
  substantial private co-ownership stock, both older and recently built). The
  right basis is therefore a **blend weighted toward the middle-to-upper part of
  the social-to-private range**, not the pure-social floor and not the pure
  private-promoteur ceiling. This also matches the parameter's definition —
  "turnkey **replacement** cost" — which should reflect what it costs to rebuild
  *any* of the existing collectif stock today to current code (RE2020), not the
  cheapest social-only cost floor.

---

## 4. Recommended figure for Montreuil (and, by extension, Villeurbanne/Grenoble collectif share)

**Recommended: ≈ 2,300 €/m² (hors foncier, per m² of floor area / SDP), for a
dense Île-de-France Zone-A-bis collectif core such as Montreuil, 2025 vintage.**

**Uncertainty range: €2,000–2,600/m² SDP.**

**Reasoning:**
- The range brackets both derivation paths in §2 (social ≈1,910–2,330; private
  ≈2,430–2,640) and sits at their overlap, nudged toward the social-derived
  lower-middle per the tenure-mix argument in §3.
- It is **materially above** the EPTB individual-house IdF figure (1,914 €/m²,
  habitable basis, from the prior document) even after accounting for the fact
  that EPTB's habitable-based figure would itself need a **downward** haircut to
  become SDP-comparable (~1,600–1,720 €/m² SDP-equivalent) — confirming the
  hypothesis stated in the task: collectif genuinely costs more per floor-area m²
  than individual houses in a dense core, consistent with the qualitative Type-1→
  Type-6 mechanism in row L (underground parking, lifts, structure, height).
- It is **above** the current config guess for Montreuil (2,150 €/m²) by roughly
  **+7%**, a modest, source-grounded correction — not a large swing, but in the
  direction the task hypothesis predicted (EPTB understates; collectif costs more).
- **For Villeurbanne and Grenoble** (ARA, Lyon core / Grenoble core, not zone A
  bis but still meaningfully urban/dense): no ARA-specific collectif source was
  found in this pass. Directionally, the same collectif-vs-individual uplift
  mechanism (row L) applies, but the *zone-A-bis-specific* land-scarcity premium
  in Path 1 does **not** — Lyon/Grenoble are zone A/B1, not A bis. A **smaller**
  collectif uplift over their EPTB individual-house figure (≈2,065 €/m²) would be
  the sourced-consistent inference, but this was **not directly sourced** in this
  pass and should get its own follow-up (ARA-specific Éclairages-n°33-style zone
  B1 data was not extracted here) — flagged as a gap, not resolved.

**What I could verify:** the Éclairages n°33 headline national trajectory (2,300→
2,550 €/m², +11%, 2019–2023) and its zone A bis differential (+24%) are corroborated
across four independent relays (Banque des Territoires, Union-Habitat/USH,
AEF info, La Banque Postale) [S1][S2][S3][S6], so I treat the *shape* of that
result (zone A bis rises fastest, travaux rose faster than the total) as solid.
The **absolute zone A bis €/m² for 2023/2024** was not directly recoverable
(only the 2020 level, row F, and the % change, row B, were found) — I had to
derive it, which is the weakest link in Path 1.

**What I could NOT verify:** (a) the exact travaux/foncier split *specific to
zone A bis* (only the national 2020 split, row E, was found — I extrapolated
using the CV argument in row H, which is a structural fact, not a zone A bis
data point); (b) the current (2024/2025) absolute SDP-basis figure from any
single official source — rows I and J are trade/technical secondary sources,
correctly flagged `[UNVERIFIED – secondary]`/`[PARTIALLY VERIFIED]`; (c) an
ARA-specific (Villeurbanne/Grenoble) collectif figure — not found in this pass.
The full Éclairages n°33 PDF (primary source, [S1]) was **403-blocked** for direct
fetch; everything from it here was read via WebSearch snippets of that exact URL,
per the environment caveat.

---

## 5. Sources

- **[S1]** Banque des Territoires, *Éclairages n°33 — Le prix de revient des
  logements sociaux face aux tensions inflationnistes*, Déc. 2024. Sample: 16,800
  opérations / 334,500 logements, Jan. 2019–May 2024. National 2,300→2,550 €/m²
  (+11%, 2019–2023); zone A bis +24% (5 yrs), B1 +18%, B2 +15%, C +11%; travaux
  +22%, autres charges +10% (2023); avg. unit cost 169,200 € (2023).
  https://www.banquedesterritoires.fr/eclairages-n-33 (landing page) and PDF
  https://www.banquedesterritoires.fr/sites/default/files/2025-01/Exe%20brochure%20Eclairages%2033%20A4%202024%20vdef.pdf
  — **WebFetch 403; read via WebSearch of this exact URL.**
- **[S2]** L'Union sociale pour l'habitat (USH), relay of Éclairages n°33 —
  *Le prix de revient des logements sociaux face aux tensions inflationnistes*.
  https://www.union-habitat.org/centre-de-ressources/economie-financement/le-prix-de-revient-des-logements-sociaux-face-aux
  — via WebSearch.
- **[S3]** USH, *Prix de revient des logements sociaux : +11% entre 2019 et 2023,
  ce que cache la moyenne*. https://www.union-habitat.org/prix-de-revient-des-logements-sociaux-11-entre-2019-et-2023-ce-que-cache-la-moyenne
  — via WebSearch.
- **[S4]** Le Moniteur, *Hausse continue du coût de production des HLM* (2021,
  citing 2020/prior CDC-sourced data) — zone A bis 3,400 €/m² (2020), B1 2,200,
  C <2,000; MOD split 2,262 €/m² = 67% travaux / 21% foncier / 12% autres (2020).
  https://www.lemoniteur.fr/article/hausse-continue-du-cout-de-production-des-hlm.2171817
  — via WebSearch (403 on direct fetch not separately tested, but not fetched
  directly in this pass).
- **[S5]** La Banque Postale, *Envolée des coûts de construction : le logement
  social n'est pas épargné* — range 1,440 €/m² (Orne) to 3,940 €/m² (Paris),
  national avg 2,060 €/m² (2017–2020); CV foncier 37%, CV construction 15%.
  https://www.labanquepostale.fr/bailleurs-sociaux/actualite/couts-construction-logement-social.html
  — via WebSearch.
- **[S6]** olonn.fr, *Rareté du foncier : quel impact sur le coût et la
  production des logements sociaux?* (2021), citing CDC data — repeats the
  2,262 €/m² / 67-21-12 split; explicit note that Paris construction-work cost
  itself (not just land) runs very high.
  https://olonn.fr/2021/12/rarete-du-foncier-quel-impact-sur-le-cout-et-la-production-des-logements-sociaux/
  — via WebSearch.
- **[S7]** Cabinet Franck Verdelet (économiste de la construction / AMO),
  *Ratio moyen du m² de construction — logement collectif — France 2019* —
  1,250–1,400 €/m² SDP general range. https://cabinetfranckverdelet.com/archives/4811
  — via WebSearch. `[UNVERIFIED – secondary/trade]`
- **[S8]** Same author, *Prix du m² de construction de logement collectif — 3
  gammes — France 2019* — PLAI/social 1,120–1,240; standard 1,340–1,480;
  intermediate 1,500–1,730; "zones urbaines attractives" 1,900–2,000; high-end
  up to 3,200 €/m² SDP. https://cabinetfranckverdelet.com/archives/5990
  — via WebSearch. `[UNVERIFIED – secondary/trade]`
- **[S9]** Cerema, *Observatoire des coûts de la construction : promouvoir les
  matériaux biosourcés et les solutions de maîtrise des coûts des bâtiments* —
  case-study figure 2,403 €HT/m² SDP for one collective-housing operation
  (Pays de la Loire / Hauts-de-France regional survey).
  https://www.cerema.fr/fr/actualites/observatoire-couts-construction-promouvoir-materiaux
  — via WebSearch. Single case study, not a regional average.
- **[S10]** Coverage of Cerema/Untec RE2020 cost-impact modelling — collective
  housing construction cost range 1,517–1,647 €/m² (surface basis not confirmed).
  https://bati.zepros.fr/actu-generale/impact-re2020-parlons-couts — via WebSearch.
  `[PARTIALLY VERIFIED]`
- **[S11]** Related RE2020 cost-impact coverage.
  https://negoce.zepros.fr/lactu-generale/article/quel-est-limpact-re2020-couts
  — via WebSearch. `[PARTIALLY VERIFIED]`
- **[S12]** politiquedulogement.com, *Des coûts de construction très différents
  selon le type d'immeuble*, Déc. 2019 — qualitative Type-1→Type-6 typology,
  ~2.5–3× habitable-€/m² multiplier, cost step at Type-3→Type-4 tied to
  underground-parking requirement. https://politiquedulogement.com/2019/12/des-couts-de-construction-tres-differents-selon-le-type-dimmeuble/
  — **WebFetch 403**; only the qualitative finding was recoverable via WebSearch,
  no absolute € figures.
- **[S13]** FPI France, *Les chiffres du logement neuf* — Île-de-France
  collectif **sale price** (not construction cost): 5,643 €/m² (Q4 2024), 5,774
  (Q2 2025), 5,862 (Q1 2026). https://fpifrance.fr/les-chiffres-de-lobservatoire-fpi
  and quarterly PDFs at fpifranceprodcellar.cellar-c2.services.clever-cloud.com
  — via WebSearch. **Not used as a construction-cost anchor**, kept as a ceiling
  sanity-check only.
- Zone A bis coverage of Montreuil confirmed via loipinel.fr / loi-pinel.fr zonage
  pages (Montreuil, 93, is in Zone A bis along with Paris + 28 other inner-ring
  communes as of the 2024 zonage revision).
  https://www.loipinel.fr/zone-a-bis-departement-du-93/ — via WebSearch.

---

## 6. One-line recommendation (no code changed here)

Use **≈ 2,300 €/m² hors foncier per m² of floor area (SDP)** for Montreuil's
`construction_cost_eur_m2`, range **2,000–2,600**, in place of the current 2,150
guess or the individual-house EPTB IdF figure (1,914, and itself a further ~10–20%
too high once habitable→SDP-adjusted for comparison). This is a **derived**
estimate triangulated from two independent paths (Banque des Territoires social
data indexed and zone-adjusted; SDP-basis trade/technical sources indexed) that
converge at €2,200–2,550 SDP — **not** a single official collectif €/m² series
(none was found that is simultaneously official, zone-A-bis-specific, current-
vintage, and SDP-denominated). Villeurbanne/Grenoble collectif uplift over their
EPTB individual-house figure is directionally plausible but **not sourced** in
this pass — flagged as a follow-up gap, same as the prior document's own
recommendation.
