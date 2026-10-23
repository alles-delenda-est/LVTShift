# Paris & Lyon (intra- and extra-muros) — review checklist

Branch `paris-lyon-territories` · prepared 2026-10-19 · nothing committed or pushed yet.

**What was added.** Paris (20 arrondissements, one city-wide rate), Lyon (9
arrondissements), *Paris extra-muros* (all 122 communes of 92/93/94) and *Lyon
extra-muros* (the 57 other communes of the Métropole). Every commune in a ring is
modelled on its **own** taxe foncière total and stays revenue-neutral on its own;
the ring figures are aggregates of those 179 separate runs, not a metropolitan tax.

**Headline numbers (central scenario, 4:1 split-rate; maintained-stock depreciation rule, local price deflator and exempt public property, branch `exempt-public-property`)**

| | Parcels | TFPB held neutral | Land share | Built parcels at 85 % cap | Amount shifted | Share paying more |
|---|---|---|---|---|---|---|
| Paris | 75,091 | €1,840.9 M | 83.3 % | 34.8 % | 15.3 % | 53.3 % |
| Lyon | 31,023 | €362.9 M | 70.4 % | 0.0 % | 14.3 % | 69.5 % |
| Paris extra-muros (122) | 566,538 | €3,569.3 M | 72.8 % | 0.8 % | 15.3 % | 68.4 % |
| Lyon extra-muros (57) | 224,911 | €528.2 M | 65.5 % | 0.0 % | 18.7 % | 69.6 % |

**About the land share.** The first version of this branch depreciated every
building by age alone, down to 25 % of rebuild cost. That treated maintained
Haussmann stock as worn out, and put 95.5 % of Paris's built parcels (Lyon 59.8 %,
55 communes in all) on the 85 % cap, so the land share there was an assumption.
The maintained-stock rule (C1, see A7) values such buildings at a 30-year
effective age where neighbourhood prices are well above rebuild cost. Cap warnings
fall from 55 communes to 1 (Neuilly-sur-Seine). Paris keeps 34.8 % of parcels at
the cap, which is genuine at Paris prices. The direction of every distributional
result is unchanged: the full before/after table is in
`output/diagnostics/depreciation_before_after.csv`, summarised under A7.

**Price deflator (spec 0001).** Sales from 2021–2025 are now brought to 2025 euros
with the most local Notaires-INSEE index (Paris flats; 92/93/94 by type; Lyon,
Marseille, Lille agglomerations; regions; Province). It takes the 2021–22 peak out
of Paris and Lyon prices: Paris land share 83.9 → 83.3 %, parcels at the cap
47.6 → 34.8 %; Lyon 72.0 → 70.5 %; Paris ring 74.1 → 73.0 %; Lyon ring 67.4 →
65.9 %. Provincial and weak markets barely move. Every distributional direction
holds (Paris quintiles −18.1/+11.4 → −18.2/+11.9).
**Exempt public property (spec 0003).** Parcels held entirely by the State, local
authorities or public hospitals / universities / schools, with no lease, condominium
or private manager, are now treated as exempt today and under the LVT (DGFiP
« personnes morales » files, conservative rule). "Parcels" above count taxable
parcels only (Paris 3,098 exempt, Lyon 3,119, Paris ring 41,711, Lyon ring 21,515,
mostly roads, parks and other public land). They carried 3.1–9.6 % of the levy the
baseline spread onto them (Paris 5.0 %, Lyon 4.7 %, Grenoble 8.2 %, Roubaix 9.6 %); that share now
falls on taxable parcels. Land shares barely move; the income gradient flattens
somewhat at the bottom (median residential parcel of the poorest quintile: Grenoble
0.0 → +4.0 %, La Rochelle −23.6 → −16.8 %); Paris −18.1/+11.9 → −17.3/+12.4. The
Domaine national de Saint-Cloud (State-owned, managed by the Centre des monuments
nationaux) now qualifies: Saint-Cloud's amount shifted falls from 49 % to 22 % of
its levy and its land share from 84 % to 79 %.

**Verified.**
- Revenue-neutral to the euro in all 181 new runs (max deviation 0.0000 %).
- Every source present for every commune: cadastre, 5 years of DVF, buildings, zoning, IRIS.
- Paris REI matches the Ville de Paris BP 2025 (€1,851 M incl. TFPNB) within 0.6 %; Lyon matches its 2025 budget (€349 M) within ~2 %.
- Cadastre-vs-BD TOPO built-map agreement passes (Paris 97 % vs 94 %, Lyon 89 % vs 81 %).
- Tests pass: 53 Python, synthetic end-to-end, 9 site tests, lint, type-check and static build.
- Adversarial security review: no critical or high findings, fixes applied, logged in `~/securitylog.md`.

---

## A. Decisions only you can make (economics / framing)

- [ ] **A1. How to present Paris.** Land share 83.3 %, with 34.8 % of built
  parcels still at the 85 % cap: in the dearest streets land really is above 85 %
  of value. So much of Paris still gets a near-uniform split, and the result reads
  largely as a move from today's floor-area bill to a market-value bill. It is
  strongly progressive (poorest income quintile −17.3 %, richest +12.4 %). Options:
  (a) publish with a caveat, framed as "where land is ~85 % of value, LVT ≈ a
      modern value tax";
  (b) also raise the cap for Paris (e.g. 0.95), letting the dearest streets
      differentiate; this is a new design choice to review.
  *Recommendation: (a).* The site already labels a land share "plafonnée" when
  half or more of the parcels sit at the cap; Paris is now just below that line.
- [ ] **A2. Income quintiles for the rings.** Ranked across the whole ring, Lyon
  extra-muros looks *regressive* (poorest +9 %, richest −1 %). Ranked within each
  commune it is *progressive* (+5 % → +12 %): the pooled view mixes in rich-vs-poor
  commune differences the reform does not touch. The site now shows both, with an
  explanation. Confirm you are happy with that framing, or prefer within-commune only.
- [ ] **A3. Syndicate layer (Métropole de Lyon).** 45 ring communes have a
  *Syndicat* foncier-bâti layer worth 5–23 % of their bill (e.g. Couzon 23 %).
  We hold Commune + Métropole neutral, as for the rest of the panel. Leaving the
  syndicate layer out changes **euro** amounts (understated by that %) but not the
  **% changes**. Keep as is (consistent), or include syndicates everywhere (`--layers Commune GFP Syndicat`)?
- [ ] **A4. Construction-cost basis.** Pilots: Paris 2,300, inner ring 2,150,
  Lyon and its ring 1,950 €/m². Research suggests 2,600 / 2,300 / 2,100 €/m² of
  *surface utile*; our floor area (footprint × storeys) is *gross*, which brings
  them roughly back to our values (÷ 1.1–1.2). Gemini 4 Argon argues for a 0.8
  gross-to-net factor. Decide the basis as part of the planned FFB/BT01
  calibration. In old stock, depreciation, not cost, decides the split.
- [ ] **A5. Public open space and industrial land priced as building land.**
  Building-less parcels in urban zones take the residential plot price. The
  aggregate effect is small (Paris 0.9 % of the levy, rings 3.6 % / 6.2 %), but it
  concentrates in a few communes:
  - **Saint-Cloud 24 %** — *UL* zone, the state-owned Domaine national (now exempt
    under spec 0003: State property managed by the Centre des monuments nationaux);
  - **Feyzin 19 %** — chemical-valley industrial land;
  - Paris: *UV* parks and cemeteries 0.35 %, *UGSU* rail yards 0.20 %;
  - Lyon: Port Édouard Herriot (*UEp*).

  Choose a rule: treat leisure / green / public-service labels (UV, UL, USP,
  UGSU…) as non-constructible, and/or price industrial zones on an industrial-land
  benchmark. This is a panel-wide method change. Use `python audit_land.py <commune>`
  to see any commune's breakdown.
- [ ] **A6. Exemptions (HLM, QPV, public land).** The real tax total is net of
  exemptions but is spread over every built parcel. This overstates today's bill
  for exempt social housing (material in 93 and Paris). Open proxies exist: the RPLS
  social-housing register, QPV boundaries, BD TOPO *zones d'activité*. Priority?

- [ ] **A7. Approve the maintained-stock depreciation rule (C1).** Effective age
  = w·min(age, 30) + (1−w)·age, where w rises from 0 to 1 as the IRIS median
  price/m² goes from 1.2× to 2.5× rebuild cost. Basis: appraisal "effective age"
  (FHFA WP 19-01), little long-run deterioration in maintained stock (Francke & van
  de Minne 2017), INSEE capitalising renovation. Gemini 4 Argon asked for the
  continuous ramp and IRIS-level prices (both adopted). It also proposed using the
  DPE energy class as a condition signal (follow-up C9).
  What it changes (before → after):
  - land share: Paris 84.9 → 83.9 %, Lyon 81.6 → 72.0 %, Montreuil 83.9 → 75.8 %,
    La Rochelle 83.5 → 74.1 %, Paris ring 80.6 → 74.1 %, Lyon ring 73.2 → 67.4 %;
  - weak markets unchanged (Roubaix, Cahors, Figeac: rule inactive);
  - poorest/richest quintile, median change: Paris −16.7/+10.5 → −18.1/+11.4;
    Montreuil −10.3/+10.7 → −13.4/+11.9; Grenoble −7.7/+21.7 → −7.5/+17.8.
    Every direction is preserved.
  Review fix (external code review): the IRIS price q is now taken over built
  parcels only, because vacant plots carried a placeholder "flat" type. Paris is
  unchanged; 15 of 188 communes move by more than 1 point of land share, at most
  2.5 points (Couzon-au-Mont-d'Or); Annemasse moves most on the site (66.1 → 64.9 %).
  Eight communes lose their land-share-band warning. Figures above include it.
  Decide: accept the 30-year cap and the 1.2–2.5 ramp, or ask for a sensitivity
  run on them (e.g. cap 20/40) before merging.

## B. Before merging this branch

- [ ] **B1.** Read the territory view locally (`cd site && npm run build`, then serve `out/`),
  or on the Vercel preview once pushed. Screenshot of the Paris ring:
  see the scratchpad `paris-ring.png` mentioned in chat.
- [ ] **B2.** Review the rewritten méthodologie paragraph ("Paris, Lyon et leurs
  couronnes"). The old text said Paris was absent and that the "métropole" levies TFPB
  in Paris; per the REI it does not.
- [ ] **B3.** Ask Claude to commit (scoped files only: **not** `charts_fr.py`,
  `Comms docs/`, `LVTShift/`), push, and open the PR; the push creates the Vercel preview.
- [ ] **B4.** On the Paris/Lyon branch the 9 existing communes' files were left
  unchanged. **The depreciation branch refreshes them**, because the method changed
  for every commune; that also brings them to today's open-data vintage. Their open data has moved since they were modelled (e.g. Grenoble now
  has 12,895 parcels vs 12,853; its headline is unchanged). Decide whether to
  refresh the whole panel to one data vintage, in a separate PR.

## C. Follow-up work (separate PRs — one feature each)

- [x] **C1.** Depreciation for old, maintained stock. Done on branch `depreciation-old-stock` (decision A7).
- [ ] **C2.** Zoning-label rule for public, green and industrial land (A5).
- [ ] **C3.** Exemption proxies: RPLS, QPV and public land (A6).
- [ ] **C4.** Fix the INSEE vacancy benchmark. It has **never** returned a value
  (null for all published communes) because the INSEE page gives counts, not a
  percentage. Its comparator is also degenerate in dense cities (Lyon shows 99.9 %
  "under-built").
- [ ] **C5.** Offices and La Défense: non-residential value still borrows the residential €/m² (Courbevoie, Puteaux, Paris 8e).
- [ ] **C6.** Cache housekeeping: add `--refresh` and record the download date in each payload's provenance (security review, info).
- [ ] **C7.** Add an aggregate-only guard to the public register writer (security review, low). The register is now 692 KB; consider splitting out the ring members.
- [ ] **C9.** DPE energy class as a building-condition signal for effective age
  (Gemini's suggestion: a 1900 building rated B/C has been renovated, F/G has not).
  Needs the DPE class field verified live and a coverage check, since only
  diagnosed dwellings have one.
- [ ] **C10.** Floor-area basis (A4): DVF prices are per m² *habitable*, our floor
  area is gross. For the land *share* this cancels only if the rebuild cost is
  also per habitable m². The +20 % cost sensitivity brackets it (Paris 81.5 %).
- [ ] **C8.** Marseille (16 arrondissements) can now be added the same way as Paris and Lyon.

---
*Reproduce:* `python run_commune.py paris --cache-dir output/cache` ·
`python run_territory.py paris-extra-muros` · `python export_web.py paris-extra-muros` ·
`python preflight.py` · `python audit_land.py saint-cloud`
