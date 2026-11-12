### 1. Rules for CGI Art. 1384 A Exemption Durations (as of 2025) & Open-Data Proxy

Under **CGI Art. 1384 A** (and **1384 C** for acquisitions), new social housing (HLM) financed by over 50% subsidized loans (*prêts aidés*: PLAI, PLUS, PLS) is exempt from TFPB starting the year after completion (*achèvement*). 

* **Base duration (15 years):** Applies to all eligible social housing, principally **PLS** (*Prêt Locatif Social*) and older cohorts.
* **Extended duration (25 years):** Applies to **PLAI** and **PLUS** (and formerly PLA/PAP) whose construction/financing opening decision occurred between **Jan 1, 2004, and Dec 31, 2026** (extended by *Loi de finances pour 2023*, Art. 73).
* **Environmental bonus (20 or 30 years):** +5 years (making it 20 years for PLS, 30 years for PLUS/PLAI) for dwellings meeting high environmental performance criteria (BBC 2005 / RT 2012 / RE 2020), for projects approved since 2009 (**CGI Art. 1384 A I bis**).

**Open-Data Estimation Rule for 2025:**
Using the **RPLS** (*Répertoire des logements locatifs des bailleurs sociaux*, published annually by SDES) mixed with *Fichiers Fonciers* (Majic):
1. **If you have RPLS financing data (`mode_financement`) and completion year (`annee_achèvement`):**
   * `PLS` completed **$\ge$ 2005** (or $\ge$ 2010 without green bonus) $\rightarrow$ **Exempt**.
   * `PLUS` / `PLAI` completed **$\ge$ 1995** (if green bonus) or **$\ge$ 2000** (standard 25-year rule, though technically the 25-year rule started for *decisions* in 2004, meaning completions around **2006+**) $\rightarrow$ **Exempt**.
2. **Simple heuristic (if only completion year is available via Fichiers Fonciers `jannat`):**
   * Completed **2006 to 2024**: **100% Exempt** (since ~80% of HLM are PLUS/PLAI getting 25–30 years, and recent PLS are within 15–20 years).
   * Completed **1996 to 2005**: **50% probability** (or prorate at 50%), capturing 30-year environmental exemptions and late-completed 25-year authorizations.
   * Completed **$\le$ 1995**: **Taxable**.

---

### 2. REI *Produit*, Exempt Bases, and State Compensation

* **Does the REI *produit* exclude exempt bases?** **Yes.** In the DGFiP *Recensement des Éléments d'Imposition* (REI), the *base nette* (taxable base) and the *produit* (tax levied on taxpayers) strictly exclude bases exempt under Art. 1384 A and the 30% abated portion of Art. 1388 bis. State compensation is accounted for separately in the REI under *allocations compensatrices*.
* **How complete is State compensation?**
  * **Historical approvals (before Jan 1, 2021):** **Very incomplete.** Under CGI Art. 1384 A, historical compensation is subject to progressive *minorations* (haircuts via the *variables d'ajustement* of the DGF). Today, communes often receive **less than 10% to 20%** of the actual lost tax revenue for older cohorts.
  * **Recent approvals (Jan 1, 2021 – Dec 31, 2026):** **100% complete (at 2020 rates).** Under *Loi de finances pour 2021* (Art. 16, IV) and subsequent extensions, the State fully compensates communes for the first 10 years of the exemption for social housing approved (*agréés*) since 2021, calculated using 2020 local tax rates.
  * **Art. 1388 bis (QPV abatement):** Compensated by the State, but subject to the same heavy DGF variable adjustments (roughly ~30–40% effective compensation today).

---

### 3. CGI Art. 1388 bis (QPV Abatement)

* **Rate:** **30% abatement** on the TFPB tax base (meaning the social landlord pays **70%** of the normal tax).
* **Conditions:** Social housing located in a *Quartier Prioritaire de la Politique de la Ville* (QPV), Provided the landlord signs the *convention d'utilité sociale* (CUS) and a quality-of-service agreement (*convention d'équilibre / gestion urbaine de proximité*) with the commune and EPCI (BOI-IF-TFB-20-30-30). Note: It applies **after** the 1384 A exemption expires.
* **End date:** Currently aligned with the *contrats de ville "Engagements Quartiers 2030"*, running until **December 31, 2030** (*Loi de finances pour 2024*, Art. 73).
* **2024 QPV list:** **Yes**, it applies to the new QPV geography defined by **Décret n° 2023-1314 of Dec 28, 2023** (in force Jan 1, 2024, for metropolitan France; end of 2024 for Overseas).

---

### 4. Is the TFPB Recoverable from Tenants?

**No, it is not.** 
Under **Loi n° 89-462 du 6 juillet 1989 (Art. 23)** and **Décret n° 87-713 du 26 août 1987** (and its equivalent for HLM, **Décret n° 82-955**), the *Taxe Foncière sur les Propriétés Bâties* itself is strictly an owner's tax and **cannot** be recovered via tenant service charges (*charges locatives récupérables*). 
*Exception:* Only the **TEOM** (*Taxe d'enlèvement des ordures ménagères*), which is collected on the same tax roll as the TFPB, is recoverable from tenants. Your model correctly isolates the TFPB incidence on the social landlord's balance sheet.

---

### 5. Arguments for the Civic Site & French Text

#### Arguments for Taxing HLM Land (Left-of-Centre Framing)
1. **Preventing Land Rent Capture by Private Developers (VEFA):** Nearly 50% of new HLM are now bought turn-key from private developers (*VEFA*). Tax exemptions for HLM allow private landowners and developers to charge higher land prices to social landlords, effectively transferring public tax subsidies into private land rent.
2. **Spatial Justice & Anti-Segregation:** Exempting land value blinds social landlords to the opportunity cost of land. Taxing all land equally while giving direct budget subsidies empowers HLM organisms to compete for well-located urban land rather than being pushed to cheap, poorly connected peripheral zones.
3. **Democratic Transparency & Local Finances:** Tax exemptions starve poor communes with high HLM shares of local tax revenue (since State compensation withers over time). Direct, budgeted subsidies (*aides à la pierre* via the FNAP) are transparent and shared nationally rather than penalizing working-class municipalities.

#### Fair Counter-Arguments to Acknowledge
1. **Cash-Flow Shock on *Bailleurs Sociaux*:** Because social rents are strictly capped by the State (PLAI/PLUS/PLS ceilings), HLM landlords cannot pass the tax onto tenants. Without an immediate, guaranteed euro-for-euro increase in State subsidies, taxing their land reduces their *autofinancement* (equity) for building new housing or thermally renovating existing stock.
2. **Vulnerability to Annual Budget Cuts:** Tax exemptions written into the CGI for 25 years give long-term visibility to secure 40-year loans from the *Caisse des Dépôts*. Direct budgetary grants are vulnerable to annual parliamentary austerity (as seen with the *Réduction de Loyer de Solidarité* - RLS).

#### Suggested Text for the Civic Site (6 sentences)

> **Pourquoi soumettre le foncier des bailleurs sociaux à l'impôt ?**  
> Dans notre modèle, les organismes HLM acquittent l'impôt sur la valeur de leurs terrains au même titre que les propriétaires privés, mettant fin aux exonérations actuelles. Ces niches fiscales finissent en effet souvent par subventionner la rente des promoteurs et propriétaires fonciers privés qui vendent des terrains ou des logements clés en main (VEFA) aux bailleurs sociaux, tout en privant les communes populaires de précieuses ressources fiscales. Assujettir le logement social à l'impôt foncier garantit la neutralité économique et la transparence démocratique : le soutien public au logement social doit passer par des subventions directes et budgétées (« aides à la pierre »), plutôt que par des dépenses fiscales opaques. Parce que la taxe foncière n'est pas récupérable sur les locataires et que les loyers HLM sont plafonnés par l'État, cette réforme ne pèse pas sur le budget des ménages modestes logés dans le parc social. Nous reconnaissons toutefois qu'à court terme, cette hausse de fiscalité réduit la capacité d'autofinancement des bailleurs pour construire et rénover. C'est pourquoi, à l'échelle nationale, la suppression de ces exonérations appelle un redéploiement équivalent des aides directes de l'État vers le secteur HLM afin de sécuriser son modèle économique.

---

### Ranking of Uncertainties

1. **High Uncertainty – Exact 25-year vs. 15-year cutoff in Open Data:** The 1384 A duration depends on the *date of the administrative financing decision* (`date d'agrément`), whereas open property data (`Fichiers Fonciers`) only gives the *year of completion* (`jannat`). Because construction takes 2 to 4 years, mapping completion years between 2005 and 2009 to exact exemption expirations in 2025 carries a $\pm$ 2-year margin of error unless cross-referenced with restricted RPLS micro-data.
2. **Medium Uncertainty – Local Opt-Outs and Extensions:** Communes can deliberate to suppress or reduce certain exemptions, or grant additional abatements for specific energy-renovated HLM (CGI Art. 1384 C bis). While rare, these local deliberations (available in the DGFiP *rei-deliberations* dataset) can slightly alter the 0% / 70% binary rule locally.
3. **Low Uncertainty – Legal Incidence & REI Accounting:** The non-recoverability of TFPB from tenants and the exclusion of exempt bases from the REI *base nette* are settled matters of French tax and housing law.
