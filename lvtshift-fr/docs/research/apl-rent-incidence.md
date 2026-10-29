# Housing allowances (APL/ALS/ALF) and rents: evidence review and house view

Research note for the LVTShift "Pour une terre productive" site (spec 0005, replacement scenarios). Date: 26 October 2026.

Provenance tags used throughout:
- **[V]**: verified by me from the primary source (full text or the author's own abstract, fetched in this session).
- **[S]**: taken from a secondary source (named) and not checked against the primary.
- **[I]**: my own inference or calculation.

One caveat applies to every **[V]** tag on a full text: some PDFs (Fack 2005 working paper, Fack 2005 *Économie et Statistique*, IGEDD 2025, Grislain-Letrémy & Trevien 2014 and 2022) were read through a fetch tool that returns extracted text, not the raw file. I cross-checked the key Fack numbers in two separate extractions and against the separately published *Économie et Statistique* version, and they matched. Even so, before anything is quoted on the public site, someone should open the PDFs and check the tables directly.

---

## 1. Summary (house view)

1. **Demand subsidies to tenants (APL type):** central pass-through to rents of **0.45** (range **0.2 to 0.8**) at a 3 to 8 year horizon. The figure is higher in tight markets and small units in the first years, and lower once supply responds. Fack's widely quoted "50 to 80 %" is the top of her own range and is not robust. The IGEDD null result is not robust either: it is an absence of evidence, not a precise zero.
2. **What the site needs (a change in taxes on landlords' rental income, passed into rents):** **short run (1 to 3 years) 0.10 (range 0 to 0.2); 5 years 0.3 (0.1 to 0.5); long run (10+ years) 0.5 (range 0.25 to 0.75)**. The share of the rental-income tax that falls on land rent is capitalised into prices, never passed into rents.
3. **The APL evidence transfers, but with the opposite sign of what is often assumed.** In a competitive market, a subsidy to tenants and a tax on landlords are passed through in complementary proportions: π_subsidy = ε_D/(ε_D+ε_S) and π_tax = ε_S/(ε_D+ε_S). High APL capture by landlords therefore means *inelastic* supply, and so *low* pass-through of landlord taxes to rents. "French APL studies show rents are very elastic" is therefore not an argument that cutting landlords' taxes would lower rents a lot. It argues the opposite.
4. The biggest uncertainties are the long-run elasticity of rental supply (new building plus switching between owner-occupation and letting), the land share of rental value, and French rent regulation, which makes short-run pass-through close to zero for sitting tenants in either direction.
5. Fack (2005/2006) and Friggit (IGEDD 2019/2025) cannot be fully adjudicated without the ENL (Enquête Logement) microdata. On the published numbers, the "omitted logarithm" by itself barely moves Fack's raw estimate. The real issue is which structure controls are included.

---

## 2. Studies assessed

Credibility: **H** = clean identification, transparent, replicated or published in a strong venue. **M** = plausible design with notable threats. **L** = weak identification or no estimate.

### 2a. Demand subsidies (housing allowances / vouchers) and rents

| Study | Data | Method | Estimate (rent € per € of subsidy unless stated) | Cred. | Notes / provenance |
|---|---|---|---|---|---|
| **Fack (2005) WP CEPREMAP 0516; Économie et Statistique 381-382 (2005); Labour Economics 13(6) 2006** | INSEE Enquêtes Logement (ENL) 1973 to 2002, private-sector renters; difference-in-differences N=4,476, triple difference N=9,635 | 1991 to 1993 "bouclage" extension of ALS. Treated = 1st income quartile of private renters, control = 2nd quartile. IV/Wald on **rent per m² in levels** | No controls: DD 0.94 (0.20), TD 1.33 (0.37). **With controls: DD 0.45 (0.18), TD 0.78 (0.31)**. Excluding students: DD 0.39 (0.24), TD 1.02 (0.52). Comfort-corrected: DD 0.29 (0.25), TD 0.76 (0.40). By zone: high-student DD 0.58 (0.32), low-student DD 0.10 (0.37) | M– | [V] tables from the WP and E&S versions. Controls cover only family type, urban unit × region and age of reference person: no surface, building age or comfort (except Table 7), and no occupancy duration (fn. 8 says adding it "ne change presque pas les résultats"). Headline 0.78 = TD with controls. [V] Labour Econ abstract: "78 cents". See section 3. |
| **Laferrère & Le Blanc (2002, E&S 351; 2004, JHE 13(1) 36–67)** | ENL, including panel of dwellings | Natural experiment (1992 to 1994 extension) plus dwelling panel: rent growth when a unit switches to "assisted" | Pure rent increase exists, even at equal quality. **Authors state they cannot measure the effect on the overall rent level** | M (sign), L (size) | [V] E&S abstract via RePEc. Full text not reachable (Persée blocks automated fetching; JHE is paywalled). [S] IGEDD 2025: authors "ne concluent pas quant à son ampleur". |
| **Grislain-Letrémy & Trevien (2014, INSEE G2014/08; INSEE Analyses 19)** | Enquête Loyers et charges 2005 to 2012; 1,638 dwellings, 63 agglomerations of 50k to 200k inhabitants | Fuzzy geographic regression discontinuity: APL zone II vs III at the 100,000-inhabitant threshold; IV with first-stage F = 125 | Log rent/m²: **+5.3 % (SE 1.9 pp; 95 % CI 1.6 to 8.9 %)**, about **€25/month**, against a subsidy gap of **€20 to 30/month**. Authors state their method "ne permet pas de calculer la part de l'aide absorbée". Effect also for predicted non-low-income dwellings (+4.5 %) | M | [V]. [I] Crude per-recipient ratio about 0.8 to 1.25. Applied to all tenants while only about 40 to 50 % receive APL, aggregate rent increases would exceed outlays, which requires near-zero supply elasticity or confounding at the 100k threshold. Treat this as an upper-side estimate. |
| **Grislain-Letrémy & Trevien (2022, Banque de France WP 886; BdF Bloc-notes 302, 2023)** | Loyers et charges + ENL 1984 to 2016; 3,967 dwellings, 60 agglomerations | Same regression discontinuity, by period | Zone II effect on log rent/m²: 1984–94 0.038 (not significant); **1995–99 0.074**; 2000–08 0.058; 2009–16 0.05. Overall "+5 %", about €20 to 25 on a €454 average rent; subsidy gap "approximately 15 to 40 €/month". More one-room units built; no detectable effect on quality | M | [V]. Key qualitative result: in small dwellings, rent effects faded after 1999 as supply (new studios) responded. Large dwellings stayed inelastic. [I] Per-recipient ratio roughly 0.5 to 1.7: imprecise. |
| **IGEDD/CGEDD, Friggit (2015, 2019, 2020, 2022, 2025)** | ENL 1973 to 2013 (2019); CAF ALS/ALF beneficiary file at 31/12/2018 (2020); student reform 1999–2001 (2015) | Structure-effect decomposition of low-income rent growth; histogram "bunching" test at the rent ceiling (2020); before/after for students (2015) | No precise estimate. 2019: rent "surcroissance" of low-income tenants almost entirely due to structure effects (size, quality, location, occupancy duration). 2020: no bunching below the rent ceiling. 2015: about €40 aid cut, no significant rent fall. 2025: the effect is "tout à fait possible, et même probable" but its size "reste à évaluer" | L–M | [V] for the 2020 note and the 2025 report (fetched); [S] for 2015/2019/2022 (summaries on the IGEDD page and in the 2025 report). **I could not locate the full 2019 report (007987-03).** The 2020 bunching test addresses only the marginal (rent-indexed) part of the formula, not the general demand shift. See section 3. |
| **Gibbons & Manning (2006, J Public Econ 90(4–5))** | Two UK datasets, mid-1990s | DD on 1996–97 cuts to maximum Housing Benefit for new claimants | Benefit receipt −10 to 15 %, rents −6 to 11 %; **landlords bore 60 % to two-thirds** of the cut | H– | [V] LSE eprint abstract. Datasets disagree on magnitude; supports a matching (bargaining) model over perfect competition. |
| **Beatty, Cole et al. (2014)** (UK LHA reforms) | UK | Reform evaluation | Tenants bore about 89 to 90 % of the cut (landlords about 10 %) | M | [S] IGEDD 2025 and Terra Nova 2017; not verified. |
| **Brewer, Brown et al. (2019)** (UK LHA) | UK | Reform evaluation | Heterogeneous; no single figure | – | [S] IGEDD 2025. |
| **Collinson & Ganong (2018, AEJ: Policy 10(2) 62–89)** | US Housing Choice Voucher administrative data | Changes in voucher rent ceilings (FMR rebenchmarking; Dallas ZIP-level ceilings) | Rents **+$0.46** per $1 of ceiling (rebenchmarking); +$0.47 (2001 FMR change); +$0.57 (Dallas). Little quality change | H | [V] abstract (AEA); point estimates [S] UCLA Lewis Center summary quoting the paper. A ceiling the landlord observes makes capture partly a bargaining effect. |
| **Eriksen & Ross (2015, AEJ: Policy 7(3) 154–176)** | American Housing Survey unit panel | Voucher supply expansion | **No overall rent effect**; increases for some units, largest where supply is inelastic | H– | [V] APPAM abstract; no numeric estimate retrieved. |
| **Susin (2002)** (US) | US | Cross-metro | Vouchers raised low-income rents, including for non-recipients; total rent rise exceeded the subsidy (>100 %) | L–M | [S] INSEE Analyses 19; IGEDD 2025 (criticised for omitted quality controls). |
| **Rydell, Neels & Barnett (1982)** (US Housing Assistance Supply Experiment) | 2 US metros with open enrolment | Randomised supply experiment | "only small price increases, even in the short run" | H (slack markets only) | [S] IGEDD 2025. |
| **Kangasharju (2010, Scand J Econ 112(3) 595–617)** | Finland, about 12,000 renter households | 2002 reform as instrument | **0.60 to 0.70** private sector; 0 in municipal sector | M+ | [V] RePEc abstract. |
| **Virén (2013, Empirical Econ 44(3) 1497–1518)** | Finland, about 50,000 recipient households 2000–08, plus cross-sections | Panel | **about 1/3 ("conservative"), possibly up to 0.5** | M | [V] RePEc abstract. |
| **Hyslop & Rea (2019, JHE 46)** | New Zealand administrative data | 2005 Accommodation Supplement boundary discontinuity (Auckland) | Support +$6.80/week, rent +$2.44, so **about 0.36** | H– | [V] RePEc abstract. |
| **Sayag & Zussman (2015)** (Israel) | – | – | "Marked" effect (IGEDD groups C&G, Kangasharju, S&Z and Virén at 30 to 80 %) | ? | [S] IGEDD 2025 only. |

### 2b. Taxes on landlords / rental property and rents (the parameter the site needs)

| Study | Setting | Method | Estimate (share of the tax passed into rents) | Cred. | Notes / provenance |
|---|---|---|---|---|---|
| **Löffler & Siegloch (IZA DP 14195, 2021; later versions)** | Germany, about 5,200 municipal Grundsteuer B reforms; ImmobilienScout24 rental ads 2008–15 | Event study plus IV | **About 1/3 within 2 years; full pass-through to gross rents from year 3**; lower where supply is inelastic | H (for Germany) | [V] DP text. **Transfer caveat [V]/[I]:** German Grundsteuer is legally recoverable from tenants as a service charge (§2 BetrKV). French taxe foncière is *not* recoverable; only TEOM is (décret 87-713). The German result is therefore partly mechanical: an upper bound for France, not a central value. |
| **Carroll & Yinger (1994, NTJ 47(2))** | Boston-area municipalities | Cross-community, with tenant mobility | Tenants bear **about $0.15 per $1** of local property tax differential (range 0.10 to 0.25); landlords about 85 % | M | [S] Yinger's course notes and a progress.org summary quoting pp. 308–309; abstract [V]. Measures *local differentials*, which under the "new view" fall on immobile factors. A lower bound for a nationwide change. |
| **Schwegman & Yinger (2020, US Census CES WP 20-43)** | New York State homestead tax option | Policy variation | **About 14 %** shifted to renters; notes earlier studies found >60 % | M | [V] RePEc abstract. |
| **Bono & Trannoy (2019, Économie et Statistique 507–508)** | France, Scellier rental-investment income-tax relief; land sale prices (BNDP) 2004–10 | Border DD, zone B2 vs adjacent zone C | Building-land prices **+8 % in year 1, +9 to 10 % after 2 years** (about €7 to 9/m²) | M+ | [V]. A tax break to landlords was **capitalised into land prices**. The paper does not measure rents. Directly relevant: French landlord tax changes show up in land values. |
| Theory: Mieszkowski/Zodrow "new view"; standard partial-equilibrium incidence | – | – | National tax on capital returns borne by capital in general. A sector-specific tax on rental housing is passed to tenants in the long run only through the elastic factor (structures, plus switching between owning and letting). Land-rent share is capitalised | – | [I] |

---

## 3. The Fack vs IGEDD dispute

### 3.1 What Fack did (verified from the WP and E&S full text)

- **Identification.** The 1991 to 1993 "bouclage" extended ALS to all low-income households regardless of family status: first Île-de-France (1991), then large cities (1992), then nationwide (1993). Treated group: bottom income quartile of private-sector renters. Control: second quartile. ENL waves 1984, 1988, 1996 and 2002 (1992 excluded as mid-rollout).
- **Specification.** Second stage L_it = α + β·Q1 + γ·post + Σδ_j X_ij + θ·Aide_it + ε, with L = **annual rent per m² in constant 2002 euros, in levels**. Aide (allowance per m²) is instrumented by Q1×post. θ is "euros of rent per euro of allowance".
- **Raw Wald (Table 1, 1988 vs 1996).** Rent/m² Q1 64.1 → 90.2; Q2 67.8 → 79.0; DD = 14.9. Allowance/m² DD = 15.8. θ = 0.94.
- **The "50 % to 80 %" headline mixes two different ratios** ([V] E&S text; [I] interpretation):
  - **78 %** = θ (TD with controls), described by the author as "sans doute l'estimation la plus satisfaisante". This is the share of each euro of allowance absorbed by rent.
  - **58 %** = 0.78 × 22.2 / 29.9, i.e. the share of Q1's *rent increase* 1988–2002 attributable to allowances. It is **not** a share of allowances absorbed.
  - So the abstract's "50 % à 80 % des allocations perçues absorbés" is loose. The only allowance-absorption estimates in the paper are the θs, which run from 0.10 to 1.42 depending on specification.
- **Fack's own controlled DD estimates are much lower than the headline:** 0.45 (95 % CI about 0.10 to 0.80); excluding students 0.39 (about −0.08 to 0.86; the table's "**" corresponds to a 10 % test by its own legend); comfort-corrected 0.29 (about −0.20 to 0.78). The 0.78 relies on the triple difference, which extrapolates the Q1–Q2 trend gap from 1984–88 and 1996–2002. That assumption is shakier than the DD, because 1996–2002 is itself a post-reform adjustment period.

### 3.2 What IGEDD alleges

- [V] IGEDD 2025 (Friggit, report 007987-04, §2.2.2, pp. 14–15): the study "souffre d'erreurs méthodologiques qui suffisent à en invalider le résultat". The two main errors:
  1. the structure correction is "linéaire appliqué au loyer et non à son logarithme ou à une autre forme fonctionnelle du loyer" (log or Box-Cox would give "une bien meilleure approximation");
  2. some structure effects are omitted.
- [S] IGEDD summary page of the 2019 report (007987-03): low-income rent growth 1984–2013 is "almost entirely due to structure effects (size, quality, location, length of occupancy)". Any bouclage effect was spread evenly across income, age and dwelling size. The 2022 addendum says shorter occupancy durations explain any overinflation of small Paris-region dwellings.
- [V] **Neither the 2025 report nor the summary page gives a corrected estimate.** I could not find the 2019 report itself online (only its errata sheet), so I cannot check whether a log re-estimate of Fack's model was ever produced.

### 3.3 Does the "omitted logarithm" critique hold? Recalculation and bound

**(a) On the published group means, the log/level choice is immaterial** [I]:
- Level DD: 14.9 €/m², so θ = 14.9/15.8 = **0.94**.
- Log DD: ln(90.2/64.1) − ln(79.0/67.8) = 0.342 − 0.153 = **0.189 log points**. Converted at Q1's base, the counterfactual Q1 1996 rent = 64.1 × 79.0/67.8 = 74.7, so the excess = 15.5 €/m² and θ = **0.98**.
- The reason: Q1 and Q2 started at almost the same rent level (64.1 vs 67.8 €/m²). Additive and multiplicative trends therefore coincide. **A log transform by itself cannot overturn the raw result.**

**(b) The critique can only bite through the covariates**, i.e. through what the structure correction includes and how. Here IGEDD's second point (omitted structure effects) is the stronger one [V/I]:
- Fack's controls exclude surface, building age, comfort (except Table 7) and occupancy duration.
- The dependent variable is rent per m², which is strongly convex in surface (studios cost more per m²).
- If the reform drew students and young singles into Q1, then Q1's mix shifted toward small, recently let units. That raises rent/m² with no change in price for a given dwelling.

**(c) Bound on the size-composition bias** [I]. Assume the elasticity of rent/m² with respect to surface is −0.3 to −0.5. That range is a plausible French hedonic value, assumed here and not taken from the ENL. A relative fall in Q1 mean surface of X then biases the log DD by 0.3X to 0.5X:

| Relative fall in Q1 surface vs Q2, 1988–96 | Bias (log points) | Share of raw 0.189 effect |
|---|---|---|
| 10 % | 0.03 to 0.05 | 16 to 26 % |
| 20 % | 0.06 to 0.10 | 32 to 53 % |
| 30 % | 0.09 to 0.15 | 48 to 79 % |

Surface composition alone would need a very large relative shift (30 % or more) to erase the effect. Combined with comfort (Fack's own Table 7 already cuts the DD to 0.29) and shorter occupancy (new leases are priced at market, sitting tenants are indexed), a near-zero result is *possible* but not demonstrated.

- Fack's fn. 8 says occupancy duration "ne change presque pas les résultats". IGEDD 2022 says it explains the overinflation. These claims conflict and cannot be adjudicated without the microdata.
- ENL microdata are, to my knowledge, distributed to researchers through Réseau Quetelet/Progedo or CASD (not verified here). They were not accessible in this session.

**(d) Threats to IGEDD's null** [I]:
1. **Bad controls.** If the reform itself caused shorter tenures (new household formation, more moves), then controlling for occupancy duration absorbs part of the treatment effect. New leases are exactly where a demand shock shows up first.
2. **Spillovers to the control group.** A subsidy-driven rise in market rents for small units also hits Q2 tenants in the same segment. Grislain-Letrémy & Trevien find effects on non-recipients. Within-market DD (Fack and IGEDD alike) then biases *toward zero*.
3. **The 2020 bunching test is the wrong test for the main channel.** It detects landlords exploiting the rent-indexed part of the schedule. But about 90 % of private rents are above the ceiling ([S] IGAS 2012, via Terra Nova 2017), where APL works as a lump sum. Absence of bunching says nothing about the aggregate demand shift.
4. **The 2015 student test is about a cut,** and rents are sticky downward under French lease law. A null is expected even if increases are passed through.
5. **IGEDD 2025 criticises Grislain-Letrémy & Trevien for not reporting R².** R² is irrelevant to the validity of an IV/RD causal estimate. The stronger critique would be confounding at the 100k threshold, which the report does not make.

**(e) Verdict** [I]:
- Fack's headline 0.78 (and especially the "50 to 80 %" framing) overstates what her own design supports. Her cleaner DD-with-controls estimates are about 0.3 to 0.45, imprecise (95 % CIs reach roughly 0 to 0.8), and exposed to composition bias.
- IGEDD is right that the result is fragile and that structure effects matter. It is wrong (or at least unsupported) to say that the logarithm is the decisive error, and it has not produced a credible alternative estimate.
- Independent French evidence (Grislain-Letrémy & Trevien, a different design and different data) finds a positive effect of a similar order per recipient, fading in small units once supply responds.
- **A positive pass-through of roughly 0.3 to 0.6 in the medium run is the best reading of the French evidence. Neither zero nor 0.8 is well supported.**

---

## 4. Transfer to the site's parameter (landlord rental-income taxes and rents)

**4.1 The complementarity result** [I, standard incidence theory]. Take one rental market (competitive, per-unit, same horizon), with ε_D the absolute price elasticity of rental demand and ε_S the elasticity of rental supply:
- a subsidy to tenants raises rents by π_sub = ε_D/(ε_D+ε_S) per euro;
- a tax on landlords raises rents by π_tax = ε_S/(ε_D+ε_S) per euro;
- **so π_tax = 1 − π_sub.**

| APL-type estimate | Implied landlord-tax pass-through |
|---|---|
| Fack 0.78 | 0.22 |
| Gibbons & Manning 0.6 to 0.66 | 0.34 to 0.4 |
| Kangasharju 0.6 to 0.7 | 0.3 to 0.4 |
| Collinson & Ganong 0.46 | 0.54 |
| Hyslop & Rea 0.36 | 0.64 |
| Virén 0.33 to 0.5 | 0.5 to 0.67 |
| Eriksen & Ross about 0 | about 1 |

**The "high" APL studies are evidence that landlords' taxes are *not* largely passed to tenants.**

**4.2 Why the mapping is only approximate** [I]:
1. **Bargaining and salience.** Part of measured APL capture is non-competitive: tiers-payant, a landlord who observes the benefit, matching frictions (Gibbons & Manning favour a matching model). That inflates π_sub without implying low ε_S. **1 − π_sub is therefore a lower bound on π_tax.**
2. **Segment vs market.** APL shifts demand in the low-rent, small-unit segment. A rental-income tax hits all let dwellings. Segment-level ε_S (filtering, conversions) can differ from market-level ε_S.
3. **Land rent is never shiftable.** The rental-income tax falls on net rent = return on structure capital + land rent. In the long run only the structure share is shifted through ordinary supply. The land share is capitalised into prices (consistent with Bono & Trannoy's Scellier result). This caps long-run π_tax at roughly the non-land share of value, which is lowest in Paris and tight zones. The land share of French residential value is commonly put at around half nationally and much higher in Paris; that is an order of magnitude I have not verified here, and it should be taken from the site's own INSEE patrimoine data.
4. **The tenure margin pushes the other way.** Owner-occupiers pay no tax on imputed rent, so a landlord-specific tax can be escaped by selling to owner-occupiers. This makes rental supply more elastic than total housing supply and lets some even of the land-rent component reach rents, for tenants who cannot buy (credit-constrained households). This is why the long-run upper bound is about 0.75 and not just the structure share.
5. **French rent regulation makes the short run asymmetric and sticky.**
   - Sitting tenants: increases capped at IRL (loi 1989 art. 17-1).
   - Re-letting in tight-zone agglomerations: limited to the previous rent plus IRL under the annual art. 18 decree ([V] ANIL; décret 2016-1040 and successors).
   - Rent caps (encadrement des loyers) in Paris, Lille, Lyon and others.
   - So a tax *increase* cannot be passed on quickly, and a tax *cut* will not lower sitting tenants' nominal rents. Pass-through can only build up through new lets and new supply.
6. **The tax base is net income, with large regime differences** (micro-foncier 30 % abatement, régime réel with déficit foncier, LMNP depreciation). The relevant ε_S responds to the *marginal effective* tax rate on new rental investment, not to average revenue. Convert revenue changes to an effective rate change before applying π.

**4.3 Direct evidence on landlord-side taxes.**
- Germany (Löffler & Siegloch): full pass-through in about 3 years, but inflated by the legal recoverability of Grundsteuer, which does not exist in France.
- US local differentials (Carroll & Yinger; Schwegman & Yinger): about 15 %. This is the right order of magnitude for local differences but too low for a nationwide change, under the new view.
- France (Bono & Trannoy): landlord tax relief was capitalised into land prices.
- Together these bracket a national, French, long-run pass-through at well above 0.15 and below 1. The 0.25 to 0.75 band is consistent with all three once each one's design is taken into account.

---

## 5. Recommended parameter and range

Use the formula ΔRent/Rent = −π(t) × ΔT/R, where ΔT/R is the change in tax as a share of gross rent at the *marginal effective* rate. Apply π to the rental-income-tax component only; the new land tax itself has π = 0 by construction.

| Parameter | Central | Range | Supply-elasticity assumption (ε_D ≈ 0.5–1, central 0.7) |
|---|---|---|---|
| (a) APL-type demand subsidy, years 1–3, tight markets / small units | 0.6 | 0.4–0.9 | ε_S ≈ 0.1–0.4 (fixed stock) |
| (a) APL-type demand subsidy, 3–8 years, national | **0.45** | **0.2–0.8** | ε_S ≈ 0.5–1 |
| (a) APL-type demand subsidy, long run, small units | 0.3 | 0.1–0.5 | new studio supply responds (Grislain-Letrémy & Trevien 2022) |
| (b) Landlord rental-income tax → rents, years 1–3 | **0.10** | **0–0.2** | ε_S ≈ 0.1 plus legal rent stickiness (IRL cap, art. 18 decree, rent caps) |
| (b) Same, year 5 | 0.3 | 0.1–0.5 | partial supply and tenure adjustment |
| (b) Same, 10+ years | **0.5** | **0.25–0.75** | ε_S(rental) ≈ 0.7–1.5 (new build plus tenure switching). Upper part bounded by the non-land share of value plus the tenure margin |
| (b) Zonal split (optional) | tight zones (A bis/A) 0.35; other zones 0.6 | ±0.2 | tight zones: low ε_S and high land share; elsewhere the reverse |

Implementation suggestions [I]:
- Phase the effect in with a simple adjustment path, e.g. π(t) = 0.5 × (1 − e^(−t/5)), which gives about 0.09 at 1 year, 0.32 at 5 years and 0.43 at 10 years.
- Expose the long-run value as a slider over 0.25 to 0.75, with the pedagogical note: "the more easily rental housing can be built or switched from owner-occupation, the more of a landlord tax cut reaches tenants; whatever falls on land is capitalised into land prices instead".
- Do **not** present the APL literature as support for a high pass-through of landlord tax cuts. If it is cited at all, cite it via the complementarity argument in section 4.1.

---

## 6. What would change the view

1. **A replication of Fack on ENL microdata** using log rent, surface and comfort controls, and occupancy duration modelled as an outcome rather than a control. If the DD estimate falls below 0.2 with a tight CI, lower (a) to about 0.25 (and raise (b)'s lower bound). If it stays near 0.45 with a tight CI, keep the current values.
2. **The full IGEDD 2019 report (007987-03).** If it contains an actual corrected estimate with standard errors, weigh it accordingly. I could not access it.
3. **French natural experiments not yet exploited (as far as I found):**
   - the €5/month APL cut of October 2017 (a known event, but I found no evaluation);
   - the 2021 move to contemporaneous income assessment of APL ("contemporanéisation");
   - landlord-side changes: the 2018 IFI (wealth tax restricted to real estate); Pinel phase-out; the 2025 change to LMNP depreciation in capital-gains tax.
   - An event study of rents (e.g. observatoires locaux des loyers, Clameur/Clameur successors) around these would directly measure π_tax for France.
4. **Better French estimates of rental supply elasticity** by zone, including switching between owner-occupation and letting (e.g. Filocom/Fidéli transitions). If long-run ε_S(rental) is below 0.5, lower (b) long run to about 0.35. If above 2, raise it to about 0.7.
5. **The land share of rental value in the zones modelled.** A higher land share means lower long-run π_tax.

---

## 7. Sources

Primary sources accessed (V = verified in this session; the access route is noted):

1. Fack, G. (2005). "Pourquoi les ménages pauvres paient-ils des loyers de plus en plus élevés ? L'incidence des aides au logement en France (1973-2002)". CEPREMAP Docweb 0516. RePEc page: https://ideas.repec.org/p/cpm/docweb/0516.html ; PDF: https://www.cepremap.fr/depot/docweb/docweb0516.pdf (V, full text via fetch tool).
2. Fack, G. (2005). Same title, *Économie et Statistique* 381-382, pp. 17–40. https://www.insee.fr/fr/statistiques/fichier/1376573/es381-382b.pdf (V, full text via fetch tool).
3. Fack, G. (2006). "Are housing benefit an effective way to redistribute income? Evidence from a natural experiment in France". *Labour Economics* 13(6), 747–771. doi:10.1016/j.labeco.2006.01.001. https://ideas.repec.org/p/hal/journl/hal-00813573.html (V, abstract only).
4. Friggit, J. / IGEDD (2025). Rapport n° 007987-04, « L'effet inflationniste des aides personnelles au logement reste à évaluer ». https://igedd.documentation.developpement-durable.gouv.fr/documents/Affaires-0014474/007987-04_rapport-publi%C3%A9.pdf (V, via fetch tool); errata: https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/coquilles_007987-04_effet_inflationniste_cle7b2ead.pdf
5. IGEDD summary page listing the 2015, 2019, 2020, 2022 and 2025 reports: https://www.igedd.developpement-durable.gouv.fr/the-inflationary-effect-of-housing-benefits-in-a4315.html (V).
6. Friggit, J. / CGEDD (2019). Rapport n° 007987-03, « L'incidence déterminante des effets de structure sur la surcroissance du loyer des locataires à bas revenu du parc privé, 1973-2013 ». **Full text not found**; errata only: https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/coquilles_007987-03_incidence_effets_de_structure_cle01b981.pdf (S for content).
7. Friggit, J. / CGEDD (2020). « Test de l'effet haussier de la partie progressive par rapport au loyer du barème des aides personnelles au logement ». https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/effet-haussier-apl_cle59af18.pdf (V, via fetch tool).
8. Friggit, J. / CGEDD (2012). Mission sur les aides personnelles au logement, note de fin de mission (007987-01). https://igedd.documentation.developpement-durable.gouv.fr/documents/Affaires-0007024/007987-01_note-fin-mission.pdf (V, via fetch tool).
9. Laferrère, A. & Le Blanc, D. (2004). "How do housing allowances affect rents? An empirical analysis of the French case". *Journal of Housing Economics* 13(1), 36–67. https://ideas.repec.org/a/eee/jhouse/v13y2004i1p36-67.html (no abstract on RePEc; paywalled).
10. Laferrère, A. & Le Blanc, D. (2002). « Comment les aides au logement affectent-elles les loyers ? ». *Économie et Statistique* 351, 3–30. https://ideas.repec.org/a/prs/ecstat/estat_0336-1454_2002_num_351_1_7403.html (V, abstract); Persée full text https://www.persee.fr/doc/estat_0336-1454_2002_num_351_1_7403 (blocked to automated fetch).
11. Grislain-Letrémy, C. & Trevien, C. (2014). "The Impact of Housing Subsidies on the Rental Sector: the French Example". INSEE Working Paper G2014/08. https://www.insee.fr/en/statistiques/fichier/1381153/G2014-08.pdf (V); INSEE Analyses n° 19 (Nov. 2014): https://www.insee.fr/fr/statistiques/1521337 (V).
12. Grislain-Letrémy, C. & Trevien, C. (2022). "The Long-Term Impact of Housing Subsidies on the Rental Sector: the French Example". Banque de France WP 886. https://www.banque-france.fr/system/files/2023-01/wp886.pdf (V); Bloc-notes Éco n° 302 (2023): https://www.banque-france.fr/en/publications-and-statistics/publications/housing-subsidies-smaller-upward-impact-rents-if-supply-adjusts (V).
13. Gibbons, S. & Manning, A. (2006). "The incidence of UK housing benefit: Evidence from the 1990s reforms". *Journal of Public Economics* 90(4–5), 799–822. https://eprints.lse.ac.uk/3179 (V, abstract).
14. Collinson, R. & Ganong, P. (2018). "How Do Changes in Housing Voucher Design Affect Rent and Neighborhood Quality?". *AEJ: Economic Policy* 10(2), 62–89. https://www.aeaweb.org/doi/10.1257/pol.20150176 (V, abstract); estimates via https://www.lewis.ucla.edu/2022/01/05/episode-17-housing-vouchers-with-rob-collinson/ (S).
15. Eriksen, M. & Ross, A. (2015). "Housing Vouchers and the Price of Rental Housing". *AEJ: Economic Policy* 7(3), 154–176. https://appam.confex.com/appam/2013/webprogram/Paper7023.html (V, abstract).
16. Kangasharju, A. (2010). "Housing Allowance and the Rent of Low-income Households". *Scandinavian Journal of Economics* 112(3), 595–617. https://ideas.repec.org/a/bla/scandj/v112y2010i3p595-617.html (V, abstract).
17. Virén, M. (2013). "Is the housing allowance shifted to rental prices?". *Empirical Economics* 44(3), 1497–1518. https://ideas.repec.org/a/spr/empeco/v44y2013i3p1497-1518.html (V, abstract).
18. Hyslop, D. & Rea, D. (2019). "Do housing allowances increase rents? Evidence from a discrete policy change". *Journal of Housing Economics* 46. https://ideas.repec.org/a/eee/jhouse/v46y2019ics1051137718302602.html (V, abstract).
19. Löffler, M. & Siegloch, S. (2021). "Welfare Effects of Property Taxation". IZA DP 14195. https://docs.iza.org/dp14195.pdf (V).
20. Carroll, R. & Yinger, J. (1994). "Is the Property Tax a Benefit Tax? The Case of Rental Housing". *National Tax Journal* 47(2), 295–316. https://ideas.repec.org/a/ntj/journl/v47y1994i2p295-316.html (V, abstract); numbers via https://joyinger.expressions.syr.edu/pai735ecn635-notes-on-the-incidence-of-the-property-tax/ and https://www.progress.org/wiki/carroll-yinger-benefit-tax-rental/ (S).
21. Schwegman, D. & Yinger, J. (2020). "The Shifting of the Property Tax on Urban Renters: Evidence from New York State's Homestead Tax Option". US Census CES WP 20-43. https://ideas.repec.org/p/cen/wpaper/20-43.html (V, abstract).
22. Bono, P.-H. & Trannoy, A. (2019). "The Impact of the 'Scellier' Income Tax Relief on Building Land Prices in France". *Économie et Statistique* 507-508. https://www.insee.fr/en/statistiques/fichier/4173213/507-508_Bono-Trannoy-EN.pdf (V).
23. Madec, P. (c. 2013). « Augmenter les aides au logement, une fausse bonne idée ? ». OFCE blog. https://ofce.sciences-po.fr/blog/augmenter-les-aides-au-logement-une-fausse-bonne-idee/ (V; relies on Fack for its only figure).
24. Costa, A. et al. (2017). « L'effet inflationniste des APL sur les loyers : le risque d'une fausse piste ». Terra Nova. https://tnova.fr/site/assets/files/10760/terra-nova_note-apl_141217.pdf (V).
25. Gorreri, S. (2015). « Aides au logement : quand une vraie réforme ? ». IFRAP. https://www.ifrap.org/emploi-et-politiques-sociales/aides-au-logement-quand-une-vraie-reforme (V; cites Fack 80 %).
26. ANIL, « Encadrement de l'évolution du montant des loyers – nouvelle location et renouvellement dans les zones tendues ». https://www.anil.org/documentation-experte/analyses-juridiques-jurisprudence/analyses-juridiques/analyses-juridiques-2014/encadrement-de-levolution-du-montant-des-loyers-/-nouvelle-location-et-renouvellement-dans-les-zones-tendues/ (V).
27. Charges récupérables (décret 87-713): https://www.bailfacile.fr/guide/les-charges/29-liste-des-charges-recuperables (V, secondary legal guide); German §2 BetrKV recoverability of Grundsteuer: https://conny.de/en/rent/tenant-protection/information (V, secondary legal guide).

Not accessed or only via secondary citation:
- Cour des comptes (November 2021) observation (known only via the IGEDD summary; report not located).
- Beatty, Cole et al. (2014); Brewer, Brown et al. (2019); Susin (2002); Rydell, Neels & Barnett (1982); Sayag & Zussman (2015); Bozio, Fack & Grenet (2015, IPP); IGAS (2012); CGEDD (2015) student report. All S.

Network note: direct downloads from cepremap.fr, insee.fr, igedd.developpement-durable.gouv.fr and caf.fr were refused by this session's egress proxy (HTTP 403). Persée blocks automated fetching (robots.txt). Content from those hosts was read only through the WebFetch tool.
