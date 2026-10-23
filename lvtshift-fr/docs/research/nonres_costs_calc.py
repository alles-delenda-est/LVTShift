"""
Arithmetic behind nonres-valuation-2025.md: non-residential replacement cost
per m² of the model's gross floor area (footprint × storeys), 2025 €.

Two routes, both starting from one commercial cost guide (Quostra, Jan-2026 €,
HT, province coefficient 1.00, hors honoraires / VRD / foncier):

  Direct:     base × area coefficient × fees × VAT treatment × index 2026->2025
              × (SDP ÷ gross) for the type
  Anchored:   Direct × k_area, where k_area = model's calibrated residential
              cost ÷ the same guide's social-housing line pushed through the
              same chain. This keeps non-residential costs in the same
              proportion to housing as in the guide, while inheriting the
              model's (lower, official-data) residential level.

The anchored route is the recommendation; the direct route is the upper check.
Every factor is a (central, low, high) triple; ranges are geometric means of
central and bounds, as in house_costs_calc.py.

Run:  python nonres_costs_calc.py
"""

from math import sqrt

INDEX_2026_TO_2025 = 133.3 / 134.7   # BT01 2025 average (approx.) ÷ Jan-2026 base

# Model's calibrated residential collective cost (gross m², 2025 €, TTC, fees in)
RESID = {"Paris": 2650, "Paris inner ring": 2400, "Lyon": 2000, "Lyon ring": 1850}

# Quostra geographic coefficients: "full" for buildings with local trades,
# "shed" = half the premium (judgement: steel/precast sheds are bought on a
# national market).
COEF_FULL = {"Paris": 1.275, "Paris inner ring": 1.22, "Lyon": 1.10, "Lyon ring": 1.05}
COEF_SHED = {k: 1 + (v - 1) / 2 for k, v in COEF_FULL.items()}

SOCIAL_HOUSING = (1835, 1630, 2040)  # Quostra PLAI/PLUS €/m² SDP HT
HOUSING_FEES, HOUSING_VAT, HOUSING_SDP_PER_GROSS = 1.15, 1.20, 0.92

# type: (base HT province (c, lo, hi), coef table, fees, VAT factor, SDP÷gross)
# VAT factor 1.00 = businesses recover VAT; 1.003 = public owner net of FCTVA
# (1.2 × (1 − 0.16404)); 1.20 = households (annexes).
TYPES = {
    "logistics / industrial shed": ((600, 450, 800), COEF_SHED, 1.08, 1.00, 0.98),
    "light industrial / workshop": ((850, 650, 1200), COEF_SHED, 1.10, 1.00, 0.97),
    "retail box / commercial":     ((1000, 700, 1600), COEF_FULL, 1.12, 1.00, 0.97),
    "offices":                     ((1800, 1400, 2300), COEF_FULL, 1.15, 1.00, 0.93),
    "agricultural shed":           ((180, 120, 300), COEF_SHED, 1.05, 1.00, 0.99),
    "greenhouse (glass)":          ((200, 80, 400), COEF_SHED, 1.05, 1.00, 1.00),
    "sports hall":                 ((2200, 1800, 2800), COEF_FULL, 1.15, 1.003, 0.95),
    "annex (garage, shed)":        ((480, 220, 850), COEF_FULL, 1.00, 1.20, 0.92),
}


def chain(base, coef, fees, vat, sdp_per_gross):
    return base * coef * fees * vat * INDEX_2026_TO_2025 * sdp_per_gross


def k_area(area):
    q = chain(SOCIAL_HOUSING[0], COEF_FULL[area], HOUSING_FEES, HOUSING_VAT,
              HOUSING_SDP_PER_GROSS)
    return RESID[area] / q


if __name__ == "__main__":
    for area in RESID:
        k = k_area(area)
        print(f"\n{area}: anchor k = {k:.2f} "
              f"(model resid {RESID[area]} ÷ guide social housing pushed to our basis)")
        for name, (base, coefs, fees, vat, spg) in TYPES.items():
            c, lo, hi = (chain(b, coefs[area], fees, vat, spg) for b in base)
            lo, hi = sqrt(c * lo), sqrt(c * hi)
            print(f"  {name:30s} anchored {c * k:5.0f} ({lo * k:4.0f}-{hi * k:4.0f})"
                  f"   direct {c:5.0f}   ratio to resid {c * k / RESID[area]:.2f}")
