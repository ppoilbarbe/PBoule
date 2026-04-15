#!/usr/bin/env python3
"""
Incrémente le numéro de version dans pyproject.toml et ajoute
un placeholder dans CHANGELOG.md.

Usage :
    python python/bump_version.py {major|minor|patch}

Comportement :
    - Lit la version courante dans pyproject.toml.
    - Calcule la nouvelle version (remise à zéro des composantes inférieures).
    - Met à jour la ligne ``version = "..."`` dans pyproject.toml.
    - Insère une section ``## [X.Y.Z] – YYYY-MM-DD`` en tête de CHANGELOG.md.
    - Affiche l'ancienne et la nouvelle version.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

# Chemins relatifs à la racine du projet (là où le Makefile est invoqué)
_PYPROJECT = Path("pyproject.toml")
_CHANGELOG = Path("CHANGELOG.md")


def _bump(version: str, part: str) -> str:
    """Retourne la version incrémentée selon la partie demandée."""
    major, minor, patch = (int(x) for x in version.split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"  # patch


def _read_version(pyproject: Path) -> str:
    content = pyproject.read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not m:
        sys.exit(f"Erreur : champ version introuvable dans {pyproject}")
    return m.group(1)


def _update_pyproject(pyproject: Path, old: str, new: str) -> None:
    content = pyproject.read_text(encoding="utf-8")
    new_content, n = re.subn(
        r'^(version\s*=\s*)"[^"]+"',
        rf'\1"{new}"',
        content,
        count=1,
        flags=re.MULTILINE,
    )
    if n == 0:
        sys.exit(f"Erreur : remplacement de version échoué dans {pyproject}")
    pyproject.write_text(new_content, encoding="utf-8")


def _prepend_changelog(changelog: Path, new_version: str) -> None:
    """Insère une section placeholder avant la première section ## [...]."""
    content = changelog.read_text(encoding="utf-8")
    today = date.today().isoformat()
    placeholder = f"## [{new_version}] – {today}\n\n*(à compléter)*\n\n"
    new_content, n = re.subn(
        r"(## \[)",
        placeholder + r"\1",
        content,
        count=1,
    )
    if n == 0:
        # Aucune section existante : ajouter en fin de fichier
        new_content = content.rstrip("\n") + "\n\n" + placeholder
    changelog.write_text(new_content, encoding="utf-8")


def main() -> None:
    part = sys.argv[1] if len(sys.argv) > 1 else ""
    if part not in ("major", "minor", "patch"):
        sys.exit(f"Usage : {sys.argv[0]} {{major|minor|patch}}")

    old_version = _read_version(_PYPROJECT)
    new_version = _bump(old_version, part)

    _update_pyproject(_PYPROJECT, old_version, new_version)
    _prepend_changelog(_CHANGELOG, new_version)

    print(f"{old_version} → {new_version}")


if __name__ == "__main__":
    main()
