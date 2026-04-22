# Makefile — PBoule
# Pilote la génération de tous les documents de la compétition.

# =============================================================================
# Paramètres de la compétition
# Priorité décroissante : ligne de commande > variable d'environnement > valeur ci-dessous
#   Ligne de commande    : make all TEAMS_MAX=24
#   Variable d'env.      : export TEAMS_MAX=24 && make all
# =============================================================================

TEAMS_MIN     ?= 6    # Nombre minimal d'équipes pouvant participer à la compétition
TEAMS_MAX     ?= 32   # Nombre maximal d'équipes pouvant participer à la compétition

POOL_BASE     ?= 4    # Taille de base des poules (nombre d'équipes par poule)
                      # • Les poules font POOL_BASE ou POOL_BASE+1 équipes.
                      # • Quand le nombre total d'équipes n'est pas un multiple de
                      #   POOL_BASE, certaines poules reçoivent une équipe de plus.
                      # • Les configurations non décomposables (ex. 6 ou 7 équipes
                      #   avec POOL_BASE=4) génèrent une feuille "Poule UNIQUE".

LOGO_MAIN     ?= logo_COF_montlaur_rose.png  # Logo principal (COF Montlaur)
LOGO_PETANQUE ?= logo_petanque.png           # Logo pétanque (boules)
LOGO_H        ?= 3.5                         # Hauteur des logos en cm
LOGO_YAML     ?= logo.yaml                   # Cache des caractéristiques des logos

# =============================================================================
# Configuration technique  (ne pas modifier sauf raison spécifique)
# =============================================================================

PYTHON        := conda run -n pboule python
PANDOC        := conda run -n pboule pandoc
PANDOC_FLAGS  := --pdf-engine=tectonic -V lang=fr -V papersize=a4 \
                 -V geometry:margin=1cm
DOCS_DIR      := documents
PAGES_DIR     := pages
ENV_NAME      := pboule
PYTHON_DIR    := python

PBOULE_PDF    := $(DOCS_DIR)/pboule.pdf
GUIDE_PDF     := $(DOCS_DIR)/guide_organisateur.pdf

.DEFAULT_GOAL := help

# ---------------------------------------------------------------------------
# Aide
# ---------------------------------------------------------------------------

.PHONY: help
help: ## Affiche cette aide
	@awk 'BEGIN { FS = ":.*##" } \
	    /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } \
	    /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2 }' \
	    $(MAKEFILE_LIST)
	@echo ""
	@echo "  Paramètres actifs :"
	@echo "    TEAMS_MIN=$(strip $(TEAMS_MIN))  TEAMS_MAX=$(strip $(TEAMS_MAX))  POOL_BASE=$(strip $(POOL_BASE))"
	@echo "    LOGO_H=$(strip $(LOGO_H)) cm  LOGO_MAIN=$(strip $(LOGO_MAIN))  LOGO_PETANQUE=$(strip $(LOGO_PETANQUE))"
	@echo "    DOCS_DIR=$(strip $(DOCS_DIR))  PAGES_DIR=$(strip $(PAGES_DIR))"
	@echo ""
	@echo "  Surcharge des paramètres (priorité décroissante) :"
	@echo "    Ligne de commande    : make all TEAMS_MAX=24 POOL_BASE=5"
	@echo "    Variable d'env.      : export TEAMS_MAX=24 && make all"
	@echo ""

# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------

##@ Documents

.PHONY: all
all: pboule-pdf guide-pdf feuilles-poules feuille-inscription feuilles-finales ## Génère tous les documents

.PHONY: pages
pages: guide-pdf feuilles-poules feuille-inscription feuilles-finales ## Génère le site statique dans pages/
	@echo "Génération du site de documentation…"
	@$(PYTHON) $(PYTHON_DIR)/generate_pages.py \
	    --docs-dir         $(DOCS_DIR) \
	    --output-dir       $(PAGES_DIR) \
	    --pboule-md        PBOULE.md \
	    --changelog        CHANGELOG.md \
	    --logo-creation-md creation_logo_petanque.md \
	    --logo-yaml        $(LOGO_YAML)

.PHONY: feuilles-poules
feuilles-poules: $(LOGO_YAML) | init ## Génère tous les gabarits de feuilles de poule
	@echo "Génération des feuilles de poule…"
	@$(PYTHON) $(PYTHON_DIR)/generate_feuille_poule.py \
	    --teams-min     $(TEAMS_MIN) \
	    --teams-max     $(TEAMS_MAX) \
	    --pool-base     $(POOL_BASE) \
	    --output        $(DOCS_DIR) \
	    --logo-yaml     $(LOGO_YAML)

.PHONY: feuille-inscription
feuille-inscription: $(LOGO_YAML) | init ## Génère la feuille d'inscription (A4 portrait)
	@echo "Génération de la feuille d'inscription…"
	@$(PYTHON) $(PYTHON_DIR)/generate_feuille_inscription.py \
	    --n-equipes     $(TEAMS_MAX) \
	    --output        $(DOCS_DIR) \
	    --logo-yaml     $(LOGO_YAML)

.PHONY: feuilles-finales
feuilles-finales: $(LOGO_YAML) | init ## Génère les feuilles de phases finales (une par nombre d'équipes)
	@echo "Génération des feuilles de phases finales…"
	@$(PYTHON) $(PYTHON_DIR)/generate_phases_finales.py \
	    --teams-min     $(TEAMS_MIN) \
	    --teams-max     $(TEAMS_MAX) \
	    --pool-base     $(POOL_BASE) \
	    --output        $(DOCS_DIR) \
	    --logo-yaml     $(LOGO_YAML)

.PHONY: pboule-pdf
pboule-pdf: $(PBOULE_PDF) ## Génère documents/pboule.pdf depuis PBOULE.md

$(PBOULE_PDF): PBOULE.md $(LOGO_YAML) | init
	@echo "Génération de $@…"
	@$(PANDOC) $< -o $@ $(PANDOC_FLAGS)
	@echo "  → $@ généré."

.PHONY: guide-pdf
guide-pdf: $(GUIDE_PDF) ## Génère documents/guide_organisateur.pdf depuis GUIDE_ORGANISATEUR.md

$(GUIDE_PDF): GUIDE_ORGANISATEUR.md $(LOGO_YAML) | init
	@echo "Génération de $@…"
	@$(PANDOC) $< -o $@ $(PANDOC_FLAGS)
	@echo "  → $@ généré."

# ---------------------------------------------------------------------------
# Développement
# ---------------------------------------------------------------------------

##@ Développement

.PHONY: env
env: environment.yml ## Crée ou met à jour l'environnement conda 'pboule'
	@if conda env list | grep -qE "^$(ENV_NAME)\s"; then \
	    echo "Mise à jour de l'environnement conda '$(ENV_NAME)'…"; \
	    conda env update -n $(ENV_NAME) -f environment.yml --prune; \
	else \
	    echo "Création de l'environnement conda '$(ENV_NAME)'…"; \
	    conda env create -f environment.yml; \
	fi
	@echo "Environnement '$(ENV_NAME)' prêt."

.PHONY: check
check: ## Vérifie que l'environnement conda 'pboule' est disponible
	@conda run -n $(ENV_NAME) python --version \
	    && echo "Environnement conda '$(ENV_NAME)' : OK" \
	    || echo "ERREUR : environnement conda '$(ENV_NAME)' introuvable"

.PHONY: lint
lint: ## Analyse le code Python avec ruff (lint + formatage)
	@echo "Analyse ruff — vérification du formatage…"
	@$(PYTHON) -m ruff format --check $(PYTHON_DIR)/
	@echo "Analyse ruff — lint…"
	@$(PYTHON) -m ruff check $(PYTHON_DIR)/
	@echo "Analyse ruff : OK"

.PHONY: bump-major bump-minor bump-patch

bump-major: ## Incrémente la version majeure : X.Y.Z → (X+1).0.0
	@$(PYTHON) $(PYTHON_DIR)/bump_version.py major

bump-minor: ## Incrémente la version mineure : X.Y.Z → X.(Y+1).0
	@$(PYTHON) $(PYTHON_DIR)/bump_version.py minor

bump-patch: ## Incrémente la version patch  : X.Y.Z → X.Y.(Z+1)
	@$(PYTHON) $(PYTHON_DIR)/bump_version.py patch

.PHONY: install-hooks
install-hooks: ## Installe les hooks pre-commit dans le dépôt git local
	@conda run -n $(ENV_NAME) pre-commit install
	@echo "Hooks pre-commit installés."

.PHONY: logo
logo: $(LOGO_YAML) ## Calcule les caractéristiques des logos → logo.yaml

$(LOGO_YAML): $(wildcard $(LOGO_MAIN) $(LOGO_PETANQUE))
	@echo "Calcul des caractéristiques des logos…"
	@$(PYTHON) $(PYTHON_DIR)/compute_logo_yaml.py \
	    --logo-main     $(LOGO_MAIN) \
	    --logo-petanque $(LOGO_PETANQUE) \
	    --logo-height   $(LOGO_H) \
	    --output        $(LOGO_YAML)

.PHONY: init
init: ## Crée le dossier de sortie
	@mkdir -p $(DOCS_DIR)
	@echo "Dossier $(DOCS_DIR)/ prêt."

.PHONY: clean
clean: ## Supprime les documents générés, les pages et les fichiers temporaires Python
	@rm -rf $(DOCS_DIR) $(PAGES_DIR)
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -name '*.pyc' -o -name '*.pyo' | xargs rm -f 2>/dev/null || true
	@echo "Nettoyage terminé."

.PHONY: clean-all
clean-all: clean ## Supprime les documents générés ET l'environnement conda 'pboule'
	@if conda env list | grep -qE "^$(ENV_NAME)\s"; then \
	    echo "Suppression de l'environnement conda '$(ENV_NAME)'…"; \
	    conda env remove -n $(ENV_NAME) -y; \
	    echo "Environnement '$(ENV_NAME)' supprimé."; \
	else \
	    echo "Environnement conda '$(ENV_NAME)' inexistant, rien à supprimer."; \
	fi
