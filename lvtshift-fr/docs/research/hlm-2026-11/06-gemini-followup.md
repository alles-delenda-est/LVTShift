Here is a brief, critical review of your four points. 

### 1. LOCAT Semantics
**Your conclusion is completely correct.** 
Empirically, RPLS data is exported from landlords' heterogeneous ERP systems (e.g., Ikos, Immoware, Sopra), which often lack a dedicated field for "first *social* letting." When acquiring existing private buildings (*acquisition-amélioration*), many landlords simply copy `CONSTRUCT` into `LOCAT` to pass validation rules. Your cross-check proving that `FINAN` (e.g., PLUS) did not legally exist in the `LOCAT` year is definitive proof. `LOCAT` cannot be used to detect inter-landlord transfers.

### 2. New Transfer Rule (DATCONV vs. PATRIMOINE)
**The rule is much sounder than the `LOCAT` test, and your results (23–25%) align well with national macroeconomic benchmarks.** However, there are three flaws to address:

*   **Threshold (`PATRIMOINE - 2` is too loose):** It is legally and administratively impossible to sign an APL convention *more than a few months before* acquiring the property (you cannot convention a property you do not own, though *promesse de vente* + prefectural *agrément* dates sometimes get muddled in the ERP). Setting the threshold at `PATRIMOINE - 2` means a convention signed in Year $T-2$ for an acquisition in Year $T$ is treated as a *new* acquisition. That makes no sense. **Change the threshold to `DATCONV < PATRIMOINE - 1` (or even `< PATRIMOINE`).** If the convention strictly predates the acquisition year, it was already conventioned when bought (a transfer).
*   **The Merger/Avenant Risk (False Positives):** Because of the 2018 ELAN law (requiring *regroupement* of landlords below 12,000 units), the 2020–2024 period saw massive mergers. Landlords often sign a global *avenant* to transfer the conventions and erroneously overwrite `DATCONV` with the *avenant* date. Under your rule, a 1985 building transferred in a 2021 merger with an overwritten `DATCONV` of 2021 will look like a brand-new 2021 exempt acquisition. 
    *   *Fix:* Override the rule using `FINAN`. If `FINAN` is an extinct loan (see Point 3) or a loan that doesn't match `ORIGINE` 2/3, force it to be a transfer/expired, regardless of `DATCONV`.
*   **The Clock for ORIGINE 2 (Acquisition *with* works):** For `ORIGINE` 2, the 1384 C exemption clock starts the year following the **completion of the improvement works**, not the acquisition of the walls (`PATRIMOINE`). Using `PATRIMOINE` starts the clock 1 to 2 years too early, slightly understating 2025 exemptions. If `DATCONV > PATRIMOINE`, `DATCONV` (or `LOCAT` if $> \text{PATRIMOINE}$) is actually a better proxy for the completion of works than `PATRIMOINE`.

### 3. Extinct Loans (FINAN 10, 11, 12)
**You are right on Code 12, right on Code 11, and wrong on Code 10.**

*   **Code 12 (PLA):** **Correct.** Replaced by PLUS in late 1999. Even with construction delays and the 20-year environmental bonus (rare for late-stage PLA), any 15- or 20-year clock expired well before 2025. Forcing Code 12 to "non-exempt" is a great way to neutralize the `DATCONV` overwrite bug mentioned in Point 2.
*   **Code 11 (PLAI / PLA-LM / PLATS):** **Correct.** In the official RPLS nomenclature, Code 11 is the active code for modern **PLAI** (*Prêt Locatif Aidé d'Intégration*, created in 2000 and still issued today). You must keep it eligible.
*   **Code 10 (PLA d'intégration):** **Wrong.** Code 10 is specifically the *historic* 1990s PLA d'intégration (and PAP locatif), which was replaced by the PLAI (Code 11) in 2000. Just like Code 12, no genuine Code 10 decision was issued after 2000. While a few landlords might fat-finger a modern PLAI as "10" instead of "11", in reality, 1970s/1980s HLM/PAP loans (codes 01–09) and 1990s PLA-I (code 10) plagued by the `DATCONV` merger bug are a much bigger risk. **You should treat Code 10 as never exempt in 2025, just like Code 12** (as well as Codes 01 to 09, 16, and 18/ILN/ILM). *(Note: Also ensure you are allowing the 25-year and 30-year extended clocks for modern PLUS/PLAI/PLS achieved between 2004 and ~2020).*

### 4. Statistical Disclosure (The 3 / 85% Rule)
**Yes, this is completely fine and is standard practice.** 
You have implemented the exact French **CASD / INSEE dominance rule** for enterprise and fiscal data (minimum 3 units, no single unit contributing $>85\%$ of the value). 

*One minor caveat:* Check your geographic granularity. In many rural or suburban *communes*, a single Departmental OPH owns $>85\%$ of the social stock. If you apply this at the *commune* or *section cadastrale* level, your "Social Housing" category will vanish into "Other" in a vast majority of French municipalities. If your output is at the *commune* level or higher, note that `RPLS` itself is open data that names the landlord (`SIRET`) and address of every dwelling, so strict fiscal secrecy is technically only required because you are merging it with the *Majic / Locaux* tax base values. Your rule is legally safe.
