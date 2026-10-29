### 1. Commune Model: PLU Zoning vs. Cadastral *Nature de Culture*

Using PLU zoning (GPU) rather than the cadastral *groupe de nature de culture* (BOI-IF-TFNB-20-10-10-10) is **conceptually superior for an LVT, provided it is a deliberate choice**, not a data shortcut. An LVT taxes location and development rights: an orchard (Group 5) zoned U/AU holds urban development value and *should* pay the LVT; a golf course (Group 12) zoned N cannot be developed and should not.

**Where you are wrong / at risk:**
*   **Double taxation and double exemption:** You are excluding by *PLU zone* at the micro level, while keeping the status-quo TFPNB by *cadastral group* at the macro level. Consequently, a parcel of *terres* (Group 1) inside a U/AU zone will pay the new LVT **and** continue paying its agricultural TFPNB. Conversely, a *terrain d'agrément* (Group 12) in an N zone is dropped from the LVT **and** dropped from the non-agricultural TFPNB replacement.
*   **Missing GPU data (RNU / *Cartes communales*):** Treating unbuilt parcels with "no known zoning" as taxable under the LVT is **wrong**. Over 15,000 rural communes lack a digital PLU on the GPU or are under the *Règlement National d’Urbanisme* (RNU, where building outside the *parties actuellement urbanisées* is banned under C. urb. L111-3). Taxing all unzoned rural farmland at the LVT rate will break the model in rural France.
*   **CGI 1382 6°:** Correct. These buildings sit on *sols* (Group 10, exempted from TAFNB by CGI 1519 I explicitly referencing 1382 6°) and belong in the excluded agricultural bucket.

---

### 2. National Totals: The TAFNB / REI Method

**(a) Validity of the TAFNB proxy:**
Using the TAFNB base (CGI 1519 I; BOI-IF-AUT-80) as the exact complement of CGI 1394 B bis is clever, and your 0.6% cross-check against `D21 / 0.2 * 0.8` proves its macro accuracy. However, you have **one major formula bug** and minor statutory leaks:
*   **The Formula Bug (Double Counting):** In the REI, when an EPCI or the MGP levies the TAFNB (under CGI 1609 nonies C or 1379-0 bis), the commune does not. However, in the few cases or specific REI fields where bases overlap, summing `B11TAFNB + B31TAFNB + B31MGPTAFNB` over the commune base `B11` is risky if a territory shifts or if temporary exemptions differ between levels. Always check that your numerator never exceeds `B11`.
*   **Statutory mismatches:** Group 9 (*eaux*, *marais salants*) and *tourbières* in Group 7 are outside 1394 B bis **and** outside TAFNB (which only hits 10–13 and *carrières/sablières* in 7). They vanish into your "agricultural" residual. Conversely, *sols* (Group 10) of buildings exempt under CGI 1382 1°–12° are exempt from TAFNB; if they pay TFPNB, your residual absorbs them as "agricultural".
*   **The Corsica trap:** Under CGI 1394 B, agricultural land (Groups 1–6, 8, 9) in Corsica is **100% exempt** from TFPNB. It does not use the 20%/30% 1394 B bis abatement (`D21 = 0`). Because TAFNB still applies to Groups 7 and 10–13 in Corsica, your `TAFNB / B11` ratio should yield ~100% non-agricultural there—verify that it does.
*   **Constructible land surcharges (CGI 1396):** Does the REI's `B11` include the flat-rate or +200% *majoration* on constructible land, while `B11TAFNB` does not? Yes (BOI-IF-AUT-80 §80: majorations are excluded from TAFNB). This artificially depresses your `TAFNB / B11` ratio, overstating the agricultural share in tense urban zones.

**(b) Rate uniformity:**
**Yes.** The commune and EPCI TFPNB rates are strictly uniform across all 13 cadastral groups within a taxing jurisdiction (CGI 1636 B sexies). (Note: the Chamber of Agriculture tax, CGI 1604, uses the same base, though you likely left it outside S1).

**(c) Macro S1 coherence:**
Removing ~973 M€ of agricultural TFPNB drops S1 from 67,113 to 66,140 M€ (-1.45%). Yet your indicative LVT rate **rises** from 1.06% to 1.09% (+2.8%). Why? Because you are dividing a 66.14 Md€ yield (which still includes DMTO, THRS, and non-farm TFPNB) by *built land only* (6,091 Md€), or because the unbuilt land you removed (~4% of your previous tax base) represented a larger share of the base than the 1.45% of yield you removed. **You must include taxable U/AU unbuilt land in the denominator** of your indicative rate, not just built land.

---

### 3. Filosofi IRIS Quintiles

Requiring $\ge 10$ distinct IRIS median incomes is **statistically weak**. In a 10-IRIS commune (like Cahors), ecological fallacy is massive: within-IRIS income variance dwarfs between-IRIS variance, and grouping parcels by IRIS median income produces arbitrary step-effects when farmland is removed. 

---

### Priority List of Changes

1.  **Fix the "Unzoned = Taxable" rule (Critical):** For communes without GPU data (RNU), fall back to the cadastral *nature de culture* (exclude Groups 1–6, 8, 9) rather than taxing rural farmland.
2.  **Use `D21` directly for the macro split:** Instead of the TAFNB proxy (which suffers from CGI 1396 *majoration* distortions and Group 7/9 leaks), compute the agricultural share directly from the REI 1394 B bis exemption base (`D21 * 4` in 2024; `D21 * 7/3` in 2025), capped at `B11`.
3.  **Fix the macro denominator:** Ensure the 6,091 Md€ denominator includes taxable unbuilt U/AU land; reconcile the micro (PLU) and macro (cadastral) definitions to avoid double-taxing U-zoned farmland.
4.  **Raise the IRIS threshold:** Require $\ge 20$ IRIS (or $\ge 20,000$ inhabitants) to publish intra-communal distributional quintiles, or weight by parcel/household counts using the Filosofi 200m grid (*carreaux*) instead of IRIS.
