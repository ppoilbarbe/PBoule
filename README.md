# PBoule — Générateur de documents pour compétition de pétanque

Outil de génération des documents nécessaires à l'organisation d'une compétition de pétanque
avec phase de poules suivie d'une phase finale à élimination directe.

## Liens

| Ressource | URL |
|---|---|
| Dépôt GitHub | https://github.com/ppoilbarbe/PBoule |
| Documentation & documents | https://ppoilbarbe.github.io/PBoule/ |

---

## Documents produits

| Document | Description |
|---|---|
| `guide_organisateur.pdf` | Guide de l'organisateur — procédure complète étape par étape |
| `feuille_inscription.pdf` | Tableau d'inscription des équipes (jusqu'à 32 équipes, A4 portrait) |
| `poule_A.pdf` … `poule_H.pdf` | Feuilles de poule A4 paysage — 2 pages : p.1 = `POOL_BASE` équipes, p.2 = `POOL_BASE+1` équipes |
| `poule_unique_{N}eq.pdf` | Feuille pour une poule unique (cas non décomposables : 6, 7 équipes avec `POOL_BASE=4`) |
| `poule_C_11eq.pdf` | Feuille spéciale 11 équipes : répartition A=4/B=4/C=3 + feuille de poule C (3 équipes) |
| `finales_{NN}eq.pdf` | Feuille de phases finales (tableau à élimination directe, 2P < 16) |
| `finales_huitieme_{NN}eq.pdf` | 8es de finale pré-remplis + colonne « Quarts → » vide (2P ≥ 16) |
| `finales_quart_{NN}eq.pdf` | Quarts de finale → finale, tout vide + match 3e place (2P ≥ 16) |

---

## Récupérer les documents sans installer quoi que ce soit

Les PDF prêts à l'emploi sont disponibles de deux façons.

### Via le site de documentation (GitHub Pages)

Ouvrir https://ppoilbarbe.github.io/PBoule/ et télécharger les PDF directement
depuis la section **Documents créés**.

### Via une GitHub Release

1. Aller sur https://github.com/ppoilbarbe/PBoule/releases
2. Choisir la version souhaitée.
3. Télécharger l'archive ZIP ou les PDF individuels en pièces jointes de la release.

---

## Générer les documents localement

### Prérequis

- [Conda](https://docs.conda.io/) (Miniconda ou Anaconda)
- GNU Make ≥ 4.3

### Installation

```bash
git clone https://github.com/ppoilbarbe/PBoule.git
cd PBoule
make env          # crée l'environnement conda 'pboule'
make install-hooks  # installe les hooks pre-commit (optionnel)
make logo         # calcule les caractéristiques des logos → logo.yaml
make all          # génère tous les documents dans documents/
```

Les PDF sont déposés dans le dossier `documents/`.

### Personnaliser les paramètres

Les paramètres peuvent être modifiés de deux façons.

Les paramètres sont surchargés par ordre de priorité décroissant :

| Priorité | Méthode | Exemple |
|---|---|---|
| 1 (haute) | Ligne de commande | `make all TEAMS_MAX=24` |
| 2 | Variable d'environnement | `export TEAMS_MAX=24 && make all` |
| 3 (basse) | Valeur par défaut du `Makefile` | — |

| Variable | Défaut | Rôle |
|---|---|---|
| `TEAMS_MIN` | `6` | Nombre minimal d'équipes |
| `TEAMS_MAX` | `32` | Nombre maximal d'équipes |
| `POOL_BASE` | `4` | Taille de base des poules |
| `LOGO_H` | `3.5` | Hauteur des logos en cm |

Pour modifier les valeurs de façon permanente, éditer directement les variables en tête du `Makefile`.

### Cibles Makefile

| Cible | Description | Dépendances |
|---|---|---|
| `help` | Affiche la liste des cibles disponibles et les paramètres actifs | — |
| `all` | Génère tous les documents | `pboule-pdf`, `guide-pdf`, `feuilles-poules`, `feuille-inscription`, `feuilles-finales` |
| `logo` | Calcule les caractéristiques des logos → `logo.yaml` | fichiers logos |
| `feuilles-poules` | Génère tous les gabarits de feuilles de poule dans `documents/` | `logo` |
| `feuille-inscription` | Génère la feuille d'inscription dans `documents/` | `logo` |
| `pboule-pdf` | Convertit `PBOULE.md` en `documents/pboule.pdf` via pandoc + tectonic | `logo` |
| `guide-pdf` | Convertit `GUIDE_ORGANISATEUR.md` en `documents/guide_organisateur.pdf` | `logo` |
| `init` | Crée le dossier `documents/` s'il n'existe pas | — |
| `clean` | Supprime `documents/` et les caches Python | — |
| `clean-all` | `clean` + suppression de l'environnement conda `pboule` | `clean` |
| `env` | Crée ou met à jour l'environnement conda depuis `environment.yml` | — |
| `check` | Vérifie que l'environnement conda `pboule` est disponible | — |
| `lint` | Analyse le code Python avec ruff (lint + formatage) | — |
| `bump-major` | Incrémente la version majeure (`X.Y.Z → (X+1).0.0`) | — |
| `bump-minor` | Incrémente la version mineure (`X.Y.Z → X.(Y+1).0`) | — |
| `bump-patch` | Incrémente la version patch (`X.Y.Z → X.Y.(Z+1)`) | — |
| `install-hooks` | Installe les hooks pre-commit dans le dépôt git local | — |
| `feuilles-finales` | Génère les feuilles de phases finales dans `documents/` | `logo` |
| `pages` | Génère le site statique dans `pages/` (HTML + PDF) | `guide-pdf`, `feuilles-poules`, `feuille-inscription`, `feuilles-finales` |

---

## Pipeline CI/CD

Le fichier `.github/workflows/ci.yml` définit quatre jobs :

| Job | Déclencheur | Dépendances | Description |
|---|---|---|---|
| `lint` | push, PR | — | Analyse ruff via pre-commit (lint + formatage) |
| `generate` | push, PR | `lint` | Génère tous les PDF (hors `pboule-pdf`) et les archive |
| `release` | tag `vX.Y.Z` | `generate` | Crée une GitHub Release avec les PDF et une archive ZIP |
| `pages` | tag `vX.Y.Z` | `generate` | Génère et publie le site de documentation sur GitHub Pages |

### Workflow de release

Avant tout tag/release, mettre à jour `CHANGELOG.md` avec une section `## [X.Y.Z] – YYYY-MM-DD`
(via `make bump-minor` ou `make bump-patch`), compléter les notes, puis commiter et pousser.

```bash
make bump-patch           # incrémente la version et ajoute un placeholder dans CHANGELOG.md
# … compléter la section générée dans CHANGELOG.md …
git add CHANGELOG.md pyproject.toml
git commit -m "..."
git push origin main
git tag v0.3.0
git push origin v0.3.0
```

Le pipeline CI publie alors :
- **GitHub Release** — archive ZIP + PDF individuels (feuilles de poule, feuille d'inscription)
- **GitHub Pages** — site de documentation statique avec les spécifications, les liens vers les PDF et le changelog

### Site GitHub Pages (`pages/`)

| Fichier | Description |
|---|---|
| `index.html` | Site complet (spécifications + documents + changelog) |
| `style.css` | Feuille de style |
| `guide_organisateur.pdf` | Copie du PDF (téléchargement direct) |
| `feuille_inscription.pdf` | Copie des PDF (téléchargement direct) |
| `poule_*.pdf` | Copie des PDF (téléchargement direct) |
| `finales_*.pdf` | Copie des PDF de phases finales (téléchargement direct) |

Le dossier `pages/` n'est pas versionné (dans `.gitignore`) et est supprimé par `make clean`.

---

## Structure du projet

```
PBoule/
├── python/                        # Scripts Python de génération
│   ├── pboule/                    # Package partagé
│   │   ├── __init__.py
│   │   ├── poules.py              # Répartition, COULEURS, NOMS_POULES
│   │   ├── palette.py             # Constantes de couleur ReportLab
│   │   ├── logos.py               # Rendu des logos sur les PDF
│   │   └── utils.py               # charger_logo_yaml
│   ├── generate_feuille_poule.py  # Feuilles de poule
│   ├── generate_feuille_inscription.py  # Feuille d'inscription
│   ├── generate_phases_finales.py # Feuilles de phases finales
│   ├── generate_pages.py          # Site de documentation GitHub Pages
│   ├── compute_logo_yaml.py       # Cache des caractéristiques des logos
│   └── extract_changelog.py       # Extraction des notes de release
├── documents/                     # PDF générés (ignoré par git)
├── pages/                         # Site statique généré (ignoré par git)
├── .github/workflows/ci.yml       # Pipeline CI/CD GitHub Actions
├── Makefile                       # Pilote la génération
├── environment.yml                # Dépendances conda
├── PBOULE.md                      # Spécifications complètes du projet
├── CHANGELOG.md                   # Historique des versions
├── creation_logo_petanque.md      # Méthode de création du logo pétanque
├── logo_COF_montlaur_rose.png     # Logo principal (COF Montlaur)
├── logo_petanque.png              # Logo secondaire (boules)
└── logo.yaml                      # Cache des ratios d'aspect des logos
```

---

## Documentation complète

Les spécifications détaillées du projet (règles de répartition en poules,
formats des documents, algorithmes, pipeline CI/CD) sont dans
[PBOULE.md](PBOULE.md) et consultables en ligne sur le
[site de documentation](https://ppoilbarbe.github.io/PBoule/).
