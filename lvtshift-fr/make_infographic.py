"""Compose a one-page infographic from one or more commune exports.

Reads output/<commune>.csv (produced by run_commune.py) and renders a shareable
landscape PNG: per-commune headline cards, the income-quintile progressivity
panel, and the impact-by-property-category panel. Labels in French.

Usage:
    python make_infographic.py cahors montreuil roubaix
    python make_infographic.py            # defaults to those three
"""

import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

from config import COMMUNES

DEPT = {"46": "Lot", "93": "Seine-Saint-Denis", "59": "Nord", "69": "Rhône",
        "74": "Haute-Savoie", "38": "Isère"}
COLOR = {"cahors": "#2e7d32", "montreuil": "#1565c0", "roubaix": "#c62828",
         "villeurbanne": "#6a1b9a", "figeac": "#00838f",
         "grenoble": "#ef6c00", "annemasse": "#5d4037"}
RES = ["Single Family Residential", "Condominium", "Large Multi-Family (5+ units)"]
CAT_FR = {"Single Family Residential": "Maison", "Condominium": "Appartement",
          "Large Multi-Family (5+ units)": "Immeuble collectif",
          "Commercial": "Commerce", "Industrial": "Industrie", "Other": "Autre"}
CAT_ORDER = ["Maison", "Appartement", "Immeuble collectif", "Commerce", "Industrie"]
QLAB = ["Q1\n(+ pauvre)", "Q2", "Q3", "Q4", "Q5\n(+ aisé)"]


def load(commune):
    cfg = COMMUNES[commune]
    df = pd.read_csv(f"output/{commune}.csv")
    df["inc"] = pd.to_numeric(df.get("median_income"), errors="coerce")
    vac = df["property_category"] == "Vacant Land"
    # income quintiles over residential built parcels
    b = df[(df["current_tax"] > 0) & df["property_category"].isin(RES)].dropna(subset=["inc"])
    quint = None
    if b["inc"].nunique() >= 5:
        q = pd.qcut(b["inc"], 5, labels=["Q1", "Q2", "Q3", "Q4", "Q5"], duplicates="drop")
        quint = b.groupby(q, observed=True)["tax_change_pct"].median()
    cats = (df[~vac].groupby("property_category")["tax_change_pct"].median()
            .rename(index=CAT_FR))
    return {
        "key": commune, "name": cfg.name, "dept": DEPT.get(cfg.departement, cfg.departement),
        "n": len(df), "produit": df["new_tax"].sum(),
        "land_mill": df["land_millage"].iloc[0], "imp_mill": df["improvement_millage"].iloc[0],
        "income_med": df["inc"].median(),
        "vacant_share": 100 * df.loc[vac, "new_tax"].sum() / df["new_tax"].sum(),
        "quint": quint, "cats": cats,
    }


def euro(x):
    return f"{x/1e6:.1f} M€" if x >= 1e6 else f"{x:,.0f} €".replace(",", " ")


def main(communes):
    data = [load(c) for c in communes]

    fig = plt.figure(figsize=(16, 10), dpi=150)
    fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(2, 6, height_ratios=[0.95, 2.7],
                          left=0.045, right=0.965, top=0.85, bottom=0.155,
                          hspace=0.30, wspace=0.9)

    # ---- title ----
    fig.text(0.045, 0.965, "Taxe foncière → valeur du terrain : qui gagne, qui paie ?",
             fontsize=23, fontweight="bold", va="top")
    fig.text(0.045, 0.925,
             "Simulation d'un transfert de la taxe foncière vers une taxe sur la valeur "
             "du foncier (LVT), à recettes constantes, sur données ouvertes — "
             f"{len(data)} communes françaises.",
             fontsize=12.5, color="#444", va="top")

    # ---- commune cards ----
    for i, d in enumerate(data):
        ax = fig.add_subplot(gs[0, 2 * i:2 * i + 2]); ax.axis("off")
        ax.add_patch(FancyBboxPatch((0.02, 0.05), 0.96, 0.9, boxstyle="round,pad=0.01,rounding_size=0.04",
                     transform=ax.transAxes, facecolor=COLOR[d["key"]], edgecolor="none", alpha=0.10))
        ax.add_patch(plt.Rectangle((0.02, 0.86), 0.96, 0.10, transform=ax.transAxes,
                     facecolor=COLOR[d["key"]], edgecolor="none"))
        ax.text(0.06, 0.91, f"{d['name'].upper()}", color="white", fontsize=13.5,
                fontweight="bold", va="center", transform=ax.transAxes)
        ax.text(0.94, 0.91, d["dept"], color="white", fontsize=10, ha="right",
                va="center", transform=ax.transAxes, alpha=0.9)
        lines = [
            (f"{d['n']:,}".replace(",", " "), "parcelles"),
            (euro(d["produit"]), "produit TFPB (cible exacte)"),
            (f"{d['land_mill']:.2f} : {d['imp_mill']:.2f}", "taux terrain : bâti (pour 1000)"),
            (f"{d['income_med']:,.0f} €".replace(",", " "), "revenu médian du quartier"),
            (f"{d['vacant_share']:.1f} %", "du prélèvement sur le foncier sous-utilisé"),
        ]
        y = 0.74
        for val, lab in lines:
            ax.text(0.06, y, val, fontsize=13, fontweight="bold", va="center",
                    color=COLOR[d["key"]], transform=ax.transAxes)
            ax.text(0.06, y - 0.075, lab, fontsize=8.3, color="#555", va="center",
                    transform=ax.transAxes)
            y -= 0.165

    # ---- income quintile panel (the hero) ----
    axq = fig.add_subplot(gs[1, 0:3])
    axq.axhline(0, color="#999", lw=1)
    for d in data:
        if d["quint"] is None:
            continue
        axq.plot(range(5), d["quint"].reindex(["Q1", "Q2", "Q3", "Q4", "Q5"]).values,
                 marker="o", lw=2.6, ms=8, color=COLOR[d["key"]], label=d["name"])
    axq.set_xticks(range(5)); axq.set_xticklabels(QLAB, fontsize=9.5)
    axq.set_title("Impact par quintile de revenu du quartier (logements)",
                  fontsize=13.5, fontweight="bold", loc="left", pad=8)
    axq.set_ylabel("Variation médiane de la taxe (%)", fontsize=10.5)
    axq.legend(frameon=False, fontsize=10, loc="upper left")
    axq.grid(axis="y", color="#eee"); axq.set_axisbelow(True)
    for s in ("top", "right"):
        axq.spines[s].set_visible(False)
    axq.text(0.0, -0.135, "← baisses pour les quartiers modestes      hausses pour les "
             "quartiers aisés →", transform=axq.transAxes, fontsize=9, color="#666")

    # ---- category panel ----
    axc = fig.add_subplot(gs[1, 3:6])
    cats = [c for c in CAT_ORDER if any(c in d["cats"].index for d in data)]
    y = np.arange(len(cats)); h = 0.8 / len(data)
    for j, d in enumerate(data):
        vals = [d["cats"].get(c, np.nan) for c in cats]
        axc.barh(y + (j - (len(data) - 1) / 2) * h, vals, height=h,
                 color=COLOR[d["key"]], label=d["name"])
    axc.axvline(0, color="#999", lw=1)
    axc.set_yticks(y); axc.set_yticklabels(cats, fontsize=10)
    axc.invert_yaxis()
    axc.set_title("Impact par catégorie de bien", fontsize=13.5, fontweight="bold",
                  loc="left", pad=8)
    axc.set_xlabel("Variation médiane de la taxe (%)", fontsize=10.5)
    axc.grid(axis="x", color="#eee"); axc.set_axisbelow(True)
    for s in ("top", "right"):
        axc.spines[s].set_visible(False)
    axc.text(1.0, -0.135, "Terrain sous-utilisé : passe de ~0 à positif (incite à bâtir)",
             transform=axc.transAxes, fontsize=9, color="#666", ha="right")

    # ---- footer ----
    fig.text(0.045, 0.075,
             "À recettes constantes (vérifié à l'euro)  ·  données ouvertes uniquement "
             "(cadastre, DVF, BD TOPO, DPE, GPU, REI/OFGL, IRIS, Filosofi)  ·  "
             "valeur du terrain imputée par méthode résiduelle.",
             fontsize=9.2, color="#555")
    fig.text(0.045, 0.045,
             "À lire en agrégat (catégorie / quintile), jamais comme une facture "
             "individuelle. La répartition de la taxe actuelle entre bâtis est le maillon "
             "le plus faible : lire les variations comme une tendance.  Voir METHODOLOGIE.md.",
             fontsize=8.6, color="#888", style="italic")

    out = "output/infographic.png"
    fig.savefig(out, dpi=150, facecolor="white", bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
    communes = sys.argv[1:] or ["cahors", "montreuil", "roubaix"]
    main(communes)
