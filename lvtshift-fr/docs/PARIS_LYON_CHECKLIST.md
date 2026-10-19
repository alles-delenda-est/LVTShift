# Paris & Lyon (intra- and extra-muros) — review checklist

Branch `paris-lyon-territories` · prepared 2026-10-19 · nothing committed or pushed yet.

**What was added.** Paris (20 arrondissements, one city-wide rate), Lyon (9
arrondissements), *Paris extra-muros* (all 122 communes of 92/93/94) and *Lyon
extra-muros* (the 57 other communes of the Métropole). Every commune in a ring is
modelled on its **own** taxe foncière total and stays revenue-neutral on its own;
the ring figures are aggregates of those 179 separate runs, not a metropolitan tax.

**Headline numbers (central scenario, 4:1 split-rate)**

| | Parcels | TFPB held neutral | Land share | Amount shifted | Share paying more |
|---|---|---|---|---|---|
| Paris | 78,189 | €1,840.9 M | 84.9 % ⚠ *set by cap* | 14.4 % | 52.5 % |
| Lyon | 34,142 | €362.9 M | 81.6 % ⚠ *mostly cap* | 14.7 % | 73.1 % |
| Paris extra-muros (122) | 608,220 | €3,569.3 M | 80.6 % | 15.8 % | 69.8 % |
| Lyon extra-muros (57) | 246,397 | €528.2 M | 73.2 % | 19.6 % | 69.8 % |

⚠ **The land share is not a finding where most parcels hit the 85 % cap.** Share of
built parcels at the cap: Paris 95.5 %, Lyon 59.8 %, Paris ring 36.5 %, Lyon ring 5.6 %.
Before the cap, Paris comes out at 92.9 %, because the depreciation rule writes old,
maintained buildings down to 25 % of rebuild cost. Valuing them without that
write-down gives 63–79 %. The site now labels capped land shares "plafonnée"
(`headline.built_at_cap_pct` ≥ 50 %). The fix is C1, now in progress on its own branch.

**Verified.**
- Revenue-neutral to the euro in all 181 new runs (max deviation 0.0000 %).
- Every source present for every commune: cadastre, 5 years of DVF, buildings, zoning, IRIS.
- Paris REI matches the Ville de Paris BP 2025 (€1,851 M incl. TFPNB) within 0.6 %; Lyon matches its 2025 budget (€349 M) within ~2 %.
- Cadastre-vs-BD TOPO built-map agreement passes (Paris 97 % vs 94 %, Lyon 89 % vs 81 %).
- Tests pass: 53 Python, synthetic end-to-end, 9 site tests, lint, type-check and static build.
- Adversarial security review: no critical or high findings, fixes applied, logged in `~/securitylog.md`.

---

## A. Decisions only you can make (economics / framing)

- [ ] **A1. How to present Paris.** 95.5 % of Paris's built parcels sit at the
  85 % land-share cap. Old stock (median age ~95 years) is depreciated to the 25 %
  floor, so the land share before the cap is ~93 %, an artefact of the depreciation
  rule rather than a measurement (see the ⚠ note above). With every parcel at the same split, the
  land tax becomes a tax proportional to market value: the Paris result is
  really a revaluation from today's floor-area bill to a market-value bill. It
  is strongly progressive (poorest income quintile −16.7 %, richest +10.5 %), and
  the sensitivity band is flat. Options:
  (a) publish with a prominent caveat, framed as "where land is ~90 % of value,
      LVT ≈ a modern value tax";
  (b) hold Paris back until the cap / depreciation question (C1) is settled;
  (c) publish an uncapped variant alongside.
  *Recommendation: (a) now, (c) as follow-up.* The register flags the same
  cap problem for Lyon and 53 other communes (`land_share_clip`).
- [ ] **A2. Income quintiles for the rings.** Ranked across the whole ring, Lyon
  extra-muros looks *regressive* (poorest +9 %, richest −1 %). Ranked within each
  commune it is *progressive* (+5 % → +12 %): the pooled view mixes in rich-vs-poor
  commune differences the reform does not touch. The site now shows both, with an
  explanation. Confirm you are happy with that framing, or prefer within-commune only.
- [ ] **A3. Syndicate layer (Métropole de Lyon).** 45 ring communes have a
  *Syndicat* foncier-bâti layer worth 5–23 % of their bill (e.g. Couzon 23 %).
  We hold Commune + Métropole neutral, as for the rest of the panel. Leaving the
  syndicate layer out changes **euro** amounts (understated by that %) but not the
  **% changes**. Keep as is (consistent), or include syndicates everywhere (`--layers Commune GFP Syndicat`)?
- [ ] **A4. Construction-cost basis.** Pilots: Paris 2,300, inner ring 2,150,
  Lyon and its ring 1,950 €/m². Research suggests 2,600 / 2,300 / 2,100 €/m² of
  *surface utile*; our floor area (footprint × storeys) is *gross*, which brings
  them roughly back to our values (÷ 1.1–1.2). Gemini 4 Argon argues for a 0.8
  gross-to-net factor. Decide the basis as part of the planned FFB/BT01
  calibration. In old stock, depreciation, not cost, decides the split.
- [ ] **A5. Public open space and industrial land priced as building land.**
  Building-less parcels in urban zones take the residential plot price. The
  aggregate effect is small (Paris 0.9 % of the levy, rings 3.6 % / 6.2 %), but it
  concentrates in a few communes:
  - **Saint-Cloud 24 %** — *UL* zone, very likely the state-owned Domaine national;
  - **Feyzin 19 %** — chemical-valley industrial land;
  - Paris: *UV* parks and cemeteries 0.35 %, *UGSU* rail yards 0.20 %;
  - Lyon: Port Édouard Herriot (*UEp*).

  Choose a rule: treat leisure / green / public-service labels (UV, UL, USP,
  UGSU…) as non-constructible, and/or price industrial zones on an industrial-land
  benchmark. This is a panel-wide method change. Use `python audit_land.py <commune>`
  to see any commune's breakdown.
- [ ] **A6. Exemptions (HLM, QPV, public land).** The real tax total is net of
  exemptions but is spread over every built parcel. This overstates today's bill
  for exempt social housing (material in 93 and Paris). Open proxies exist: the RPLS
  social-housing register, QPV boundaries, BD TOPO *zones d'activité*. Priority?

## B. Before merging this branch

- [ ] **B1.** Read the territory view locally (`cd site && npm run build`, then serve `out/`),
  or on the Vercel preview once pushed. Screenshot of the Paris ring:
  see the scratchpad `paris-ring.png` mentioned in chat.
- [ ] **B2.** Review the rewritten méthodologie paragraph ("Paris, Lyon et leurs
  couronnes"). The old text said Paris was absent and that the "métropole" levies TFPB
  in Paris; per the REI it does not.
- [ ] **B3.** Ask Claude to commit (scoped files only: **not** `charts_fr.py`,
  `Comms docs/`, `LVTShift/`), push, and open the PR; the push creates the Vercel preview.
- [ ] **B4.** The 9 existing communes' published files were deliberately left
  unchanged. Their open data has moved since they were modelled (e.g. Grenoble now
  has 12,895 parcels vs 12,853; its headline is unchanged). Decide whether to
  refresh the whole panel to one data vintage, in a separate PR.

## C. Follow-up work (separate PRs — one feature each)

- [ ] **C1.** Land-share cap and depreciation: depreciation calibrated for old, maintained stock (unblocks A1). **In progress**, branch `depreciation-old-stock`.
- [ ] **C2.** Zoning-label rule for public, green and industrial land (A5).
- [ ] **C3.** Exemption proxies: RPLS, QPV and public land (A6).
- [ ] **C4.** Fix the INSEE vacancy benchmark. It has **never** returned a value
  (null for all published communes) because the INSEE page gives counts, not a
  percentage. Its comparator is also degenerate in dense cities (Lyon shows 99.9 %
  "under-built").
- [ ] **C5.** Offices and La Défense: non-residential value still borrows the residential €/m² (Courbevoie, Puteaux, Paris 8e).
- [ ] **C6.** Cache housekeeping: add `--refresh` and record the download date in each payload's provenance (security review, info).
- [ ] **C7.** Add an aggregate-only guard to the public register writer (security review, low). The register is now 692 KB; consider splitting out the ring members.
- [ ] **C8.** Marseille (16 arrondissements) can now be added the same way as Paris and Lyon.

---
*Reproduce:* `python run_commune.py paris --cache-dir output/cache` ·
`python run_territory.py paris-extra-muros` · `python export_web.py paris-extra-muros` ·
`python preflight.py` · `python audit_land.py saint-cloud`
