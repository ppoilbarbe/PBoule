# Changelog

Tous les changements notables de ce projet sont documentés ici.
Ce projet suit le [versionnage sémantique](https://semver.org/lang/fr/).

## [0.4.0] – 2026-04-22

### Added
- **`GUIDE_ORGANISATEUR.md`** : guide de l'organisateur étape par étape (inscription,
  phase de poules avec tableau de répartition N=6–32 et instruction impression recto-verso,
  phase finale) ; compilé en `guide_organisateur.pdf` via `make guide-pdf` et intégré dans
  `make all`, `make pages` et le site de documentation GitHub Pages.
- **`python/pboule/`** : package partagé (`poules.py`, `palette.py`, `logos.py`, `utils.py`) ;
  tous les scripts de génération importent depuis ce package.
- **Makefile** : cibles `guide-pdf` et `pages-site` ; paramètres de compétition en `?=`
  pour autoriser la surcharge par variable d'environnement ou ligne de commande ; aide mise à jour.

### Changed
- **CI (`ci.yml`)** : le job `generate` appelle `make all` et le job `pages` appelle
  `make pages-site` au lieu de dupliquer les appels Python. Ajouter un nouveau document
  n'implique désormais que de modifier le Makefile. Correctif : génération des phases finales
  et assets `finales_*.pdf` dans la release absents depuis v0.3.0.
- **`PBOULE.md`** : `guide_organisateur.pdf` ajouté aux documents produits.
- **`README.md`** : noms de fichiers de poules corrigés (`poule_A.pdf` au lieu de
  `poule_A_04eq.pdf`) ; section paramètres enrichie (trois modes de surcharge) ;
  dépendances des cibles `all` et `pages` mises à jour ; `guide_organisateur.pdf`
  ajouté au site Pages.
- **`CLAUDE.md`** : reformulation concise (mêmes directives, moins de tokens).

## [0.3.0] – 2026-04-17

### Added
- **`python/generate_phases_finales.py`** : nouveau script générant les feuilles de phases
  finales (tableau à élimination directe, sans bye, avec matches préliminaires si nécessaire).
  Un fichier par groupe de N équipes partageant le même nombre de poules P.
  Page d'instructions incluse. Mode A3 automatique si les cases sont trop petites.
- **Makefile** : cible `phases-finales` et dépendance dans `all` et `pages`.

### Changed
- **Feuilles de poule** : les deux tailles (`POOL_BASE` et `POOL_BASE+1` équipes) sont
  désormais regroupées dans un seul PDF par lettre de poule (`poule_A.pdf`, `poule_B.pdf`…)
  au lieu de deux fichiers séparés (`poule_A_04eq.pdf` / `poule_A_05eq.pdf`).
- **`python/generate_pages.py`** : section « Feuilles de poule » adaptée au nouveau
  nommage ; section « Phases finales » ajoutée.
- **`PBOULE.md`** : table des documents mise à jour (nouveau nommage `poule_{lettre}.pdf`) ;
  tableau de répartition en poules étendu à toutes les valeurs N de `TEAMS_MIN` à `TEAMS_MAX`
  (24 lignes au lieu de 9) ; section « Règles de la phase finale » complétée ;
  spécifications allégées (suppression des redondances).

## [0.2.1] – 2026-04-15

### Added
- **Makefile** : cibles `bump-major`, `bump-minor`, `bump-patch` pour
  incrémenter la version dans `pyproject.toml` et préparer `CHANGELOG.md`.
- **`python/bump_version.py`** : script sous-jacent aux cibles bump-*.
- **`README.md`** : table complète des cibles Makefile (avec dépendances) et
  section Pipeline CI/CD (jobs, workflow de release, structure `pages/`).

### Changed
- **`PBOULE.md`** : recentré sur les spécifications du domaine — sections
  « Structure des fichiers », « Cibles Makefile » et « Pipeline CI/CD »
  déplacées vers `README.md`. Correction de l'en-tête LaTeX pour `pboule.pdf`
  (hauteurs et superposition des logos conformes à la spec).
- **`CLAUDE.md`** : ajout de `README.md` dans les fichiers de référence à
  maintenir ; règle canal conda (uniquement `conda-forge`, jamais `defaults`).
- **`environment.yml`** : ajout de `nodefaults` dans les canaux.
- **CI** : `conda-remove-defaults: "true"` sur les 4 jobs ; arguments
  `--logo-yaml` et `--logo-creation-md` ajoutés au job `pages` (logos absents
  de `index.html` sur GitHub Pages).

### Fixed
- **Logo secondaire** : rendu obligatoire dans `compute_logo_yaml.py`,
  `logos.py` et `generate_pages.py` — erreur explicite si le fichier PNG est
  absent (au lieu d'un fallback silencieux).
- **`pyproject.toml`** : version portée à `0.2.0` (oubli lors de la v0.2.0) ;
  `scripts/` retiré de `src` (dossier supprimé).

## [0.2.0] – 2026-04-15

### Changed
- **Renommage du projet** : « petanque » → « pboule » dans tous les fichiers
  (environnement conda, CI, noms d'artefacts, titres de release).
- **Renommage du fichier de spécifications** : `PETANQUE.md` → `PBOULE.md`.
- **Migration des scripts** : `scripts/extract_changelog.py` et
  `scripts/generate_pages.py` déplacés dans `python/`.
- **Logo pétanque** : remplacement du SVG par le PNG généré
  (`logo_petanque.png`) ; CI et `compute_logo_yaml.py` mis à jour.
- **`generate_pages.py`** : réécriture complète — TOC et logos côte à côte
  (flex), CSS enrichi, section « Documents créés » avec sous-groupes
  (inscription, poules uniques, poules standard par taille).
- **`PBOULE.md` — en-tête LaTeX** : correction du positionnement et des
  tailles des logos dans `pboule.pdf` (`\rlap` pour la superposition,
  hauteurs 3,5 cm et 1,167 cm conformes à la spec).

### Added
- **`README.md`** : présentation du projet, liens GitHub et GitHub Pages,
  instructions d'installation et de génération.
- **`creation_logo_petanque.md`** : documentation de la création du logo.

### Fixed
- **Spécifications logos** : distinction entre la disposition dans les
  documents PDF et dans le site de documentation (`index.html`) — logos à
  droite de la page au même niveau que la table des matières.

## [0.1.1] – 2026-04-14

### Fixed
- **CI — génération des documents** : migration de `pip` + `apt-get` vers
  `conda-incubator/setup-miniconda` avec `environment.yml` dans tous les
  jobs. `pycairo` (dépendance transitive de `svglib`) est désormais fourni
  par conda-forge (wheel binaire), ce qui supprime la compilation depuis les
  sources et l'erreur « Dependency "cairo" not found ».
- **CI — déclencheur push** : étendu à toutes les branches (`branches: ["**"]`)
  afin que `lint` et `generate` s'exécutent systématiquement, pas seulement
  sur `main`.

## [0.1.0] – 2026-04-14

### Added
- **Feuilles de poule** : génération PDF A4 paysage pour les poules A–H
  (4 ou 5 équipes) et les cas « Poule UNIQUE » non décomposables (6, 7, 11 équipes
  avec `POOL_BASE=4`).
- **Feuille d'inscription** : génération PDF A4 portrait (jusqu'à 32 équipes,
  découpe automatique sur 2 pages si nécessaire).
- **Gestion des logos** : `compute_logo_yaml.py` calcule les ratios d'aspect,
  rasterise le SVG pétanque en PNG (cairosvg 150 dpi) et écrit `logo.yaml` (cache
  JSON persistant). Logo COF en haut à droite ; logo pétanque superposé en
  bas-gauche à 1/3 de la taille du logo principal, première page uniquement.
- **Makefile** : cibles `all`, `logo`, `feuilles-poules`, `feuille-inscription`,
  `petanque-pdf`, `pages`, `lint`, `install-hooks`, `env`, `check`, `init`,
  `clean`, `clean-all`. Paramètres affichés dans `make help`.
- **Site de documentation statique** (`make pages`) : `python/generate_pages.py`
  combine les spécifications, les liens vers les PDF et le changelog en un
  `index.html` avec table des matières (pandoc), copie les PDF dans `pages/`.
- **Pipeline CI GitHub Actions** (`.github/workflows/ci.yml`) :
  - Job `lint` (push, PR) : pre-commit ruff sur tous les fichiers.
  - Job `generate` (push, PR) : génération des PDF, archivage artefact.
  - Job `release` (tag `vX.Y.Z`) : GitHub Release avec ZIP + PDF individuels,
    notes extraites depuis `CHANGELOG.md` via `python/extract_changelog.py`.
  - Job `pages` (tag `vX.Y.Z`) : déploiement GitHub Pages.
- **Hooks pre-commit** : `trailing-whitespace`, `end-of-file-fixer`,
  `check-yaml`, `check-added-large-files`, `check-merge-conflict`, ruff lint,
  ruff format.
- **`pyproject.toml`** : nom `pboule`, version, licence MIT, métadonnées,
  dépendances runtime et dev.
- **`LICENSES`** : licence MIT complète du projet et tableau des licences de
  tous les outils tiers (Python, ReportLab, cairosvg, svglib, PyYAML, pandoc,
  tectonic, ruff, pre-commit, gh).
- **`CHANGELOG.md`**, **`PETANQUE.md`** (spécifications complètes),
  **`CLAUDE.md`** (instructions de travail), **`environment.yml`**.

### Changed
- **Feuille d'inscription** : le titre est désormais centré verticalement sur
  le canvas dans la zone logo ; le tableau commence strictement sous le logo
  (plus de risque de chevauchement).
- **Feuilles de poule — tableau Résultats** : tiret quadratin (—) centré dans
  chaque cellule de la colonne Résultats.
- **Feuilles de poule — tableau Classement** : ajout de la colonne « Points »
  après « Équipe ».
- **Feuilles de poule** : le logo n'est dessiné que sur la première page en
  cas de document multi-pages.
