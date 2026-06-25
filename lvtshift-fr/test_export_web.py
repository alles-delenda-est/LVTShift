import json
import numpy as np
import pandas as pd
import pytest
import export_web as ew


def _toy_df():
    return pd.DataFrame({
        "property_category": ["Single Family Residential", "Vacant Land",
                               "Commercial", "Condominium"],
        "current_tax": [1000.0, 50.0, 2000.0, 800.0],
        "new_tax":     [900.0, 400.0, 1900.0, 850.0],
        "tax_change":  [-100.0, 350.0, -100.0, 50.0],
        "tax_change_pct": [-10.0, 700.0, -5.0, 6.25],
        "taxable_land_value":        [50000.0, 80000.0, 120000.0, 40000.0],
        "taxable_improvement_value": [150000.0, 0.0, 180000.0, 110000.0],
        "is_fully_exempt": [False, False, False, False],
        "median_income": [22000.0, 22000.0, 35000.0, 35000.0],
    })


def test_build_headline_basic():
    h = ew.build_headline(_toy_df())
    assert h["parcels_modeled"] == 4
    assert h["land_base_eur"] == 290000.0
    assert h["improvement_base_eur"] == 440000.0
    assert h["tax_base_eur"] == 730000.0
    assert h["neutral_levy_eur"] == 4050.0          # Σ new_tax
    assert h["gross_shifted_eur"] == 600.0          # Σ|Δ|
    assert h["net_shifted_eur"] == 400.0            # Σ Δ>0
    assert h["land_share_pct"] == 39.7
    assert h["gross_pct_of_levy"] == 14.8
    assert h["currency"] == "EUR"


def test_build_buckets_partition_and_sum():
    buckets = ew.build_buckets(_toy_df())
    assert [b["bucket"] for b in buckets] == ["vacant", "lt10", "r10_25", "r25_50", "ge50"]
    assert sum(b["parcels"] for b in buckets) == 4
    # Vacant Land has 0 improvement -> 1 parcel in the vacant bucket
    assert next(b for b in buckets if b["bucket"] == "vacant")["parcels"] == 1
    assert abs(sum(b["value_pct_of_base"] for b in buckets) - 100.0) < 0.5
