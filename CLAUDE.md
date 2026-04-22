# Directives

## Fichiers de référence — mettre à jour après chaque modification

| Fichier | Rôle |
|---|---|
| **PBOULE.md** | Spécifications du domaine (règles, formats, algorithmes) — pas de contenu opérationnel |
| **README.md** | Documentation utilisateur (cibles Makefile, structure, CI/CD) — pas de spécifications |
| **Makefile** | Cibles de génération et paramètres |
| **CLAUDE.md** | Instructions de travail pour Claude |

## Langue

- Interactions, réponses, commentaires code : **français**
- Identifiants (variables, fonctions, fichiers) : **anglais**
- Commits git et noms de tags : **français**
- Spécifications domaine : lire **PBOULE.md** en début de tâche

## Workflow Git

**Avant tout commit :** `pre-commit run --all-files` — code 0, aucun fichier modifié.

**Avant tout push — squash obligatoire :**
```
git log --oneline origin/main..HEAD   # compter N commits
git reset --soft HEAD~N
git commit -m "..."
```
Un push = un commit résumant tous les changements inclus.

**Avant tout tag/release :** mettre à jour `CHANGELOG.md` avec `## [X.Y.Z] – YYYY-MM-DD` (Added / Changed / Fixed). Le pipeline CI extrait les notes depuis ce fichier.

## Environnement

- Conda : env **pboule** — canal exclusivement **conda-forge** (`nodefaults` dans `environment.yml` ; `conda-remove-defaults: "true"` dans chaque step `setup-miniconda` du CI)
- Scripts Python : sous-répertoire **python/**
- Installation : `make env`
