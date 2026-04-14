#!/usr/bin/env python3
"""Extrait les notes de release pour une version donnée depuis CHANGELOG.md.

Usage
-----
    python scripts/extract_changelog.py v1.0.0
    python scripts/extract_changelog.py 1.0.0   # le 'v' initial est facultatif
    python scripts/extract_changelog.py v1.0.0 > RELEASE_NOTES.md

Codes de sortie
---------------
0  – succès
1  – version introuvable dans CHANGELOG.md ou usage incorrect
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def extract_notes(version: str) -> str:
    """Retourne le corps du changelog pour *version* (le 'v' initial est retiré)."""
    version = version.lstrip("v")

    changelog = Path(__file__).parent.parent / "CHANGELOG.md"
    if not changelog.exists():
        print(f"erreur : CHANGELOG.md introuvable à {changelog}", file=sys.stderr)
        sys.exit(1)

    text = changelog.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Localiser la ligne d'en-tête : ## [X.Y.Z] …
    header_re = re.compile(rf"^##\s+\[{re.escape(version)}\]")
    start: int | None = None
    for i, line in enumerate(lines):
        if header_re.match(line):
            start = i + 1
            break

    if start is None:
        print(
            f"erreur : version '{version}' introuvable dans CHANGELOG.md",
            file=sys.stderr,
        )
        sys.exit(1)

    # Collecter les lignes jusqu'à la prochaine section ## (ou fin de fichier).
    end = len(lines)
    for i in range(start, len(lines)):
        if re.match(r"^##\s+\[", lines[i]):
            end = i
            break

    return "\n".join(lines[start:end]).strip()


def main() -> None:
    if len(sys.argv) < 2:
        print(f"usage : {sys.argv[0]} <version>", file=sys.stderr)
        sys.exit(1)

    print(extract_notes(sys.argv[1]))


if __name__ == "__main__":
    main()
