# Instructions générales

Après chaque modification du projet, maintenir à jour les trois fichiers de référence :

| Fichier | Rôle |
|---|---|
| **PBOULE.md** | Spécifications du domaine (règles, formats, algorithmes) |
| **Makefile** | Cibles de génération et paramètres |
| **CLAUDE.md** | Instructions de travail pour Claude |

# Langue
* La langue par défaut pour toutes les interactions est le **français**.
* Toutes les réponses, explications, messages d'erreur et commentaires doivent être en français.
* Les messages de commit git doivent être rédigés en français.
* Les commentaires dans le code doivent être en français.
* Les noms de variables, fonctions et fichiers restent en anglais (convention technique).

# Spécifications
* Les spécifications du projet sont enregistrées dans le fichier **PBOULE.md** et doivent être lues depuis ce fichier au début de chaque tâche nécessitant une compréhension du domaine.

# Workflow Git

**Avant tout commit :**
```
pre-commit run --all-files
```
Vérifier que tous les hooks passent (code 0, aucun fichier modifié). Ne jamais publier
si cette commande échoue ou modifie des fichiers.

**Avant tout push — squash obligatoire :**
```
git log --oneline origin/main..HEAD   # compter N commits
git reset --soft HEAD~N
git commit -m "..."
```
Un push = un commit. Le message de commit résume **tous** les changements inclus.

**Messages de commit et noms de tags** : toujours en français.

**Avant tout tag/release :**
Mettre à jour `CHANGELOG.md` avec une section `## [X.Y.Z] – YYYY-MM-DD` (Added /
Changed / Fixed). Le pipeline CI extrait les notes de release depuis ce fichier.

# Environnement

## Général
* L'environnement conda par défaut est **pboule**. Toutes les commandes Python doivent être exécutées dans cet environnement.
* Les scripts Python de génération sont dans le sous-répertoire **python/**.

## Installation (environnement conda)

```
make env
```
