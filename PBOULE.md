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

## Documents produits

| Fichier | Description |
|---|---|
| `guide_organisateur.pdf` | Guide de l'organisateur — procédure étape par étape |
| `feuille_inscription.pdf` | Feuille d'inscription des équipes |
| `pboule.pdf` | Transcription PDF de ce fichier |
| `poule_A.pdf` … `poule_H.pdf` | Gabarits poules A–H — 2 pages : `POOL_BASE` équipes + `POOL_BASE+1` équipes |
| `poule_unique_{N:02d}eq.pdf` | Poule UNIQUE pour chaque N non décomposable (ex. 6, 7 avec `POOL_BASE=4`) |
| `poule_{lettre}_{N:02d}eq.pdf` | Feuille spéciale : répartition + feuille de la dernière poule (ex. `poule_C_11eq.pdf` pour N=11, base=4 → A=4, B=4, C=3) |

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
| **Points** | Points réalisés dans le match : 13 pour le gagnant, score réel pour le perdant |

---

## Règles de répartition en poules

### Algorithme

- Taille de base : `POOL_BASE` équipes (défaut 4)
- Priorités pour la répartition (ordre strict — la première règle applicable s'applique) :
  1. Distribution uniforme en poules de `POOL_BASE` si N est divisible par `POOL_BASE`,
     **y compris si N est aussi divisible par `POOL_BASE+1`**
     (ex. POOL_BASE=4, N=20 → 5 poules de 4, **pas** 4 poules de 5)
  2. Distribution uniforme en poules de `POOL_BASE+1` si N est divisible par `POOL_BASE+1`
  3. Distribution mixte : nombre de poules minimal, poules de `POOL_BASE` en tête,
     poules de `POOL_BASE+1` en fin

| N  | Répartition                    | Ordre des poules               | Poules |
|----|--------------------------------|--------------------------------|--------|
| 8  | 2 × 4                          | A=4, B=4                       | A–B    |
| 9  | 1 × 4 + 1 × 5                  | A=4, B=5                       | A–B    |
| 10 | 2 × 5                          | A=5, B=5                       | A–B    |
| 12 | 3 × 4                          | A=4, B=4, C=4                  | A–C    |
| 13 | 2 × 4 + 1 × 5                  | A=4, B=4, C=5                  | A–C    |
| 14 | 1 × 4 + 2 × 5                  | A=4, B=5, C=5                  | A–C    |
| 15 | 3 × 5                          | A=5, B=5, C=5                  | A–C    |
| 16 | 4 × 4                          | A=4, B=4, C=4, D=4             | A–D    |
| 17 | 3 × 4 + 1 × 5                  | A=4, B=4, C=4, D=5             | A–D    |
| 18 | 2 × 4 + 2 × 5                  | A=4, B=4, C=5, D=5             | A–D    |
| 19 | 1 × 4 + 3 × 5                  | A=4, B=5, C=5, D=5             | A–D    |
| 20 | 5 × 4                          | A=4, B=4, C=4, D=4, E=4        | A–E    |
| 21 | 4 × 4 + 1 × 5                  | A=4, B=4, C=4, D=4, E=5        | A–E    |
| 22 | 3 × 4 + 2 × 5                  | A=4, B=4, C=4, D=5, E=5        | A–E    |
| 23 | 2 × 4 + 3 × 5                  | A=4, B=4, C=5, D=5, E=5        | A–E    |
| 24 | 6 × 4                          | A=4, …, F=4                    | A–F    |
| 25 | 5 × 5                          | A=5, …, E=5                    | A–E    |
| 26 | 4 × 4 + 2 × 5                  | A=4, B=4, C=4, D=4, E=5, F=5  | A–F    |
| 27 | 3 × 4 + 3 × 5                  | A=4, B=4, C=4, D=5, E=5, F=5  | A–F    |
| 28 | 7 × 4                          | A=4, …, G=4                    | A–G    |
| 29 | 1 × 4 + 5 × 5                  | A=4, B=5, C=5, D=5, E=5, F=5  | A–F    |
| 30 | 6 × 5                          | A=5, …, F=5                    | A–F    |
| 31 | 4 × 4 + 3 × 5                  | A=4, B=4, C=4, D=4, E=5, F=5, G=5 | A–G |
| 32 | 8 × 4                          | A=4, …, H=4                    | A–H    |

> **Cas particuliers avec POOL_BASE = 4 :**
> - **N = 6, 7 :** non décomposables en poules de 4 ou 5. Une feuille **Poule UNIQUE de N équipes** est générée.
> - **N = 11 :** réparti en 3 poules (A=4, B=4, C=3). Une feuille spéciale `poule_C_11eq.pdf` est générée, contenant la répartition des 3 poules et la feuille de poule C (3 équipes).

**Qualifiés par poule : 2** (1er et 2e). Pour P poules → **2P qualifiés** en phase finale.

---

## Règles de la phase finale

### Équipes qualifiées

Pour chaque poule, les **2 premiers** (1er et 2e) se qualifient pour la phase finale.
Pour P poules, cela donne **2P qualifiés**.

### Structure du tableau

Tableau à **élimination directe** pour 2P équipes qualifiées. Soit q la puissance de 2
immédiatement inférieure ou égale à 2P, et r = 2P − q :

- Si r = 0 (2P est une puissance de 2) : toutes les équipes entrent directement en round 1.
- Si r > 0 : **r matches préliminaires** (colonne « Prél. ») disputés avant le round 1 ;
  les q − r équipes restantes entrent directement en round 1.

Il n'y a pas de cases bye : toutes les équipes jouent un match dès le départ.

Noms des tours selon le nombre d'équipes engagées :

| Équipes dans le tour | Nom du tour       |
|----------------------|-------------------|
| 64                   | 32es de finale    |
| 32                   | 16es de finale    |
| 16                   | 8es de finale     |
| 8                    | Quarts de finale  |
| 4                    | Demi-finales      |
| 2                    | Finale            |

### Placement des équipes dans le tableau

Les 2P équipes sont regroupées en P paires (case haute, case basse) :

**Paire i (i = 0 … P−1) :**
- Case haute : **1er de la poule i+1** (A1, B1, C1…)
- Case basse : **2e de la poule ((i + P//2) mod P) + 1**

Selon la valeur de r = 2P − q :
- Paires 0 … r−1 → **matches préliminaires** (colonne « Prél. »)
- Paires r … P−1 → **entrées directes** en round 1 (si r = 0 : toutes les paires)

**Exemple P = 4, r = 0** (N = 16, 17, 18, 19 — toutes entrées directes) :

| Paire | Case haute | Case basse |
|-------|-----------|-----------|
| 0     | A1        | C2        |
| 1     | B1        | D2        |
| 2     | C1        | A2        |
| 3     | D1        | B2        |

→ A1 et A2 sont dans des moitiés de tableau opposées (ne peuvent se rencontrer qu'en finale).

**Exemple P = 5, r = 2** (N = 20, 21, 22, 23, 25 — 2 matches préliminaires) :

| Paire | Case haute | Case basse | Rôle |
|-------|-----------|-----------|------|
| 0     | A1        | C2        | Match préliminaire |
| 1     | B1        | D2        | Match préliminaire |
| 2     | C1        | E2        | Entrée directe round 1 |
| 3     | D1        | A2        | Entrée directe round 1 |
| 4     | E1        | B2        | Entrée directe round 1 |

### Format de la feuille de phases finales

- Format **A4 paysage**. Si la hauteur minimale de case (6 mm) ne peut être respectée,
  le document est produit sur **2 pages A4 paysage** à assembler côte à côte.
- Logo en haut à droite sur la première page.
- Colonnes = tours de gauche à droite, puis colonne « Gagnant ».
- **Chaque case** comporte 3 sous-colonnes :
  - **Résultat de poule** (ex. `A1`, `B2`) : pré-rempli, fond coloré de la couleur de la poule.
  - **Nom** : vide, rempli à la main par les organisateurs.
  - **Score** : vide, rempli à la main.
- Les cases des tours suivants (non pré-remplies) n'ont que 2 sous-colonnes (Nom, Score).
- **Match pour la 3e place** inclus (2 cases vides + case résultat).

### Documents produits

Les valeurs de N qui donnent le même nombre de poules P génèrent un document identique ;
un seul fichier est donc produit par valeur de P.

Quand 2P >= 16 (les 8es de finale sont possibles), **deux fichiers** sont générés à la place d'un :

| Fichier | Contenu |
|---|---|
| `finales_huitieme_{NS}eq.pdf` | 8es de finale : cases pré-remplies (poule + rang) + colonne « Quarts de finale → » vide |
| `finales_quart_{NS}eq.pdf` | Quarts de finale → demi-finales → finale + match pour la 3e place (tout vide) |

Quand 2P < 16, un seul fichier est produit :

| Nommage | Condition | Exemple (TEAMS_MIN=6, TEAMS_MAX=32, POOL_BASE=4) |
|---|---|---|
| `finales_{NN}eq.pdf` | une seule valeur de N pour ce P | `finales_06-10eq.pdf` (N=6–10 → P=2) |
| `finales_{N1}-{N2}eq.pdf` | plage de N consécutifs pour ce P | `finales_16-19eq.pdf` (N=16–19 → P=4) |
| `finales_{N1}_{N2}_...eq.pdf` | valeurs de N non consécutives | `finales_20_21_22_23_25eq.pdf` (N=20–23, 25 → P=5) |

Avec les paramètres par défaut (TEAMS_MIN=6, TEAMS_MAX=32, POOL_BASE=4), seul N=32 (P=8, 2P=16)
déclenche la génération des fichiers `finales_huitieme_32eq.pdf` et `finales_quart_32eq.pdf`.

---

## Format des feuilles

- Chaque feuille est au format **A4** (portrait ou paysage selon le document).
- Le **logo** figure en haut à droite, sur la première page uniquement.
- Les documents multi-pages sont imprimés séparément, sans traits de coupe,
  avec **numérotation des pages** (ex. « Page 1 / 2 »).

*Exemple : feuille d'inscription pour 32 équipes → 2 pages A4 portrait.*
