# Spec 0005 — Three equal-yield replacement scenarios

**Status:** Draft — all decisions taken (D1–D4 2026-10-25, D5–D8 2026-10-26) · **Priority:** P0 (changes what the site models) ·
**Source:** Patrick, 2026-10-25 · **Est. effort:** several PRs over 3–5 working
sessions, plus pipeline reruns on a machine with data access

---

## 1. Problem

The site models one reform: the TFPB moved onto land value, revenue-neutral
inside each commune. This spec is to expand that scope to model a land value tax replacing
existing property taxes **one for one, at equal yield** ("au rendement égal").
we have the following potential nested scenarios:

| # | LVT replaces | Adds to the previous scenario |
|---|---|---|
| **S1** | Taxe foncière (TFPB + TFPNB) + DMTO | (base) |
| **S2** | S1 + IR/IS on real-estate capital gains with optional inclusion of IFI (user-exposed toggle) | the taxes on holding wealth and on gains, with and without IFI |
| **S3** | S2 + IR/IS on rental income | the taxes on rental income, preserving IFI optionality |

For each scenario the site must show: the yield to be replaced (by tax, sourced),
the LVT rate that raises it, who pays more or less, and the effect on land values.

## 2. What changes conceptually

**Three levels of government.** Today's model is one tier: each commune replaces
its own TFPB. The new taxes belong to three different budgets, and each needs a
rate that is neutral for that budget:

| Tier | Taxes replaced | Budget | LVT rate set… |
|---|---|---|---|
| Local | TFPB, TFPNB, communal DMTO surcharge | communes, EPCI, syndicates | per commune (as today) |
| Departmental | departmental DMTO | départements | per département |
| National | IFI, IR/IS on gains and rents, frais d'assiette | State (+ Sécurité sociale for the 17,2 % levies, see D2) | one national rate |

The national tier creates **transfers between territories** (Paris and the
Hauts-de-Seine pay a large share of IFI today; a national land rate charges every
commune by land value). The site must show these transfers, not hide them in the
commune totals.

**Land values move, and not equally across scenarios.** Answering Patrick's
2026-10-25 question: what drives the land price is the tax attached to the land.
An equal-yield swap lowers land values whenever it moves tax onto land:
- TF building share → land: lowers land values (offset by lower tax on buildings)
  but does not lower property values **on average**. Per property it does:
  land-heavy properties (houses on large plots) lose value, building-heavy ones
  (flats) gain. Modelled per parcel, see §4.5.
- DMTO → recurrent land tax: roughly neutral in aggregate, because DMTO is already
  capitalised into prices; only timing changes. The incidence of the DMTO paid on
  the building share is uncertain and should be shown as an assumption.
- IFI, IR/IS on gains and rents → land: lowers land values. These taxes fall on
  some owners or on income; the replacement falls on every plot. Partly offset,
  for rented and traded property, by the capitalisation of the taxes removed
  (removing IR/PS on rents raises the net return of rented property; removing
  the tax on gains raises the value of property that is sold). Owner-occupied
  property gets no offset. Tenants' incomes do not change, so little reaches
  rents through household income.

For each change, the expected effect on GDP is **flagged, not modelled** (§4.6):
direction and, where the literature supports it, a range for the long-run
*level* of GDP, with a link to a research note on a separate page.

The model is static (values unchanged), so the site shows an **indicative
capitalisation** per scenario (§4.5) rather than claiming values hold.

## 3. Yields to replace

Sources disagree by scope (housing only vs all real estate) and year. Starting
figures, all to be re-verified live per CLAUDE.md, with the additional use of adversarial agents and Gemini Argon review before coding against them:

| Tax | Yield | Year | Source | Scope note |
|---|---|---|---|---|
| TFPB | > 40 Md€ (communes alone) | 2025 | DGCL, BIS 210 (May 2026) | all premises; exact total incl. EPCI from REI 2025 national file |
| TFPB, housing only | 25,5 / 30,5 Md€ | 2022 / 2024 | CPO 2023 / Compte du logement 2024 | housing only, **not** our scope |
| TFPNB | to measure | 2025 | REI 2025 | |
| DMTO | 13,0 (dép.) + 3,1 (communes) = 16,1 Md€ | 2023 | DGCL, BIS 190 (Nov 2024) | cyclical: ~16,7 Md€ (dép.) in 2022, lower in 2024 |
| IFI | 1,9 / 2,2 / 2,3 Md€ | 2023 / 2024 / 2025 | DGFiP Statistiques n° 23 (Apr 2024); DGFiP via press for 2024–25 | Compte du logement shows 2,64 for 2024: reconcile |
| IR + PS on real-estate gains (individuals) | avg 3,5 Md€; 3,6 (2023); 2,8 (2024) | 2017–2024 | Cour des comptes, 25 Nov 2025 | CPO gives 2,8 for 2022 vs Cour's 4,7: scope differs, reconcile |
| IR on rental income | 4,2 Md€ | 2022 | CPO 2023; IGF/Le Meur, May 2024 | furnished lets (BIC) not separated |
| PS on rental income | 2,4 Md€ | 2022 | CPO 2023 | |
| IR + PS on rental income, housing | 8,9 Md€ | 2024 | Compte du logement 2024 | housing only, includes ? — reconcile with the two lines above |
| IS on companies' real-estate gains and rents | no public figure found | | | see D3 |

**Indicative national rates** (to orient, not to publish): against INSEE's built
land at end-2023 (6 346 Md€, Insee Première n° 2028), S1 ≈ 56+ Md€ → ~0,9 % of
land value a year; S2 ≈ +5–6 Md€ → ~1,0 %; S3 ≈ +6,6 Md€ → ~1,1 %. Non-built land
would lower these rates.

Rule for the build: one table `yields.py` (value, year, source URL, scope, status
verified/estimated), one research note `docs/research/yields-2026.md` explaining
each reconciliation, and the site displays the same table. The first major element on the page should be a graphical representation for pedagogical purposes.

## 4. Method

### 4.1 Rates
- **Local tier:** as today, per commune, now including TFPNB and the communal DMTO
  surcharge in the product to replace.
- **Departmental tier:** rate_dép = departmental DMTO / taxable land value of the
  département. Our panel does not cover whole départements, so the denominator
  comes from §4.2.
- **National tier:** rate_nat = national yield (S2, S3 taxes) / national taxable
  land base (§4.2).

Each modelled parcel's new bill = land value × (local + departmental + national rate).

### 4.2 Land base outside the panel
The panel is 188 communes; départements and France are not modelled parcel by
parcel. This is overcome by using **INSEE national accounts** for the national base (6 346 Md€ built land,
  plus non-built land from the same accounts), scaled to départements by DVF price
  levels; with a published consistency check: panel land values against INSEE's land/housing
  ratios.

### 4.3 Exclusions
Exempt public land stays exempt (spec 0003). Agricultural and natural land is in
the departmental and national base at SAFER values (D6), with the effect on farm
land shown separately.

### 4.4 Who pays today, per parcel
Needed for the distribution charts. Quality differs a lot by tax; each line gets
a quality flag on the site.

| Tax | Attribution to parcels | Data | Quality |
|---|---|---|---|
| TFPB | done (REI split + floor area) | REI | medium |
| TFPNB | non-built parcels, by land class | REI, GPU, SAFER | medium |
| DMTO | value × rate × annual turnover probability (by type and IRIS, from DVF sales / stock): an annualised expected DMTO | DVF, DGCL totals to validate | medium |
| IFI | no parcel attribution possible (owner wealth unknown). Commune total from DGFiP (communes > 20 000 inhabitants with > 50 taxpayers), shown at commune level only | data.gouv « IFI par collectivité » | aggregate only |
| Gains (IR+PS) | non-main-residence dwellings × turnover × gain proxy | INSEE census (tenure, second homes) by IRIS, DVF | low: aggregate only unless D4 says otherwise |
| Rental income (IR+PS) | privately rented dwellings × local rent × effective rate; social housing pays none | INSEE census tenure by IRIS; Carte des loyers (MTE/ANIL); effective rate from DGFiP aggregates | medium-low |

Consequence to state on the site: S3 moves tax from landlords onto
owner-occupiers (who pay no tax on the rent they don't pay themselves). The
distribution must be shown **by tenure** (owner-occupier, private landlord,
social landlord), not only by property type and income quintile.

Rent pass-through of the removed taxes on rental income is a **parameter with
a range**, not an assumption baked in. The French evidence usually cited is
contested: Fack (CEPREMAP 2005) finds 50–80 % of housing allowances absorbed by
rents; IGEDD (2019) attributes that mainly to an omitted logarithm and
composition effects, and its August 2025 report says the effect "remains to be
assessed". Those studies also measure a demand subsidy to tenants, not a tax on
landlords. House view, from `docs/research/apl-rent-incidence.md`:
- Fack's 0,78 is the top of her own range; her controlled difference-in-differences
  estimates are 0,3–0,45 and imprecise. IGEDD's "omitted logarithm" barely moves
  the raw estimate (recomputed); its stronger point is omitted structure effects.
  Best reading for allowances: 0,3–0,6 in the medium run.
- In a competitive market, the share of a landlord tax passed to rents is one
  minus the share of a tenant subsidy captured by landlords. High allowance
  capture therefore implies **low** pass-through of landlord taxes, not high.
- Parameter for the removed taxes on rental income: years 1–3 **0,1** (0–0,2,
  rents are sticky under French lease law); 10 years and more **0,5**
  (0,25–0,75). The new land tax itself: 0.

### 4.5 Capitalisation (indicative)
Per scenario: Δ = change in the annual tax attached to land, nationally and per
commune. Indicative change in land value = −Δ / r, with r = 3 % and 4 % real
(range shown), and the DMTO incidence stated as an assumption (§2). Labelled as
a static upper bound: more construction partly offsets it. Capitalisation rate:
100 % central (full for the Danish land tax, Høj et al. 2018), 60 % sensitivity
(`docs/research/dynamic-effects.md` §5).

The same arithmetic per parcel on the change in *total* tax on the property gives
the indicative change in **property value** (−Δ_property / r), reported by
property type, tenure and income quintile. It costs nothing beyond the per-parcel
results already computed, so it is modelled rather than only flagged in text.

### 4.6 Static model, dynamic effects flagged
"Rendement égal" means equal at today's bases: no behavioural response. The site
stays static, but each scenario **flags** its expected dynamic effects, each with
a direction, the mechanism, and a range where the literature gives one:
- transactions and mobility rise when DMTO goes: direction established abroad
  (about −6 % to −14 % of sales per point of duty); the only French study (2014
  rise) finds a timing effect only. No range for full removal;
- construction: direction favourable, evidence weak, response muted by French
  planning rules. No range;
- GDP: the OECD ranking (Johansson et al. 2008) gives the direction, but its
  robustness is contested (Xing 2012; Baiardi et al. 2019) and it concerns moves
  away from income taxes, not S1's swap between property taxes. Direction only;
- rents: per the pass-through range in §4.4;
- property values: redistributed rather than reduced on average (§2), by land
  share in S1 and from owner-occupiers to landlords and investors in S2–S3.
Evidence, grades and proposed site wording: `docs/research/dynamic-effects.md`.
Quantifying them belongs to the budget simulator, using its elasticities.

## 5. Site

- Scenario selector (S1/S2/S3) on Résultats, kept in the URL (`?scenario=2`,
  works with `?commune=`).
- "Rendement à remplacer" panel: the §3 table for the chosen scenario, sources and
  years, and the resulting local / departmental / national rates.
- Per commune: new LVT vs taxes removed, split by tier; distribution by property
  type, income quintile and (S3) tenure, with each tax's attribution quality.
- National page: inter-territorial transfers from the national tier.
- Home, Sceptiques, Exonérations: text per scenario, numbers computed from the
  payloads as in PR #40 (`impactSummary`).
- Methodology: §4 in full, the yield reconciliations, the capitalisation caveat.

## 6. Data sources to verify live before coding

REI 2025 national file (TFPB, TFPNB; communal DMTO if present) · DGCL DMTO by
département (BIS 190 series) · OFGL commune accounts (communal DMTO surcharge,
c/7381) · DGFiP « IFI par collectivité territoriale » (data.gouv) · Cour des
comptes, *L'imposition des plus-values immobilières des particuliers* (Nov 2025) ·
CPO, *Pour une fiscalité du logement plus cohérente* (Dec 2023) · IGF/Le Meur,
*Propositions de réforme de la fiscalité locative* (May 2024) · SDES, *Compte du
logement 2024* · INSEE census housing by IRIS (tenure, second homes) · Carte des
loyers (MTE/ANIL) · INSEE, *Le patrimoine économique national en 2023* (Dec 2024).

## 7. Phasing

| PR | Content | Needs pipeline rerun? |
|---|---|---|
| 1 | `yields.py` + research note + site "Rendement" panel and indicative national rates per scenario | no |
| 2 | S1 local tier: TFPNB + communal DMTO in the product; DMTO attribution from DVF | yes (all 188 communes) |
| 3 | Departmental tier + land base (§4.2) + capitalisation output | yes |
| 4 | S2: national tier, IFI at commune level, gains attribution (per D4) | yes |
| 5 | S3: tenure + rents, distribution by tenure | yes |
| 6 | Scenario selector across the site, text per scenario | no |

Reruns need live access to data.gouv / IGN / INSEE / OFGL, which the cloud
sandbox does not have: they run on Patrick's machine (`PYTHONUTF8=1` on Windows)
or in a CI job with network access. Economic parameter choices (r, turnover,
effective rates, DMTO incidence range) go through the usual Gemini review.

## 8. Decisions

| # | Question | Decision / recommendation |
|---|---|---|
| D1 | Reference year for cyclical yields (DMTO, gains) | **Decided:** average of the last 5 available years; latest year shown as a sensitivity |
| D2 | Include the 17,2 % social levies on gains and rents? (they fund Sécurité sociale, so the LVT would partly fund the PLFSS) | **Decided:** include, on a separate line, consistent with the budget simulator's PLF+PLFSS scope |
| D3 | IS on companies' real-estate gains and rents: no public figure found | **Decided:** exclude for now and say so on the site; revisit if a source turns up |
| D4 | S2/S3 distribution: parcel level (weak attribution for gains) or aggregate first | **Decided:** aggregate yields, rates, transfers and capitalisation first (PR 1, 3); parcel-level rental attribution in PR 5; gains stay aggregate |
| D5 | Land base outside the panel | **Decided:** INSEE national accounts, with a published consistency check |
| D6 | Agricultural and natural land in the national and departmental tiers | **Decided:** include in the base at SAFER values; show the effect on farm land separately |
| D7 | Furnished lets (BIC/LMNP) in "rental income" | **Decided:** include if a yield source is found; otherwise flag as missing |
| D8 | Commune-level DMTO: DVF-based estimate or OFGL accounts | **Decided (most accurate per question):** yields from the **accounts** (DGCL by département; communal receipts from OFGL/DGFiP commune accounts, availability to verify live; communes under 5 000 inhabitants receive theirs through the departmental equalisation fund, so their receipts are not their own transactions); **who pays** from **DVF** (transactions are where the tax falls). Fallback for yields where accounts are missing: DVF × the communal rate (1,20 %) |

## 9. Risks

- Yields differ across sources by up to ~70 % (gains 2022: 2,8 vs 4,7 Md€). One
  reconciled table, published with its choices, is a precondition.
- IFI cannot be attributed to parcels; any parcel-level picture of S2 understates
  how much the top of the distribution gains.
- The national tier's transfers (Paris, Hauts-de-Seine) will dominate the headline;
  present them deliberately.
- Alsace-Moselle has no DVF: DMTO estimates fail there (Mulhouse already excluded).
- Scope drift into dynamic effects: keep them in the budget simulator.
