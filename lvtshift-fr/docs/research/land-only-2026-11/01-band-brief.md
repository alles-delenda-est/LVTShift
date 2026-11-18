# Brief sent to Gemini (gemini-4-argon), 11 November 2026

You are reviewing a sensitivity-analysis design for a French land value tax model. Be concise and blunt; say if it is wrong.

CONTEXT: per parcel we have market value V (hedonic, DVF), building value B (depreciated replacement cost) and land value L. Land is a residual V - B at neighbourhood (IRIS) level, then re-shared within the IRIS by plot area x max(own floor-area ratio, zone-typical FAR)^0.5 ("site value"). The reform is changing from a 4:1 split-rate tax (land taxed 4x buildings) to a PURE land tax: each parcel pays levy x L_i / sum(L), revenue-neutral per commune.

OLD BAND (for the 4:1 tax): "land share +/-10 points": every parcel's L scaled by one factor and B by another, so the aggregate land share moves 10 points, total value fixed, then re-solve. Under a pure land tax uniform scaling of L changes nothing (bills depend only on L_i / sum L), so this band would collapse to zero and falsely signal no uncertainty.

PROPOSED BAND (for the pure land tax): treat the dominant uncertainty, building cost, directly. Building values all scaled by (1 - k): L'_i = clip(V_i - (1-k) B_i, 0, V_i) = clip(L_i + k B_i, 0, V_i), with k found by bisection so the aggregate land share moves +/-10 points; then re-solve the land tax. Vacant plots (B = 0) are unaffected, so a lower land share shifts tax toward vacant and large-plot parcels, a higher one toward densely built parcels. Applied commune by commune.

QUESTIONS: (1) Is this a sound replacement? (2) Should the shift be applied to parcel-level L_i (as proposed) or to IRIS land totals before the site-value re-sharing (which the export cannot redo; it only has per-parcel L and B)? Is the parcel-level version a fair approximation? (3) Is +/-10 points of aggregate land share still a sensible magnitude, or should it be stated as +/-X % on building cost? (4) Anything else that becomes uncertain under a pure land tax that the band misses (e.g. the within-IRIS sharing exponent 0.5)? Short answers.
