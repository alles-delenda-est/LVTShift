# Yields to replace — sources and reconciliations (October 2026)

Companion to `yields.py` and spec 0005 §3. Each figure in `yields.py` was read
on 26 October 2026 from the source named on its line, then re-derived by an
independent verification pass (same day) that read the primary sources
separately. This note records the choices that are not visible in the table:
scope, series breaks, corrections and what is left out.

Status of each line: **verified** (read from the primary source), **derived**
(computed from primary figures, method stated) or **reported** (a secondary
source quoting the primary). Reported lines are listed under *Open points*.

## Result

| Scenario | Yield to replace (M€) | Indicative rate, % of taxable built land |
|---|---:|---:|
| S1 — TF + DMTO | 63 081 | 1,04 |
| S2 — + taxes on real-estate gains | 66 757 | 1,10 |
| S2 + IFI | 69 057 | 1,13 |
| S3 — + taxes on rental income | 73 357 | 1,20 |
| S3 + IFI | 75 657 | 1,24 |

S1 is 83–94 % of every variant; the taxe foncière with the State's fee
(45,3 Md€) is 60–72 %. The choice of scenario changes the national rate by at
most a fifth; the local tier (TF + communal DMTO, 47,4 Md€) is identical in all
five.

Rates are national averages against built land only. They will fall once
agricultural and natural land is added (D6, not yet sourced) and are not the
rates the model applies: the local tier is set commune by commune.

## Corrections made by the verification pass

| Change | Effect on totals |
|---|---:|
| Paris's communal DMTO was counted twice (in OFGL's departmental aggregate and in the communal accounts) | −336 M€ |
| Single authorities of Corse, Martinique and Guyane were missing from departmental DMTO | +138 M€ |
| State's fee on DMTO recomputed on the corrected base | −5 M€ |
| State's 3 % fee on the taxe foncière added, for consistency with the fee on DMTO | +1 319 M€ (S1) |
| 2024 IR on gains counted the surtax and land taxes twice | −18 M€ (S2, S3) |
| Land base moved to INSEE end-2025 (provisional), after INSEE revised its accounts | rates −11 % |

## Line by line

### Taxe foncière bâtie (S1, local) — 42 776 M€, 2025

OFGL's REI dataset (DGFiP's *recensement des éléments d'imposition*),
« MONTANT RÉEL », commune share 40 157 M€ + intercommunal share 2 619 M€.

Scope matches the model (commune + EPCI). Excluded and stated on the page:
syndicates (184 M€), taxes spéciales d'équipement, GEMAPI and TASA (710 M€ on
built property in 2025; 923 M€ with the non-built parts and syndicates), and
the TEOM (9,2 Md€), a charge for a service. DGCL BIS 209 gives about
43,1 Md€ for all TFPB in 2025, consistent with commune + EPCI + syndicates
(42 961 M€).

Why not the CPO's 25,5 Md€ or the compte du logement's 30,5 Md€: both cover
housing only. A land value tax replaces the tax on all built property,
offices, shops and industry included.

### Taxe foncière non bâtie (S1, local) — 1 188 M€, 2025

REI, FNB commune + EPCI + taxe additionnelle (TAFNB). Falling (1 296 M€ in
2024). Excludes chambres d'agriculture (345 M€), which belong in S1 only once
agricultural land is in the base (D6).

### Taxe foncière — State's fee (S1, national) — 1 319 M€, 2025

The State adds 3 % to the taxe foncière of communes and intercommunalities for
assessment, relief and bad debts (CGI art. 1641), paid by the taxpayer. The REI
records 2 068 M€ of such fees on the whole bill in 2025, TEOM and other levies
included at higher rates; 3 % of the TF in scope is consistent with that total.
The rate was not read on Légifrance (blocked from here). The line is included
because the equivalent fee on DMTO is; counting one and not the other would be
inconsistent.

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
The average also mixes rate regimes: since April 2025 departments may charge
up to 5 % (until March 2028), against 4,5 % before.

### DMTO — State's fee (S1, national) — 333 M€, derived

CGI art. 1647 V: the State levies 2,37 % on top of the departmental duty
(2,14 % where the departmental rate is the reduced 0,70 %). Applied at 2,37 % to
the whole corrected departmental series, a slight overstatement.

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

The PS lines are 17,2 % of the gain, of which 7,5 points (prélèvement de
solidarité) go to the State, not Social Security. The 2026 increase in CSG on
capital income spares real-estate income and gains according to secondary
sources; not checked against the LFSS text.

Companies' gains (IS) are excluded: no public figure (D3).

### IFI (S2 toggle, national) — 2 300 M€, 2025

DGFiP Statistiques n° 15, 23, 33 and 45: 1,8 / 1,9 / 2,2 / 2,3 Md€ for 2022–2025
(2025: 193 600 households). These are amounts on tax notices. Budget receipts
are higher: 2 739 M€ in 2024 and 2 965 M€ forecast for 2025 (PLF 2026, Voies et
moyens, line 1406). The source does not explain the gap; late payments and
reassessments are a plausible cause, not a confirmed one. Using receipts would
add 0,4–0,7 Md€ to the IFI variants.

IFI is a tax on net real-estate wealth, buildings included. Replacing it with
a tax on land shifts its burden from expensive buildings to valuable land; the
toggle exists because whether to include it is a political choice, not a
measurement one.

### Rental income (S3, national) — IR 4 200 M€ + PS 2 400 M€, 2022

CPO, *Pour une fiscalité du logement plus cohérente* (December 2023), p. 23,
housing only. The same page lists CSG on property income (1,1 Md€) and the
contribution sur les revenus locatifs (0,1 Md€), and a total of 8,3 Md€ that its
own lines do not reach (7,8 Md€). Neither reading of the CSG line fits a 17,2 %
rate: if PS included CSG, the CSG share would be about 1,3 Md€; if not, about
2,8. The compte du logement 2024 gives 8,9 Md€ but does not break out these
lines. Commercial lettings by individuals and furnished lets (BIC, D7) are
missing. Both lines stay "reported"; S3 could move by about −1,1 to +1,5 Md€.

## Land base

INSEE, Chiffres-clés « Patrimoine national par secteur institutionnel et grand
type d'actif » (30 July 2026), provisional figures for end-2025: built land
7 032 Md€, of which general government 941 Md€. Public land is exempt from
property tax and is removed, leaving 6 091 Md€. End-2024 final: 6 729 Md€, of
which 903 public (Insee Première n° 2081).

INSEE revised its accounts in 2026: the 2023 fall in land values is now 8,6 %
(previously 13,7 %), and 2024 is −2,7 %. The earlier version of this table used
end-2023 (6 346 / 916, Insee Première n° 2028); the move to end-2025 lowers
the indicative rates by about 11 % and aligns the base with the 2025 yields.

Two caveats:
- **Coverage.** Built land only. Agricultural and natural land (D6) is not
  isolated in these publications. "Autres actifs non produits" (1 982 Md€ end-
  2024) contains it among other items and is only an upper bound.
- **Public land.** The APU column includes land under roads and networks; the
  commune-level model must exclude the same land, or national and local rates
  will not reconcile. Legally exempt private property (e.g. recent social
  housing) remains in the base, so the rate is slightly understated.

## Left out, with yields (for decision)

| Item | Yield | Natural place | Status here |
|---|---:|---|---|
| TSE, GEMAPI, TASA, syndicates on the TF bill | 923 M€ (2025) | S1: same base, same bill | Out (levied by bodies other than the commune); stated |
| Taxe d'habitation on second homes (THRS) | 2 583 M€ (2025); 3 255 (2024) | Optional S1 toggle | Out; stated |
| State compensations for exempt property (mostly industrial) | ≈ 2,7 Md€ (2025) | S1, if the exemptions go | Out (not a tax); stated |
| TEOM | 9 164 M€ (2025) | Out: service charge | Stated |
| CFE | 8 219 M€ (2025) | Out: tax on business occupancy | Stated |
| Île-de-France regional DMTO on offices (CGI art. 1599 sexies) | 47 M€ (avg 2021–25) | S1 | Out (no regional tier in the model); small |
| Chambres d'agriculture | 345 M€ | S1 once agricultural land is in | Out until D6 |
| Contribution sur les revenus locatifs | ≈ 100 M€ (2022) | S3, mostly companies (D3) | Out |
| Vacant-dwelling taxes (THLV, TLV) | 124 M€ (THLV 2025) | Out: penalty taxes the LVT supersedes | Out |
| Contribution de sécurité immobilière, IdF office tax (TSBCS) | not found | S1 / toggle | Unknown |

## Open points

1. Rental income: settle the CPO's CSG line and its 8,3 vs 7,8 Md€ total;
   find figures for commercial lettings and furnished lets (D7).
2. Agricultural and natural land (D6): INSEE detailed account (AN.2112
   "terrains cultivés") or Agreste price × area.
3. IFI basis: notices (used) or budget receipts.
4. DMTO average across the 2025 rate change: keep D1, or weight to current law.
5. The four inclusion choices above (TSE etc., THRS, compensations, regional DMTO).
6. CGI art. 1641 (3 %) and 1647 V (2,37 %) to be read on Légifrance.
