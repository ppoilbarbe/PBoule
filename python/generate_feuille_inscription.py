#!/usr/bin/env python3
"""
Génère la feuille d'inscription au format PDF A4 portrait.

Structure par équipe : N°, nom d'équipe, 3 noms de membres, 3 cases de paiement.
Si le contenu ne tient pas raisonnablement sur une feuille (hauteur de ligne
inférieure au seuil MIN_H_SUB), deux pages sont générées sans traits de coupe,
avec numérotation de page.

Usage :
    python python/generate_feuille_inscription.py --n-equipes 32 \\
           --output documents/ \\
           --logo-yaml logo.yaml
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import argparse

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from pboule.logos import draw_logos
from pboule.palette import _BLANC, _BLEU, _GRIS_FOND, _GRIS_GRILLE, _NOIR
from pboule.utils import charger_logo_yaml

N_MEMBRES = 3  # membres par équipe
MIN_H_SUB = 0.50 * cm  # hauteur minimale acceptable d'une sous-ligne
MAX_H_SUB = 0.80 * cm  # hauteur maximale (au-delà c'est du gaspillage)


# ── Construction du tableau d'inscription ────────────────────────────────────


def _build_table(
    equipes: range,
    cw: list[float],
    h_sub: float,
    h_hdr: float,
    fs_hdr: int,
    fs_body: int,
    start_idx: int = 0,  # index de départ pour l'alternance des fonds
) -> Table:
    """
    Construit le tableau pour une plage d'équipes.

    Chaque équipe occupe N_MEMBRES sous-lignes :
    - Colonnes N° et Nom d'équipe : fusionnées (SPAN) sur les N_MEMBRES lignes.
    - Colonne Noms des membres    : une sous-ligne par membre.
    - Colonne Paiement            : une case à cocher par membre.
    """

    def _st(name: str, **kw) -> ParagraphStyle:
        return ParagraphStyle(name, **kw)

    st_ent = _st(
        "E",
        fontName="Helvetica-Bold",
        fontSize=fs_hdr,
        textColor=_BLANC,
        alignment=TA_CENTER,
    )
    st_num = _st(
        "N",
        fontName="Helvetica-Bold",
        fontSize=fs_body,
        textColor=_NOIR,
        alignment=TA_CENTER,
    )

    # ── En-tête ───────────────────────────────────────────────────────────────
    data = [
        [
            Paragraph("N°", st_ent),
            Paragraph("NOM D'ÉQUIPE", st_ent),
            Paragraph("NOMS DES MEMBRES", st_ent),
            Paragraph("PAIEMENT", st_ent),
        ]
    ]
    row_heights = [h_hdr]

    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), _BLEU),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, _BLEU),
        ("GRID", (0, 0), (-1, -1), 0.5, _GRIS_GRILLE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]

    # ── Lignes de données ─────────────────────────────────────────────────────
    for idx, team_num in enumerate(equipes):
        base = 1 + idx * N_MEMBRES
        last = base + N_MEMBRES - 1
        bg = _BLANC if (idx + start_idx) % 2 == 0 else _GRIS_FOND

        for m in range(N_MEMBRES):
            data.append(
                [
                    Paragraph(str(team_num), st_num) if m == 0 else "",
                    "",  # nom d'équipe (spanné)
                    "",  # nom du membre (zone de saisie)
                    "",
                ]
            )  # paiement (case à cocher)
            row_heights.append(h_sub)

        style_cmds += [
            # Fusion N° et Nom sur les N_MEMBRES sous-lignes
            ("SPAN", (0, base), (0, last)),
            ("SPAN", (1, base), (1, last)),
            # Fond alternant par équipe
            ("BACKGROUND", (0, base), (-1, last), bg),
            # Séparateur inter-équipes (trait épais)
            ("LINEBELOW", (0, last), (-1, last), 1.0, _GRIS_GRILLE),
        ]
        # Traits fins inter-membres (colonnes Membres et Paiement seulement)
        for m in range(N_MEMBRES - 1):
            r = base + m
            style_cmds.append(("LINEBELOW", (2, r), (3, r), 0.3, _GRIS_GRILLE))

    table = Table(data, colWidths=cw, rowHeights=row_heights)
    table.setStyle(TableStyle(style_cmds))
    return table


# ── Générateur principal ──────────────────────────────────────────────────────


def generer(
    n_equipes: int,
    sortie: Path | None = None,
    logo_data: dict | None = None,
) -> Path:
    """
    Génère la feuille d'inscription.

    Args:
        n_equipes : Nombre maximum d'équipes (= nombre de lignes du tableau).
        sortie    : Chemin complet du PDF à produire.
        logo_data : Dict chargé depuis logo.yaml (logos et dimensions).

    Returns:
        Chemin absolu du PDF produit.
    """
    if sortie is None:
        sortie = Path("feuille_inscription.pdf")
    sortie.parent.mkdir(parents=True, exist_ok=True)

    page_w, page_h = A4  # portrait
    marge = 1.0 * cm
    larg = page_w - 2 * marge

    # ── Largeurs des colonnes ────────────────────────────────────────────────
    cw_num = 1.2 * cm  # N°
    cw_nom = 5.0 * cm  # Nom d'équipe
    cw_pay = 2.0 * cm  # Paiement (cases à cocher)
    cw_mbr = larg - cw_num - cw_nom - cw_pay  # Noms des membres
    cw = [cw_num, cw_nom, cw_mbr, cw_pay]

    # ── Dimensions de la zone en-tête (logo) ─────────────────────────────────
    h_hdr = 0.9 * cm
    h_footer = 0.5 * cm

    # Hauteur et largeur réservées pour le logo (depuis logo_data ou défaut)
    logo_h = (logo_data.get("logo_h_cm", 3.5) * cm) if logo_data else 1.5 * cm

    # ── Calcul des hauteurs disponibles par page ──────────────────────────────
    # Page 1 : l'en-tête occupe logo_h (logo + titre dans la même zone)
    # Page 2 : pas d'en-tête (le tableau commence directement en haut)
    avail1 = page_h - 2 * marge - logo_h - h_hdr - h_footer
    avail2 = page_h - 2 * marge - h_hdr - h_footer

    h_ideal = min(avail1 / (n_equipes * N_MEMBRES), MAX_H_SUB)
    two_pages = h_ideal < MIN_H_SUB

    if two_pages:
        # Répartition asymétrique : page 1 a moins de place (logo)
        max_n1 = int(avail1 / (N_MEMBRES * MIN_H_SUB))
        n1 = min(max(max_n1, 1), n_equipes - 1)
        n2 = n_equipes - n1
        h_sub = min(
            min(avail1 / (n1 * N_MEMBRES), MAX_H_SUB),
            min(avail2 / (n2 * N_MEMBRES), MAX_H_SUB),
        )
    else:
        n1 = n_equipes
        n2 = 0
        h_sub = h_ideal

    # Taille de police adaptée à la hauteur de ligne
    fs_body = 9 if h_sub >= 0.55 * cm else 8
    fs_hdr = fs_body
    fs_tit = 16

    # ── Story ─────────────────────────────────────────────────────────────────
    # Un Spacer de logo_h réserve la zone en-tête (logo + titre dessinés sur
    # le canvas). Le tableau commence donc strictement sous le logo.
    story = []

    story.append(Spacer(1, logo_h))
    story.append(
        _build_table(
            range(1, n1 + 1),
            cw,
            h_sub,
            h_hdr,
            fs_hdr,
            fs_body,
            start_idx=0,
        )
    )

    if two_pages:
        story.append(PageBreak())
        story.append(
            _build_table(
                range(n1 + 1, n_equipes + 1),
                cw,
                h_sub,
                h_hdr,
                fs_hdr,
                fs_body,
                start_idx=n1,
            )
        )

    # ── Construction du PDF ───────────────────────────────────────────────────
    n_pages = 2 if two_pages else 1

    def _draw_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(
            page_w / 2,
            marge * 0.4,
            f"Page {doc.page} / {n_pages}",
        )
        canvas.restoreState()

    def _cb_first(canvas, doc):
        # Logos uniquement sur la première page
        draw_logos(canvas, page_w, page_h, marge, logo_data)
        # Titre centré verticalement dans la zone en-tête (hauteur logo_h)
        canvas.saveState()
        canvas.setFont("Helvetica-Bold", fs_tit)
        canvas.setFillColor(_BLEU)
        zone_bas = page_h - marge - logo_h  # bas de la zone, coord. canvas
        baseline_y = zone_bas + (logo_h - fs_tit * 0.3) / 2
        canvas.drawString(marge, baseline_y, "FEUILLE D'INSCRIPTION")
        canvas.restoreState()
        _draw_footer(canvas, doc)

    def _cb_later(canvas, doc):
        # Pages suivantes : pas de logos, seulement le pied de page
        _draw_footer(canvas, doc)

    doc = SimpleDocTemplate(
        str(sortie),
        pagesize=A4,
        leftMargin=marge,
        rightMargin=marge,
        topMargin=marge,
        bottomMargin=marge,
        title="Feuille d'inscription",
    )
    doc.build(story, onFirstPage=_cb_first, onLaterPages=_cb_later)
    return sortie.resolve()


# ── Interface en ligne de commande ────────────────────────────────────────────


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Génère la feuille d'inscription au format PDF A4 portrait.",
    )
    ap.add_argument(
        "--n-equipes",
        type=int,
        required=True,
        metavar="N",
        help="Nombre maximum d'équipes (= nombre de lignes)",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("."),
        metavar="DIR",
        help="Dossier de sortie (défaut : répertoire courant)",
    )
    ap.add_argument(
        "--logo-yaml",
        type=Path,
        default=None,
        metavar="FILE",
        help="Chemin vers logo.yaml (optionnel)",
    )

    args = ap.parse_args()

    logo_data = None
    if args.logo_yaml and args.logo_yaml.exists():
        logo_data = charger_logo_yaml(args.logo_yaml)

    chemin = args.output / "feuille_inscription.pdf"
    pdf = generer(n_equipes=args.n_equipes, sortie=chemin, logo_data=logo_data)
    print(f"Feuille d'inscription générée : {pdf}")


if __name__ == "__main__":
    main()
