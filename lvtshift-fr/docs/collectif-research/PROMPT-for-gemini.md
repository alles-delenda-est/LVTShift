# Gemini research prompt — collectif (multi-family) construction cost €/m²

> This is the **identical prompt** given to the Opus and Sonnet research agents
> (outputs: `collectif-opus.md`, `collectif-sonnet.md`). Gemini could not be run
> from the automation environment (no Gemini CLI/API key present). Run this in
> your own Gemini setup and save the answer to `collectif-gemini.md` in this
> folder; the three will then be evaluated head-to-head.

---

Find an **authoritative, open-source construction cost (€/m²) for COLLECTIF
(multi-family) residential buildings in France**, ideally regional and for dense
Île-de-France cores, to calibrate a model parameter `construction_cost_eur_m2`
for collectif-heavy communes. **Gather and cite only — do not fabricate numbers.**

## Why this specific gap
An earlier pass sourced construction costs from **SDES EPTB** (*Enquête sur le
prix des terrains et du bâti*, 2024), but EPTB covers **individual houses only**.
Several pilot communes are heavily **collectif** — most acutely **Montreuil**
(dense Île-de-France inner suburb), and to a lesser degree Villeurbanne and
Grenoble. For those the individual-house EPTB figure (IdF ~1 914 €/m², ARA
~2 065 €/m²) likely **understates** the true construction cost (collectif carries
structure/lifts/underground parking/RE2020 costs a detached house does not).

## Parameter definition (match figures to this)
`construction_cost_eur_m2` = **turnkey replacement construction cost, gros œuvre
+ second œuvre, HORS FONCIER, €/m² of floor area**. It is applied to
**`floor_area` = footprint × storeys (surface de plancher / SDP-like, walls
included)**, NOT habitable area. So for every figure, state its **surface basis**
(SDP / surface de plancher, surface habitable/SHAB, surface utile, SHON) and
whether it **includes land**: a per-*habitable*-m² figure must be scaled DOWN
~10–20 % to per-*floor-area*; a figure including land/charge foncière or VAT must
be adjusted.

## What to find (prefer official/institutional over trade sources)
1. **Prix de revient des logements sociaux** (most authoritative open collectif
   series): **Banque des Territoires / CDC, *Éclairages* n°33** ("Le prix de
   revient des logements sociaux", Dec 2024); **USH** cost studies; CDC/BdT
   "coût de construction du logement social". State surface basis and whether
   *charge foncière incluse* (subtract it for hors-foncier).
2. **Promoteur / private collectif** (dearer than social): **FPI** *Les chiffres
   du logement neuf* (careful: FPI usually reports **sale prices**, not
   construction cost), **FFB** collectif references, **SDES/CGDD**, **Grand
   Paris / DRIEAT** IdF construction-cost studies.
3. **RE2020 cost-impact studies** (CEREMA, CSTB, USH) for a current-vintage
   collectif €/m².
4. Trade sources only as a flagged fallback (**[UNVERIFIED – secondary]**).

For each figure: **€/m² · surface basis · hors/avec foncier · social vs private ·
region · vintage · source (title, body, date, URL)**.

## Deliverable
A document with: a sourced figures table; the surface-basis and hors/avec-foncier
adjustments needed to make each figure comparable to the parameter; a
**social vs private/promoteur** distinction; and a **single recommended collectif
€/m² (hors foncier, per floor area/SDP) for a dense Île-de-France core like
Montreuil**, with an uncertainty range and reasoning. Note explicitly which basis
(social, private, or a stock-weighted mix) is right for a model that values the
*existing* building stock.

## Discipline
Cite every number (title, date, URL); mark anything unverifiable **[UNVERIFIED]**
with a caveat — never fabricate. Be explicit about the social-vs-private gap.
