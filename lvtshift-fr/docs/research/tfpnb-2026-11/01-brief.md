# Replacing the TFPNB on non-agricultural unbuilt land in a commune-level land value tax model (France)

You are reviewing a design as an independent expert in French local taxation (TFPB, TFPNB, TAFNB, cadastral valuation) and tax-incidence modelling. Be concrete and critical. Say plainly where the design is wrong, and rank the issues. Flag anything you are unsure of.

## Context

A civic open-data model shifts each commune's taxe foncière revenue-neutrally onto a 4:1 split-rate tax on land and buildings. Until now the revenue held constant was the TFPB only (REI 2025 "montant réel", commune + EPCI shares). Building-less parcels therefore carried a modelled tax of 0 today, and their new land tax appeared as a rise from nothing.

Unbuilt agricultural and natural land (PLU zones A and N) is outside the reform: it keeps today's TFPNB and takes no share of the new tax.

The project owner has now decided that the reform REPLACES the TFPNB on the other unbuilt land (building plots and the like), rather than sitting on top of it. The national scenario page of the same project already assumes this.

## Proposed design

1. Amount replaced, per commune, from the REI 2025 (via OFGL):
   - non-agricultural share = TAFNB base (B11TAFNB + B31TAFNB + B31MGPTAFNB) / TFPNB base (B11 for the commune, B31 for the EPCI), capped at 1. Reason: the TAFNB (CGI art. 1519 I) is assessed on cadastral groups 7 and 10 to 13 only (quarries, building plots, amenity land, railways, sols), and the art. 1394 B bis exemption covers the mirror groups, so this ratio is the non-agricultural share of the TFPNB base. One TFPNB rate applies to all groups in a commune, so the share applies to the amount.
   - amount = share x B13 (commune TFPNB) + share x B33 (EPCI TFPNB) + the whole TAFNB amount (B13TAFNB + B33TAFNB + B33MGPTAFNB).
   - Syndicate shares, TSE, GEMAPI and the chambers of agriculture tax are left out, as they are for the TFPB.
   - Measured: this is 0.1 % to 0.8 % of the commune's TFPB (Paris 1.7 M EUR against 1,841 M EUR of TFPB; La Rochelle 0.29 M EUR; Villeurbanne 0.21 M EUR; Sète 0.37 M EUR; Cahors 0.11 M EUR, where the non-agricultural share is 51 %).
2. The revenue held constant becomes TFPB + this amount.
3. Today's tax on a parcel: built parcels share the TFPB as before (by floor area, calibrated by tax group). The replaced amount is shared among building-less parcels that are inside the reform (not zone A/N, not exempt public property), in proportion to parcel area.
4. Result: vacant land gets a real percentage change. Measured on the current run: about +83 % in Sète, +89 % in Villeurbanne, +408 % in Montreuil, +750 % in Lyon, +960 % in Paris, x30 in La Rochelle, x48 in Annemasse. Within a commune nearly every vacant parcel gets the same percentage, because the model also prices vacant building land at one EUR/m2 per commune (terrain-à-bâtir comparables are too thin for finer cells), so the new tax is proportional to area too.

## Known weaknesses I would state

- Cadastral groups are not PLU zones. A field zoned U stays in an agricultural group until reclassified: it pays the land tax in the model while its (agricultural) TFPNB is not in the replaced amount. Amenity land in an N zone is the reverse.
- The non-agricultural TFPNB is also paid on the excess gardens of built parcels (terrains d'agrément as a separate fiscal subdivision of a house's parcel), on quarries and on railway land. The model gives all of it to building-less parcels, which overstates their tax today.
- The distribution between parcels is unknown (1961/1980 cadastral tariffs by class, never revalued), so the percentage is a commune average, not a parcel result.

## Questions

1. Is the TAFNB-base method right for the non-agricultural share, and is adding the whole TAFNB amount right? Is the art. 1396 surcharge on building land (majoration de la valeur locative, optional, per m2) inside B11/B13? Is it inside the TAFNB base? If it is in the TFPNB base but not the TAFNB base, how does that bias the share, and can it be corrected from open REI lines?
2. Sharing by parcel area: is that the best open-data proxy, or would you share by modelled land value, or by something else? Is there any open source for the cadastral nature (groupe de nature de culture) or the revenu cadastral per parcel?
3. How material is the garden problem? Is there any way to bound the share of the non-agricultural TFPNB paid on built parcels' gardens (group 11) against building plots (group 10)?
4. Are there other components that a reform replacing "the TFPNB on building land" should also remove or keep (taxe pour frais de chambres d'agriculture, TSE, GEMAPI, frais de gestion, the State's compensations for TFPNB exemptions)?
5. Presentation: a category whose tax rises by +400 % to x48 next to categories at -85 % to +110 %. Would you show a percentage, a multiple, or euros? What is the honest one-sentence caveat for a general reader?
6. Anything else that would silently bias the result.
