# LVTShift-FR — Prise en main (sans jargon)

Un guide sans jargon pour faire tourner l'outil sur votre propre machine. Si une
étape échoue, copiez le texte en rouge et demandez — ne devinez pas.
(Version française de `GUIDE.md`.)

> **Ce que ça fait, en une phrase :** ça estime, parcelle par parcelle, qui
> paierait plus ou moins si une commune française basculait sa *taxe foncière*
> sur la **valeur du terrain** (une taxe foncière sur la valeur foncière, LVT),
> à recettes constantes — et écrit la réponse sous forme de tableur (CSV) plus
> quelques graphiques.

---

## 1. Ce qu'il vous faut d'abord (une seule fois)

- **Python 3.11+** — depuis python.org. À l'installation, cochez
  **« Add Python to PATH »**.
- **Git** — depuis git-scm.com (vous l'avez déjà).

Pour vérifier qu'ils sont installés, ouvrez **PowerShell** et lancez :

```powershell
python --version
git --version
```

Les deux doivent afficher un numéro de version.

---

## 2. Installation (une seule fois, ~3 minutes)

Collez ces blocs dans PowerShell, un par un :

```powershell
# Récupérer le projet (ce fork contient déjà le moteur US sur lequel il s'appuie)
git clone https://github.com/alles-delenda-est/LVTShift.git
cd LVTShift

# Créer un environnement isolé (bac à sable) pour ses bibliothèques Python
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Installer les bibliothèques nécessaires
pip install pandas numpy geopandas matplotlib seaborn
```

Vous saurez que le bac à sable est actif quand votre invite commence par
`(.venv)`.

> **Windows bloque la ligne `Activate.ps1` ?** Si vous voyez *« …Activate.ps1
> cannot be loaded because running scripts is disabled on this system »*, c'est
> un réglage de sécurité par défaut de Windows, pas un problème du projet.
> Corrigez-le **une fois**, pour votre compte uniquement (sans droits admin) :
>
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
>
> Répondez `Y` si demandé, puis relancez la ligne `Activate.ps1`.
> (`RemoteSigned` autorise les scripts de votre machine tout en bloquant ceux,
> non signés, téléchargés sur internet — le réglage développeur standard.)
>
> **Vous préférez ne rien changer ?** Sautez l'activation et appelez directement
> le Python du bac à sable : utilisez `.\.venv\Scripts\python.exe` à la place de
> `python` pour l'installation, et `..\.venv\Scripts\python.exe` une fois dans
> `lvtshift-fr/`.

---

## 3. Le voir tourner en 2 minutes (sans données)

Le projet est livré avec une **commune synthétique (« pour de faux »)** pour voir
toute la machine tourner de bout en bout sans rien télécharger :

```powershell
cd lvtshift-fr
python test_synthetic.py
```

Vous devez voir la fin avec **`ALL CHECKS PASSED`** et une ligne confirmant la
**neutralité budgétaire à 1 % près** (le test clé : le total de la taxe collectée
est inchangé — la taxe est seulement *redistribuée*).

---

## 4. Ce que vous obtenez, et où

Après une exécution, regardez dans `lvtshift-fr/output/` :

- **`grenoble.csv`** — une ligne par parcelle : valeur du terrain, valeur du
  bâti, ancienne taxe, nouvelle taxe, et la variation. C'est le vrai livrable.
- **`reports/grenoble/*.png`** — graphiques (en euros) :
  - `category_impact.png` — gagnants/perdants par type de bien
  - `income_quintile_*.png` — impact selon le niveau de revenu du quartier
  - `ten_pct_share.png` — part des parcelles qui bougent de plus de ±10 %
  - `distribution.png` — l'étalement des variations sur toutes les parcelles

> Deux graphiques que vous pourriez attendre (basés sur l'origine ethnique) ne
> sont **pas** produits : la France ne collecte pas de statistiques ethniques,
> donc l'analyse se fait sur le **revenu**.

---

## 5. Le faire tourner pour une *vraie* commune

Ça marche désormais sur **données ouvertes en direct** — une seule commande :

```powershell
python run_commune.py montreuil
```

Ça télécharge les parcelles de la commune (cadastre), les ventes (DVF), les
bâtiments (BD TOPO), l'année de construction (DPE) et le produit réel de taxe
foncière (REI via OFGL), puis lance le modèle et écrit le CSV + graphiques en
euros. Communes pré-configurées : `villeurbanne`, `roubaix`, `cahors`, `figeac`,
`montreuil`, `grenoble`, `annemasse`. Ajoutez `--no-report` pour un export
tableur seul.

> Sous Windows, lancez `$env:PYTHONUTF8 = "1"` une fois dans la même fenêtre
> PowerShell avant la commande (certains libellés utilisent des caractères que la
> vieille console ne sait pas afficher).

**Lire les résultats avec discernement :** les communes denses (Montreuil,
Villeurbanne, Roubaix) comme rurales (Cahors, Figeac) donnent désormais des
agrégats crédibles — le foncier non bâti est classé par son zonage PLU et
valorisé soit en terrain à bâtir, soit en terre agricole bon marché, si bien que
la campagne ne déforme plus le résultat. Le maillon le plus faible reste la base
de la *taxe actuelle* (voir *Limites connues* du README), donc lisez la
**variation** par catégorie comme une tendance, pas le montant de départ.
Publiez par catégorie de bien ou quintile de revenu, jamais comme la facture
d'un ménage.

Les graphiques basés sur le revenu apparaissent aussi : chaque parcelle reçoit le
revenu médian de son quartier (IRIS) via INSEE Filosofi, d'où l'**impact par
quintile de revenu** — p. ex. à Montreuil les quartiers les plus pauvres voient
des baisses et les plus aisés paient plus. (Le revenu n'existe que pour les
communes de 5 000+ habitants, données 2021 ; quelques quartiers sont vides pour
raison de confidentialité et sortent de l'analyse.)

**Comparer plusieurs communes sur une page :** après en avoir lancé quelques-unes,
créez une infographie partageable avec
`python make_infographic.py cahors montreuil roubaix` (les communes de votre
choix, déjà exécutées). Elle est écrite dans `output/infographic.png`.

---

## 6. Lire les résultats avec discernement (important)

- **Fiez-vous aux agrégats, pas aux factures individuelles.** Les chiffres par
  parcelle reposent sur des imputations ; publiez par **catégorie de bien ou
  quintile de revenu**, jamais comme la facture d'un ménage.
- **Foncier non bâti : lisez les euros, pas les %.** Le terrain nu ne paie pas de
  taxe sur le *bâti* aujourd'hui (c'est normal — c'est la taxe sur le non-bâti,
  distincte), donc sur les graphiques il affiche ~0 % de variation mais une vraie
  hausse en **euros** sous LVT. Ce passage de rien à quelque chose est tout le
  but de la réforme ; le pourcentage est juste indéfini à partir d'une base nulle.
- La base de la taxe actuelle est désormais le maillon le plus faible (comment la
  facture d'aujourd'hui se répartit *entre les bâtis*) — voir *Limites connues*
  du README avant de citer un chiffre.

> Vous voulez la méthode complète — chaque source de données, formule, hypothèse
> et limite réunies ? Voir **`METHODOLOGIE.md`**.

---

## 7. Si quelque chose casse

- `running scripts is disabled on this system` (sur la ligne `Activate.ps1`) →
  lancez `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
  une fois, puis réessayez. Voir l'encadré de la section 2.
- `'python' is not recognized` → Python n'est pas dans le PATH ; réinstallez en
  cochant la case PATH.
- `ModuleNotFoundError` → le bac à sable n'est pas actif (relancez
  `.\.venv\Scripts\Activate.ps1`) ou un `pip install` a été sauté.
- Un `Traceback` rouge → copiez les **dernières lignes** et envoyez-les.
