# Registre d'ingestion & validations par commune

*Généré par `preflight.py`. Pour chaque commune : disponibilité des sources ouvertes, cause analysée de tout échec, adaptation, et les validations clés du modèle. C'est un contrôle, jamais une cible de calibration.*

## Synthèse

| Commune | INSEE | Dépt | Modélisable | Verdict | FAIL | WARN |
|---|---|---|---|---|---|---|
| Grenoble | 38185 | 38 | oui | OK | 0 | 0 |
| Annemasse | 74012 | 74 | oui | OK | 0 | 0 |
| Villeurbanne | 69266 | 69 | oui | OK | 0 | 0 |
| Roubaix | 59512 | 59 | oui | WARN | 0 | 1 |
| Cahors | 46042 | 46 | oui | WARN | 0 | 1 |
| Montreuil | 93048 | 93 | oui | OK | 0 | 0 |
| Figeac | 46102 | 46 | oui | WARN | 0 | 1 |
| Sète | 34301 | 34 | oui | OK | 0 | 0 |
| La Rochelle | 17300 | 17 | oui | WARN | 0 | 1 |
| Mulhouse | 68224 | 68 | **non** | FAIL | 1 | 1 |
| Paris | 75056 | 75 | oui | WARN | 0 | 1 |
| Lyon | 69123 | 69 | oui | OK | 0 | 0 |

## Détail par commune

### Grenoble (38185, dépt 38) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP'] ; modélisé Commune+GFP = 189,047,707 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 12,895 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (65 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 55.1 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 3.7 % au plancher (15%).

### Annemasse (74012, dépt 74) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP'] ; modélisé Commune+GFP = 23,048,511 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 5,204 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (10 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 52.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Villeurbanne (69266, dépt 69) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 87,188,801 € ; hors périmètre 1.7 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 10,782 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (45 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 52.4 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.2 % au plancher (15%).

### Roubaix (59512, dépt 59) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 37,738,326 € ; hors périmètre 5.3 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 33,992 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (34 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 42.3 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 3.4 % au plancher (15%).

### Cahors (46042, dépt 46) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP'] ; modélisé Commune+GFP = 22,690,869 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 21,906 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (9 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 41.2 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 4.6 % au plancher (15%).

### Montreuil (93048, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 101,780,897 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 14,218 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (40 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 63.9 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Figeac (46102, dépt 46) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP'] ; modélisé Commune+GFP = 10,022,009 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 12,877 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (4 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 46.2 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 1.4 % au plancher (15%).

### Sète (34301, dépt 34) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP'] ; modélisé Commune+GFP = 47,431,792 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 11,300 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (17 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 55.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 0.4 % au plancher (15%).

### La Rochelle (17300, dépt 17) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP'] ; modélisé Commune+GFP = 73,238,295 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 29,209 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (29 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 66.1 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Mulhouse (68224, dépt 68) — FAIL

> **Non modélisable** par la méthode actuelle (voir ci-dessous).

- **[FAIL] dvf_coverage** (source) — Dépt 68 (Alsace-Moselle) : ventes au Livre Foncier, absentes du DVF ouvert.  
  *Adaptation :* Non modélisable par la méthode hédonique DVF. Pistes : source Livre Foncier (DGFiP/ANCT) ou retrait du panel.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP'] ; modélisé Commune+GFP = 61,665,015 € ; hors périmètre 0.0 % du produit FB total.
- **[WARN] model_ran** (run) — Modèle non exécuté (pas de sortie standard).

### Paris (75056, dépt 75) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 1,840,896,539 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 78,189 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (754 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 74.2 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 3.2 % au plafond (85%), 0.0 % au plancher (15%).

### Lyon (69123, dépt 69) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 362,922,188 € ; hors périmètre 0.4 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 34,142 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (160 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 57.8 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).


# Territoire Paris extra-muros (petite couronne) — communes membres

*Généré par `preflight.py`. Pour chaque commune : disponibilité des sources ouvertes, cause analysée de tout échec, adaptation, et les validations clés du modèle. C'est un contrôle, jamais une cible de calibration.*

## Synthèse

| Commune | INSEE | Dépt | Modélisable | Verdict | FAIL | WARN |
|---|---|---|---|---|---|---|
| Antony | 92002 | 92 | oui | OK | 0 | 0 |
| Asnières-sur-Seine | 92004 | 92 | oui | OK | 0 | 0 |
| Bagneux | 92007 | 92 | oui | OK | 0 | 0 |
| Bois-Colombes | 92009 | 92 | oui | WARN | 0 | 1 |
| Boulogne-Billancourt | 92012 | 92 | oui | WARN | 0 | 1 |
| Bourg-la-Reine | 92014 | 92 | oui | OK | 0 | 0 |
| Châtenay-Malabry | 92019 | 92 | oui | OK | 0 | 0 |
| Châtillon | 92020 | 92 | oui | OK | 0 | 0 |
| Chaville | 92022 | 92 | oui | OK | 0 | 0 |
| Clamart | 92023 | 92 | oui | WARN | 0 | 1 |
| Clichy | 92024 | 92 | oui | WARN | 0 | 1 |
| Colombes | 92025 | 92 | oui | OK | 0 | 0 |
| Courbevoie | 92026 | 92 | oui | OK | 0 | 0 |
| Fontenay-aux-Roses | 92032 | 92 | oui | OK | 0 | 0 |
| Garches | 92033 | 92 | oui | WARN | 0 | 1 |
| La Garenne-Colombes | 92035 | 92 | oui | WARN | 0 | 1 |
| Gennevilliers | 92036 | 92 | oui | OK | 0 | 0 |
| Issy-les-Moulineaux | 92040 | 92 | oui | WARN | 0 | 1 |
| Levallois-Perret | 92044 | 92 | oui | WARN | 0 | 1 |
| Malakoff | 92046 | 92 | oui | WARN | 0 | 1 |
| Marnes-la-Coquette | 92047 | 92 | oui | WARN | 0 | 2 |
| Meudon | 92048 | 92 | oui | WARN | 0 | 1 |
| Montrouge | 92049 | 92 | oui | WARN | 0 | 1 |
| Nanterre | 92050 | 92 | oui | OK | 0 | 0 |
| Neuilly-sur-Seine | 92051 | 92 | oui | WARN | 0 | 1 |
| Le Plessis-Robinson | 92060 | 92 | oui | WARN | 0 | 1 |
| Puteaux | 92062 | 92 | oui | WARN | 0 | 1 |
| Rueil-Malmaison | 92063 | 92 | oui | OK | 0 | 0 |
| Saint-Cloud | 92064 | 92 | oui | WARN | 0 | 1 |
| Sceaux | 92071 | 92 | oui | WARN | 0 | 1 |
| Sèvres | 92072 | 92 | oui | WARN | 0 | 1 |
| Suresnes | 92073 | 92 | oui | WARN | 0 | 1 |
| Vanves | 92075 | 92 | oui | WARN | 0 | 1 |
| Vaucresson | 92076 | 92 | oui | WARN | 0 | 1 |
| Ville-d'Avray | 92077 | 92 | oui | WARN | 0 | 1 |
| Villeneuve-la-Garenne | 92078 | 92 | oui | OK | 0 | 0 |
| Aubervilliers | 93001 | 93 | oui | OK | 0 | 0 |
| Aulnay-sous-Bois | 93005 | 93 | oui | OK | 0 | 0 |
| Bagnolet | 93006 | 93 | oui | OK | 0 | 0 |
| Le Blanc-Mesnil | 93007 | 93 | oui | OK | 0 | 0 |
| Bobigny | 93008 | 93 | oui | OK | 0 | 0 |
| Bondy | 93010 | 93 | oui | OK | 0 | 0 |
| Le Bourget | 93013 | 93 | oui | WARN | 0 | 1 |
| Clichy-sous-Bois | 93014 | 93 | oui | WARN | 0 | 1 |
| Coubron | 93015 | 93 | oui | WARN | 0 | 1 |
| La Courneuve | 93027 | 93 | oui | OK | 0 | 0 |
| Drancy | 93029 | 93 | oui | OK | 0 | 0 |
| Dugny | 93030 | 93 | oui | WARN | 0 | 1 |
| Épinay-sur-Seine | 93031 | 93 | oui | OK | 0 | 0 |
| Gagny | 93032 | 93 | oui | OK | 0 | 0 |
| Gournay-sur-Marne | 93033 | 93 | oui | WARN | 0 | 1 |
| L'Île-Saint-Denis | 93039 | 93 | oui | WARN | 0 | 1 |
| Les Lilas | 93045 | 93 | oui | WARN | 0 | 2 |
| Livry-Gargan | 93046 | 93 | oui | OK | 0 | 0 |
| Montfermeil | 93047 | 93 | oui | OK | 0 | 0 |
| Neuilly-Plaisance | 93049 | 93 | oui | OK | 0 | 0 |
| Neuilly-sur-Marne | 93050 | 93 | oui | OK | 0 | 0 |
| Noisy-le-Grand | 93051 | 93 | oui | OK | 0 | 0 |
| Noisy-le-Sec | 93053 | 93 | oui | OK | 0 | 0 |
| Pantin | 93055 | 93 | oui | OK | 0 | 0 |
| Les Pavillons-sous-Bois | 93057 | 93 | oui | OK | 0 | 0 |
| Le Pré-Saint-Gervais | 93061 | 93 | oui | WARN | 0 | 1 |
| Le Raincy | 93062 | 93 | oui | WARN | 0 | 1 |
| Romainville | 93063 | 93 | oui | OK | 0 | 0 |
| Rosny-sous-Bois | 93064 | 93 | oui | OK | 0 | 0 |
| Saint-Denis | 93066 | 93 | oui | OK | 0 | 0 |
| Saint-Ouen-sur-Seine | 93070 | 93 | oui | OK | 0 | 0 |
| Sevran | 93071 | 93 | oui | OK | 0 | 0 |
| Stains | 93072 | 93 | oui | OK | 0 | 0 |
| Tremblay-en-France | 93073 | 93 | oui | OK | 0 | 0 |
| Vaujours | 93074 | 93 | oui | WARN | 0 | 2 |
| Villemomble | 93077 | 93 | oui | OK | 0 | 0 |
| Villepinte | 93078 | 93 | oui | OK | 0 | 0 |
| Villetaneuse | 93079 | 93 | oui | WARN | 0 | 1 |
| Ablon-sur-Seine | 94001 | 94 | oui | WARN | 0 | 1 |
| Alfortville | 94002 | 94 | oui | OK | 0 | 0 |
| Arcueil | 94003 | 94 | oui | WARN | 0 | 1 |
| Boissy-Saint-Léger | 94004 | 94 | oui | WARN | 0 | 1 |
| Bonneuil-sur-Marne | 94011 | 94 | oui | WARN | 0 | 1 |
| Bry-sur-Marne | 94015 | 94 | oui | WARN | 0 | 1 |
| Cachan | 94016 | 94 | oui | OK | 0 | 0 |
| Champigny-sur-Marne | 94017 | 94 | oui | OK | 0 | 0 |
| Charenton-le-Pont | 94018 | 94 | oui | WARN | 0 | 1 |
| Chennevières-sur-Marne | 94019 | 94 | oui | WARN | 0 | 1 |
| Chevilly-Larue | 94021 | 94 | oui | OK | 0 | 0 |
| Choisy-le-Roi | 94022 | 94 | oui | OK | 0 | 0 |
| Créteil | 94028 | 94 | oui | OK | 0 | 0 |
| Fontenay-sous-Bois | 94033 | 94 | oui | OK | 0 | 0 |
| Fresnes | 94034 | 94 | oui | WARN | 0 | 1 |
| Gentilly | 94037 | 94 | oui | WARN | 0 | 1 |
| L'Haÿ-les-Roses | 94038 | 94 | oui | OK | 0 | 0 |
| Ivry-sur-Seine | 94041 | 94 | oui | OK | 0 | 0 |
| Joinville-le-Pont | 94042 | 94 | oui | WARN | 0 | 1 |
| Le Kremlin-Bicêtre | 94043 | 94 | oui | WARN | 0 | 1 |
| Limeil-Brévannes | 94044 | 94 | oui | WARN | 0 | 2 |
| Maisons-Alfort | 94046 | 94 | oui | OK | 0 | 0 |
| Mandres-les-Roses | 94047 | 94 | oui | WARN | 0 | 2 |
| Marolles-en-Brie | 94048 | 94 | oui | WARN | 0 | 1 |
| Nogent-sur-Marne | 94052 | 94 | oui | OK | 0 | 0 |
| Noiseau | 94053 | 94 | oui | WARN | 0 | 1 |
| Orly | 94054 | 94 | oui | WARN | 0 | 1 |
| Ormesson-sur-Marne | 94055 | 94 | oui | WARN | 0 | 1 |
| Périgny | 94056 | 94 | oui | WARN | 0 | 1 |
| Le Perreux-sur-Marne | 94058 | 94 | oui | OK | 0 | 0 |
| Le Plessis-Trévise | 94059 | 94 | oui | WARN | 0 | 1 |
| La Queue-en-Brie | 94060 | 94 | oui | WARN | 0 | 1 |
| Rungis | 94065 | 94 | oui | WARN | 0 | 1 |
| Saint-Mandé | 94067 | 94 | oui | WARN | 0 | 1 |
| Saint-Maur-des-Fossés | 94068 | 94 | oui | OK | 0 | 0 |
| Saint-Maurice | 94069 | 94 | oui | WARN | 0 | 1 |
| Santeny | 94070 | 94 | oui | WARN | 0 | 1 |
| Sucy-en-Brie | 94071 | 94 | oui | OK | 0 | 0 |
| Thiais | 94073 | 94 | oui | OK | 0 | 0 |
| Valenton | 94074 | 94 | oui | WARN | 0 | 1 |
| Villecresnes | 94075 | 94 | oui | WARN | 0 | 1 |
| Villejuif | 94076 | 94 | oui | OK | 0 | 0 |
| Villeneuve-le-Roi | 94077 | 94 | oui | OK | 0 | 0 |
| Villeneuve-Saint-Georges | 94078 | 94 | oui | WARN | 0 | 1 |
| Villiers-sur-Marne | 94079 | 94 | oui | OK | 0 | 0 |
| Vincennes | 94080 | 94 | oui | WARN | 0 | 1 |
| Vitry-sur-Seine | 94081 | 94 | oui | OK | 0 | 0 |

## Détail par commune

### Antony (92002, dépt 92) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 47,997,327 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 12,930 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (27 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 64.2 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Asnières-sur-Seine (92004, dépt 92) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 40,796,419 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 6,329 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (30 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 63.3 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Bagneux (92007, dépt 92) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 31,607,496 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 3,977 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (17 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 56.3 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Bois-Colombes (92009, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 19,306,523 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,111 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (10 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 66.4 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Boulogne-Billancourt (92012, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 70,049,286 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 5,153 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (40 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 71.6 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 4.6 % au plafond (85%), 0.0 % au plancher (15%).

### Bourg-la-Reine (92014, dépt 92) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 13,908,549 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,685 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (8 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 61.7 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Châtenay-Malabry (92019, dépt 92) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 23,470,230 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 3,784 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (14 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 60.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 0.0 % au plancher (15%).

### Châtillon (92020, dépt 92) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 25,377,871 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 3,855 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (11 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 63.7 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Chaville (92022, dépt 92) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 11,681,623 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 3,141 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (9 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 64.8 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Clamart (92023, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 30,750,877 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 9,963 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (20 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 65.1 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Clichy (92024, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 57,222,506 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,489 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (20 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 67.6 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Colombes (92025, dépt 92) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 48,996,924 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 13,743 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (31 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 60.9 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Courbevoie (92026, dépt 92) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 89,916,027 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,082 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (30 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 63.4 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Fontenay-aux-Roses (92032, dépt 92) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 15,705,213 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 3,050 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (11 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 57.9 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Garches (92033, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 11,565,771 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 3,025 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (8 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 66.9 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### La Garenne-Colombes (92035, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 21,071,931 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,958 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (11 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 66.0 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Gennevilliers (92036, dépt 92) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 47,229,689 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 5,454 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (16 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 59.6 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Issy-les-Moulineaux (92040, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 66,607,091 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,787 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (18 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 69.0 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Levallois-Perret (92044, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 69,499,463 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,542 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (22 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 73.2 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Malakoff (92046, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 24,075,736 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 3,719 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (11 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 66.0 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Marnes-la-Coquette (92047, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 1,112,753 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 726 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[WARN] land_share_band** (validation) — Part foncière 67.6 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.2 % au plafond (85%), 0.0 % au plancher (15%).

### Meudon (92048, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 36,919,008 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,797 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (16 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 65.8 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Montrouge (92049, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 29,917,421 € ; hors périmètre 0.1 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,643 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (17 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 67.2 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Nanterre (92050, dépt 92) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 78,761,344 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 10,616 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (32 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 60.4 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Neuilly-sur-Seine (92051, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 56,107,505 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,706 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (26 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 77.2 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 25.0 % au plafond (85%), 0.0 % au plancher (15%).

### Le Plessis-Robinson (92060, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 32,310,782 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,706 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (9 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 59.3 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Puteaux (92062, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 65,322,269 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,573 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (17 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 65.9 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Rueil-Malmaison (92063, dépt 92) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 59,600,666 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 12,476 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (29 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 64.7 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Saint-Cloud (92064, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 24,598,736 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 3,502 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (12 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 69.8 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Sceaux (92071, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 19,479,453 € ; hors périmètre 0.4 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 3,089 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (8 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 66.4 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Sèvres (92072, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 17,922,619 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 3,023 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (10 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 63.5 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Suresnes (92073, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 38,377,406 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,772 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (10 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 68.7 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Vanves (92075, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 20,327,385 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,048 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (11 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 65.6 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Vaucresson (92076, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 6,401,670 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 1,981 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (4 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 61.6 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Ville-d'Avray (92077, dépt 92) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 7,806,971 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 1,241 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (5 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 63.3 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Villeneuve-la-Garenne (92078, dépt 92) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 15,517,454 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 1,656 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (9 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 50.7 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.6 % au plancher (15%).

### Aubervilliers (93001, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 65,678,888 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 5,113 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (25 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 56.5 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).

### Aulnay-sous-Bois (93005, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 46,038,546 € ; hors périmètre 1.5 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 15,820 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (30 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 58.3 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.2 % au plancher (15%).

### Bagnolet (93006, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 41,936,420 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 3,420 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (15 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 59.2 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Le Blanc-Mesnil (93007, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 37,718,303 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 9,562 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (17 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 58.8 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).

### Bobigny (93008, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 44,394,880 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 5,830 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (16 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 48.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.4 % au plancher (15%).

### Bondy (93010, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 28,067,191 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 7,167 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (20 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 54.8 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.7 % au plancher (15%).

### Le Bourget (93013, dépt 93) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 11,707,241 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 1,712 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (6 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 54.6 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.2 % au plancher (15%).

### Clichy-sous-Bois (93014, dépt 93) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 8,731,609 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,734 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (8 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 45.8 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 3.0 % au plancher (15%).

### Coubron (93015, dépt 93) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 2,639,413 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,571 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 59.5 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 0.3 % au plancher (15%).

### La Courneuve (93027, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 29,485,765 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,131 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (12 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 53.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 1.1 % au plancher (15%).

### Drancy (93029, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 42,709,933 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 13,117 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (28 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 57.3 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.2 % au plancher (15%).

### Dugny (93030, dépt 93) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 8,350,486 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 773 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (4 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 50.7 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 1.9 % au plancher (15%).

### Épinay-sur-Seine (93031, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 30,466,312 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 5,095 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (18 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 51.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 1.3 % au plancher (15%).

### Gagny (93032, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 21,361,606 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 9,117 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (17 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 56.9 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.3 % au plancher (15%).

### Gournay-sur-Marne (93033, dépt 93) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 5,017,571 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,437 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (3 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 54.6 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### L'Île-Saint-Denis (93039, dépt 93) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 6,156,918 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 479 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (3 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 52.1 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 1.1 % au plancher (15%).

### Les Lilas (93045, dépt 93) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 19,353,471 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 1,930 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (10 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[WARN] land_share_band** (validation) — Part foncière 65.3 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Livry-Gargan (93046, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 31,873,631 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 9,466 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (17 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 46.4 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.3 % au plancher (15%).

### Montfermeil (93047, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 14,365,624 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 8,264 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (10 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 59.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.5 % au plancher (15%).

### Neuilly-Plaisance (93049, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 13,509,514 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 5,439 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (9 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 61.5 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).

### Neuilly-sur-Marne (93050, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 20,736,523 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,175 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (12 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 52.3 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.5 % au plancher (15%).

### Noisy-le-Grand (93051, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 50,850,413 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 11,025 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (18 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 50.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.5 % au plancher (15%).

### Noisy-le-Sec (93053, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 32,570,204 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 6,665 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (16 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 55.8 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.2 % au plancher (15%).

### Pantin (93055, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 60,930,640 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,922 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (18 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 63.8 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Les Pavillons-sous-Bois (93057, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 16,180,609 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 5,049 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (9 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 56.3 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.3 % au plancher (15%).

### Le Pré-Saint-Gervais (93061, dépt 93) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 13,866,221 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 1,033 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (7 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 64.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Le Raincy (93062, dépt 93) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 10,469,345 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,931 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (6 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 58.8 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Romainville (93063, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 24,010,047 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,568 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (10 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 63.4 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Rosny-sous-Bois (93064, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 35,807,190 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 6,477 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (14 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 57.5 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).

### Saint-Denis (93066, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 131,514,486 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 13,548 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (35 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 56.4 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.3 % au plancher (15%).

### Saint-Ouen-sur-Seine (93070, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 60,493,371 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,001 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (17 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 64.9 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Sevran (93071, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 23,579,838 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 8,046 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (20 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 51.1 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.7 % au plancher (15%).

### Stains (93072, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 21,381,251 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 5,450 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (14 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 54.9 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.7 % au plancher (15%).

### Tremblay-en-France (93073, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 60,445,648 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 10,725 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (13 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 47.6 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 1.4 % au plancher (15%).

### Vaujours (93074, dépt 93) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 3,436,478 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,353 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (2 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[WARN] land_share_band** (validation) — Part foncière 39.0 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 0.1 % au plancher (15%).

### Villemomble (93077, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 17,358,131 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 6,236 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (12 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 58.5 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).

### Villepinte (93078, dépt 93) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 33,822,711 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 7,528 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (14 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 42.8 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 1.7 % au plancher (15%).

### Villetaneuse (93079, dépt 93) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 7,522,410 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 1,855 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (5 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 48.6 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 2.1 % au plancher (15%).

### Ablon-sur-Seine (94001, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 3,291,743 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 1,310 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 56.1 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.3 % au plancher (15%).

### Alfortville (94002, dépt 94) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 31,303,882 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,130 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (15 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 59.5 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Arcueil (94003, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 21,282,440 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,827 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (9 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 57.6 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Boissy-Saint-Léger (94004, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 9,983,752 € ; hors périmètre 1.7 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,917 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (6 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 45.7 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 1.7 % au plancher (15%).

### Bonneuil-sur-Marne (94011, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 15,652,367 € ; hors périmètre 2.8 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,496 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (7 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 61.9 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 0.3 % au plancher (15%).

### Bry-sur-Marne (94015, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 14,173,991 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,743 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (6 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 59.7 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Cachan (94016, dépt 94) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 23,212,937 € ; hors périmètre 3.1 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 3,813 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (11 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 57.1 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Champigny-sur-Marne (94017, dépt 94) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 41,547,661 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 15,492 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (32 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 57.1 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).

### Charenton-le-Pont (94018, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 26,522,001 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 1,162 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (10 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 67.4 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Chennevières-sur-Marne (94019, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 15,966,224 € ; hors périmètre 0.9 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,430 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (8 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 59.3 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.2 % au plancher (15%).

### Chevilly-Larue (94021, dépt 94) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 19,270,840 € ; hors périmètre 3.9 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 1,984 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (8 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 49.6 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Choisy-le-Roi (94022, dépt 94) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 28,074,759 € ; hors périmètre 4.1 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 5,089 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (17 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 54.8 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.2 % au plancher (15%).

### Créteil (94028, dépt 94) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 77,108,288 € ; hors périmètre 0.9 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 6,907 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (30 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 53.9 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.2 % au plancher (15%).

### Fontenay-sous-Bois (94033, dépt 94) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 54,858,206 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 10,139 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (20 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 63.8 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Fresnes (94034, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 17,609,262 € ; hors périmètre 3.6 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,061 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (9 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 50.3 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.5 % au plancher (15%).

### Gentilly (94037, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 22,685,860 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 1,605 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (8 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 61.4 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### L'Haÿ-les-Roses (94038, dépt 94) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 20,445,985 € ; hors périmètre 4.1 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,664 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (12 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 56.6 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).

### Ivry-sur-Seine (94041, dépt 94) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 71,900,663 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,095 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (21 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 59.7 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Joinville-le-Pont (94042, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 16,003,508 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 3,076 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (8 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 64.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Le Kremlin-Bicêtre (94043, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 24,660,386 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 1,195 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (9 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 59.5 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Limeil-Brévannes (94044, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 12,276,206 € ; hors périmètre 3.9 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,654 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (7 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[WARN] land_share_band** (validation) — Part foncière 38.0 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 2.3 % au plancher (15%).

### Maisons-Alfort (94046, dépt 94) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 31,572,094 € ; hors périmètre 1.2 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 5,873 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (23 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 60.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Mandres-les-Roses (94047, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 2,891,586 € ; hors périmètre 5.5 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 2,445 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 60.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.2 % au plafond (85%), 0.1 % au plancher (15%).

### Marolles-en-Brie (94048, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 3,267,601 € ; hors périmètre 2.1 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 1,828 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (2 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 45.8 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).

### Nogent-sur-Marne (94052, dépt 94) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 24,404,583 € ; hors périmètre 1.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 3,880 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (11 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 64.7 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Noiseau (94053, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 2,858,440 € ; hors périmètre 1.4 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 1,788 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 51.9 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.3 % au plafond (85%), 0.2 % au plancher (15%).

### Orly (94054, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 19,980,743 € ; hors périmètre 2.7 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 3,321 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (7 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 57.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.5 % au plancher (15%).

### Ormesson-sur-Marne (94055, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 8,231,758 € ; hors périmètre 1.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,534 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (5 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 64.9 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 0.0 % au plancher (15%).

### Périgny (94056, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 1,291,669 € ; hors périmètre 4.2 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 1,597 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 41.8 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 1.2 % au plancher (15%).

### Le Perreux-sur-Marne (94058, dépt 94) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 24,323,589 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 7,256 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (13 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 63.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Le Plessis-Trévise (94059, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 10,448,157 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 3,613 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (7 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 46.1 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.8 % au plancher (15%).

### La Queue-en-Brie (94060, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 7,184,494 € ; hors périmètre 2.5 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 3,835 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (5 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 46.8 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 0.1 % au plancher (15%).

### Rungis (94065, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 14,013,480 € ; hors périmètre 3.6 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 1,688 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (2 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 46.1 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 0.0 % au plancher (15%).

### Saint-Mandé (94067, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 18,292,417 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 1,100 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (9 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 72.5 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Saint-Maur-des-Fossés (94068, dépt 94) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 59,920,568 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 16,690 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (34 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 64.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Saint-Maurice (94069, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 11,829,598 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 811 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (4 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 62.4 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Santeny (94070, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 3,141,206 € ; hors périmètre 0.6 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,778 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 40.4 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 0.5 % au plancher (15%).

### Sucy-en-Brie (94071, dépt 94) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 17,917,365 € ; hors périmètre 1.3 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 7,644 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (11 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 60.6 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Thiais (94073, dépt 94) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 22,679,156 € ; hors périmètre 0.5 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,288 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (12 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 58.2 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.2 % au plancher (15%).

### Valenton (94074, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 9,064,654 € ; hors périmètre 0.7 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,870 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (5 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 61.6 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 0.6 % au plancher (15%).

### Villecresnes (94075, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 7,192,262 € ; hors périmètre 4.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 5,923 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (4 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 51.2 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).

### Villejuif (94076, dépt 94) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 42,882,253 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 6,404 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (21 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 59.8 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Villeneuve-le-Roi (94077, dépt 94) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 12,701,880 € ; hors périmètre 3.6 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 6,133 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (8 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 61.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).

### Villeneuve-Saint-Georges (94078, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 13,103,080 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 5,730 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (13 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 53.7 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.2 % au plancher (15%).

### Villiers-sur-Marne (94079, dépt 94) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'Syndicat'] ; modélisé Commune+GFP = 17,879,209 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 6,340 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (9 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 55.6 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).

### Vincennes (94080, dépt 94) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 41,173,145 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 2,971 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (17 revenus IRIS distincts).
- **[WARN] land_share_band** (validation) — Part foncière 73.5 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Vitry-sur-Seine (94081, dépt 94) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune'] ; modélisé Commune+GFP = 59,541,928 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 12,806 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (36 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 56.4 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).


# Territoire Lyon extra-muros (Métropole hors Lyon) — communes membres

*Généré par `preflight.py`. Pour chaque commune : disponibilité des sources ouvertes, cause analysée de tout échec, adaptation, et les validations clés du modèle. C'est un contrôle, jamais une cible de calibration.*

## Synthèse

| Commune | INSEE | Dépt | Modélisable | Verdict | FAIL | WARN |
|---|---|---|---|---|---|---|
| Albigny-sur-Saône | 69003 | 69 | oui | WARN | 0 | 2 |
| Bron | 69029 | 69 | oui | OK | 0 | 0 |
| Cailloux-sur-Fontaines | 69033 | 69 | oui | WARN | 0 | 2 |
| Caluire-et-Cuire | 69034 | 69 | oui | OK | 0 | 0 |
| Champagne-au-Mont-d'Or | 69040 | 69 | oui | WARN | 0 | 2 |
| Charbonnières-les-Bains | 69044 | 69 | oui | WARN | 0 | 2 |
| Charly | 69046 | 69 | oui | WARN | 0 | 2 |
| Collonges-au-Mont-d'Or | 69063 | 69 | oui | WARN | 0 | 3 |
| Couzon-au-Mont-d'Or | 69068 | 69 | oui | WARN | 0 | 2 |
| Craponne | 69069 | 69 | oui | WARN | 0 | 2 |
| Curis-au-Mont-d'Or | 69071 | 69 | oui | WARN | 0 | 2 |
| Dardilly | 69072 | 69 | oui | WARN | 0 | 1 |
| Écully | 69081 | 69 | oui | WARN | 0 | 2 |
| Fleurieu-sur-Saône | 69085 | 69 | oui | WARN | 0 | 3 |
| Fontaines-Saint-Martin | 69087 | 69 | oui | WARN | 0 | 2 |
| Fontaines-sur-Saône | 69088 | 69 | oui | WARN | 0 | 2 |
| Francheville | 69089 | 69 | oui | WARN | 0 | 2 |
| Givors | 69091 | 69 | oui | WARN | 0 | 2 |
| Grigny-sur-Rhône | 69096 | 69 | oui | WARN | 0 | 2 |
| Irigny | 69100 | 69 | oui | WARN | 0 | 2 |
| Limonest | 69116 | 69 | oui | WARN | 0 | 2 |
| Lissieu | 69117 | 69 | oui | WARN | 0 | 2 |
| Marcy-l'Étoile | 69127 | 69 | oui | WARN | 0 | 1 |
| La Mulatière | 69142 | 69 | oui | WARN | 0 | 1 |
| Neuville-sur-Saône | 69143 | 69 | oui | WARN | 0 | 2 |
| Oullins-Pierre-Bénite | 69149 | 69 | oui | WARN | 0 | 1 |
| Poleymieux-au-Mont-d'Or | 69153 | 69 | oui | WARN | 0 | 2 |
| Quincieux | 69163 | 69 | oui | WARN | 0 | 2 |
| Rochetaillée-sur-Saône | 69168 | 69 | oui | WARN | 0 | 2 |
| Saint-Cyr-au-Mont-d'Or | 69191 | 69 | oui | WARN | 0 | 2 |
| Saint-Didier-au-Mont-d'Or | 69194 | 69 | oui | WARN | 0 | 2 |
| Saint-Fons | 69199 | 69 | oui | WARN | 0 | 2 |
| Sainte-Foy-lès-Lyon | 69202 | 69 | oui | OK | 0 | 0 |
| Saint-Genis-Laval | 69204 | 69 | oui | WARN | 0 | 2 |
| Saint-Genis-les-Ollières | 69205 | 69 | oui | WARN | 0 | 2 |
| Saint-Germain-au-Mont-d'Or | 69207 | 69 | oui | WARN | 0 | 2 |
| Saint-Romain-au-Mont-d'Or | 69233 | 69 | oui | WARN | 0 | 2 |
| Tassin-la-Demi-Lune | 69244 | 69 | oui | WARN | 0 | 2 |
| La Tour-de-Salvagny | 69250 | 69 | oui | WARN | 0 | 2 |
| Vaulx-en-Velin | 69256 | 69 | oui | WARN | 0 | 1 |
| Vénissieux | 69259 | 69 | oui | WARN | 0 | 1 |
| Vernaison | 69260 | 69 | oui | WARN | 0 | 2 |
| Chassieu | 69271 | 69 | oui | WARN | 0 | 1 |
| Corbas | 69273 | 69 | oui | WARN | 0 | 2 |
| Décines-Charpieu | 69275 | 69 | oui | WARN | 0 | 1 |
| Feyzin | 69276 | 69 | oui | WARN | 0 | 2 |
| Genay | 69278 | 69 | oui | WARN | 0 | 2 |
| Jonage | 69279 | 69 | oui | WARN | 0 | 1 |
| Meyzieu | 69282 | 69 | oui | WARN | 0 | 1 |
| Mions | 69283 | 69 | oui | WARN | 0 | 2 |
| Montanay | 69284 | 69 | oui | WARN | 0 | 2 |
| Rillieux-la-Pape | 69286 | 69 | oui | WARN | 0 | 1 |
| Saint-Priest | 69290 | 69 | oui | WARN | 0 | 1 |
| Sathonay-Camp | 69292 | 69 | oui | WARN | 0 | 2 |
| Sathonay-Village | 69293 | 69 | oui | WARN | 0 | 2 |
| Solaize | 69296 | 69 | oui | WARN | 0 | 2 |

## Détail par commune

### Albigny-sur-Saône (69003, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 1,073,739 € ; hors périmètre 19.2 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 1,568 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 56.1 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).

### Bron (69029, dépt 69) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 21,582,099 € ; hors périmètre 1.4 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 6,132 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (16 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 49.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.8 % au plancher (15%).

### Cailloux-sur-Fontaines (69033, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 1,600,805 € ; hors périmètre 11.7 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 3,131 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 56.4 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 0.0 % au plancher (15%).

### Caluire-et-Cuire (69034, dépt 69) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 29,258,456 € ; hors périmètre 1.6 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 6,583 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (18 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 55.6 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Champagne-au-Mont-d'Or (69040, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 4,345,037 € ; hors périmètre 9.4 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 1,854 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (2 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 53.5 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Charbonnières-les-Bains (69044, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 2,659,236 € ; hors périmètre 11.5 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 2,503 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 57.9 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).

### Charly (69046, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 2,219,478 € ; hors périmètre 12.2 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 3,689 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 59.8 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Collonges-au-Mont-d'Or (69063, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 2,522,063 € ; hors périmètre 9.0 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 3,102 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[WARN] land_share_band** (validation) — Part foncière 65.1 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Couzon-au-Mont-d'Or (69068, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 1,076,712 € ; hors périmètre 23.3 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 2,167 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 59.1 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Craponne (69069, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 6,560,907 € ; hors périmètre 7.9 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 4,765 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (3 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 52.1 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Curis-au-Mont-d'Or (69071, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 418,674 € ; hors périmètre 13.0 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 1,349 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 58.8 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Dardilly (69072, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP'] ; modélisé Commune+GFP = 7,711,334 € ; hors périmètre 0.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 6,097 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (3 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 56.7 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 0.0 % au plancher (15%).

### Écully (69081, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 12,296,650 € ; hors périmètre 5.0 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 4,519 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (8 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 58.7 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Fleurieu-sur-Saône (69085, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 709,270 € ; hors périmètre 7.1 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 1,990 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[WARN] land_share_band** (validation) — Part foncière 71.9 % (bande 40–65 %).  
  *Adaptation :* Hors bande : cœur très dense ou imputation à confronter au méthodo — signalé, jamais une cible à atteindre.
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Fontaines-Saint-Martin (69087, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 1,736,663 € ; hors périmètre 6.6 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 2,176 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 57.2 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).

### Fontaines-sur-Saône (69088, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 3,302,077 € ; hors périmètre 6.6 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 1,466 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (3 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 52.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Francheville (69089, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 8,130,390 € ; hors périmètre 10.3 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 4,656 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (5 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 49.1 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Givors (69091, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 9,239,902 € ; hors périmètre 8.4 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 8,494 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (7 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 43.3 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 1.7 % au plancher (15%).

### Grigny-sur-Rhône (69096, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 4,675,440 € ; hors périmètre 13.8 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 3,955 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (3 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 51.1 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 1.2 % au plancher (15%).

### Irigny (69100, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 4,492,298 € ; hors périmètre 17.0 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 4,828 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (3 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 59.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Limonest (69116, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 5,939,063 € ; hors périmètre 9.9 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 3,619 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 50.9 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Lissieu (69117, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 1,801,114 € ; hors périmètre 13.8 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 2,992 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 48.9 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).

### Marcy-l'Étoile (69127, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 3,939,926 € ; hors périmètre 1.7 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 1,905 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 51.3 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 0.1 % au plancher (15%).

### La Mulatière (69142, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 3,005,903 € ; hors périmètre 3.8 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 625 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (3 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 52.3 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Neuville-sur-Saône (69143, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 5,319,823 € ; hors périmètre 6.9 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 2,875 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (3 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 53.1 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Oullins-Pierre-Bénite (69149, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 18,977,304 € ; hors périmètre 7.2 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 6,466 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (10 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 55.1 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Poleymieux-au-Mont-d'Or (69153, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 448,710 € ; hors périmètre 18.3 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 2,329 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 56.2 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Quincieux (69163, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 1,309,345 € ; hors périmètre 8.6 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 3,620 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 54.2 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.2 % au plancher (15%).

### Rochetaillée-sur-Saône (69168, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 659,084 € ; hors périmètre 19.0 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 987 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 54.9 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Saint-Cyr-au-Mont-d'Or (69191, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 3,799,215 € ; hors périmètre 7.8 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 4,947 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (2 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 62.4 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Saint-Didier-au-Mont-d'Or (69194, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 4,516,516 € ; hors périmètre 5.9 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 4,584 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (2 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 62.3 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Saint-Fons (69199, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 10,210,062 € ; hors périmètre 7.9 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 2,503 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (5 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 48.9 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 3.4 % au plancher (15%).

### Sainte-Foy-lès-Lyon (69202, dépt 69) — OK

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 12,031,671 € ; hors périmètre 2.7 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,810 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (8 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 55.1 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Saint-Genis-Laval (69204, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 14,616,914 € ; hors périmètre 5.2 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 7,502 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (8 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 53.5 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Saint-Genis-les-Ollières (69205, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 2,292,153 € ; hors périmètre 16.8 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 3,080 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 58.6 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Saint-Germain-au-Mont-d'Or (69207, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 1,059,928 € ; hors périmètre 9.5 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 2,137 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 58.9 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Saint-Romain-au-Mont-d'Or (69233, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 642,894 € ; hors périmètre 8.8 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 1,526 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 61.8 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Tassin-la-Demi-Lune (69244, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 11,606,087 € ; hors périmètre 7.2 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 4,010 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (5 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 55.4 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### La Tour-de-Salvagny (69250, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 2,058,649 € ; hors périmètre 13.5 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 3,344 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 54.3 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.2 % au plancher (15%).

### Vaulx-en-Velin (69256, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 26,780,695 € ; hors périmètre 3.3 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 7,974 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (14 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 45.5 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 2.5 % au plancher (15%).

### Vénissieux (69259, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 33,628,306 € ; hors périmètre 6.2 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 7,435 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (21 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 48.8 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 1.3 % au plancher (15%).

### Vernaison (69260, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 2,026,688 € ; hors périmètre 21.4 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 2,695 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 58.9 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Chassieu (69271, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 10,082,688 € ; hors périmètre 3.3 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,747 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (4 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 54.6 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Corbas (69273, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 8,808,293 € ; hors périmètre 13.2 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 4,938 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (3 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 51.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 0.5 % au plancher (15%).

### Décines-Charpieu (69275, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 18,831,122 € ; hors périmètre 5.0 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 8,436 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (9 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 50.6 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).

### Feyzin (69276, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 6,894,492 € ; hors périmètre 11.5 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 4,264 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (3 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 56.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.6 % au plancher (15%).

### Genay (69278, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 3,172,300 € ; hors périmètre 10.4 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 4,527 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 53.3 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).

### Jonage (69279, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 5,869,050 € ; hors périmètre 4.8 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 4,415 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (2 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 55.5 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 0.0 % au plancher (15%).

### Meyzieu (69282, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 20,113,544 € ; hors périmètre 5.5 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 10,638 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[OK] income_quintiles** (validation) — Quintiles de revenu : 5/5 bins produits (12 revenus IRIS distincts).
- **[OK] land_share_band** (validation) — Part foncière 53.2 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.1 % au plancher (15%).

### Mions (69283, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 8,793,234 € ; hors périmètre 7.7 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 6,923 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (4 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 52.0 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Montanay (69284, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 1,445,831 € ; hors périmètre 15.8 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 3,070 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 52.1 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.1 % au plafond (85%), 0.0 % au plancher (15%).

### Rillieux-la-Pape (69286, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 14,331,611 € ; hors périmètre 2.6 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 8,647 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (12 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 51.9 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.6 % au plancher (15%).

### Saint-Priest (69290, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[OK] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 45,145,981 € ; hors périmètre 1.1 % du produit FB total.
- **[OK] model_ran** (run) — Exécuté : 11,969 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (19 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 48.5 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.7 % au plancher (15%).

### Sathonay-Camp (69292, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 2,237,627 € ; hors périmètre 6.3 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 1,309 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 49.1 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Sathonay-Village (69293, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 890,718 € ; hors périmètre 12.8 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 2,160 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 52.7 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).

### Solaize (69296, dépt 69) — WARN

- **[OK] dvf_coverage** (source) — DVF complet : 5/5 années.
- **[OK] cadastre_parcelles** (source) — Parcellaire cadastral disponible.
- **[OK] cadastre_batiments** (source) — Bâti cadastral (DGFiP) disponible pour le contrôle croisé.
- **[WARN] rei_layers** (source) — REI FB 2025 : couches ['Commune', 'GFP', 'Syndicat'] ; modélisé Commune+GFP = 2,112,766 € ; hors périmètre 13.6 % du produit FB total.  
  *Adaptation :* Part non modélisée significative : choix de périmètre à documenter (syndicats/TSE/GEMAPI) ou à élargir.
- **[OK] model_ran** (run) — Exécuté : 2,612 parcelles.
- **[OK] revenue_neutrality** (validation) — Neutralité des recettes : écart 0.00 %.
- **[WARN] income_quintiles** (validation) — Quintiles de revenu : 0/5 bins — revenu IRIS trop peu varié (0 valeurs distinctes).  
  *Adaptation :* Structurel (petite commune / peu d'IRIS) : agrégat quintile mis à null, aucun graphique publié.
- **[OK] land_share_band** (validation) — Part foncière 51.7 % (bande 40–65 %).
- **[OK] land_share_clip** (validation) — Parcelles bâties à la borne de part foncière : 0.0 % au plafond (85%), 0.0 % au plancher (15%).
