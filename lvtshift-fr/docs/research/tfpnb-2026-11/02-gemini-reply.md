Here is a critical review of your proposed design. 

### Ranked Summary of Issues

1. **CRITICAL (Formula error):** You are summing the Commune and EPCI TAFNB bases in your numerator. The TAFNB is a single tax assigned to *either* the commune *or* the EPCI (or MGP), rarely both. Summing them is safe only if one is zero, **except** if you divide by a single denominator. More importantly, **the Art. 1396 surcharge on constructible land is included in the Commune TFPNB base (B11), excluded from the EPCI TFPNB base (B31), and excluded from the TAFNB base.** Your formula severely underestimates the current tax on vacant building land in high-pressure communes that use the Art. 1396 surcharge (which is where the x30 and x48 multiples are likely coming from).
2. **HIGH (Incidence bias):** Allocating 100% of the non-agricultural TFPNB/TAFNB to *building-less* parcels ignores *terrains d'agrément* (Group 11: large gardens of built houses > 500 m²) and *sols* (Group 13: footprints of exempt or unassessed buildings) on **built** parcels. In suburban/residential communes, the majority of the TAFNB base actually sits on built parcels. You are overstating the current tax on vacant plots (making the reform look less punitive to them than it is) and understating the current tax on large-garden villas.
3. **MEDIUM (Spatial/Value bias):** Allocating both the current TFPNB and the new Land Value Tax (LVT) by flat commune-wide €/m² means every vacant parcel in the commune gets the exact same percentage change. Why show a parcel-level metric for vacant land when you only have a commune-level average?
4. **LOW (Scope/ancillary taxes):** Ignoring the *frais de gestion* (which differ between TFPB, TFPNB, and TAFNB) and the *Taxe Chambres d'Agriculture* (which is perversely levied on urban building plots too).

---

### Detailed Answers to Your Questions

#### 1. The TAFNB-base method and the Art. 1396 surcharge

**Is the TAFNB base ratio right?**
In principle, yes: using the TAFNB base (CGI Art. 1519 I) is a clever hack to isolate Cadastral Groups 7 and 10–13 without needing the *États 1259*, because the Art. 1394 B bis agricultural 20% exemption applies to the exact mirror groups (1–6, 8, 9). 

**However, your treatment of the Art. 1396 surcharge (*majoration de la valeur locative des terrains constructibles*) is wrong, and it breaks your ratio.**
* **Where is Art. 1396 in the REI?** The Art. 1396 flat €/m² surcharge (or the automatic +25% / +5€/m² surcharge in *zones tendues* under Art. 1396 II) applies **only to the Commune share** of the TFPNB (it is inside `B11` and `B13`). By law, it does **not** apply to the EPCI share (`B31`) and it does **not** apply to the TAFNB (`B11TAFNB` / `B31TAFNB`), which is calculated strictly on the un-surcharged cadastral rental value (less 20%).
* **How it biases your design:** In a commune that applies a 3 €/m² surcharge on constructible land, the actual commune TFPNB base on a 1,000 m² plot is increased by 3,000 € (which is massive compared to a normal *revenu cadastral* of maybe 50 €). Because this 3,000 € is in `B11` (denominator) but **not** in `TAFNB base` (numerator), your formula assumes the surcharge is agricultural! You therefore throw away most of the Art. 1396 revenue instead of replacing it. That directly explains why some of your *zones tendues* (like Annemasse or La Rochelle) show a x30 or x48 jump: you are missing the massive surcharge they already pay today.
* **How to fix it from open REI lines:** 
  1. Calculate the `non_ag_share` using **only the EPCI base** (`B31`), which is never polluted by the Art. 1396 commune surcharge, or by comparing `B11` and `B31`. Specifically: the Art. 1396 surcharge base in the commune is approximately `Surcharge_Base = max(0, B11 - B31)` (differences can also arise from slightly different commune/EPCI exemptions, so check the dedicated REI columns for the *majoration terrains constructibles*—look for variables related to *majoration* in the TFPNB block of the REI dictionary, usually around the `B11`–`B19` series; if using the shortened OFGL extract, `B11 - B31` is the best proxy).
  2. Calculate the normal non-ag share on the un-surcharged base: 
     `share = (B11TAFNB + B31TAFNB + B31MGPTAFNB) / B31` (capped at 1).
  3. Then, for the commune TFPNB, take `share * (B31 * Commune_Rate) + 100% of the Surcharge_Amount`, because 100% of the Art. 1396 surcharge is by definition on constructible land (Group 10) inside the reform!

**Is adding the whole TAFNB amount right?**
Yes. A land value tax reform replacing the TFPNB on non-agricultural land would undoubtedly abolish the TAFNB, which was created as a patch to tax non-agricultural unbuilt land at TFPB-like levels after agricultural land was exempted.

#### 2. Sharing by parcel area vs. value, and open data for cadastral groups

* **Open source for Cadastral Nature / Revenu Cadastral:** **No.** The `cconvo` (nature de culture) and `drcsuba` (revenu cadastral) live in the *MAJIC* files (*fichiers fonciers* `bati` and `nbat` tables). They are restricted under tax secrecy rules to local authorities and researchers (via Cerema / data.gouv restricted access) and **cannot** be published in a public open-data civic tool at the parcel level.
* **Area vs. Value:** Today’s 1961 TFPNB tariffs for Group 10 (*terrains à bâtir*) and Group 11 (*agrément*) are mildly stratified by location/class within a commune, whereas the Art. 1396 surcharge is a flat €/m² per parcel (above a 200 m² threshold). However, since your model already prices vacant land at a single uniform €/m² across the whole commune, **sharing by area and sharing by modelled land value are mathematically identical within a commune.** If you later introduce a spatial land-value gradient for vacant plots (e.g., borrowing the €/m² gradient from nearby built parcels—which I strongly recommend you do!), you should still allocate *today's* TFPNB mostly by area (or mildly weighted by value, e.g., 50/50), because 1961 tariffs and flat €/m² surcharges are much flatter than modern market land values.

#### 3. How material is the "Garden Problem" (Group 11 vs. Group 10)?

**It is very material—often > 50% of the base in built-up or suburban communes.**
* Under French cadastral rules (BOI-IF-TFNB-10-50-10), when a house sits on a parcel, the building footprint and immediate yard up to **500 m²** are rolled into the **TFPB** as *dépendances indispensables et immédiates*. Any garden area beyond 500 m² (or 1,000 m² in some rural grids) is split off as a separate *subdivision fiscale* in **TFPNB Group 11 (*terrains d'agrément*)** and pays both TFPNB and TAFNB.
* In a dense city (Paris, Lyon, Villeurbanne) or a suburban single-family-home commune where vacant building plots (Group 10) are rare, Group 11 (large gardens of built houses), Group 12 (railways/SNCF), and Group 7 (quarries) make up the **vast majority** of the TAFNB base.
* By dumping 100% of the commune's non-ag TFPNB/TAFNB onto the few *building-less* parcels (`bati == 0`), you artificially inflate the "current tax" of vacant plots.
* **How to bound and fix it with open data:**
  You actually know from the cadastre (Etalab *parcelles* + *bâtiments*) the exact area of every **built** parcel in zones U/AU! 
  1. For every **built** parcel in your reform zone, compute `excess_garden_area = max(0, parcel_area - building_footprint - 500)`.
  2. For every **unbuilt** parcel in your reform zone, take `unbuilt_area = parcel_area`.
  3. Allocate the replaced TFPNB + TAFNB amount across **both** `unbuilt_area` and `excess_garden_area` (perhaps giving `unbuilt_area` a 2x weight per m² because Group 10 tariffs are typically ~2x higher than Group 11 tariffs).
  This is a huge improvement: it stops over-crediting vacant plots with the taxes actually paid by large-garden homeowners, and it properly adds that current TFPNB to the baseline of large-garden homeowners! (You can also subtract the area of railway parcels—easily spotted by geometry or OSM—before allocating).

#### 4. Other tax components to remove or keep

* **Frais de gestion (State collection fee, CGI Art. 1641):** Be careful whether your REI "montant réel" figures (`B13`, `B33`) include or exclude *frais de gestion*. The State adds **3.0%** on TFPB, **8.0%** on TFPNB, and **9.0%** on TAFNB. If your model holds local authority revenue constant (`B13 + B33`), you can ignore them, *or* note that taxpayers actually save an extra ~5% on the replaced TFPNB/TAFNB because collection fees drop when consolidated.
* **Taxe pour frais de chambres d'agriculture (TACFA):** By a quirk of CGI Art. 1604, the Chamber of Agriculture tax is levied on **all** TFPNB properties, including urban building plots (Group 10) and gardens (Group 11)! However, because you leave agricultural land (Zones A/N) untouched, the Chamber of Agriculture still needs its budget. Leaving it out of the reform (as you do) is the right modelling choice.
* **TSE and GEMAPI:** Leaving them out is consistent with your TFPB treatment.
* **State compensations (Art. 1394 B bis):** The 20% agricultural exemption is compensated by the State to communes, so it is outside `B13`/`B33` (*montant réel payé par le contribuable*). Since you do not touch agricultural land, you rightly ignore it.

#### 5. Presentation of "+400% to x48"

* **Do not show a percentage above +200%.** In tax-incidence communication, "+960%" and "+4,700%" look like software bugs to a general reader, because readers anchor on income or property tax reforms where changes are ±20%. Worse, becausetoday's TFPNB on a vacant plot without an Art. 1396 surcharge might be **15 € per year**, going from 15 € to 720 € is a "x48" jump, even though 720 € is a totally normal tax for a constructible plot.
* **What to show:** Show **€/m²/year** (e.g., *"de 0,08 €/m² à 2,40 €/m² — soit ×30"*), or **€ for a standard 500 m² plot** alongside the multiple (`×30`). Grounding the multiple in euros per m² immediately explains *why* the multiple is huge: not because the new tax is absurdly high, but because the 1961 unbuilt tax base was near zero.
* **One-sentence caveat for a general reader:**
  > *"Sur les terrains nus constructibles, la hausse en multiple paraît spectaculaire (×5 à ×40) car la taxe actuelle (TFPNB) repose sur des tarifs cadastraux figés depuis 1961, souvent inférieurs à quelques dizaines d'euros par an ; faute de données fiscales par parcelle, ce ratio reflète la moyenne communale."*

#### 6. Anything else silently biasing the result?

1. **Why price vacant land at a single commune-wide €/m²?** You mention that *terrain-à-bâtir* DVF comparables are too thin for finer cells. That is true, **but** inside your reform already, you must have a spatial land-value surface (or €/m² estimates) to split land vs. building on **built** parcels! A vacant constructible plot in zone U next to a built parcel has the *same* underlying land value per m² as the land underneath its built neighbour. Using your built-parcel land value surface to price vacant parcels in the same neighbourhood would eliminate the artificial uniform percentage change across the commune.
2. **Public / Exempt Unbuilt Land filter:** Make sure your filter for "not exempt public property" on unbuilt land in Zone U catches **roadways, parks, and municipal parking lots** that are sometimes cadastrally parcelled (not left in the un-parcelled *domaine public non cadastré*). If a single 10-hectare municipal park in Zone U slips into your "taxable unbuilt land" denominator (`parcel_area`), it will absorb a huge chunk of the new LVT and artificially lower the tax on private building plots. (Without MAJIC owner files, cross-referencing with OpenStreetMap `landuse=recreation_ground`, `leisure=park`, `amenity=school`, `railway=*`, etc. is essential).