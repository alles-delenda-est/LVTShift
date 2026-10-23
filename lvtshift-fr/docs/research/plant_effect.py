"""How much of industry's LVT cut is the implicit exemption of fixed plant?
First-order, commune by commune: art. 1499 TFPB base B_I (REI, from the
sidecar target x E11) -> revalued gross cost of buildings + installations
~ B_I / (0.5 x 6 %) = B_I / 0.03 (land at 4 % ignored: small). Depreciated
variant x 0.5. Plant = cost - model's industrial building value (floored 0).
Adding plant to the improvement base and re-solving the 4:1 split per commune
(revenue-neutral) gives industry's LVT share with plant taxed.
Run from <wt>/lvtshift-fr with LVTFR_CACHE_DIR set. Args: territory keys."""
import json
import sys
from pathlib import Path

import pandas as pd

import ingest
from config import COMMUNES, TERRITORIES, slug_of

for terr in sys.argv[1:]:
    tot = {"cur": 0.0, "new": 0.0, "new_g": 0.0, "new_d": 0.0}
    rows = []
    for k in TERRITORIES[terr]["members"]:
        cfg = COMMUNES[k]
        f = Path("output") / f"{slug_of(cfg)}.csv"
        side = Path("output") / f"{slug_of(cfg)}.baseline.json"
        if not (f.exists() and side.exists()):
            continue
        d = pd.read_csv(f, usecols=["property_category", "taxable_land_value",
                                    "taxable_improvement_value", "current_tax", "new_tax"])
        t = json.loads(side.read_text(encoding="utf-8"))
        share_i = (t.get("targets") or {}).get("industrial") or 0.0
        e11 = [r["valeur"] for r in ingest._ofgl_records(
            ingest.SRC["ofgl_rei"], f'idcom="{cfg.insee_code}" and annee="2025" and var="E11"',
            "var,valeur")]
        if not e11:
            continue
        cost = share_i * e11[0] / 0.03
        ind = d["property_category"].eq("Industrial")
        L, I = d.taxable_land_value.sum(), d.taxable_improvement_value.sum()
        Li, Ii = d.loc[ind, "taxable_land_value"].sum(), d.loc[ind, "taxable_improvement_value"].sum()
        levy = d.new_tax.sum()

        def ind_tax(plant):
            # revenue-neutral 4:1 split: tax_i = levy x (4 Li + Ii + plant) / (4 L + I + plant)
            return levy * (4 * Li + Ii + plant) / (4 * L + I + plant)
        g, dp = max(cost - Ii, 0.0), max(0.5 * cost - Ii, 0.0)
        tot["cur"] += d.loc[ind, "current_tax"].sum()
        tot["new"] += d.loc[ind, "new_tax"].sum()
        tot["new_g"] += ind_tax(g)
        tot["new_d"] += ind_tax(dp)
        cur = d.loc[ind, "current_tax"].sum()
        if cur > 0:
            rows.append((cfg.name, round(100 * share_i, 1), round(cost / 1e6),
                         round(Ii / 1e6), round(100 * (d.loc[ind, "new_tax"].sum() / cur - 1)),
                         round(100 * (ind_tax(dp) / cur - 1)), round(100 * (ind_tax(g) / cur - 1))))
    print(f"== {terr}: industrial bills vs today: shed only "
          f"{100 * (tot['new'] / tot['cur'] - 1):+.0f}%, with plant (depreciated) "
          f"{100 * (tot['new_d'] / tot['cur'] - 1):+.0f}%, with plant (gross) "
          f"{100 * (tot['new_g'] / tot['cur'] - 1):+.0f}%")
    df = pd.DataFrame(rows, columns=["commune", "ind_share%", "1499_cost_M", "model_imp_M",
                                     "chg_shed%", "chg_plant_dep%", "chg_plant_gross%"])
    print(df.sort_values("ind_share%", ascending=False).head(8).to_string(index=False))
