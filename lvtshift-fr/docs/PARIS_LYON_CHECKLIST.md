# Paris & Lyon (intra- and extra-muros) — review checklist

Branch `baseline-weights` (stacked on `paris-lyon-territories` and the non-residential branches) · prepared 2026-10-19, updated 2026-10-23.

**What was added.** Paris (20 arrondissements, one city-wide rate), Lyon (9
arrondissements), *Paris extra-muros* (all 122 communes of 92/93/94) and *Lyon
extra-muros* (the 57 other communes of the Métropole). Every commune in a ring is
modelled on its **own** taxe foncière total and stays revenue-neutral on its own;
the ring figures are aggregates of those 179 separate runs, not a metropolitan tax.

**Headline numbers (central scenario, 4:1 split-rate; maintained-stock depreciation rule, local price deflator, exempt public property, habitable-area basis, calibrated costs, house costs, storey counts by building type, exempt farm buildings, non-residential valuation and today's tax calibrated to each commune's REI split, central professional scale 2.5, branch `baseline-weights`)**

| | Parcels | TFPB held neutral | Land share | Built parcels at 85 % cap | Amount shifted | Share paying more |
|---|---|---|---|---|---|---|
| Paris | 75,090 | €1,840.9 M | 75.8 % | 5.6 % | 19.6 % | 52.8 % |
| Lyon | 31,022 | €362.9 M | 60.0 % | 0.8 % | 20.9 % | 74.6 % |
| Paris extra-muros (122) | 566,442 | €3,569.3 M | 65.3 % | 1.8 % | 30.4 % | 70.8 % |
| Lyon extra-muros (57) | 224,841 | €528.2 M | 55.4 % | 1.2 % | 43.0 % | 74.6 % |

**Publish distributional figures only with the low bound beside them.** The
professional-premises scale in today's-tax baseline (central 2.5, low bound 1.0)
moves household results by 10–15 points; the new bills are the same in both
cases. Low-bound amount shifted: Paris 30.2 %, Lyon 30.9 %, Paris ring 36.7 %,
Lyon ring 40.6 %; share paying more 42.5 / 51.5 / 56.1 / 58.4 %. See
"Calibrated current-tax baseline" below.

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
parcels only (Paris 3,099 exempt, Lyon 3,120, Paris ring 41,807, Lyon ring 21,585,
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
non-residential PRs; the rural-building exemption (CGI 1382 6°, below) is the
second, and per-type non-residential valuation (below) the third. Evidence:
`docs/research/nonres-valuation-2025.md` §1 and `docs/research/nonres_probes/`.

**Exempt farm buildings (second non-residential step).** CGI art. 1382 6° exempts
from the TFPB buildings permanently and exclusively used for agriculture
(greenhouses, barns, silos, stables); the land under them pays the TFPNB, outside
the modelled levy. The test is use, not ownership (`nonres-valuation-2025.md` §7,
read via doctrine.fr; Légifrance and BOFiP could not be fetched live). The open-data
proxy (`exemptions.rural_buildings`): BD TOPO usage « Agricole » with nature Serre
or Silo or a parcel in a PLU A/N zone; or a shed (« Industriel, agricole ou
commercial ») with no usage or « Indifférencié » in an A/N zone, since BD TOPO
often leaves farm sheds unlabelled. « Agricole » sheds in urban zones and
garden-centre greenhouses stay taxable. Rural buildings are dropped before
valuation and before today's TFPB is shared out; zoning is now fetched once,
before that filter. A mixed parcel keeps its farmhouse; a parcel holding only
rural buildings becomes unbuilt farmland (SAFER price or zone class), with no
TFPB today and only its land value under the LVT. 156 communes have at least one
rural building. Before → after: Périgny 41.8 → 47.9 % (about half its footprint
was greenhouses and farm buildings), Mandres-les-Roses 60.0 → 62.1 %, Solaize
51.7 → 52.3 %, Santeny 40.4 → 40.8 %, every other commune < 0.5 pt. Paris, Lyon
and both rings: land share unchanged; Paris ring share paying more 67.6 → 67.4 %;
Lyon ring amount shifted 26.4 → 26.6 %, share paying more 60.7 → 60.8 %. Band
counts unchanged (2 below 40 %: Limeil-Brévannes, Vaujours; 26 above 65 %). The
small drop in "Parcels" is public land whose only buildings were rural: it now
counts as unbuilt and qualifies as exempt public property. Caveat: in urban
communes the N-zone rule also catches park outbuildings (Vitry-sur-Seine 1.2 % of
building footprint, Villeurbanne 0.1 %), mostly public and largely exempt anyway;
the fichiers fonciers' exemption codes would verify actual use.
`--no-exemptions` turns off both exemptions.

**Non-residential valuation (third non-residential step; merge with the fourth).**
Each building is typed from BD TOPO usage and nature (`estimate.building_type`,
`config.BUILDING_TYPES`): shed, workshop, retail box, office, farm shed,
greenhouse, sports hall, annex, religious or residential. Each type's cost is a
ratio to the commune's collective-housing cost: shed 0.25, workshop 0.354,
retail box 0.467, office 0.825, farm shed 0.073, greenhouse 0.081, sports
1.033, annex 0.227. Business types exclude VAT (firms recover it; RICS adds
VAT only where irrecoverable), annexes include it. The ratios are anchored on
one commercial cost guide scaled to our housing level: ±25 %. Lives and floors:
sheds, workshops and retail boxes 40 y / 15 %, offices 60 y / 20 %, farm sheds
30 y / 10 %, greenhouses 25 y / 10 %, sports and annexes 50 y / 20 %; housing
keeps 80 y / 25 %. Non-residential buildings with no year of their own are
taken at mid-life; DPE years and the DPE median, and the maintained-stock rule,
now apply to housing only. Parcels whose largest building is a shed, workshop,
retail box, farm shed, greenhouse, sports hall or annex are valued by
depreciated replacement cost (DRC, « sol + construction »), the RICS standard
for property that rarely sells: building = depreciated cost, land = local
terrain-à-bâtir €/m² × 0.45 (Paris area) or × 0.35 (Lyon area) for business
types, from open DVF activity-land sales (93: 381 vs 658 = 0.58; 94: 282 vs
771 = 0.37; Lyon 0.29–0.40), × 1.0 for sports and annexes; market value = land
+ building, no residential price, no clip. In A/N or unzoned land only a yard
of 3 × floor area takes the building-land price, the rest is farmland (the
security review found a 10 ha farmland parcel valued at €16 M without it).
Offices keep the residual against the residential price surface, at the office
cost. The business-land ratio is published in the payload provenance
(`activity_land_ratio`). Before → after (land share): Paris 74.2 → 75.8 % (5.6 %
at the cap), Lyon 57.8 → 60.0 %, Paris ring 62.2 → 65.3 %, Lyon ring 53.0 →
55.4 %, Santeny 40.8 → 52.1 %, Vaujours 39.0 → 49.8 %, Tremblay-en-France 47.6 →
58.3 %, Villepinte 42.8 → 49.5 %, Périgny 47.9 → 50.1 %, Limeil-Brévannes 38.0 →
41.7 %. Below 40 %: 2 → 1 (Cahors 38.6 %). Above 65 %: 26 → 48, mostly
inner-ring communes next to Paris (Puteaux 71.0 %, Saint-Cloud 76.8 %, Clichy
74.8 %, Courbevoie, Nanterre, Montreuil, Pantin…). Gemini (gemini-4-argon)
judges these plausible: 40–65 % is a metro-wide reference, not a per-commune
test; communes contiguous to Paris (76 %) naturally sit at 65–75 %, and land is
65–75 % of value in prime office districts. Lyon ring by category: industrial
land €8.6bn → €3.8bn, buildings €8.5bn → €2.6bn; industrial bills −3.5 → −55 %,
commercial −7 → −17 %, houses −1 → +6 %; amount shifted 26.6 → 38.3 % of the
levy; poorest fifth's total change −13.5 → −3.7 %. Paris ring: industrial bills
−31 %; "other" (garage and sports plots) +67 %, but only 1.4 % of today's tax.
Income group totals: Paris −20.1 … +14.9 %, Lyon −18.7 … +13.6 %. These figures
were on the floor-area baseline, which the fourth step (below) replaces.
Evidence: `docs/research/nonres-valuation-2025.md` §2–5 and
`docs/research/nonres_costs_calc.py`.

**Calibrated current-tax baseline (fourth non-residential step, C11).** Today's
TFPB used to be shared over taxable built parcels by floor area. It is now
calibrated per commune to its official 2025 REI split into three groups
(`config.BASELINE_MODEL`, `ingest.fetch_rei_baseline_split`,
`estimate.baseline_floor`, `estimate.calibrated_weights`,
`run_pipeline._baseline_weights`; evidence
`docs/research/tfpb-baseline-calibration.md`):
- *Industrial establishments (art. 1499 CGI):* WC75 (the State's compensation
  for the 2021 halving) ÷ the 2020 commune + département rate (LFI 2021 art. 29;
  Métropole de Lyon communes use the Rhône 2014 rate, 11.03 %). A national run
  gives 5.7 % of the TFPB base, exactly the Cour des comptes figure (*Les taxes
  foncières*, 2023); the CFE industrial line cross-checks within 0.6–1.13.
- *Professional premises (RVLLP):* 0.5 × the CFE gross base of professional
  premises (T29_1, else T29 − X503). The 0.5 is the TFPB's 50 % deduction (CGI
  1388), which applies to all built property. The CFE is an occupier tax, so
  vacant premises and non-CFE occupiers drop out: nationally the proxy gives
  8.6 % against the Cour's 22 %. It is scaled by **2.5** (central); the raw
  proxy (× 1.0) is the lower bound.
- *Housing and other:* the rest.

Floor area is grouped by BD TOPO usage (industrial = Industriel; professional =
Commercial et services, Sportif and the ground floor of residential buildings
whose usage_2 is commercial: 45 % of residential buildings in sampled Paris
arrondissements, 5 % in Villeurbanne, < 1 % in Villepinte; housing = the rest).
The produit is shared between groups in the target proportions and by floor
area within each. Industrial merges into professional where it would pay less
per m² (Villepinte, Santeny: warehouses taxed as professional premises, about
0.42–0.46 × housing per m²). Per-m² weights are capped at 5 × housing;
communes whose industrial + professional share exceeds 75 % are scaled to 75 %
(Rungis 77 %, Marcy-l'Étoile 84 %, Vaujours 93 %). Missing REI data fall back
to floor area with a note; 188/188 communes are calibrated. Method, targets and
achieved shares are in the payload provenance (`current_tax_baseline`);
`run_commune --baseline floor` keeps the old baseline as a sensitivity. Example
weights per m² vs housing: Saint-Fons industrial 1.30, professional 0.91;
Rungis 1.71 (merged); Vaujours and Marcy-l'Étoile capped at 5. Both of Gemini's
legal claims (that the 0.5 covers housing only, and a 2017 rate) were checked on
Légifrance and were wrong; its point that the CFE proxy undercounts was right.

**Key result, the opposite of the expectation.** Business pays *more* per m²
than floor area implied: art. 1499 values include fixed plant, and professional
premises were revalued to 2013 rents while housing is on 1970 values. So the
reform shifts even more from businesses to households than the floor-area
baseline suggested. Land shares are unchanged.

| | Before (floor area) | Central (× 2.5) | Low bound (× 1.0) |
|---|---|---|---|
| Paris income totals Q1..Q5 | −20.1 −11.2 −4.2 +5.7 +14.9 | −17.4 −8.3 −1.3 +8.9 +18.9 | −27.6 −18.8 −12.1 −2.9 +3.9 |
| Lyon | −18.7 −8.5 −0.8 +3.2 +13.6 | −14.0 −3.5 +4.4 +8.5 +18.9 | −27.7 −18.2 −10.8 −7.0 +3.5 |
| Paris ring | −9.1 −5.0 −0.6 −2.7 +1.1 | −7.4 −3.0 +2.0 −1.1 +5.5 | −21.8 −16.9 −12.1 −12.6 −9.0 |
| Lyon ring | −3.7 +0.8 +5.0 −1.3 −4.7 | +0.8 +2.8 +10.7 +4.9 −1.1 | −15.8 −11.4 −7.7 −12.1 −14.2 |
| Amount shifted (% of levy): Paris / Lyon / Paris ring / Lyon ring | 19.2 / 20.4 / 28.1 / 38.3 | 19.6 / 20.9 / 30.4 / 43.0 | 30.2 / 30.9 / 36.7 / 40.6 |
| Share paying more: same order | 50.2 / 70.8 / 68.6 / 69.3 | 52.8 / 74.6 / 70.8 / 74.6 | 42.5 / 51.5 / 56.1 / 58.4 |

By category, central: Lyon ring industrial share of today's tax 10.0 → 11.9 %,
commercial 15.0 → 16.6 %; bills industrial −63 %, commercial −24 %, houses
+13 %. Paris ring industrial share 5.3 → 5.8 %; bills industrial −36 %,
commercial −15 %, houses +18 %. Low bound: Lyon ring commercial +47 %,
industrial −42 %, houses −6 %; Paris ring commercial +77 %, industrial +1 %,
houses +1 %.

**The professional scale is now the load-bearing uncertainty.** It moves
household results by 10–15 points; the new bills are identical, only the
starting point moves. 2.5 is better supported (the raw proxy captures about
40 % nationally), but one national multiplier cannot fit every commune;
per-commune professional values (Fichiers fonciers) are the real fix. Present
central and low bound side by side.

**Plant.** The modelled LVT counts only the shed in an industrial parcel's
improvement value, so it implicitly exempts the fixed plant that art. 1499
values include; taxing it is a policy choice. A first-order estimate
(`docs/research/plant_effect.py`) adds the plant's revalued cost to the
improvement base and re-solves 4:1. Industrial bills, shed only → with plant
depreciated / gross: Lyon ring −63 → −62 / −60 %, Paris ring −36 → −36 / −33 %,
Marcy-l'Étoile −90 → −84 / −76 %, Saint-Fons −60 → −59 / −53 %. Industry's cut
is overwhelmingly the land shift (cheap industrial land against today's
capital-heavy base). **Policy finding:** in the Lyon chemical and industrial
corridor, the LVT shifts tax from industry to households under the central
baseline.

**Verified.**
- Revenue-neutral to the euro in all 181 new runs (max deviation 0.0000 %).
- Every source present for every commune: cadastre, 5 years of DVF, buildings, zoning, IRIS.
- Paris REI matches the Ville de Paris BP 2025 (€1,851 M incl. TFPNB) within 0.6 %; Lyon matches its 2025 budget (€349 M) within ~2 %.
- Cadastre-vs-BD TOPO built-map agreement passes (Paris 97 % vs 94 %, Lyon 89 % vs 81 %).
- Tests pass: 53 Python, synthetic end-to-end, 9 site tests, lint, type-check and static build.
- Adversarial security review: no critical or high findings, fixes applied, logged in `~/securitylog.md`.

---

## A. Decisions only you can make (economics / framing)

- [ ] **A1. How to present Paris.** The cap issue is resolved: land share 75.8 %,
  with 5.6 % of built parcels at the 85 % cap, so the Paris split is measured
  parcel by parcel rather than set by the bound, and raising the cap is no longer
  needed. It is above 65 %, as are 47 other communes (mostly the inner ring next
  to Paris, plus La Rochelle, Fleurieu-sur-Saône, Collonges-au-Mont-d'Or,
  Feyzin); 40–65 % is now presented as a metro-wide reference, not a
  per-commune test. The result is progressive (group totals: poorest income
  quintile −17.4 %, richest +18.9 % on the central baseline; −27.6 % and +3.9 %
  on the low bound).
  *Recommendation:* publish with the usual ±10 pt band, and note that the main
  remaining uncertainty for the land share is the habitable ÷ gross ratio
  behind the costs (`cost_net_to_gross`; ±0.05 moves building value about
  ±7 %), and for the distributional results the professional scale in today's
  tax (central 2.5 vs low bound 1.0).
- [ ] **A2. Income quintiles for the rings.** Ranked across the whole ring, Lyon
  extra-muros looks flat to *regressive* (group totals, central baseline: poorest
  +0.8 %, richest −1.1 %; median residential parcel +19 % → −1 %). Ranked within
  each commune it is *progressive* (group totals −6.5 % → +9.9 %): the pooled view mixes in rich-vs-poor
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
- [x] **C5.** Non-residential valuation. Done in three stacked steps: storey counts by building type (`nonres-storeys`), farm buildings exempt under CGI 1382 6° (`rural-exemption`), per-type costs, lives and floors with replacement-cost valuation for shed-type parcels (`nonres-valuation`), and today's tax calibrated by tax group (`baseline-weights`, C11). Remaining: offices still take the residential price surface (a DVF business-premises price surface is the follow-up).
- [x] **C11.** Category weights in today's-tax baseline. Done on branch `baseline-weights`: calibrated per commune to the REI 2025 split (industrial from WC75, professional from the CFE × 0.5 × 2.5, housing the rest). The REI does not split TFPB produits by category, so the split is rebuilt from those two lines. Remaining: the professional scale is one national multiplier; per-commune values need the Fichiers fonciers.
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
