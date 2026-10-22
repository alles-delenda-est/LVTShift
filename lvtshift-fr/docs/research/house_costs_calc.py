"""
Arithmetic behind house-costs-2025.md: house cost per habitable m² by area.

Each factor is a (central, low, high) triple; see the note for sources:
EPTB 2024 € per m² SDP, index to 2025 (BT01 / ICC), finishing work, fees and
studies, tight-plot premium, habitable ÷ SDP. The range is the geometric mean
of the central value and the outer bound. Gross = habitable × 0.82 (the
model's cost_net_to_gross for houses).

Run:  python house_costs_calc.py
"""

from math import sqrt

INDEX = (1.014, 0.961, 1.030)        # 2024 -> 2025
FINISH = (1.06, 1.03, 1.10)          # finishing work left to the household
HAB_PER_SDP = (0.90, 0.97, 0.86)     # habitable ÷ surface de plancher
URBAN_FEES = (1.05, 1.00, 1.10)      # fees, insurance, soil study (dense)
RING_FEES = (1.03, 1.00, 1.06)
BASEMENT = (1.00, 1.00, 1.05)        # high case only: full basements
COST_NET_TO_GROSS_HOUSE = 0.82

AREAS = {  # EPTB base, fees, plot premium
    "Paris": ((1863, 1714, 2001), URBAN_FEES, (1.20, 1.10, 1.35)),
    "Paris inner ring": ((1863, 1714, 2001), URBAN_FEES, (1.10, 1.00, 1.20)),
    "Lyon and Villeurbanne": ((2127, 2066, 2250), URBAN_FEES, (1.10, 1.00, 1.20)),
    "Lyon ring": ((2127, 2066, 2250), RING_FEES, (1.05, 1.00, 1.15)),
}

if __name__ == "__main__":
    for name, (base, fees, plot) in AREAS.items():
        central, low, high = (
            base[i] * INDEX[i] * FINISH[i] * fees[i] * plot[i] * BASEMENT[i] / HAB_PER_SDP[i]
            for i in range(3))
        lo, hi = sqrt(central * low), sqrt(central * high)
        print(f"{name:24s} habitable {central:5.0f} ({lo:.0f}-{hi:.0f})  "
              f"gross {central * COST_NET_TO_GROSS_HOUSE:5.0f}")
