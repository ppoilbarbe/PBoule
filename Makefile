# Makefile — PBoule
# Pilote la génération de tous les documents de la compétition.

# =============================================================================
# Paramètres de la compétition  ← seule section à modifier
# =============================================================================

TEAMS_MIN     := 6    # Nombre minimal d'équipes pouvant participer à la compétition
TEAMS_MAX     := 32   # Nombre maximal d'équipes pouvant participer à la compétition

POOL_BASE     := 4    # Taille de base des poules (nombre d'équipes par poule)
                      # • Les poules font POOL_BASE ou POOL_BASE+1 équipes.
                      # • Quand le nombre total d'équipes n'est pas un multiple de
                      #   POOL_BASE, certaines poules reçoivent une équipe de plus.
                      # • Les configurations non décomposables (ex. 6 ou 7 équipes
                      #   avec POOL_BASE=4) génèrent une feuille "Poule UNIQUE".

LOGO_MAIN     := logo_COF_montlaur_rose.png  # Logo principal (COF Montlaur)
LOGO_PETANQUE := logo_petanque.png           # Logo pétanque (boules)
LOGO_H        := 3.5                         # Hauteur des logos en cm
LOGO_YAML     := logo.yaml                   # Cache des caractéristiques des logos

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

.DEFAULT_GOAL := help

# ---------------------------------------------------------------------------
# Aide
# ---------------------------------------------------------------------------

.PHONY: help
help: ## Affiche cette aide
	@echo ""
	@echo "  PBoule — Makefile"
	@echo "  =================="
	@echo ""
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) \
	    | awk -F ':.*##' '{ printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 }' \
	    | sort
	@echo ""
	@echo "  Paramètres actifs :"
	@echo "    TEAMS_MIN=$(strip $(TEAMS_MIN))  TEAMS_MAX=$(strip $(TEAMS_MAX))  POOL_BASE=$(strip $(POOL_BASE))"
	@echo "    LOGO_H=$(strip $(LOGO_H)) cm  LOGO_MAIN=$(strip $(LOGO_MAIN))  LOGO_PETANQUE=$(strip $(LOGO_PETANQUE))"
	@echo "    DOCS_DIR=$(strip $(DOCS_DIR))  PAGES_DIR=$(strip $(PAGES_DIR))"
	@echo ""

# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

.PHONY: init
init: ## Crée le dossier de sortie
	@mkdir -p $(DOCS_DIR)
	@echo "Dossier $(DOCS_DIR)/ prêt."

# ---------------------------------------------------------------------------
# Logos — cache des caractéristiques (ratio d'aspect, chemin, hauteur)
# ---------------------------------------------------------------------------

$(LOGO_YAML): $(wildcard $(LOGO_MAIN) $(LOGO_PETANQUE))
	@echo "Calcul des caractéristiques des logos…"
	@$(PYTHON) $(PYTHON_DIR)/compute_logo_yaml.py \
	    --logo-main     $(LOGO_MAIN) \
	    --logo-petanque $(LOGO_PETANQUE) \
	    --logo-height   $(LOGO_H) \
	    --output        $(LOGO_YAML)

.PHONY: logo
logo: $(LOGO_YAML) ## Calcule les caractéristiques des logos → logo.yaml

# ---------------------------------------------------------------------------
# Génération des documents
# ---------------------------------------------------------------------------

.PHONY: all
all: pboule-pdf feuilles-poules feuille-inscription ## Génère tous les documents

# documents/pboule.pdf — transcription PDF de PBOULE.md
$(PBOULE_PDF): PBOULE.md $(LOGO_YAML) | init
	@echo "Génération de $@…"
	@$(PANDOC) $< -o $@ $(PANDOC_FLAGS)
	@echo "  → $@ généré."

.PHONY: pboule-pdf
pboule-pdf: $(PBOULE_PDF) ## Génère documents/pboule.pdf depuis PBOULE.md

# ---------------------------------------------------------------------------
# Feuilles de poule
# ---------------------------------------------------------------------------

.PHONY: feuilles-poules
feuilles-poules: $(LOGO_YAML) | init ## Génère tous les gabarits de feuilles de poule
	@echo "Génération des feuilles de poule…"
	@$(PYTHON) $(PYTHON_DIR)/generate_feuille_poule.py \
	    --teams-min     $(TEAMS_MIN) \
	    --teams-max     $(TEAMS_MAX) \
	    --pool-base     $(POOL_BASE) \
	    --output        $(DOCS_DIR) \
	    --logo-yaml     $(LOGO_YAML)

# ---------------------------------------------------------------------------
# Feuille d'inscription
# ---------------------------------------------------------------------------

.PHONY: feuille-inscription
feuille-inscription: $(LOGO_YAML) | init ## Génère la feuille d'inscription (A4 portrait)
	@echo "Génération de la feuille d'inscription…"
	@$(PYTHON) $(PYTHON_DIR)/generate_feuille_inscription.py \
	    --n-equipes     $(TEAMS_MAX) \
	    --output        $(DOCS_DIR) \
	    --logo-yaml     $(LOGO_YAML)

# ---------------------------------------------------------------------------
# Nettoyage
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Environnement conda
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Vérification / qualité
# ---------------------------------------------------------------------------

.PHONY: check
check: ## Vérifie que l'environnement conda 'pboule' est disponible
	@conda run -n $(ENV_NAME) python --version \
	    && echo "Environnement conda '$(ENV_NAME)' : OK" \
	    || echo "ERREUR : environnement conda '$(ENV_NAME)' introuvable"

# ---------------------------------------------------------------------------
# Qualité du code source
# ---------------------------------------------------------------------------

.PHONY: lint
lint: ## Analyse le code Python avec ruff (lint + formatage)
	@echo "Analyse ruff — vérification du formatage…"
	@$(PYTHON) -m ruff format --check $(PYTHON_DIR)/
	@echo "Analyse ruff — lint…"
	@$(PYTHON) -m ruff check $(PYTHON_DIR)/
	@echo "Analyse ruff : OK"

# ---------------------------------------------------------------------------
# Gestion des versions
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Site de documentation statique
# ---------------------------------------------------------------------------

.PHONY: pages
pages: feuilles-poules feuille-inscription ## Génère le site statique dans pages/
	@echo "Génération du site de documentation…"
	@$(PYTHON) $(PYTHON_DIR)/generate_pages.py \
	    --docs-dir         $(DOCS_DIR) \
	    --output-dir       $(PAGES_DIR) \
	    --pboule-md        PBOULE.md \
	    --changelog        CHANGELOG.md \
	    --logo-creation-md creation_logo_petanque.md \
	    --logo-yaml        $(LOGO_YAML)
