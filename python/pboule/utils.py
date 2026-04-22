"""Utilitaires communs : chargement de logo.yaml."""

from __future__ import annotations

from pathlib import Path


def charger_logo_yaml(chemin: Path) -> dict | None:
    """Charge logo.yaml (format JSON, compatible YAML si pyyaml est installé)."""
    try:
        import yaml

        with open(chemin, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        import json

        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
