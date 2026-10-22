# Paris & Lyon (intra- and extra-muros) — review checklist

Branch `paris-lyon-territories` · prepared 2026-10-19 · nothing committed or pushed yet.

**What was added.** Paris (20 arrondissements, one city-wide rate), Lyon (9
arrondissements), *Paris extra-muros* (all 122 communes of 92/93/94) and *Lyon
extra-muros* (the 57 other communes of the Métropole). Every commune in a ring is
modelled on its **own** taxe foncière total and stays revenue-neutral on its own;
the ring figures are aggregates of those 179 separate runs, not a metropolitan tax.

**Headline numbers (central scenario, 4:1 split-rate; maintained-stock depreciation rule, local price deflator, exempt public property, habitable-area basis, calibrated costs, house costs and storey counts by building type, branch `nonres-storeys`)**

| | Parcels | TFPB held neutral | Land share | Built parcels at 85 % cap | Amount shifted | Share paying more |
|---|---|---|---|---|---|---|
| Paris | 75,091 | €1,840.9 M | 74.2 % | 3.2 % | 17.5 % | 51.2 % |
| Lyon | 31,023 | €362.9 M | 57.8 % | 0.0 % | 16.5 % | 68.8 % |
| Paris extra-muros (122) | 566,538 | €3,569.3 M | 62.2 % | 0.2 % | 21.7 % | 67.6 % |
| Lyon extra-muros (57) | 224,911 | €528.2 M | 53.0 % | 0.0 % | 26.4 % | 60.7 % |

**About the land share.** The first version of this branch depreciated every
building by age alone, down to 25 % of rebuild cost. That treated maintained
Haussmann stock as worn out, and put 95.5 % of Paris's built parcels (Lyon 59.8 %,
55 communes in all) on the 85 % cap, so the land share there was an assumption.
The maintained-stock rule (C1, see A7) values such buildings at a 30-year
effective age where neighbourhood prices are well above rebuild cost. Cap warnings
fell from 55 communes to 1 (Neuilly-sur-Seine), with Paris still at 34.8 %; the
habitable-area basis (below) removed the rest. The direction of every
distributional result is unchanged: the full before/after table is in
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

**Habitable-area basis and calibrated costs.** DVF prices are per m² of habitable
area, but both market value and building value were computed on BD TOPO footprint
× storeys. Measured on 35 communes (DPE × BD TOPO, matched by RNB id), habitable
area is 0.64 (flats) and 0.61 (houses) of that floor area: BD TOPO counts attics,
raised basements and technical levels as storeys. Both sides of the residual are
now on habitable area, and construction costs are calibrated on the DHUP/SISAL
social-housing building cost (2025 €, per m² gross, fees and VAT): Paris 2,300 →
2,650, inner ring 2,150 → 2,400, Lyon and Villeurbanne 1,950 → 2,000, Lyon ring
1,950 → 1,850 €/m²; other panel communes keep their pilots. The land share now
depends on the habitable ÷ gross ratio behind the costs (`cost_net_to_gross`,
flats 0.71, houses 0.82), not on the measured ratio, which only sets euro levels.
Before → after: Paris land share 83.3 → 74.0 % (parcels at the cap 34.8 → 0.4 %),
Lyon 70.4 → 58.6 %, Paris ring 72.8 → 60.6 %, Lyon ring 65.5 → 55.4 %; amount
shifted Paris 15.3 → 17.4 %, Lyon 14.3 → 16.4 %, Paris ring 15.3 → 19.9 %, Lyon
ring 18.7 → 24.3 %. No commune has more than half its built parcels at the cap
(Neuilly-sur-Seine has the most, 18.3 %); of the 188 modelled communes 21 are above
the 40–65 % band (138 before) and 5 below. The income gradient stays progressive
and is slightly steeper (Paris group totals: poorest fifth −17.6 → −20.0 %, richest
+14.7 → +16.3 %). Evidence: `docs/research/construction-costs-2025.md` and
`docs/research/net-to-gross-measurement.md`.

**House costs.** The calibrated costs are for collective social housing, and
every building type took them. Houses (parcels whose dominant building is a
*maison*) now have their own cost, `house_cost_eur_m2`, on the same basis (per
true-gross m², 2025 €, turnkey, building only, fees and VAT in, developer margin
out), anchored on the SDES survey of new individual houses (EPTB 2024, € per m²
of surface de plancher: Île-de-France 1,863, Rhône 2,127), indexed to 2025,
uplifted for finishing works, fees and a tight-plot premium, and converted to
habitable area: Paris 2,300 (commune cost 2,650), inner ring 2,100 (2,400), Lyon
and Villeurbanne 2,400 (2,000), Lyon ring 2,250 (1,850) €/m². Houses are cheaper
than flats around Paris but dearer around Lyon, the opposite of the
collective-housing gradient, probably because EPTB's Île-de-France sample is mostly
outer-département catalogue houses while Rhône new builds are more bespoke
(unverified); a cautious Lyon-ring alternative is about 2,080. Pilot communes
elsewhere keep one cost; the maintained-stock trigger keeps the commune cost.
Before → after: Paris land share 74.0 → 74.2 % (parcels at the cap 0.4 → 3.2 %),
Lyon 58.6 → 57.8 %, Paris ring 60.6 → 61.7 %, Lyon ring 55.4 → 52.6 %, Montreuil
62.5 → 63.7 %, Villeurbanne 54.2 → 52.5 %. Communes above the 40–65 % band 21 →
24 (Les Lilas, Vanves, Meudon, Puteaux and Malakoff just over 65; Sceaux 66.3 %,
Marnes-la-Coquette 67.3 %; four Monts-d'Or communes fell back inside), below
5 → 4. Neuilly-sur-Seine now has 25.0 % of its built parcels at the cap. Paris
group totals: poorest fifth −20.0 → −19.8 %, richest +16.3 → +16.2 %. **Key
finding:** the low outer-ring communes rise only partly (Santeny 33.2 → 36.2 %,
Vaujours 34.3 → 35.7 %, Limeil-Brévannes 35.1 → 37.4 %, Villepinte 37.4 →
39.4 %, Périgny 38.2 → 40.3 %): houses are only 18–36 % of their building value,
and industrial and commercial parcels valued at the housing cost and the flat
price dominate (Santeny 51 % industrial, Vaujours 56 % industrial, Villepinte
45 % commercial — the exhibition centre). Non-residential valuation (C5) is the
next lever; Gemini agreed it is the bigger one. Evidence:
`docs/research/house-costs-2025.md`.

**Storey counts (first non-residential step).** BD TOPO's storey count comes from
the fichiers fonciers and is never filled for annexes, light structures or
buildings not matched to them; the model imputed height ÷ 3 m. That made a 14 m
single-storey warehouse 5 storeys: the Villepinte exhibition hall (165,000 m² of
footprint) became 828,000 m² of floor. In six sample communes the count is
missing on 42–56 % of sheds, 90 % of the area of sheds with a known count is
single-storey, and the old rule inflated shed floor area 2.0–2.7×. The new rule
(`estimate.impute_levels`): 1 level whatever the height for shed-type natures
(« Industriel, agricole ou commercial », Serre, Silo), light structures and the
usages Annexe, Agricole, Industriel, Sportif and Religieux; other « Commercial et
services » buildings 1 level below 7 m, else height ÷ 3.5 m; housing height ÷ 3 m
as before (measured 2.65 m); a zero count counts as missing. Floor area also
shares out today's TFPB, so the fix lowers non-residential building values *and*
moves part of today's tax off warehouses. Before → after: Paris 74.2 % and Lyon
57.8 % unchanged, Paris ring 61.7 → 62.2 %, Lyon ring 52.6 → 53.0 %; amount
shifted Paris ring 20.6 → 21.7 %, Lyon ring 23.9 → 26.4 %. Santeny 36.2 → 40.4 %,
Vaujours 35.7 → 39.0 %, Villepinte 39.4 → 42.8 %, Tremblay-en-France 44.0 →
47.6 %, Périgny 40.3 → 41.8 %, Limeil-Brévannes 37.4 → 38.0 %. Communes below the
40–65 % band 4 → 2 (Limeil-Brévannes, Vaujours), above 24 → 26 (Clamart and
Collonges-au-Mont-d'Or just over 65). Paris group totals: poorest fifth −19.8 →
−20.0 %, richest +16.2 → +16.1 %. This is the first of three stacked
non-residential PRs; the rural-building exemption (CGI 1382 6°) and per-type
non-residential costs, with replacement-cost valuation for sheds, are still to
come. Evidence: `docs/research/nonres-valuation-2025.md` §1 and
`docs/research/nonres_probes/`.

**Verified.**
- Revenue-neutral to the euro in all 181 new runs (max deviation 0.0000 %).
- Every source present for every commune: cadastre, 5 years of DVF, buildings, zoning, IRIS.
- Paris REI matches the Ville de Paris BP 2025 (€1,851 M incl. TFPNB) within 0.6 %; Lyon matches its 2025 budget (€349 M) within ~2 %.
- Cadastre-vs-BD TOPO built-map agreement passes (Paris 97 % vs 94 %, Lyon 89 % vs 81 %).
- Tests pass: 53 Python, synthetic end-to-end, 9 site tests, lint, type-check and static build.
- Adversarial security review: no critical or high findings, fixes applied, logged in `~/securitylog.md`.

---

## A. Decisions only you can make (economics / framing)

- [ ] **A1. How to present Paris.** The cap issue is resolved: land share 74.2 %,
  with 3.2 % of built parcels at the 85 % cap, so the Paris split is measured
  parcel by parcel rather than set by the bound, and raising the cap is no longer
  needed. It is still above the 40–65 % plausibility band (as are 25 other
  communes: 22 dear communes of the Paris inner ring, La Rochelle,
  Fleurieu-sur-Saône and Collonges-au-Mont-d'Or). The result is strongly
  progressive (group totals: poorest income quintile −20.0 %, richest +16.1 %).
  *Recommendation:* publish with the usual ±10 pt band, and note that the main
  remaining uncertainty is the habitable ÷ gross ratio behind the costs
  (`cost_net_to_gross`; ±0.05 moves building value about ±7 %).
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
- [x] **A4. Construction-cost basis.** Decided on branch `habitable-area-costs`:
  costs per m² of true gross area (2025 €, building only, fees and 20 % VAT,
  developer margin excluded), calibrated on DHUP/SISAL social-housing costs
  (Paris 2,650, inner ring 2,400, Lyon and Villeurbanne 2,000, Lyon ring 1,850),
  converted to a cost per habitable m² with `cost_net_to_gross` (flats 0.71,
  houses 0.82). See "Habitable-area basis and calibrated costs" above. Houses
  take their own EPTB-based cost on branch `house-costs` (Paris 2,300, inner
  ring 2,100, Lyon and Villeurbanne 2,400, Lyon ring 2,250); see "House costs"
  above. Still to confirm: the Lyon house level, or the cautious alternative.
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
- [ ] **C5.** Non-residential valuation: offices, shops and industry still borrow the residential €/m² and the housing construction cost (La Défense: Courbevoie, Puteaux, Paris 8e; the low-land-share communes Vaujours, Limeil-Brévannes, Périgny, Villepinte). First step done on branch `nonres-storeys` (storey counts by building type); the rural-building exemption (CGI 1382 6°) and per-type costs with replacement-cost valuation for sheds are next.
- [ ] **C6.** Cache housekeeping: add `--refresh` and record the download date in each payload's provenance (security review, info).
- [ ] **C7.** Add an aggregate-only guard to the public register writer (security review, low). The register is now 692 KB; consider splitting out the ring members.
- [ ] **C9.** DPE energy class as a building-condition signal for effective age
  (Gemini's suggestion: a 1900 building rated B/C has been renovated, F/G has not).
  Needs the DPE class field verified live and a coverage check, since only
  diagnosed dwellings have one.
- [x] **C10.** Floor-area basis (A4): both sides of the residual are now on
  habitable area. Done on branch `habitable-area-costs`.
- [ ] **C8.** Marseille (16 arrondissements) can now be added the same way as Paris and Lyon.

---
*Reproduce:* `python run_commune.py paris --cache-dir output/cache` ·
`python run_territory.py paris-extra-muros` · `python export_web.py paris-extra-muros` ·
`python preflight.py` · `python audit_land.py saint-cloud`
