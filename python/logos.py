"""
Module partagé pour le rendu des logos sur les documents PDF.

Expose draw_logos(canvas, page_w, page_h, marge, logo_data)
qui dessine deux logos en haut à droite de la page :
  • logo principal (PNG) calé contre la marge droite
  • logo pétanque (PNG) superposé en bas à gauche du logo principal

logo_data est un dict chargé depuis logo.yaml (produit par compute_logo_yaml.py).
Les ratios d'aspect sont pré-calculés ; seul le rendu image est effectué ici.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

# ── Rendu image ───────────────────────────────────────────────────────────────


def _load_png(path: Path) -> ImageReader | None:
    """Charge un fichier PNG en ImageReader. Retourne None en cas d'erreur."""
    try:
        return ImageReader(BytesIO(path.read_bytes()))
    except Exception:
        return None


# ── Fonction principale ───────────────────────────────────────────────────────


def draw_logos(
    canvas,
    page_w: float,
    page_h: float,
    marge: float,
    logo_data: dict | None,
) -> None:
    """
    Dessine les deux logos en haut à droite de la page.

    Disposition :
      • Logo principal (PNG) calé contre la marge droite, hauteur logo_h.
      • Logo pétanque (PNG) superposé en bas à gauche du logo principal,
        à la même hauteur logo_h.

    Si logo_data est None ou vide, aucun logo n'est dessiné.

    Args:
        canvas    : Canvas ReportLab courant.
        page_w    : Largeur de la page en points.
        page_h    : Hauteur de la page en points.
        marge     : Marge en points.
        logo_data : Dict chargé depuis logo.yaml, ou None.
    """
    if not logo_data:
        return

    logo_h = logo_data.get("logo_h_cm", 3.5) * cm

    # ── Logo principal (PNG) ──────────────────────────────────────────────────
    cof_img = None
    cof_w = 0.0
    cof_x = page_w - marge  # bord droit par défaut (ajusté ci-dessous)
    cof_y = page_h - marge - logo_h

    cof_info = logo_data.get("logo_main")
    if cof_info and cof_info.get("path") and cof_info.get("aspect_ratio"):
        path = Path(cof_info["path"])
        if path.exists():
            try:
                cof_w = logo_h * cof_info["aspect_ratio"]
                cof_img = _load_png(path)
                cof_x = page_w - marge - cof_w
            except Exception:
                pass

    # ── Logo pétanque (PNG) ───────────────────────────────────────────────────
    pet_img = None
    pet_w = 0.0

    pet_info = logo_data.get("logo_petanque")
    if pet_info and pet_info.get("path") and pet_info.get("aspect_ratio"):
        path = Path(pet_info["path"])
        if path.exists():
            try:
                pet_w = logo_h * pet_info["aspect_ratio"]
                pet_img = _load_png(path)
            except Exception:
                pass

    # ── Dessin ────────────────────────────────────────────────────────────────
    if not cof_img and not pet_img:
        return

    canvas.saveState()
    try:
        if cof_img:
            # Logo principal calé contre la marge droite
            canvas.drawImage(
                cof_img,
                cof_x,
                cof_y,
                width=cof_w,
                height=logo_h,
                mask="auto",
                preserveAspectRatio=True,
                anchor="sw",
            )

        if pet_img:
            if cof_img:
                # Logo pétanque superposé en bas à gauche du logo principal,
                # à 1/3 de la hauteur du logo principal
                pet_h_draw = logo_h / 3
                pet_w_draw = pet_w / 3  # même facteur (ratio conservé)
                pet_x = cof_x
                pet_y = cof_y
            else:
                # Logo pétanque seul (pas de logo principal) : taille complète, a droite
                pet_h_draw = logo_h
                pet_w_draw = pet_w
                pet_x = page_w - marge - pet_w
                pet_y = page_h - marge - logo_h
            canvas.drawImage(
                pet_img,
                pet_x,
                pet_y,
                width=pet_w_draw,
                height=pet_h_draw,
                mask="auto",
                preserveAspectRatio=True,
                anchor="sw",
            )
    except Exception:
        pass
    finally:
        canvas.restoreState()
