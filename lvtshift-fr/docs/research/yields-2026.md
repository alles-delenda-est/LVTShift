# Yields to replace — sources and reconciliations (October 2026)

Companion to `yields.py` and spec 0005 §3. Each figure in `yields.py` was read
on 26 October 2026 from the source named on its line, then re-derived by an
independent verification pass (same day) that read the primary sources
separately. On 27 October Gemini (`gemini-4-argon`) reviewed the economic
choices; every factual claim it made was checked against a primary source
before anything changed (see the last section). This note records the choices
that are not visible in the table: scope, series breaks, corrections and what
is left out.

Status of each line: **verified** (read from the primary source), **derived**
(computed from primary figures, method stated) or **reported** (a secondary
source quoting the primary). No line is "reported" any more.

## Result

| Scenario | Yield to replace (M€) | Indicative rate, % of taxable land |
|---|---:|---:|
| S1 — TF + THRS + DMTO | 66 140 | 1,09 |
| S2 — + taxes on real-estate gains | 69 817 | 1,15 |
| S2 + IFI | 72 149 | 1,18 |
| S3 — + taxes on rental income | 77 507 | 1,27 |
| S3 + IFI | 79 839 | 1,31 |

S1 is 83–95 % of every variant; the taxe foncière bill with the State's fee
(46,3 Md€) is 57–69 %. The choice of scenario changes the national rate by at
most a fifth; the local tier (TF bill, THRS and communal DMTO, 51,3 Md€) is
identical in all five.

**Sensitivity, 2025 euros (D1 stays nominal).** Restating every year with
the CPI (INSEE, base 2015, idbank 001764363) raises S1 by 1 011 M€ (DMTO),
S2 by 1 322 M€ (+ gains) and S3 by 1 936 M€ (+ rents, read for 2022), with or
without IFI (2025 figures). Exported as `total_constant_meur` and stated on the
site; the headline keeps current euros because they are what was collected.

Rates are national averages against taxable built land. Agricultural and
natural land is outside the reform (D6, revised 29 October) and keeps its
TFPNB. They are not the rates the model applies: the local tier is set commune
by commune.

## Changes

| Change | Effect on totals |
|---|---:|
| *Verification pass, 26 October* | |
| Paris's communal DMTO was counted twice (in OFGL's departmental aggregate and in the communal accounts) | −336 M€ |
| Single authorities of Corse, Martinique and Guyane were missing from departmental DMTO | +138 M€ |
| State's fee on DMTO recomputed on the corrected base | −5 M€ |
| State's 3 % fee on the taxe foncière added, for consistency with the fee on DMTO | +1 319 M€ (S1) |
| 2024 IR on gains counted the surtax and land taxes twice | −18 M€ (S2, S3) |
| Land base moved to INSEE end-2025 (provisional), after INSEE revised its accounts | rates −11 % |
| *Gemini review, 27 October (each point verified first)* | |
| Syndicates, TSE, GEMAPI and TASA on the TF bill added (`tf_annexes`) | +923 M€ (all) |
| State's fee on them, at the rates of CGI art. 1641 read on Légifrance | +47 M€ (all) |
| CSG on rental income added (`rents_csg`): it is a separate line, not inside the PS | +1 093 M€ (S3) |
| Rental IR and PS at the CPO's unrounded figures (4 198, 2 399) | −3 M€ (S3) |
| IFI at DGFiP's exact figures (2 159 / 2 332 instead of 2 200 / 2 300) | +32 M€ (IFI variants) |
| *Decision of 27 October (after the review)* | |
| Taxe d'habitation on second homes added to S1, surcharge included (`thrs`), with the State's 3 % fee (`thrs_etat`) | +3 063 M€ (all) |
| Farmland added to the land base at SAFER price × area (D6), 218 Md€ | rates −3,5 % |
| *Decision of 29 October: farmland out of the reform (D6 revised)* | |
| Agricultural and natural land leaves the base and keeps its TFPNB: 922 M€ of the 1 188 M€ TFPNB (2025), and the same share of the non-built syndicates, TSE and GEMAPI, stop being replaced, with the State's fee on them | −973 M€ (all); rates +2,4 % net of both changes |

## Line by line

### Taxe foncière bâtie (S1, local) — 42 776 M€, 2025

OFGL's REI dataset (DGFiP's *recensement des éléments d'imposition*),
« MONTANT RÉEL », commune share 40 157 M€ + intercommunal share 2 619 M€.
DGCL BIS 209 gives about 43,1 Md€ for all TFPB in 2025, consistent with
commune + EPCI + syndicates (42 961 M€).

Why not the CPO's 25,5 Md€ or the compte du logement's 30,5 Md€: both cover
housing only. A land value tax replaces the tax on all built property,
offices, shops and industry included.

### Taxe foncière non bâtie (S1, local) — 1 188 M€, 2025

REI, FNB commune + EPCI + taxe additionnelle (TAFNB). Falling (1 296 M€ in
2024). Excludes chambres d'agriculture (345 M€), which belong in S1 only once
agricultural land is in the base (D6).

### Other levies on the TF bill (S1, local) — 923 M€, 2025

REI « MONTANT RÉEL », built and non-built: syndicates 191 M€ (E23, B23), taxes
spéciales d'équipement 277 M€ (E53, E53A, B53, B53A; they fund the
établissements publics fonciers), GEMAPI 397 M€ (E53gGEMAPI, B53gGEMAPI) and
the Île-de-France TASA 58 M€ (E53TASA). 867 M€ in 2024.

Added after the Gemini review. They are levied on the same base (the cadastral
rental value) and on the same bill as the taxe foncière, so a reform that
removes the taxe foncière removes their base too; spec 0005 §2 already places
syndicates in the local tier. Their budgets are not all communal (TSE and TASA
fund public agencies), which the line's budget label says.

### Taxe foncière — State's fee (S1, national) — 1 366 M€, 2025

CGI art. 1641, read on Légifrance on 27 October 2026 (version in force since
21 February 2026): the State adds 3 % to the taxe foncière (2 % for reliefs and
bad debts, I-A, and 1 % for assessment and collection, II), and also 3 % to
syndicates' levies and GEMAPI, 8 % to TASA and 9 % to TSE. Paid by the
taxpayer. The REI records 2 068 M€ of such fees on the whole bill in 2025, TEOM
(at 8 %) included; the line is consistent with that total. The line is
included because the equivalent fee on DMTO is; counting one and not the other
would be inconsistent.

### Taxe d'habitation on second homes (S1, local) — 2 974 M€, 2025; State's fee 89 M€

Added by decision on 27 October 2026. Like the taxe foncière it is a local tax
on a dwelling, and in most cases the owner pays it (the occupant of a second
home is usually its owner). REI 2025 via OFGL, « MONTANT RÉEL »: commune
1 727,4 + intercommunality 843,1 + syndicates 12,1 = 2 582,7 M€, plus the
surcharge in high-demand areas (MTMAJOTHRS, CGI art. 1407 ter) 390,9 M€, which
the communal amount does not include (checked by recomputing Paris and
Bordeaux). The tax on vacant dwellings (THLV, 124 M€) stays out: it is a
penalty the LVT makes unnecessary.

2024 was 3 691 M€ (3 255 + 436). The 19 % fall in 2025 is spread across nearly
all departments and is not explained in any source found; corrections after
the 2023 occupancy declarations are the likely cause. D1 takes the latest year
for non-cyclical taxes, so 2025 is used; 2024 would add 0,7 Md€.

The State's fee is 3 % (CGI art. 1641: 2 % under I-A c, 1 % under II), 89 M€;
the REI records 93 M€ of fees on the THRS bill (H01).

### DMTO — communes (S1, local) — 3 403 M€, average 2021–2025

OFGL grand livre, all budgets. The accounts changed between nomenclatures M14
and M57 during the period, so the sum is taken over c/7381 (M14), c/73123 (M57)
and c/7332, plus the departmental fund for communes under 5 000 inhabitants
(c/73223, c/73224), which redistributes the communal 1,2 % levied in those
communes. Equalisation transfers between authorities (c/739225, c/73225) are
not taxes and are left out.

This line includes Paris's communal tax (289 M€ in 2023 per DGCL). Without it,
our 3 356 M€ for 2023 gives DGCL BIS 190's 3,1 Md€.

### DMTO — départements (S1, departmental) — 14 062 M€, average 2021–2025

OFGL comptes des départements, agrégat « DMTO avant péreq. »
(16 511 / 16 776 / 13 044 / 11 297 / 13 669), corrected twice:

- **Minus Paris's communal share.** OFGL's definition of the aggregate
  includes, for Paris, the communal additional tax, which the communal line
  already counts. Estimated as OFGL's Paris aggregate minus Paris's
  departmental account (c/73121): 397 / 392 / 301 / 268 / 320.
- **Plus Corse, Martinique and Guyane**, whose single authorities levy the
  departmental duty but sit in OFGL's regions dataset: 145 / 154 / 139 / 116 /
  135 (DGCL: 139 M€ in 2023).

Corrected series: 16 259 / 16 538 / 12 882 / 11 145 / 13 484.

The five-year average (D1) sits 4 % above 2025 and 15 % below the 2022 peak.
Taking the latest year for all DMTO lines instead would lower S1 by 0,84 Md€.

**The 2025 rate change does not call for an adjustment.** Loi n° 2025-127,
art. 116 (read on Légifrance) lets departments charge up to 5 % instead of
4,5 % (CGI art. 1594 D), but only for deeds signed from 1 April 2025 to
31 March 2028, never for first-time buyers of a main residence, and rates revert
to their 31 January 2025 level from 1 April 2028. The permanent law is 4,5 %,
which is what 2021–2024 reflect; 2025 carries nine months of the temporary
increase.

**Sensitivity: constant euros.** The average is in nominal euros. Restating
each year in 2025 euros (INSEE CPI, series 001764363) would add 1,01 Md€ to
S1 (communes +188, départements +804, State's fee +19) and 0,31 Md€ to the
gains lines (S2, S3). Not applied: it changes decision D1.

### DMTO — State's fee (S1, national) — 333 M€, derived

CGI art. 1647 V, read on Légifrance on 27 October 2026 (version in force since
1 July 2026): the State levies 2,37 % on top of the departmental duty (2,14 %
where the departmental rate is the reduced 0,70 %). Applied at 2,37 % to the
whole corrected departmental series, a slight overstatement.

### Real-estate gains (S2, national) — IR 1 267 M€ + PS 2 410 M€, average 2020–2024

Cour des comptes, *L'imposition des plus-values immobilières des particuliers*
(25 November 2025), open-data files G9+10 (2017–2023) and T7 (2023–2024).
IR includes the 2–6 % surtax on large gains and the two taxes on land made
constructible (communal and national), all paid by the seller on the gain.

**The two files overlap on 2023.** For IR they agree once read correctly: T7's
"IR" column (1 278 M€) equals G9+10's IR + surtax + land taxes (1 278 M€) to
within 0,5 M€, so T7 already includes those taxes and the 2024 value is its IR
column alone (908 M€). For PS they do not agree: T7 gives 2 583 M€ against
G9+10's 2 347 (+10 %), and the Cour does not explain the gap.

We use G9+10 for 2020–2023 and T7 for 2024, the only source for that year (and
provisional). The Cour itself compares the two: it reports 2024 down "de l'ordre
de 19 %", which is T7-2024 against G9-2023. Sensitivity of the five-year average
to the choice of series: −54 M€ (all on the G9+10 basis) to +317 M€ (all on the
T7 basis). The Cour's own average over 2017–2023 is 3,5 Md€; ours over 2020–2024
is 3,7 Md€.

The window is 2020–2024, one year behind DMTO's, because 2025 gains are not
published; D1 takes the last five *available* years for each tax.

The PS lines are 17,2 % of the gain, of which 7,5 points (prélèvement de
solidarité) go to the State, not Social Security. The 2026 increase in CSG on
capital income spares real-estate income and gains according to secondary
sources; not checked against the LFSS text.

Companies' gains (IS) are excluded: no public figure (D3).

### IFI (S2 toggle, national) — 2 332 M€, 2025

DGFiP Statistiques n° 15 and 23 (1,8 and 1,9 Md€ for 2022–2023) and n° 45
(April 2026), table 1: 2 159 M€ (2024) and 2 332 M€ (2025), amounts on tax
notices.

Budget receipts are higher: 2 739 M€ in 2024 and 2 771 M€ actually collected in
2025 (DGFiP gross receipts, line 1406; the 2 965 M€ quoted earlier was the PLF
2026 forecast). DGFiP (Statistiques n° 45) says receipts also include unpaid
amounts from earlier notices and the yield of tax audits. Line 1406 also
carries what remains of the old ISF (its 2023 value, 2 354 M€, equals DGFiP's
"ISF / IFI" series). For 2022 the Cour des comptes (S2023-1489) puts notices at
1,8 Md€ and IFI receipts at 2,1 Md€, the gap including 197 M€ of supplementary
declarations and audit results, and about 0,3 Md€ of residual ISF on top.
Notices measure what current holders pay each year; receipts add catch-up and
the tail of a tax that no longer exists. Notices stay the reference; receipts
would add 0,44 Md€ to the IFI variants.

IFI is a tax on net real-estate wealth, buildings included. Replacing it with
a tax on land shifts its burden from expensive buildings to valuable land; the
toggle exists because whether to include it is a political choice, not a
measurement one.

### Rental income (S3, national) — IR 4 198 + PS 2 399 + CSG 1 093 M€, 2022

CPO, *Pour une fiscalité du logement plus cohérente* (December 2023), p. 23,
and its background study (rapport particulier n° 1, p. 47 and table 28), both
taken from the compte du logement 2022 (part 6, table 1). Housing only,
individuals, net of income-tax reductions such as Pinel.

The CPO's total of 8,3 Md€ is the compte du logement line « impositions sur les
revenus immobiliers », 8 264 M€: IR 4 198 + PS 2 399 + CSG 1 093 + contribution
sur les revenus locatifs (CRL) 107 + corporate tax (IS) 467. The earlier
version of this note read the PS and CSG lines as possibly overlapping; the
background study shows them as separate lines that add up, so CSG is now its
own line (+1 093 M€). CRL and IS are paid by companies and stay out (D3).

The split between "PS" and "CSG" in the compte du logement is an accounting
convention (CSG jumps from 87 M€ in 2017 to 1 016 M€ in 2018 while PS barely
moves); only their sum, 3 492 M€, is reliable.

Still missing:
- **A recent year.** The compte du logement 2024 gives 8 895 M€ for 2024, same
  line, no breakdown, and revises 2022 to 8 541 M€. Scaling gives about
  8,0–8,3 Md€ for the three lines in 2024 (+0,3 to +0,6 Md€); not applied
  because no breakdown is published.
- **Furnished lets (BIC, D7).** No official yield. An estimate from the 2022
  tax-return boxes gives roughly 1,2–1,6 Md€ of IR + PS, assuming a 20–30 %
  average marginal rate: an order of magnitude, not a source. Under D7 the
  line stays out and is flagged.
- **Non-residential lettings by individuals.** Inside declared revenus fonciers
  (≥ 31 Md€ net for 2022 across all property, DGFiP) but not split out by
  DGFiP. No figure.

## Land base

INSEE, Chiffres-clés « Patrimoine national par secteur institutionnel et grand
type d'actif » (30 July 2026), provisional figures for end-2025: built land
7 032 Md€, of which general government 941 Md€. Public land is exempt from
property tax (CGI art. 1382 1°, only when it serves a public purpose and earns
no income) and is removed, leaving 6 091 Md€. End-2024 final: 6 729 Md€, of
which 903 public (Insee Première n° 2081).

INSEE revised its accounts in 2026: the 2023 fall in land values is now 8,6 %
(previously 13,7 %), and 2024 is −2,7 %. The earlier version of this table used
end-2023 (6 346 / 916, Insee Première n° 2028); the move to end-2025 lowers
the indicative rates by about 11 % and aligns the base with the 2025 yields.

Of the 6 091 Md€, households and non-profits hold 4 190 Md€ and companies
1 901 Md€ (non-financial 1 701, financial 200; INSEE T_8200_2025).

Caveats:
- **Agricultural and natural land (D6), revised 29 October: outside the
  reform.** It keeps today's TFPNB with its exemptions, so neither its value
  nor its TFPNB enters the totals. Only the TFPNB on other unbuilt land
  (cadastral groups 7, 10–13: quarries, building plots, amenity land,
  railways, sols) is replaced: 263 M€ in 2024, 266 M€ in 2025. The split is
  not published; it was rebuilt commune by commune from the REI (OFGL): the
  TAFNB base covers exactly groups 7 and 10–13 (BOI-IF-AUT-80; the art. 1394 B
  bis exemption covers the mirror groups 1–6, 8, 9, BOI-IF-TFNB-10-40-50), so
  TAFNB base ÷ TFPNB base gives each commune's non-agricultural share of its
  TFPNB, and the whole TAFNB (≈ 99 M€) is non-agricultural. Cross-check: the
  2024 base of the 20 % agricultural exemption implies an agricultural base of
  2 046 M€ after the exemption, against 2 059 M€ by this method (0,6 %; 2 028
  against 2 032 on mainland France excluding Corsica, where farmland is wholly
  exempt). Script: `docs/research/tfpnb_farm_split.py`, which downloads the
  REI rows and reproduces 1 032,9 and 922,2 M€. Agricultural
  and natural: 1 033 M€ in 2024 (80 %), 922 M€ in 2025 (78 %; the agricultural
  exemption rose from 20 % to 30 % in 2025, LF 2025 art. 66). "Agricultural"
  here is the legal bucket, which includes forests, heath, water and vegetable
  gardens. Caveats: cadastral groups are not PLU zones (a field zoned U stays
  in group 1 until reclassified, so some building land is counted as farmland);
  the State's compensation for the agricultural exemption (≈ 131 M€, 2024)
  stays outside, like the other compensations. Research note and scripts: the
  agent pass of 29 October, reproduced before use.
  **Sensitivity, farmland in at SAFER price × area (D6 as decided on 27
  October):** `yields.Farmland`: SAU des exploitations 2025, metropolitan France
  (Agreste, SAA 2025 provisional) 26,64 Mha, of which vines 0,748 Mha.
  The other 25,89 Mha (arable, grassland, orchards and other permanent crops)
  are valued at the midpoint of the SAFER 2025 prices for vacant (6 460 €/ha)
  and let (5 350 €/ha) land; vines at the AOP price excluding Champagne
  (87 400 €/ha), which undervalues Champagne and overvalues non-AOP vines.
  Result 218 Md€ (204–233 using either price alone; the vine price is a further
  uncertainty of perhaps ±30 Md€), 3,5 % of the taxable base of 6 309 Md€.
  With farmland in and its TFPNB replaced too, the S1 rate is 1,06 % and
  farmland would pay ≈ 2,3 Md€ a year, against 0,9 Md€ of TFPNB today.
  INSEE's terrains cultivés (AN.2112, 902 Md€ at end-2025, *Comptes de la
  Nation 2025*, T_8201; companies 710, households 193) is not used: it implies
  ≈ 31 500 €/ha, about five times observed prices, and INSEE publishes no
  method. Forests (17,5 Mha at 4 950 €/ha, timber included, so an upper bound
  of 87 Md€) stay out; they would lower rates by about 1,4 %. Public ownership
  of farmland is not removed (small, unmeasured).
- **Public land.** The APU column includes land under roads and networks; the
  commune-level model must exclude the same land, or national and local rates
  will not reconcile.
- **Exempt private land stays in the base.** Recent social housing is exempt
  from TFPB for 15 to 30 years (CGI art. 1384 A; the 25–30-year terms apply to
  funding decided before the end of 2026), and HLM housing in priority
  neighbourhoods has a 30 % abatement for 2025–2030 (art. 1388 bis). The
  yields exclude what these owners do not pay, while their land is in the
  base, so the indicative rate is understated by an unmeasured amount.
- **Companies in S2 and S3.** The national tier charges companies' land
  (1 901 Md€, 31 % of the base) the national rate, but S2 and S3 remove only
  individuals' taxes on gains and rents; companies' corporate tax on the same
  income stays (D3). At 31 % of the base, the national lines added by S2–S3
  (11,4 Md€ in S3, 13,7 with IFI) put about 3,5 to 4,3 Md€ a year onto
  companies' land, to fund cuts for individual landlords and sellers.
  Shown on the site since 27 October (`yields.companies_shift`, exported as
  `companies_shift_meur`): companies' share of taxable built land (31,2 %),
  applied to the whole base, times the S2–S3 lines: S2 1 147 M€, S2 + IFI
  1 875, S3 3 548, S3 + IFI 4 275. Upper estimate on one count: if INSEE puts
  in S11 some property companies whose partners pay IR, those partners also
  gain from the cut. Economic incidence (pass-through to tenants or
  shareholders) is not modelled.

## Left out, with yields (for decision)

| Item | Yield | Natural place | Status here |
|---|---:|---|---|
| State compensations for exempt property (mostly industrial) | ≈ 2,7 Md€ (2025) | S1, if the exemptions go | Out (not a tax); stated. Since 2026 multiplied by 0,807 (loi 2020-1721, art. 29 III-A-4) |
| Contribution de sécurité immobilière (0,10 %, CGI art. 881 K) | 745 M€ (2025, provisional); 692 (2024) | S1, paid by the buyer at each sale | Out; stated |
| Île-de-France office tax (TSBCS, CGI art. 231 ter) | ≈ 0,93 (2023) to 1,0–1,06 Md€ (2025), rebuilt from its beneficiaries | S1 toggle (a tax on floor area, not land) | Out; stated |
| TEOM | 9 164 M€ (2025) | Out: service charge | Stated |
| CFE | 8 219 M€ (2025) | Out: tax on business occupancy | Stated |
| Île-de-France regional DMTO on offices (CGI art. 1599 sexies) | 47 M€ (avg 2021–25) | S1 | Out (no regional tier in the model); small |
| Chambres d'agriculture | 345 M€ | S1 once agricultural land is in | Out until D6 |
| Contribution sur les revenus locatifs | 107 M€ (2022) | S3, mostly companies (D3) | Out |
| Vacant-dwelling taxes (THLV, TLV) | 124 M€ (THLV 2025) | Out: penalty taxes the LVT supersedes | Out |

## Open points

1. Rental income: a recent-year breakdown; furnished lets (D7) and
   non-residential lettings.
2. Agricultural land (D6): decided, SAFER price × area. Still open: forests,
   the share of farmland let versus vacant (the midpoint stands in for it), and
   the vine mix by appellation.
3. D1 in constant euros: decided 27 October, shown as a sensitivity only
   (+1,0 Md€ on S1, +1,9 on S3).
4. The inclusion choices above: compensations, CSI, TSBCS (decided 27 October:
   kept out; THRS added to S1).
5. The transfer onto companies' land in S2–S3 (D3): shown on the site.
   Open: how INSEE classifies property companies taxed at IR.

## Gemini critique (model `gemini-4-argon`, 2026-10-27) and how I responded

The questions, Gemini's full reply and the three verification reports are in
[`gemini-argon-2026-10-27/`](gemini-argon-2026-10-27/README.md). Every factual claim
was checked against a primary source (Légifrance, DGFiP, INSEE, OFGL, CPO,
Cour des comptes, Agreste) before anything changed. Points f–g (capitalisation
and rents) are answered in `dynamic-effects.md` on spec 0005's research-notes
branch.

| Gemini point | My response |
|---|---|
| **a.** Keep the 5-year average; do not scale earlier years to the 5 % cap, which is temporary (LF 2025 art. 116, 1 April 2025 to 31 March 2028). | **Adopted (no change).** Verified on Légifrance; Gemini missed that first-time buyers are excluded and that rates revert in April 2028, which strengthens the point. |
| **a.** Restate 2020–2024 in 2025 euros (≈ +0,8–1,0 Md€); align the DMTO and gains windows. | **Partly adopted.** Computed with INSEE CPI: +1,01 Md€ on S1, +1,32 on S2–S3. Shown as a sensitivity, not applied: it changes decision D1. Windows **not** aligned: 2025 gains are not published, and D1 takes the last five available years. |
| **b(i).** Put syndicates, TSE, GEMAPI and TASA (0,9 Md€) in S1: same base, same bill. | **Adopted.** New line `tf_annexes`, 923 M€ (REI 2025, re-queried), plus 47 M€ of State's fee. |
| **b(ii).** THRS: keep out of core S1, offer as a toggle; THRS carries a 5,4 % State fee; the 391 M€ surcharge may be extra. | **Partly adopted.** Kept out, as before. The **5,4 % is wrong**: art. 1641 gives 3 %. The surcharge is indeed **not** inside the 2 583 M€ (checked by recomputing Paris and Bordeaux): 2 974 M€ with it, now stated. |
| **b(iii).** Include the State's compensations (≈ 2,7 Md€), codified at "CGI art. 1499-0 A"; otherwise halve industrial land in the base. | **Rejected.** The compensation is State money, not a tax paid by owners: replacing only the tax keeps each commune whole (it still receives the compensation) and equal yield holds for taxpayers. Including it is a decision to end the industrial relief, not a measurement correction. The citation is wrong: the halving is in art. 1499, and the compensation is uncodified (loi 2020-1721, art. 29 III-A). Gemini also missed that it has been cut by a factor of 0,807 since 2026. |
| **b(iv).** Keep TEOM and CFE out; document CFE prominently. | **Adopted (no change).** Both are already stated on the page. |
| **b(v).** Include both State fees; art. 1641 = 1 % (I-A) + 2 % (I-B-1); art. 1647 V = 2,37 % / 2,14 %. | **Partly adopted.** Both fees stay in. Art. 1647 V confirmed. The 1641 total of 3 % is right but **Gemini's split is reversed**: 2 % (I-A) + 1 % (II). |
| **c.** Keep notices (2,3 Md€); the gap to receipts is audits and old ISF, ≈ 0,4–0,6 Md€. | **Adopted, with a corrected explanation.** DGFiP n° 45 attributes the gap to arrears on earlier notices and to tax audits; IFI audits are about 0,1 Md€ a year (Cour des comptes, 2022), and line 1406 also carries ISF residuals. The 2025 receipt is 2 771 M€ collected, not the 2 965 M€ forecast. Notices updated to DGFiP's exact 2 159 / 2 332. |
| **d.** Removing public land is right (art. 1382 1° requires public use and no income); social-housing land stays in the base and understates rates by 5–8 %. | **Partly adopted.** Art. 1382 1°, 1384 A and 1388 bis verified and stated. Gemini's 5–8 % is unsourced and not used; the bias is stated without a size. |
| **d.** Agricultural land: INSEE AN.2112 ≈ 170–230 Md€; SAFER ≈ 200–250 Md€; add chambres d'agriculture. | **Partly adopted.** The **INSEE figure is wrong**: AN.2112 is 902 Md€ (T_8201). The SAFER-based order of magnitude holds (≈ 190–270 Md€ for farmland at 2025 prices). The gap between the two is now an open point for D6. Chambres d'agriculture already listed. |
| **e.** The CSG line (1,1 Md€) is additional to PS; S3 omits it. Net declared revenus fonciers ≈ 20 Md€. Move to the 2024 total (8,9) split 55/45. | **Partly adopted.** CSG confirmed as a separate line in the CPO's background study and added (+1 093 M€). The 8,3 Md€ gap is corporate tax (467 M€), not "minor items". **Rejected:** declared revenus fonciers are ≥ 31 Md€ (DGFiP), and the 55/45 split of the 2024 total has no source. |
| **e.** LMNP ≈ 0,5–0,8 Md€; non-residential lettings ≈ 0,5–0,8 Md€. | **Rejected as figures.** No source found for either. Our own order of magnitude for LMNP is higher (1,2–1,6 Md€); both stay flagged as missing (D7). |
| **h.** IS on companies' gains and rents: S2–S3 charge companies' land the national rate while removing only individuals' taxes. | **Adopted as a caveat.** INSEE confirms companies hold 1 901 Md€ of built land (31 % of the base). The transfer is now stated under *Land base*; no yield added (D3). |
| **h.** TSBCS ≈ 0,95–1,10 Md€; CSI ≈ 0,25–0,30 Md€; add to S1. | **Partly adopted.** TSBCS ≈ 0,93–1,06 Md€, rebuilt from what each beneficiary receives (no official total found). **CSI is 2,5–3 times higher than Gemini said**: 745 M€ (2025), and its rate is in art. 881 K, not 879. Both are now in the *Left out* table, for decision. |
| **h.** Pinel-type reductions (≈ 1,5–2,0 Md€): is the CPO's IR gross or net? | **Adopted (clarification).** Duflot/Pinel cost 1 469 M€ in 2024 (PLF 2026, Voies et moyens II); the compte du logement's IR is net of them, now stated. |
