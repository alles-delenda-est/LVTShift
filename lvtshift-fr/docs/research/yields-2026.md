# Yields to replace — sources and reconciliations (October 2026)

Companion to `yields.py` and spec 0005 §3. Each figure in `yields.py` was read
on 26 October 2026 from the source named on its line. This note records the
choices that are not visible in the table: scope, series breaks, and figures
we could not yet confirm.

Status of each line: **verified** (read from the primary source), **derived**
(computed from primary figures, method stated) or **reported** (a secondary
source quoting the primary). Reported lines are listed under *Open points*.

## Result

| Scenario | Yield to replace (M€) | Indicative rate, % of taxable built land |
|---|---:|---:|
| S1 — TF + DMTO | 61 964 | 1,14 |
| S2 — + taxes on real-estate gains | 65 658 | 1,21 |
| S2 + IFI | 67 958 | 1,25 |
| S3 — + taxes on rental income | 72 258 | 1,33 |
| S3 + IFI | 74 558 | 1,37 |

S1 is 83–94 % of every variant; the taxe foncière alone (44,0 Md€) is 59–71 %.
The choice of scenario changes the national rate by at most a fifth; the
local tier (TF + communal DMTO, 47,4 Md€) is identical in all five.

Rates are national averages against built land only. They will fall once
agricultural and natural land is added (D6, not yet sourced) and are not the
rates the model applies: the local tier is set commune by commune.

## Line by line

### Taxe foncière bâtie (S1, local) — 42 776 M€, 2025

OFGL's REI dataset (DGFiP's *recensement des éléments d'imposition*),
« MONTANT RÉEL », commune share 40 157 M€ + intercommunal share 2 619 M€.

Scope matches the model (commune + EPCI). Excluded and disclosed: syndicates
(184 M€), taxes spéciales d'équipement, GEMAPI and TASA (≈ 0,7 Md€ together,
to confirm),
and the TEOM, which is a charge for a service rather than a tax on property.
Including the first three would add ≈ 0,9 Md€ (+1,4 % on S1).

Why not the CPO's 25,5 Md€ or the compte du logement's 30,5 Md€: both cover
housing only. A land value tax replaces the tax on all built property,
offices, shops and industry included.

### Taxe foncière non bâtie (S1, local) — 1 188 M€, 2025

REI, FNB commune + EPCI + taxe additionnelle (TAFNB). Falling (1 296 M€ in
2024). Excludes chambres d'agriculture.

### DMTO — communes (S1, local) — 3 403 M€, average 2021–2025

OFGL grand livre, all budgets. The accounts changed between nomenclatures M14
and M57 during the period, so the sum is taken over c/7381 (M14), c/73123 (M57)
and c/7332, plus the departmental fund for communes under 5 000 inhabitants
(c/73223, c/73224), which redistributes the communal 1,2 % levied in those
communes. Equalisation transfers between authorities (c/739225, c/73225) are
not taxes and are left out.

Cross-check: DGCL BIS 190 gives 3,1 Md€ for 2023; we get 3 356 M€. The gap is
probably the fund for small communes. To confirm in the verification pass.

### DMTO — départements (S1, departmental) — 14 259 M€, average 2021–2025

OFGL comptes des départements, agrégat « DMTO avant péreq. ». Series:
16 511 / 16 776 / 13 044 / 11 297 / 13 669. Matches DGCL BIS 190 (13,0 Md€ in
2023).

The five-year average (D1) sits 4 % above 2025 and 15 % below the 2022 peak.
Taking the latest year instead would lower S1 by 0,6 Md€.

### DMTO — State collection fee (S1, national) — 338 M€, derived

CGI art. 1647 V: the State levies 2,37 % on top of the departmental duty
(2,14 % where the departmental rate is the reduced 0,70 %). Applied at 2,37 % to
the whole departmental series, a slight overstatement.

### Real-estate gains (S2, national) — IR 1 284 M€ + PS 2 410 M€, average 2020–2024

Cour des comptes, *L'imposition des plus-values immobilières des particuliers*
(25 November 2025), open-data files G9+10 (2017–2023) and T7 (2023–2024).
IR includes the 2–6 % surtax on large gains and the two taxes on land made
constructible (communal and national), all paid by the seller on the gain.

**Series break.** The two files overlap on 2023 and disagree:

| 2023 | G9+10 | T7 | Gap |
|---|---:|---:|---:|
| IR | 1 145 | 1 278 | +11,6 % |
| PS | 2 347 | 2 583 | +10,1 % |
| All lines | 3 625 | 3 994 | +10,2 % |

We use G9+10 for 2020–2023 and T7 for 2024, the only source for that year.
If T7's higher basis applies throughout, the average is understated by ~2 %;
if G9+10's applies, 2024 is overstated by ~10 % and the average by ~2 %. Either
way the effect on S2 is under 0,1 Md€. The Cour's own average for 2017–2024
(3,5 Md€) is consistent with ours (3,7 Md€ over 2020–2024).

Companies' gains (IS) are excluded: no public figure (D3).

The CPO gives 2,8 Md€ for 2022 against the Cour's 4,7 Md€. The CPO figure is
housing-only; whether that explains the whole gap is not established. We use
the Cour, which covers all property sold by individuals.

### IFI (S2 toggle, national) — 2 300 M€, 2025

DGFiP Statistiques n° 23 gives 1,9 Md€ for 2023. The 2,2 (2024) and 2,3 (2025)
figures are DGFiP numbers quoted by the press; the compte du logement 2024 gives
2,64 Md€. Reported, not verified.

IFI is a tax on net real-estate wealth, buildings included. Replacing it with
a tax on land shifts its burden from expensive buildings to valuable land; the
toggle exists because whether to include it is a political choice, not a
measurement one.

### Rental income (S3, national) — IR 4 200 M€ + PS 2 400 M€, 2022

CPO, *Pour une fiscalité du logement plus cohérente* (December 2023), p. 23.
The same page lists CSG on property income (1,1 Md€) and the contribution sur
les revenus locatifs (0,1 Md€), and a total of 8,3 Md€ that its own lines do
not reach (7,8 Md€). The compte du logement 2024 gives 8,9 Md€ for housing.
Which of these overlap is not stated. Furnished lets (BIC regime) are not
separated (D7). Reported until the scope is settled; S3 could move by
±1,5 Md€ on this alone.

## Land base

INSEE, Insee Première n° 2028 (December 2024), national accounts base 2020:
built land 6 346 Md€ at end-2023, of which general government 916 Md€.
Public land is exempt from property tax and is removed, leaving 5 430 Md€.

Two mismatches to keep in mind:
- **Year.** Land is end-2023, after a 13,7 % fall in one year; yields are
  2025 or five-year averages. If land has recovered since, rates are
  overstated.
- **Coverage.** Built land only. Agricultural and natural land (D6) is not
  isolated in this publication.

## Open points (for the verification pass)

1. IFI 2024 and 2025: read the DGFiP publications themselves; reconcile with
   the compte du logement's 2,64 Md€.
2. Rental income: settle which of the CPO lines and the compte du logement
   cover what; decide whether CSG on property income belongs with PS.
3. Communal DMTO: reconcile 3 356 M€ (ours, 2023) with DGCL's 3,1 Md€.
4. TFPB: confirm the 2025 REI totals against DGCL BIS 210, and the ≈ 0,7 Md€
   of TSE, GEMAPI and TASA.
5. Land base: source agricultural and natural land (D6).
6. LMNP / furnished lets: find a yield or confirm none exists (D7).
