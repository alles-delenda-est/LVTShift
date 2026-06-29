# Registre d'ingestion & validations par commune

*Généré par `preflight.py`. Pour chaque commune : disponibilité des sources ouvertes, cause analysée de tout échec, adaptation, et les validations clés du modèle. C'est un contrôle, jamais une cible de calibration.*

## Synthèse

| Commune | INSEE | Dépt | Modélisable | Verdict | FAIL | WARN |
|---|---|---|---|---|---|---|
| Grenoble | 38185 | 38 | oui | WARN | 0 | 1 |
| Annemasse | 74012 | 74 | oui | WARN | 0 | 1 |
| Villeurbanne | 69266 | 69 | oui | WARN | 0 | 1 |
| Roubaix | 59512 | 59 | oui | OK | 0 | 0 |
| Cahors | 46042 | 46 | oui | WARN | 0 | 1 |
| Montreuil | 93048 | 93 | oui | WARN | 0 | 1 |
| Figeac | 46102 | 46 | oui | WARN | 0 | 1 |
| Sète | 34301 | 34 | oui | WARN | 0 | 1 |
| La Rochelle | 17300 | 17 | oui | WARN | 0 | 1 |
| Mulhouse | 68224 | 68 | **non** | FAIL | 1 | 1 |

## Détail par commune

### Grenoble (38185, dépt 38) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] model_ran** (run) — Exécuté : 12,853 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (65 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 70.0 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.

### Annemasse (74012, dépt 74) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] model_ran** (run) — Exécuté : 5,111 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (10 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 70.0 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.

### Villeurbanne (69266, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] model_ran** (run) — Exécuté : 10,753 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (45 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 72.4 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.

### Roubaix (59512, dépt 59) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] model_ran** (run) — Exécuté : 33,917 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (34 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 57.0 % (bande 40–65 %).

### Cahors (46042, dépt 46) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] model_ran** (run) — Exécuté : 21,796 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (9 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 54.0 % (bande 40–65 %).

### Montreuil (93048, dépt 93) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] model_ran** (run) — Exécuté : 14,189 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (40 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 83.9 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.

### Figeac (46102, dépt 46) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] model_ran** (run) — Exécuté : 12,809 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (4 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 58.4 % (bande 40–65 %).

### Sète (34301, dépt 34) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] model_ran** (run) — Exécuté : 11,272 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (17 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 71.5 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.

### La Rochelle (17300, dépt 17) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] model_ran** (run) — Exécuté : 29,108 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (29 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 83.5 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.

### Mulhouse (68224, dépt 68) — FAIL

> **Non modélisable** par la méthode actuelle (voir ci-dessous).

- **[FAIL] dvf_coverage** (source) — Dépt 68 (Alsace-Moselle) : ventes au Livre Foncier, absentes du DVF ouvert.  
  *Adaptation :* Non modélisable par la méthode hédonique DVF. Pistes : source Livre Foncier (DGFiP/ANCT) ou retrait du panel.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] model_ran** (run) — Modèle non exécuté (pas de sortie standard).
