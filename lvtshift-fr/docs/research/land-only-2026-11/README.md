# The land-only tax and its sensitivity band (November 2026)

**Decision (project lead, 11 November 2026):** the reform taxes land alone,
at its site value (as if vacant, at the zone's typical density), buildings
untaxed. Until then the commune results used a 4:1 split rate. The upstream
`model_full_building_abatement` at 100 % does the solve, so upstream stays
unmodified.

**Consequence for the band:** under a land-only tax each parcel pays
levy × L_i / ΣL, so scaling all land by one factor changes no bill. The
split-rate band (land share ±10 points, uniform scaling) would have shown no
uncertainty at all.

**First proposal (rejected by Gemini, rightly):** shift each parcel's land by
k × its own building value. That made two identical plots in one IRIS move
differently according to what stands on them, against the logic of the site
value, which shares land within an IRIS by plot area and permitted density.

**What we did, following Gemini (02):**
- Shock building values ±20 % (not "land share ±10 points"): directly
  interpretable as construction-cost uncertainty, and it avoids distortions
  in communes whose land share is low.
- Apply it where building cost enters land: each IRIS's built land total
  (L − 0.2 B, clipped to [0, L + B]), every built parcel of the IRIS moving by
  the same factor. Building-less parcels, priced from plot sales, do not move;
  Gemini's version scaled them too, which is wrong for land not valued by the
  residual.

**Known limits:** the shock is applied to the exported values, without
re-running the site-value step; cost-priced parcels (sheds, retail boxes)
move with their IRIS. In a commune of one IRIS with no vacant land, the band
is zero: correct for a uniform cost error, but the within-IRIS uncertainty
remains.

**Not covered, and now the main uncertainty:** the within-IRIS sharing of
land by plot area × the zone's reference floor-area ratio^0.5 (at permitted use since 2026-11-11). The exponent
and the reference density decide who pays between dense flats, houses on large
plots and vacant land. A second band on the exponent is the obvious follow-up.
