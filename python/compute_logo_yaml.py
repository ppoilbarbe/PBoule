#!/usr/bin/env python3
"""
Calcule les caractéristiques des logos et les enregistre dans logo.yaml.

Ce script est invoqué par la cible Makefile 'logo'. Il lit les fichiers image
une seule fois et mémorise les ratios d'aspect, ce qui évite de les recalculer
à chaque génération de document.

Usage :
    python python/compute_logo_yaml.py \\
        --logo-main     logo_COF_montlaur_rose.png \\
        --logo-petanque logo_petanque.png \\
        --logo-height   3.5 \\
        --output        logo.yaml
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path


def _png_aspect(path: Path) -> float | None:
    """Retourne le ratio largeur/hauteur d'un fichier PNG (lecture du chunk IHDR)."""
    try:
        data = path.read_bytes()
        w, h = struct.unpack(">II", data[16:24])
        return w / h if h > 0 else None
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Calcule les caractéristiques des logos → logo.yaml.",
    )
    ap.add_argument(
        "--logo-main",
        type=Path,
        default=None,
        metavar="FILE",
        help="Chemin vers le logo principal PNG (optionnel)",
    )
    ap.add_argument(
        "--logo-petanque",
        type=Path,
        required=True,
        metavar="FILE",
        help="Chemin vers le logo pétanque PNG (obligatoire)",
    )
    ap.add_argument(
        "--logo-height",
        type=float,
        default=3.5,
        metavar="CM",
        help="Hauteur des logos en cm (défaut : 3.5)",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("logo.yaml"),
        metavar="FILE",
        help="Fichier de sortie (défaut : logo.yaml)",
    )
    args = ap.parse_args()

    data: dict = {"logo_h_cm": args.logo_height}

    # ── Logo principal (PNG) ─────────────────────────────────────────────────
    if args.logo_main and args.logo_main.exists():
        ratio = _png_aspect(args.logo_main)
        data["logo_main"] = {
            "path": str(args.logo_main),
            "aspect_ratio": round(ratio, 6) if ratio is not None else None,
        }
        status = f"ratio={ratio:.4f}" if ratio else "ratio=indéterminé"
        print(f"  logo_main     : {args.logo_main}  ({status})")
    else:
        data["logo_main"] = None
        if args.logo_main:
            print(f"  logo_main     : {args.logo_main}  (introuvable, ignoré)")

    # ── Logo pétanque (PNG) — obligatoire ────────────────────────────────────
    if not args.logo_petanque.exists():
        sys.exit(f"Erreur : logo pétanque introuvable : {args.logo_petanque}")
    ratio = _png_aspect(args.logo_petanque)
    data["logo_petanque"] = {
        "path": str(args.logo_petanque),
        "aspect_ratio": round(ratio, 6) if ratio is not None else None,
    }
    status = f"ratio={ratio:.4f}" if ratio else "ratio=indéterminé"
    print(f"  logo_petanque : {args.logo_petanque}  ({status})")

    # ── Écriture du fichier YAML (format JSON, compatible YAML) ─────────────
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"  → {args.output.resolve()}")


if __name__ == "__main__":
    main()
