# Brief sent to Gemini (gemini-4-argon), 11 November 2026

You are reviewing a modelling design for a French land value tax study. Please critique it as an expert in French local taxation (fiscalité directe locale) and property economics. Be specific and blunt; say where the design is wrong, not only where it could be better.

CONTEXT
The model simulates, for 188 French communes, a revenue-neutral replacement of the taxe foncière sur les propriétés bâties (TFPB) and the non-agricultural part of the TFPNB by a "taxe foncière sur la valeur nue" (TFVN). Per parcel:
- Market value: hedonic model on open DVF transactions; land value: site value from comparables; improvement value = market value - land value.
- TODAY'S TAX (baseline): the commune's real TFPB amount (REI) is shared across built, non-exempt parcels in proportion to floor area, with per-m2 weights calibrated so that three groups (industrial establishments, professional premises, housing+other) each carry their official REI share. Social housing exemptions (CGI 1384 A/C) and the QPV 30 % abatement reduce the housing weight. Unbuilt non-agricultural land carries the commune's TFPNB (non-agricultural share) + TAFNB, shared by area. We do NOT have the real 1970 rental values (Fichiers fonciers are restricted access), so the baseline uses floor area as the proxy for the VLC within each group, deliberately with no market-value tilt.
- REFORM: one revenue-neutral solve over land and improvements with land taxed at 4x the improvement rate; social housing exemptions end; farmland and exempt public property stay outside.

REQUEST FROM THE AUTHOR
Separate the redistributive effect of revaluing the 1970 rental values from the effect of moving to a land-based tax. Many of the gains for poorer neighbourhoods may come simply from updating an obsolete base, which a revaluation alone would deliver.

PROPOSED DESIGN
Add an intermediate per-parcel bill, "revalued_tax", the counterfactual of the pending housing revision (RVLLH) alone:
1. Each tax group keeps its share of the TFPB amount (professional premises were already revised in 2017; industrial premises are valued by the accounting method). Only the housing group's amount is redistributed.
2. Within the housing group, each parcel's weight = parcel market value x (housing floor / total floor of the parcel) x social housing factor (exemptions and QPV abatement kept, since a revaluation does not change exemption rules).
3. Unbuilt land keeps today's TFPNB/TAFNB bill; exempt property stays exempt.
4. Decomposition: revaluation effect = revalued_tax - today's tax; land-tax effect = new_tax (TFVN) - revalued_tax. Published as aggregate EUR and % changes by property category and by household income quintile (medians are not additive, so the decomposition uses group totals).

QUESTIONS
a) Is parcel market value a defensible proxy for the RVLLH's revised rental value within a commune? The RVLLH sets tariffs per m2 by sector from declared rents. Rental yields fall as prices rise, so a value proxy may overstate the transfers. Would floor area x a sector-level rent per m2 (e.g. the open "carte des loyers" is only commune-level) be better, or is there a simple yield adjustment you would apply (e.g. weight = value^b with b < 1)? What b would you defend, and from what evidence?
b) The baseline is itself a floor-area proxy, not the real 1970 VLC, which contains location elements (category, coefficient de situation). So "revaluation effect" here means "from size-based to value-based shares within housing". Is it honest to call it the effect of the revision, or must it be labelled differently? How would you word it for a general French audience?
c) Should the revaluation counterfactual keep each group's share fixed (neutralisation as in the 2017 RVLLP), or let housing's share move against professional/industrial premises? What does current law on the RVLLH provide?
d) Does the order of decomposition matter (revalue first then shift to land, vs shift first), and should we show both or just one? Interaction terms?
e) Anything else that would make the decomposition misleading: the social housing factor, mixed-use parcels, flats in co-ownership (one parcel, many owners), the unbuilt land bill, vacancy, the 4:1 split rate.

Answer each question in a short paragraph, then give your overall recommendation.
