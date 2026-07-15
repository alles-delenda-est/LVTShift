# Collectif (multi-family) construction cost €/m² — sourcing for `construction_cost_eur_m2`

**Purpose.** Source an *authoritative, open* collectif (multi-family) construction
cost (€/m², **hors foncier**, per floor area) to correct the `construction_cost_eur_m2`
parameter for **collectif-heavy pilot communes** — most acutely **Montreuil** (dense
Île-de-France inner suburb, **officially Zone A bis**), and secondarily Villeurbanne
(Lyon core) and Grenoble. The prior pass sourced costs from **SDES EPTB**, which covers
**individual houses only** (IdF ~1 914 €/m² habitable), and flagged that this
*understates* collectif cores. This document fills that gap.

**Discipline.** Data-gathering and citation only. **No code changed. No number tuned
to any land-share target.** Every figure is cited; anything not pinned to a primary
source is marked `[DERIVED]`, `[PARTIALLY VERIFIED]`, or `[UNVERIFIED – secondary]`.

**Author / date.** Research agent (Opus), 2026-07-15. Model reference year = **2025**.

---

## 0. Access / verification note (read first)

Same environment constraints as the prior pass, re-confirmed today:

- **`curl` is fully blocked** at the egress proxy — the gateway answers **403 to the
  CONNECT tunnel** ("policy denial") for *every* external host (verified against the
  proxy status endpoint: recent `connect_rejected` entries for insee.fr, data.gouv.fr,
  example.com, juristique.org). No scripted download or open-data API pull was possible
  (CDC `opendata.caissedesdepots.fr` and IdF `data.smartidf.services` REST endpoints
  both 403).
- **`WebFetch` returns HTTP 403** for banquedesterritoires.fr, union-habitat.org,
  opendata.caissedesdepots.fr, data.smartidf.services, politiquedulogement.com — all
  block non-browser clients.
- **`WebSearch` works** and surfaces/quotes the content of the primary pages. Every
  figure below is cited to its **primary URL** (browser-verifiable) and was **read via
  WebSearch of that page**. Nothing here is invented.

---

## 1. Sourced figures table

Basis legend: **PdR** = prix de revient (full cost, **avec foncier**); **travaux** =
construction only (**hors foncier**); **Su** = surface utile; **Shab** = surface
habitable; **SDP** = surface de plancher; **SP-like** = footprint × storeys (the
model's `floor_area`, walls included).

| # | Figure (€/m²) | What it is | Surface basis | Foncier? | Social/Private | Region | Vintage | Source |
|---|---|---|---|---|---|---|---|---|
| A | **2 550** (was 2 300 in 2019, +11%/4y) | PdR, social housing, national average | **surface utile** | **AVEC foncier** | Social collectif | National | **2023** | Éclairages n°33 [E33] |
| A′ | avg **169 200 €/logement** (2023); 16 800 ops | PdR per unit | (per logement) | avec | Social | National | 2023 | [E33] |
| B | split **67% travaux / 21% foncier / 12% autres** (of a 2 262 €/m² PdR) | Cost-component structure, direct MOA | Su | — | Social collectif | National | **2020** | Éclairages n°25 [E25] |
| C | **Zone A bis 3 400** · B1 2 200 · C <2 000 · nat ~2 325 | PdR by tension zone | **Su** | **AVEC foncier** | Social collectif | by zone | **2020** | [E25] |
| C′ | **Zone A bis +24% / 5y** (record); A bis costs ~**+50% vs Zone A** | PdR growth by zone | Su | avec | Social | by zone | 2019→24 | [E33] |
| D | travaux (construction) **+22% / 4y**; foncier "moderate"; autres +10% (2023) | Component growth | Su | — | Social | National | 2019–23 | [E33] |
| E | **1 340–1 480 €/m² SDP** (standard); up to **~2 000** in Paris/Lyon/Nice; social ~1 120; high-end >3 200 | Construction (build) cost | **SDP** | **HORS foncier** | Private collectif | National/urban | 2024–26 | trade [T1] `[UNVERIFIED – secondary]` |
| F | **RE2025 surcoût 90–150 €/m² (+5–10%)**; implies base collectif ~**1 500–1 800 €/m²** | RE2020/2025 cost impact | (per m²) | hors | collectif | National | **2025** | Rivaton report, gov [RIV] |
| F′ | collectif **+4% to +15%** for jalon 2031; +3% collectif for Bbio−30% | RE2020 cost impact | Shab | hors | collectif | National | 2022–31 | CEREMA [CER] |
| G | sale price IdF new collectif **5 643 €/m²** (Q4-2024); France 5 143 (2025) | **SALE PRICE — not cost** | (sale, HT, hors pkg) | (incl. land+margin) | Private | IdF / FR | 2024–25 | FPI [FPI] — **do not use as cost** |

**Montreuil zonage (load-bearing):** Montreuil (93) is on the **official Zone A bis
commune list** (Annexe 11, Financement du logement social) — Paris + 76 communes of
92/93/94 [Z11]. So the **Zone A bis** social series (rows C, C′) is the right anchor
for Montreuil, not the national average.

---

## 2. Surface-basis adjustment (Su / Shab → the model's `floor_area`)

The parameter multiplies `construction_cost_eur_m2` by **`floor_area` = footprint ×
storeys** (SDP-like, **walls included**) — a *gross* floor measure. The social figures
(rows A–D) are per **surface utile**; the private trade figures (row E) are per **SDP**.
These must be reconciled:

- **Regulatory surface chain** (from the DHUP *Guide de la surface utile* and Carrez/SDP
  references [SU][RATIO]): `Su = Shab + ½ × annexes` ⇒ **Su ≈ 1.08–1.10 × Shab** for
  collectif. And **Shab ≈ 0.92 × SDP** ⇒ **SDP ≈ 1.087 × Shab** [RATIO]. Therefore
  **Su ≈ SDP** for collectif (both ~1.08–1.09 × Shab) — they are close, and much closer
  to each other than either is to Shab.
- **`floor_area` = footprint × storeys** is *gross* (exterior walls + all common
  circulation included), i.e. **SHOB/GFA-like, ~10% larger than SDP/Su** (SDP is measured
  from the *interior* of façade walls and drops several voids; GFA does not).
- **Net adjustment, per-Su → per-floor-area: multiply by ≈ 0.90 (range 0.85–0.95),
  i.e. a ~10% DOWNWARD haircut.** Same total euros spread over a larger (gross) surface
  ⇒ lower €/m². *(The private row-E figures are already per-SDP, so they need only a
  small ~5% haircut to per-floor-area.)*

> This is a definitional scaling, **not** a sourced number; the ~0.90 factor is derived
> from the published Su/Shab/SDP relationships above. It is deliberately smaller than the
> 10–20% haircut the prior pass cited for **habitable** figures, because **surface utile
> is already ~8–10% larger than habitable**, so most of that haircut is already spent.

---

## 3. Social vs private collectif — and which the model should use

- **Social collectif is the well-sourced, authoritative anchor** (CDC/Banque des
  Territoires financing data, 16 800 operations). Its PdR is **avec foncier**, so the
  **travaux** (construction) component must be extracted (row B: ~67% nationally; less in
  A bis where foncier's share is larger).
- **Private/promoteur collectif** construction is **comparable-to-dearer** than social
  (higher finishes, similar structure) — but the only open figures are **trade sources**
  (row E, `[UNVERIFIED – secondary]`). FPI (row G) publishes **sale prices**, not
  construction cost — explicitly excluded (5 643 €/m² is sale, incl. land + developer
  margin + VAT).
- **Which basis for the model?** The model values the **existing stock** — a **mix** of
  social and private, mostly older buildings, on a **replacement-cost** (rebuild-today)
  basis. In a dense Grand Paris core the social-travaux and private-construction costs
  **converge** at ~1 900–2 100 €/m² Su (§4), so a **mid/blended figure anchored on the
  authoritative social series, nudged up slightly toward private**, is the right choice —
  not the cheap social-only floor, not the high-end promoteur ceiling.

---

## 4. Derivation — Montreuil (Zone A bis) collectif construction cost, hors foncier

**Step 1 — Zone A bis PdR (avec foncier, Su), current vintage.**
Éclairages n°25 gives Zone A bis **3 400 €/m² Su in 2020** (row C). Éclairages n°33 gives
Zone A bis **+24% over 5 years** (row C′). Trajectory ⇒ **2023 A bis PdR ≈ 3 700–3 950
€/m² Su** (avec foncier). `[DERIVED — the exact 2023 A bis level was not published in a
form I could read directly; it is reconstructed from the 2020 level + the +24% zone
trend. Treat as ±5%.]`

**Step 2 — strip foncier + other charges → travaux (construction, hors foncier).**
National component split is 67/21/12 (travaux/foncier/autres, row B). In **Zone A bis
the foncier share is much higher** (land scarce/expensive — "record" +24% "essentially
due to rising construction costs" but the *level* of foncier in A bis is far above the
21% national share): plausibly **foncier ~30–40%, travaux ~50–57%, autres ~10–13%**.
⇒ **A bis travaux ≈ 3 800 × 0.53 ≈ 2 015 €/m² Su**, range **~1 900–2 200 €/m² Su**.
- **Cross-check (independent):** national travaux ≈ 0.67 × 2 550 ≈ **1 710 €/m² Su**
  (2023), × a **+15–25% dense-core uplift** (taller structure, underground parking,
  higher standards) ≈ **1 965–2 140 €/m² Su**. **Converges** with the share method →
  **A bis social travaux ≈ 2 000–2 200 €/m² Su** (hors foncier).

**Step 3 — Su → `floor_area` (SP-like) haircut, ×0.90 (§2).**
2 000–2 200 × 0.90 ⇒ **≈ 1 800–1 980 €/m² floor-area** (hors foncier, social collectif).

**Step 4 — private/promoteur cross-check.** Trade sources (row E) put standard private
collectif at 1 340–1 480 €/m² SDP, up to **~2 000 €/m² in attractive cores (Paris/Lyon)**;
the Rivaton report (row F) implies a base collectif ~**1 500–1 800 €/m²** before the
RE2025 +90–150 €/m² increment. For an attractive Grand Paris core, private new collectif
construction ~**1 800–2 200 €/m² SDP** is consistent, **bracketing the social figure from
above**.

**Step 5 — RE2020 vintage.** Current-vintage replacement cost already embeds the
RE2020-2022 baseline (mandatory since 2022); the RE2025 jalon adds only **+5–10%
(90–150 €/m²)** on the forward margin (row F). No large separate uplift needed for a 2025
reference; a small nudge at most.

---

## 5. RECOMMENDATION — Montreuil collectif €/m² (hors foncier, per floor area / SDP-like)

> ### Central: **≈ 1 950 €/m²** floor-area (SP-like), hors foncier.
> ### Uncertainty range: **1 750 – 2 200 €/m²**.

**Reasoning.** Zone A bis **social** collectif *travaux* ≈ 2 000–2 200 €/m² Su, minus the
~10% Su→floor-area haircut → ~1 800–1 980; **private/promoteur** collectif in an
attractive Grand Paris core ≈ 1 800–2 200 €/m² SDP. The two independent anchors bracket
**~1 850–2 050**, and the authoritative-social vs dearer-private mix (the stock the model
values) centres on **~1 950 €/m²**. The low end (~1 750) is a social-leaning / lower
dense-core-uplift reading; the high end (~2 200) is a private/high-finish reading and the
top of the plausible band.

**Comparison to the prior pass and current config:**
- EPTB **individual** IdF = 1 914 €/m² *habitable* → after habitable→floor-area haircut
  (~10–15%) ≈ **1 650–1 750 €/m² floor-area**. The sourced **collectif** figure is
  **~+12–18% above** that — confirming EPTB *understates* Montreuil, exactly as flagged.
- Current config Montreuil = **2 150** — at the **top of my range**, defensible but a
  touch high; my central **1 950** sits between the EPTB individual figure and the current
  guess.
- **Villeurbanne / Grenoble** (ARA cores, less tense than A bis): the same method with
  **Zone A / B1** social levels (row C: B1 ~2 200 €/m² Su PdR in 2020, lower foncier share
  than A bis) lands the collectif construction cost **below** Montreuil's — roughly
  **1 700–1 950 €/m² floor-area** — i.e. close to, or modestly above, the EPTB ARA
  individual figure (~2 065 habitable → ~1 800 floor-area). Collectif uplift is **largest
  for Montreuil**, small-to-nil for the ARA cores. (Villeurbanne/Grenoble not derived in
  full here — flagged for a follow-up if needed.)

---

## 6. What I could and could NOT verify

**Verified (primary URL, read via WebSearch):**
- National social PdR 2 300→2 550 €/m² Su (2019→2023), +11%/4y, 169 200 €/logement,
  16 800 ops, travaux +22% — **Éclairages n°33** [E33].
- Zone levels A bis 3 400 / B1 2 200 / C <2 000 (2020) and the 67/21/12 component split —
  **Éclairages n°25** [E25].
- Zone A bis +24%/5y and ~+50% vs Zone A — [E33].
- Montreuil in **Zone A bis** — official **Annexe 11** [Z11].
- Su/Shab/SDP ratios (Su≈1.08–1.10 Shab; Shab≈0.92 SDP) — DHUP guide + Carrez/SDP refs
  [SU][RATIO].
- RE2025 surcoût 90–150 €/m² (+5–10%) — **Rivaton report**, ecologie.gouv.fr [RIV];
  CEREMA collectif +4–15% (2031) [CER].
- FPI sale prices (5 643 €/m² IdF) — confirmed to be **sale price, not cost** [FPI].

**NOT verified / weak:**
- **Exact 2023–2024 Zone A bis PdR level** — `[DERIVED]` from 2020 (3 400) + the +24%
  zone trend; not published in a directly readable form (BdT/CDC pages 403; open-data
  API 403). ±5%.
- **Zone A bis foncier/travaux split** — the *national* 67/21/12 is sourced (2020, [E25]);
  the *A-bis-specific* foncier share (~30–40%) is a reasoned estimate, cross-checked
  against the national-travaux × dense-core-uplift route, **not** a directly sourced A-bis
  breakdown. This is the single biggest uncertainty in the point estimate.
- **Private/promoteur collectif construction €/m²** — only **trade sources**
  (`[UNVERIFIED – secondary]`, [T1]); no open *institutional* private-collectif
  construction-cost series exists (FPI reports sale prices). Used only as a bounding
  cross-check, not as the primary anchor.
- **Su→floor_area 0.90 factor** — derived from published surface ratios, not a measured
  project figure; range 0.85–0.95.

---

## 7. Sources

- **[E33]** Banque des Territoires (CDC), *Éclairages* n°33, *« Le prix de revient des
  logements sociaux face aux tensions inflationnistes »*, **déc. 2024**. National PdR
  2 300→2 550 €/m² (2019→2023), 169 200 €/logement, 16 800 ops; travaux +22%; Zone A bis
  +24%/5y, ~+50% vs Zone A.
  https://www.banquedesterritoires.fr/eclairages-n-33 ·
  PDF https://www.banquedesterritoires.fr/sites/default/files/2025-01/Exe%20brochure%20Eclairages%2033%20A4%202024%20vdef.pdf ·
  USH relay https://www.union-habitat.org/prix-de-revient-des-logements-sociaux-11-entre-2019-et-2023-ce-que-cache-la-moyenne
  — read via WebSearch (direct fetch 403).
- **[E25]** Banque des Territoires / USH, *Éclairages* n°25, *« Coûts de construction des
  logements sociaux : un prix de revient en hausse modérée »*, **oct. 2021** (2020 data).
  Zone A bis 3 400 €/m² Su · B1 2 200 · C <2 000 · nat ~2 325; split 67% travaux / 21%
  foncier / 12% autres (PdR 2 262 €/m², direct MOA).
  https://www.union-habitat.org/sites/default/files/articles/pdf/2021-11/eclairage-25.pdf
  — read via WebSearch.
- **[Z11]** DHUP, *Annexe 11 – Liste des communes constituant la zone A bis*
  (Financement du logement social). Montreuil (93) listed.
  https://www.financement-logement-social.logement.gouv.fr/annexe-11-liste-des-communes-constituant-la-zone-a-a1255.html ·
  PDF https://www.financement-logement-social.logement.gouv.fr/IMG/pdf/Annexe_11_cle0af75a.pdf
- **[SU]** DHUP, *Guide de la surface utile* (`Su = Shab + ½ annexes`); regulatory basis
  of social-housing €/m² (loyers en surface utile).
  https://www.ecologie.gouv.fr/sites/default/files/documents/DHUP_guide_surface_utile.pdf ·
  https://www.hlm.coop/file/3799/download?token=YlflLhvf
- **[RATIO]** Surface-de-plancher vs surface-habitable references: Shab ≈ 0.92 × SDP;
  collectif circulation ~15–20%; −10% common-area rule.
  https://www.diag68.fr/carrez/surfaces_logement.pdf ·
  https://www.appartement-hipa.fr/surface-de-plancher-et-surface-habitable/
- **[RIV]** R. Rivaton, *Rapport d'évaluation de la RE2020* (mission ministérielle),
  **10 juil. 2025**, ecologie.gouv.fr. RE2025 surcoût 90–150 €/m² (+5–10%); +11%
  investissement à 2035.
  https://www.ecologie.gouv.fr/sites/default/files/documents/10.07.2025_Rapport__Robin_Rivaton_RE2020.pdf ·
  https://www.ecologie.gouv.fr/presse/remise-du-rapport-rivaton-re2020-valerie-letard-ouvre-nouvelle-phase-dajustement
- **[CER]** CEREMA / CSTB RE2020 cost-impact estimates (collectif +4–15% for jalon 2031;
  +3% collectif for Bbio−30%; Untec +7% (2022)).
  https://bati.zepros.fr/actu-generale/impact-re2020-parlons-couts ·
  https://www.batirama.com/article/37464-re2020-le-bbio-30-va-t-il-faire-exploser-les-couts-de-construction.html
- **[FPI]** FPI, *Les chiffres du logement neuf* (T4-2024 / 2025). **Sale prices** — IdF
  collectif 5 643 €/m² (Q4-2024), France 5 143 €/m² (2025). **Not construction cost.**
  https://fpifranceprodcellar.cellar-c2.services.clever-cloud.com/public/media/file/FPIDPObsT42024VDEF.pdf
- **[T1]** Trade/economist sources on private collectif construction €/m² SDP
  (`[UNVERIFIED – secondary]`, indicative only): standard 1 340–1 480 €/m² SDP, up to
  ~2 000 in Paris/Lyon/Nice, social ~1 120, high-end >3 200.
  https://www.renovationettravaux.fr/cout-construction-immeuble ·
  https://www.mbg-construction.fr/combien-coute-la-construction-d-un-immeuble-au-m----_ad46.html ·
  https://cabinetfranckverdelet.com/archives/5990
- **Open-data leads (could not pull — API/HTML 403):** CDC *Coûts et surfaces moyens des
  logements sociaux* https://opendata.caissedesdepots.fr/explore/dataset/constructionrehabilitation_logementsocial_surface_prix/
  · IdF *Financement et coût des logements sociaux construits*
  https://data.smartidf.services/explore/dataset/financement-et-cout-des-logements-sociaux-construits/
  — these carry **region/zone-level PdR + charge-foncière splits** and would let a
  browser-equipped follow-up replace the `[DERIVED]` A-bis level with an exact figure.

---

## 8. One-line recommendation

For **Montreuil** (Zone A bis, collectif-heavy), set the collectif
`construction_cost_eur_m2` to **≈ 1 950 €/m²** (hors foncier, per floor-area / SDP-like),
range **1 750–2 200** — a **~+12–18% uplift** over the EPTB individual-house IdF figure,
anchored on the Éclairages n°33/25 **social** series (Zone A bis, travaux extracted,
Su→floor-area haircut applied) and cross-checked against private/promoteur and RE2020
sources. Apply a **smaller or nil** collectif uplift to the ARA cores (Villeurbanne/
Grenoble), where the individual-house EPTB figure is already high and the zone tension is
lower.
