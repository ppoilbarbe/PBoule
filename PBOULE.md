---
header-includes:
  - \usepackage{graphicx}
---

```{=latex}
\noindent\hfill%
\rlap{\includegraphics[height=1.167cm]{logo_petanque.png}}%
\includegraphics[height=3.5cm]{logo_COF_montlaur_rose.png}%
\par\vspace{0.3cm}
```

# Compétition de Pétanque — Spécifications du projet

## Objectif

Générer les documents nécessaires à l'organisation d'une compétition de pétanque avec phase de poules suivie d'une phase finale.

---

## Nomenclature

| Terme | Définition |
|---|---|
| **Document** | Document complet utilisé par les organisateurs. Composé d'une ou plusieurs feuilles. |
| **Feuille** | Document de base imprimé au format A4. Brique élémentaire d'un document. |
| **Poule** | Ensemble d'équipes dont les matches préliminaires servent à établir la feuille de matches finale. |
| **Feuille de poule** | Feuille permettant d'inscrire les résultats des matches d'une poule. |
| **Feuille de matches** | Document couvrant la phase finale, des 16es de finale jusqu'à la finale (tableau à élimination directe). |
| **Feuille d'inscription** | Document permettant d'enregistrer les équipes participantes et le paiement de leur inscription. |

---

## Structure d'une compétition

1. **Inscription** — les équipes s'inscrivent. Les informations sont enregistrées sur la feuille d'inscription.
2. **Phase de poules** — les équipes sont réparties en poules et jouent des matches préliminaires. Les résultats sont inscrits sur les feuilles de poule.
3. **Phase finale** — tableau à élimination directe, des 16es de finale jusqu'à la finale. Géré par la feuille de matches.

---

## Paramètres

| Paramètre | Valeur | Emplacement |
|---|---|---|
| Nombre min d'équipes | **6** | `TEAMS_MIN` dans le Makefile |
| Nombre max d'équipes | **32** | `TEAMS_MAX` dans le Makefile |
| Taille de base des poules | **4 équipes** | `POOL_BASE` dans le Makefile |

---

## Identité visuelle

### Logos

Deux logos sont utilisés sur tous les documents imprimés.

| Fichier | Rôle | Format |
|---|---|---|
| `logo_COF_montlaur_rose.png` | Logo principal — Comité des fêtes de Montlaur | PNG |
| `logo_petanque.png` | Logo secondaire — scène de boules réaliste | PNG |

**Disposition — Documents PDF** : logo principal calé en haut à droite ; logo secondaire superposé en bas à gauche du logo principal, affiché à 1/3 de la taille du logo principal (hauteur et largeur divisées par 3, ratio conservé). Première page uniquement pour les documents multi-pages.

**Disposition — Site de documentation (`index.html`)** : les logos sont affichés à droite de la page, au même niveau que la table des matières (conteneur flex : TOC à gauche, logos à droite). Logo principal à hauteur `LOGO_H` ; logo secondaire superposé en bas à gauche du logo principal, à 1/3 de la taille du logo principal (mêmes règles qu'en PDF).

**Hauteur d'affichage** : paramètre `LOGO_H` dans le Makefile (défaut 3,5 cm).

### Fichiers de configuration des logos

| Fichier | Origine | Fonction |
|---|---|---|
| `logo.yaml` | `make logo` | Cache JSON des chemins et ratios d'aspect des logos. Évite de relire les fichiers image à chaque génération de document. Persistant : non supprimé par `make clean`. |

Ce fichier est produit par la commande `compute_logo_yaml.py` : si absent ou périmé, il est régénéré par `make logo`.

### Couleurs des poules

Chaque poule se voit attribuer une couleur distincte pour faciliter l'identification visuelle.
Les noms des poules sont des **lettres** (A, B, C…) ; les couleurs n'ont qu'un rôle visuel.

| Poule | Lettre | Couleur       | Code hex   |
|-------|--------|---------------|------------|
| 1     | A      | Rouge         | `#E53935`  |
| 2     | B      | Bleu          | `#1E88E5`  |
| 3     | C      | Vert          | `#43A047`  |
| 4     | D      | Orange        | `#FB8C00`  |
| 5     | E      | Violet        | `#8E24AA`  |
| 6     | F      | Cyan          | `#00ACC1`  |
| 7     | G      | Rose          | `#D81B60`  |
| 8     | H      | Brun          | `#6D4C41`  |
| …     | …      | …             | …          |
| 16    | P      | Indigo        | `#4527A0`  |

---

## Structure des fichiers source

Tous les scripts Python du projet sont placés dans le dossier **`python/`**, sans exception.
Le dossier `scripts/` n'est pas utilisé pour du code Python.

## Structure des fichiers produits

- Dossier de sortie unique : `documents/`
- Pas de sous-dossiers — tous les fichiers sont directement dans `documents/`
- Le nommage encode le contexte ; trié par nom, les fichiers se groupent logiquement
- La création des documents est pilotée par le `Makefile` à la racine du projet

---

## Documents produits

| Fichier | Description | Cible Makefile |
|---|---|---|
| `feuille_inscription.pdf` | Feuille d'inscription des équipes | `feuille-inscription` |
| `pboule.pdf` | Transcription PDF de ce fichier | `pboule-pdf` |
| `poule_A_04eq.pdf` … `poule_H_04eq.pdf` | Gabarits poules A–H, `POOL_BASE` équipes | `feuilles-poules` |
| `poule_A_05eq.pdf` … `poule_H_05eq.pdf` | Gabarits poules A–H, `POOL_BASE+1` équipes | `feuilles-poules` |
| `poule_unique_{N:02d}eq.pdf` | Poule UNIQUE pour chaque N non décomposable (ex. 6, 7, 11 avec `POOL_BASE=4`) | `feuilles-poules` |

**Convention de nommage des feuilles de poule :**
- Standard : `poule_{lettre}_{taille:02d}eq.pdf`
- Unique : `poule_unique_{N:02d}eq.pdf`

---

## Cibles Makefile

| Cible | Description | Dépendances |
|---|---|---|
| `help` | Affiche la liste des cibles disponibles et les paramètres actifs | — |
| `all` | Génère tous les documents | `pboule-pdf`, `feuilles-poules`, `feuille-inscription` |
| `logo` | Calcule les caractéristiques des logos → `logo.yaml` | fichiers logos (si présents) |
| `feuilles-poules` | Génère tous les gabarits de feuilles de poule dans `documents/` | `logo` |
| `feuille-inscription` | Génère la feuille d'inscription dans `documents/` | `logo` |
| `pboule-pdf` | Convertit `PBOULE.md` en `documents/pboule.pdf` via pandoc + tectonic | `logo` |
| `init` | Crée le dossier `documents/` s'il n'existe pas | — |
| `clean` | Supprime `documents/` et les caches Python (`__pycache__`, `*.pyc`) | — |
| `clean-all` | `clean` + suppression de l'environnement conda `pboule` | `clean` |
| `env` | Crée ou met à jour l'environnement conda depuis `environment.yml` | `environment.yml` |
| `check` | Vérifie que l'environnement conda `pboule` est disponible | — |
| `lint` | Analyse le code Python avec ruff (lint + formatage) | — |
| `install-hooks` | Installe les hooks pre-commit dans le dépôt git local | — |
| `pages` | Génère le site statique dans `pages/` (HTML + PDF) | `feuilles-poules`, `feuille-inscription` |

**Ordre de première utilisation** (dépôt cloné, sans `logo.yaml`) :

```
make env            # créer l'environnement conda
make install-hooks  # installer les hooks pre-commit (optionnel)
make logo           # générer logo.yaml
make all            # générer tous les documents
```

`make all` déclenche automatiquement `make logo` si `logo.yaml` est absent.

---

## Pipeline CI / CD

Le fichier `.github/workflows/ci.yml` définit quatre jobs :

| Job | Déclencheur | Dépendances | Description |
|---|---|---|---|
| `lint` | push, PR | — | Analyse ruff via pre-commit (lint + formatage) |
| `generate` | push, PR | `lint` | Génère tous les PDF (hors `pboule-pdf`) et les archive |
| `release` | tag `vX.Y.Z` | `generate` | Crée une GitHub Release avec les PDF et une archive ZIP |
| `pages` | tag `vX.Y.Z` | `generate` | Génère et publie le site de documentation sur GitHub Pages |

### Workflow de release

Avant tout tag/release, mettre à jour `CHANGELOG.md` avec une section `## [X.Y.Z] – YYYY-MM-DD`.
Le job `release` extrait automatiquement les notes depuis ce fichier via `python/extract_changelog.py`.

```
# 1. Mettre à jour CHANGELOG.md
# 2. Commiter et pousser sur main
git tag v1.0.0
git push origin v1.0.0
```

Le pipeline CI publie alors :
- **GitHub Release** — archive ZIP + PDF individuels (feuilles de poule, feuille d'inscription)
- **GitHub Pages** — site de documentation statique (`index.html`) contenant les spécifications, les liens vers tous les PDF et le changelog

### Structure du site GitHub Pages (`pages/`)

| Fichier | Description |
|---|---|
| `index.html` | Site complet (spécifications + documents + changelog) |
| `style.css` | Feuille de style |
| `feuille_inscription.pdf` | Copie des PDF (téléchargement direct) |
| `poule_*.pdf` | Copie des PDF (téléchargement direct) |

Le dossier `pages/` n'est pas versionné (dans `.gitignore`) et est supprimé par `make clean`.

---

## Format de la feuille d'inscription

- Format **A4 portrait**
- Logo en haut à droite (première page uniquement)
- Titre : **FEUILLE D'INSCRIPTION**
- Numérotation des pages si le document s'étend sur 2 pages (ex. 32 équipes)
- Pas de traits de coupe (pages imprimées séparément)

### Colonnes du tableau

| Colonne | Contenu |
|---|---|
| **N°** | Numéro d'équipe, pré-rempli de 1 à `TEAMS_MAX` |
| **Nom d'équipe** | Nom de l'équipe (zone de saisie) |
| **Noms des membres** | Noms et prénoms des membres (1 à 3 par équipe) |
| **Paiement** | Case à cocher par membre (état du paiement de l'inscription) |

Chaque équipe occupe 3 sous-lignes (une par membre potentiel).
Le numéro et le nom d'équipe sont fusionnés sur les 3 sous-lignes.

---

## Format de la feuille de poule

- Format **A4 paysage**, une feuille par poule
- Logo en haut à droite
- Couleur de la poule pour les en-têtes
- Titre : **Poule « A » — 4 équipes**

### Tableau 1 — NOMS – PRÉNOMS

| Colonne | Contenu |
|---|---|
| **Équipe** | Numéro dans la poule (Équipe 1, 2…) |
| **N° inscription** | Numéro de la feuille d'inscription |
| **Noms – Prénoms** | Noms des membres ou nom d'équipe |

### Tableau 2 — Résultats des matches

C(N, 2) lignes de matches pour N équipes dans la poule.

| Colonne | Contenu |
|---|---|
| **Matchs** | Identifiant du match (ex. « 1 – 3 ») |
| **Résultats** | Score (points), rempli par l'arbitre |
| **Éq. 1 … Éq. N** | **Case libre** si l'équipe joue ce match (0 ou 1), **case noire** sinon |
| *(ligne TOTAL)* | TOTAL sur 2 colonnes ; cases = nombre de matches gagnés |

### Tableau 3 — Classement

| Colonne | Contenu |
|---|---|
| **Classement** | Rang ordinal (1er, 2e…) |
| **Équipe** | Équipe classée (remplie après les matches) |

---

## Règles de répartition en poules

### Algorithme

- Taille de base : `POOL_BASE` équipes (défaut 4)
- Priorités pour la répartition :
  1. Distribution uniforme en poules de `POOL_BASE+1` si N est divisible par `POOL_BASE+1`
  2. Distribution uniforme en poules de `POOL_BASE` si N est divisible par `POOL_BASE`
  3. Distribution mixte : `x` poules de `POOL_BASE+1` + `y` poules de `POOL_BASE` telles que la somme vaut N, avec `x+y` minimal

| N  | Répartition       | Poules |
|----|-------------------|--------|
| 8  | 2 × 4             | A–B    |
| 9  | 1 × 5 + 1 × 4    | A–B    |
| 12 | 3 × 4             | A–C    |
| 16 | 4 × 4             | A–D    |
| 20 | 4 × 5             | A–D    |
| 24 | 6 × 4             | A–F    |
| 25 | 5 × 5             | A–E    |
| 28 | 7 × 4             | A–G    |
| 32 | 8 × 4             | A–H    |

> **Cas particuliers (N = 6, 7, 11 avec POOL_BASE = 4) :** non décomposables
> en poules de 4 ou 5. Une feuille **Poule UNIQUE de N équipes** est générée.

*(Nombre de qualifiés par poule : à compléter)*

---

## Règles de la phase finale

*(à compléter — format du tableau, gestion des têtes de série, match pour la 3e place, etc.)*

---

## Format des feuilles

- Chaque feuille est au format **A4** (portrait ou paysage selon le document).
- Le **logo** figure en haut à droite, sur la première feuille uniquement.

### Documents multi-feuilles (règle générale)

Quand un document est composé de plusieurs feuilles A4 destinées à être assemblées :

- Un **seul fichier PDF** est produit.
- Ce PDF contient, dans l'ordre :
  1. Toutes les feuilles entourées de **traits de coupe** (repères de découpe).
  2. Un **schéma de montage** (dernière page).

### Documents multi-pages imprimés séparément (exception)

Certains documents s'étendent sur plusieurs pages **imprimées séparément** (sans assemblage) :
- Pas de traits de coupe.
- **Numérotation des pages** (ex. « Page 1 / 2 »).

*Exemple : feuille d'inscription pour 32 équipes → 2 pages.*
