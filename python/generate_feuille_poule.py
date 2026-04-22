#!/usr/bin/env python3
"""
Génère une feuille de poule au format PDF A4 paysage.

Chaque feuille comporte :
  • un titre « Poule <nom> »
  • tableau 1 : NOMS – PRÉNOMS (équipes de la poule)
  • tableau 2 : résultats de tous les matches de la poule
  • tableau 3 : classement de la poule

Usage :
    python python/generate_feuille_poule.py --teams-min 6 --teams-max 32 \\
           --pool-base 4 --output documents/ \\
           --logo-yaml logo.yaml
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import argparse
import itertools

from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
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
from pboule.poules import COULEURS, NOMS_POULES, repartition_poules
from pboule.utils import charger_logo_yaml

# ── Utilitaires ──────────────────────────────────────────────────────────────


def _matches(n: int) -> list[tuple[int, int]]:
    """Toutes les combinaisons de 2 équipes parmi n (ordre croissant)."""
    return list(itertools.combinations(range(1, n + 1), 2))


def _rang(n: int) -> str:
    """Rang ordinal français : 1er, 2e, 3e…"""
    return "1er" if n == 1 else f"{n}e"


# ── Construction de la story Platypus ────────────────────────────────────────


def _build_story(
    num_poule: int,
    n_equipes: int,
    equipes: list[tuple[int | None, str]] | None = None,
    titre_complet: str | None = None,
) -> list:
    """Construit la story Platypus pour une feuille de poule."""
    nom = NOMS_POULES.get(num_poule, f"Poule {num_poule}")
    coul = COULEURS.get(num_poule, _NOIR)

    if equipes is None:
        equipes = [(None, "") for _ in range(n_equipes)]

    page_w, _page_h = landscape(A4)
    marge = 1.0 * cm
    larg = page_w - 2 * marge

    if n_equipes <= 4:
        h_row = 0.80 * cm
        fs_body = 10
        fs_head = 10
        fs_tit = 20
        esp = 0.28 * cm
    elif n_equipes <= 5:
        h_row = 0.65 * cm
        fs_body = 9
        fs_head = 9
        fs_tit = 18
        esp = 0.18 * cm
    else:
        h_row = 0.52 * cm
        fs_body = 8
        fs_head = 8
        fs_tit = 16
        esp = 0.12 * cm

    def _st(name: str, **kw) -> ParagraphStyle:
        return ParagraphStyle(name, **kw)

    st_titre = _st(
        "Titre",
        fontName="Helvetica-Bold",
        fontSize=fs_tit,
        textColor=coul,
        alignment=TA_LEFT,
        spaceAfter=0,
    )

    def st_ent(**kw) -> ParagraphStyle:
        return _st(
            "Ent",
            fontName="Helvetica-Bold",
            fontSize=fs_head,
            textColor=_BLANC,
            alignment=TA_CENTER,
            **kw,
        )

    def st_sh(**kw) -> ParagraphStyle:
        return _st(
            "SH",
            fontName="Helvetica-Bold",
            fontSize=fs_head,
            textColor=_NOIR,
            alignment=TA_CENTER,
            **kw,
        )

    def st_body(align=TA_CENTER) -> ParagraphStyle:
        return _st(
            "Body",
            fontName="Helvetica",
            fontSize=fs_body,
            textColor=_NOIR,
            alignment=align,
        )

    _pad = [
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]

    story: list = []

    # ── Titre principal ───────────────────────────────────────────────────────
    titre = titre_complet or (f"Poule « {nom} » — {n_equipes} équipes")
    story.append(Paragraph(titre, st_titre))
    story.append(Spacer(1, fs_tit * 0.6))

    # ── Tableau 1 — NOMS – PRÉNOMS ────────────────────────────────────────────
    half = larg / 2
    cw1 = [3.0 * cm, 3.2 * cm, half - 6.2 * cm]

    data1 = [
        [
            Paragraph("ÉQUIPE", st_ent()),
            Paragraph("N° INSCRIPTION", st_ent()),
            Paragraph("NOMS – PRÉNOMS", st_ent()),
        ]
    ]
    for i in range(n_equipes):
        num_insc, noms = equipes[i]
        data1.append(
            [
                Paragraph(f"<b>Équipe {i + 1}</b>", st_body()),
                Paragraph(str(num_insc) if num_insc else "", st_body()),
                Paragraph(noms or "", st_body(align=TA_LEFT)),
            ]
        )

    st1 = [
        ("BACKGROUND", (0, 0), (-1, 0), coul),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, coul),
        ("GRID", (0, 0), (-1, -1), 0.5, _GRIS_GRILLE),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        *_pad,
    ]
    for row in range(1, len(data1)):
        st1.append(
            ("BACKGROUND", (0, row), (-1, row), _BLANC if row % 2 == 1 else _GRIS_FOND)
        )

    t1 = Table(data1, colWidths=cw1, rowHeights=h_row)
    t1.setStyle(TableStyle(st1))
    t1.hAlign = "LEFT"
    story.append(t1)
    story.append(Spacer(1, esp))

    # ── Tableau 2 — Résultats des matches ─────────────────────────────────────
    liste_matches = _matches(n_equipes)

    cw_m = 2.3 * cm
    cw_r = 2.8 * cm
    cw_e = (larg - cw_m - cw_r) / n_equipes
    cw2 = [cw_m, cw_r] + [cw_e] * n_equipes

    data2 = [
        [
            Paragraph("Matchs", st_ent()),
            Paragraph("Résultats", st_ent()),
            *[Paragraph(f"Éq. {i}", st_ent()) for i in range(1, n_equipes + 1)],
        ]
    ]

    for ea, eb in liste_matches:
        ligne = [
            Paragraph(f"{ea} – {eb}", st_body()),
            Paragraph("—", st_body()),
        ]
        for eq in range(1, n_equipes + 1):
            ligne.append("" if eq in (ea, eb) else "_NOIR_")
        data2.append(ligne)

    idx_total = len(data2)
    data2.append(
        [Paragraph("<b>TOTAL</b>", st_ent()), ""] + ["" for _ in range(n_equipes)]
    )

    st2 = [
        ("BACKGROUND", (0, 0), (-1, 0), coul),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, coul),
        ("GRID", (0, 0), (-1, -1), 0.5, _GRIS_GRILLE),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), fs_body),
        ("SPAN", (0, idx_total), (1, idx_total)),
        ("BACKGROUND", (0, idx_total), (1, idx_total), coul),
        ("TEXTCOLOR", (0, idx_total), (1, idx_total), _BLANC),
        ("FONTNAME", (0, idx_total), (-1, idx_total), "Helvetica-Bold"),
        ("FONTSIZE", (0, idx_total), (-1, idx_total), fs_head),
        ("BACKGROUND", (2, idx_total), (-1, idx_total), _GRIS_FOND),
        ("LINEABOVE", (0, idx_total), (-1, idx_total), 1.5, coul),
        *_pad,
    ]

    for r_idx, (ea, eb) in enumerate(liste_matches):
        row = r_idx + 1
        for eq in range(1, n_equipes + 1):
            if eq not in (ea, eb):
                col = eq + 1
                st2.append(("BACKGROUND", (col, row), (col, row), _NOIR))

    for ligne in data2[1:idx_total]:
        for j, v in enumerate(ligne):
            if v == "_NOIR_":
                ligne[j] = ""

    t2 = Table(data2, colWidths=cw2, rowHeights=h_row)
    t2.setStyle(TableStyle(st2))
    story.append(t2)
    story.append(Spacer(1, esp))

    # ── Tableau 3 — Classement ────────────────────────────────────────────────
    cw3 = [2.5 * cm, 7.5 * cm, 2.0 * cm]
    nom_classement = "UNIQUE" if titre_complet else nom
    titre_t3 = f"CLASSEMENT POULE {nom_classement.upper()}"

    data3 = [
        [Paragraph(f"<b>{titre_t3}</b>", st_ent()), "", ""],
        [
            Paragraph("Classement", st_sh()),
            Paragraph("Équipe", st_sh()),
            Paragraph("Points", st_sh()),
        ],
    ] + [[Paragraph(_rang(i + 1), st_body()), "", ""] for i in range(n_equipes)]

    st3 = [
        ("SPAN", (0, 0), (2, 0)),
        ("BACKGROUND", (0, 0), (2, 0), coul),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, coul),
        ("BACKGROUND", (0, 1), (-1, 1), _GRIS_FOND),
        ("LINEBELOW", (0, 1), (-1, 1), 0.5, _GRIS_GRILLE),
        ("GRID", (0, 0), (-1, -1), 0.5, _GRIS_GRILLE),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 2), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 2), (-1, -1), fs_body),
        *_pad,
    ]
    for row in range(2, len(data3)):
        st3.append(
            ("BACKGROUND", (0, row), (-1, row), _BLANC if row % 2 == 0 else _GRIS_FOND)
        )

    t3 = Table(data3, colWidths=cw3, rowHeights=h_row)
    t3.setStyle(TableStyle(st3))
    story.append(t3)

    return story


# ── Générateur principal ─────────────────────────────────────────────────────


def generer(
    num_poule: int,
    n_equipes: int,
    equipes: list[tuple[int | None, str]] | None = None,
    sortie: Path | None = None,
    logo_data: dict | None = None,
    titre_complet: str | None = None,
) -> Path:
    """
    Génère la feuille de poule au format PDF A4 paysage.

    Args:
        num_poule     : Numéro de la poule (détermine la couleur).
        n_equipes     : Nombre d'équipes dans la poule.
        equipes       : Liste (num_inscription, noms) par équipe.
                        Si None, génère un gabarit vierge.
        sortie        : Chemin complet du PDF à produire.
        logo_data     : Dict chargé depuis logo.yaml (logos et dimensions).
        titre_complet : Remplace le titre standard (ex. «Poule UNIQUE de 6 équipes»).

    Returns:
        Chemin absolu du PDF produit.
    """
    nom = NOMS_POULES.get(num_poule, f"Poule {num_poule}")
    if sortie is None:
        sortie = Path(f"poule_{num_poule:02d}.pdf")
    sortie.parent.mkdir(parents=True, exist_ok=True)

    page_w, page_h = landscape(A4)
    marge = 1.0 * cm
    story = _build_story(num_poule, n_equipes, equipes, titre_complet)

    doc = SimpleDocTemplate(
        str(sortie),
        pagesize=landscape(A4),
        leftMargin=marge,
        rightMargin=marge,
        topMargin=marge,
        bottomMargin=marge,
        title=f"Poule {nom}",
    )

    def _cb_first(canvas, _doc):
        draw_logos(canvas, page_w, page_h, marge, logo_data)

    doc.build(story, onFirstPage=_cb_first, onLaterPages=lambda c, d: None)
    return sortie.resolve()


def generer_multi(
    num_poule: int,
    tailles: list[int],
    sortie: Path,
    logo_data: dict | None = None,
) -> Path:
    """
    Génère un PDF multi-pages regroupant plusieurs tailles de poule.

    Chaque taille occupe une page A4 paysage. Logo présent sur chaque page
    (chaque page est une feuille de poule indépendante).

    Args:
        num_poule : Numéro de la poule (détermine la couleur et la lettre).
        tailles   : Liste des tailles à inclure (ex. [4, 5]).
        sortie    : Chemin du PDF à produire.
        logo_data : Dict chargé depuis logo.yaml.

    Returns:
        Chemin absolu du PDF produit.
    """
    nom = NOMS_POULES.get(num_poule, f"Poule {num_poule}")
    page_w, page_h = landscape(A4)
    marge = 1.0 * cm

    combined_story: list = []
    for i, taille in enumerate(tailles):
        if i > 0:
            combined_story.append(PageBreak())
        combined_story.extend(_build_story(num_poule, taille, None, None))

    sortie.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(sortie),
        pagesize=landscape(A4),
        leftMargin=marge,
        rightMargin=marge,
        topMargin=marge,
        bottomMargin=marge,
        title=f"Poule {nom}",
    )

    def _cb(canvas, _doc):
        draw_logos(canvas, page_w, page_h, marge, logo_data)

    doc.build(combined_story, onFirstPage=_cb, onLaterPages=_cb)
    return sortie.resolve()


# ── Cas particulier : poule réduite ──────────────────────────────────────────


def _est_pool_reduite(tailles: list[int], pool_base: int) -> bool:
    """
    Vrai si la répartition correspond au cas « poule réduite » :
    au moins 3 poules, toutes de taille pool_base sauf la dernière
    qui vaut pool_base-1.
    """
    return (
        len(tailles) >= 3
        and tailles[-1] == pool_base - 1
        and all(t == pool_base for t in tailles[:-1])
    )


def _build_info_repartition(n_total: int, tailles: list[int]) -> list:
    """Bloc compact indiquant la répartition des poules."""
    n_poules = len(tailles)

    st_hdr = ParagraphStyle(
        "IHdr",
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=_BLANC,
        alignment=TA_CENTER,
    )
    st_poule = ParagraphStyle(
        "IPoule",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=_NOIR,
        alignment=TA_CENTER,
    )
    st_val = ParagraphStyle(
        "IVal",
        fontName="Helvetica",
        fontSize=9,
        textColor=_NOIR,
        alignment=TA_CENTER,
    )

    data: list[list] = [
        [
            Paragraph(
                f"{n_total} équipes — {n_poules} poules",
                st_hdr,
            ),
            "",
        ]
    ]
    for i, n in enumerate(tailles):
        lettre = NOMS_POULES.get(i + 1, str(i + 1))
        data.append(
            [
                Paragraph(f"Poule {lettre}", st_poule),
                Paragraph(f"{n} équipes", st_val),
            ]
        )

    col_w = [3.5 * cm, 3.0 * cm]
    h_row = 0.65 * cm
    n_rows = len(data)

    style = [
        ("SPAN", (0, 0), (1, 0)),
        ("BACKGROUND", (0, 0), (1, 0), _BLEU),
        ("GRID", (0, 0), (-1, -1), 0.5, _GRIS_GRILLE),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]
    for i in range(1, n_rows):
        coul = COULEURS.get(i, _NOIR)
        style.extend(
            [
                ("TEXTCOLOR", (0, i), (0, i), coul),
                ("BACKGROUND", (0, i), (-1, i), _BLANC if i % 2 == 1 else _GRIS_FOND),
            ]
        )

    t = Table(data, colWidths=col_w, rowHeights=h_row)
    t.setStyle(TableStyle(style))
    t.hAlign = "LEFT"

    return [t, Spacer(1, 0.4 * cm)]


def generer_pool_reduite(
    n_total: int,
    tailles: list[int],
    sortie: Path,
    logo_data: dict | None = None,
) -> Path:
    """
    Génère la feuille spéciale pour le cas « poule réduite » :
    page unique contenant un tableau de répartition suivi de la feuille
    de la dernière poule (taille pool_base-1).
    """
    n_poules = len(tailles)
    n_reduite = tailles[-1]
    page_w, page_h = landscape(A4)
    marge = 1.0 * cm

    story: list = []
    story.extend(_build_info_repartition(n_total, tailles))
    story.extend(_build_story(n_poules, n_reduite))

    sortie.parent.mkdir(parents=True, exist_ok=True)
    lettre = NOMS_POULES.get(n_poules, str(n_poules))
    doc = SimpleDocTemplate(
        str(sortie),
        pagesize=landscape(A4),
        leftMargin=marge,
        rightMargin=marge,
        topMargin=marge,
        bottomMargin=marge,
        title=(f"Poule {lettre} — {n_reduite} équipes ({n_total} équipes au total)"),
    )

    def _cb_first(canvas, _doc):
        draw_logos(canvas, page_w, page_h, marge, logo_data)

    doc.build(story, onFirstPage=_cb_first, onLaterPages=lambda c, d: None)
    return sortie.resolve()


# ── Génération de l'ensemble des gabarits ────────────────────────────────────


def generer_toutes_feuilles(
    teams_min: int,
    teams_max: int,
    pool_base: int,
    output: Path,
    logo_data: dict | None,
) -> list[Path]:
    """
    Génère l'ensemble des gabarits de feuilles de poule.

    Produit :
    • poule_{lettre}.pdf  pour chaque lettre de poule (A, B, C…) jusqu'au
      maximum nécessaire — chaque PDF contient 2 pages :
        page 1 : pool_base équipes
        page 2 : pool_base+1 équipes
    • poule_{lettre}_{N:02d}eq.pdf  quand la répartition de N équipes donne
      au moins 3 poules de pool_base + une dernière poule de pool_base-1
      (ex. N=11, base=4 → A=4, B=4, C=3 → poule_C_11eq.pdf).
    • poule_unique_{N:02d}eq.pdf  pour chaque N non décomposable autrement
      (ex. N=6, N=7 avec base=4).
    """
    output.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    valides = {pool_base, pool_base + 1}

    # ── Cas particuliers ──────────────────────────────────────────────────────
    for n in range(teams_min, teams_max + 1):
        tailles = repartition_poules(n, pool_base)
        if any(t not in valides for t in tailles):
            if _est_pool_reduite(tailles, pool_base):
                lettre = NOMS_POULES.get(len(tailles), str(len(tailles)))
                chemin = output / f"poule_{lettre}_{n:02d}eq.pdf"
                pdf = generer_pool_reduite(n, tailles, chemin, logo_data)
                generated.append(pdf)
                tag = f"Poule {lettre} réduite — {tailles[-1]} éq."
                print(f"  {pdf}  [{tag}]")
            else:
                chemin = output / f"poule_unique_{n:02d}eq.pdf"
                pdf = generer(
                    num_poule=1,
                    n_equipes=n,
                    sortie=chemin,
                    logo_data=logo_data,
                    titre_complet=f"Poule UNIQUE de {n} équipes",
                )
                generated.append(pdf)
                print(f"  {pdf}  [Poule UNIQUE]")

    # ── Cas normaux : un PDF par lettre, regroupant les deux tailles ─────────
    normaux = [
        n
        for n in range(teams_min, teams_max + 1)
        if all(t in valides for t in repartition_poules(n, pool_base))
    ]
    if normaux:
        max_pools = max(len(repartition_poules(n, pool_base)) for n in normaux)
        for num_poule in range(1, max_pools + 1):
            lettre = NOMS_POULES.get(num_poule, str(num_poule))
            chemin = output / f"poule_{lettre}.pdf"
            pdf = generer_multi(
                num_poule=num_poule,
                tailles=[pool_base, pool_base + 1],
                sortie=chemin,
                logo_data=logo_data,
            )
            generated.append(pdf)
            print(f"  {pdf}  [{pool_base} eq. + {pool_base + 1} eq.]")

    return generated


# ── Interface en ligne de commande ────────────────────────────────────────────


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Génère les gabarits de feuilles de poule au format PDF A4 paysage."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemple :\n"
            "  python python/generate_feuille_poule.py \\\n"
            "      --teams-min 6 --teams-max 32 --pool-base 4 \\\n"
            "      --output documents/ \\\n"
            "      --logo-yaml logo.yaml\n"
        ),
    )
    ap.add_argument(
        "--teams-min",
        type=int,
        required=True,
        metavar="N",
        help="Nombre minimal d'équipes dans la compétition",
    )
    ap.add_argument(
        "--teams-max",
        type=int,
        required=True,
        metavar="N",
        help="Nombre maximal d'équipes dans la compétition",
    )
    ap.add_argument(
        "--pool-base",
        type=int,
        default=4,
        metavar="N",
        help="Taille de base des poules (défaut : 4)",
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

    pdfs = generer_toutes_feuilles(
        teams_min=args.teams_min,
        teams_max=args.teams_max,
        pool_base=args.pool_base,
        output=args.output,
        logo_data=logo_data,
    )
    print(f"{len(pdfs)} feuille(s) générée(s) dans {args.output}/")


if __name__ == "__main__":
    main()
