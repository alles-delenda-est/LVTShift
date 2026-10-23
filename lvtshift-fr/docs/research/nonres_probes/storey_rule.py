"""Compare current storey imputation (height/3) with a usage/nature rule on the BD TOPO probe."""
import sys
import numpy as np
import pandas as pd

b = pd.read_csv(sys.argv[1], low_memory=False)
b["cur"] = np.where(b.lv > 0, b.lv, (b.h.fillna(0) / 3).clip(lower=1).round())
SHED = {"Industriel, agricole ou commercial", "Serre", "Silo"}


def rule(r):
    if r.lv > 0:
        return r.lv
    h = 0 if pd.isna(r.h) else r.h
    if r.nature in SHED or r.usage_1 in ("Annexe", "Agricole", "Industriel", "Sportif") \
            or str(r.construction_legere).lower() == "true":
        return 1
    if r.usage_1 == "Commercial et services":
        return max(1, round(h / 3.5)) if h >= 7 else 1
    return max(1, round(h / 3.0))


b["new"] = b.apply(rule, axis=1)
for k, g in b.groupby(["nature", "usage_1"]):
    if g.area.sum() < 40000:
        continue
    m = g[~(g.lv > 0)]
    print(k, "null-lv area share %.2f" % (m.area.sum() / g.area.sum()),
          "floor area current/rule ratio %.2f" % ((g.cur * g.area).sum() / (g.new * g.area).sum()))
iac = b[(b.nature == "Industriel, agricole ou commercial") & (b.lv > 0)]
print("IAC lv==1 height p10/p50/p90", iac[iac.lv == 1].h.quantile([.1, .5, .9]).round(1).tolist())
cs = b[(b.nature == "Indifférenciée") & (b.usage_1 == "Commercial et services") & (b.lv > 0)]
print("Indiff C&S known lv: area share by lv", (cs.groupby("lv").area.sum() / cs.area.sum()).round(2).head(8).to_dict())
m = cs[cs.lv >= 2]
print("Indiff C&S lv>=2 h/lv p25/p50/p75", (m.h / m.lv).quantile([.25, .5, .75]).round(2).tolist(),
      "n", len(m), " slope %.2f" % ((m.h * m.lv).sum() / (m.lv ** 2).sum()))
tot = b[b.usage_1 != "Résidentiel"]
print("all non-residential: floor area current/rule %.2f" % ((tot.cur * tot.area).sum() / (tot.new * tot.area).sum()))
