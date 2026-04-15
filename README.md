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
| `feuille_inscription.pdf` | Tableau d'inscription des équipes (jusqu'à 32 équipes, A4 portrait) |
| `poule_A_04eq.pdf` … `poule_H_05eq.pdf` | Feuilles de poule A4 paysage (4 ou 5 équipes par poule) |
| `poule_unique_NNéq.pdf` | Feuille pour une poule unique (cas non décomposables : 6, 7, 11 équipes…) |

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

**De façon permanente** — éditer les variables en tête du `Makefile` :

| Variable | Défaut | Rôle |
|---|---|---|
| `TEAMS_MIN` | `6` | Nombre minimal d'équipes |
| `TEAMS_MAX` | `32` | Nombre maximal d'équipes |
| `POOL_BASE` | `4` | Taille de base des poules |
| `LOGO_H` | `3.5` | Hauteur des logos en cm |

**À la volée** — passer les variables directement sur la ligne de commande,
sans toucher au `Makefile` :

```bash
make all TEAMS_MAX=24 POOL_BASE=4
```

Cette syntaxe est pratique pour un usage ponctuel. Attention : les valeurs
passées en ligne de commande ne sont pas mémorisées. Il faut les répéter à
chaque invocation de `make` pour conserver une cohérence entre les documents
générés.

### Cibles Makefile disponibles

```
make help           # liste toutes les cibles et les paramètres actifs
make all            # génère tous les documents
make feuilles-poules      # feuilles de poule uniquement
make feuille-inscription  # feuille d'inscription uniquement
make logo           # recalcule logo.yaml (après changement de logo)
make pages          # génère le site de documentation dans pages/
make lint           # vérifie le code Python (ruff)
make clean          # supprime les documents générés
make clean-all      # clean + supprime l'environnement conda
```

---

## Structure du projet

```
PBoule/
├── python/                        # Scripts Python de génération
│   ├── generate_feuille_poule.py  # Feuilles de poule
│   ├── generate_feuille_inscription.py  # Feuille d'inscription
│   ├── generate_pages.py          # Site de documentation GitHub Pages
│   ├── compute_logo_yaml.py       # Cache des caractéristiques des logos
│   ├── extract_changelog.py       # Extraction des notes de release
│   └── logos.py                   # Rendu des logos sur les PDF
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
