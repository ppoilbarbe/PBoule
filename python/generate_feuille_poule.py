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

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from logos import draw_logos

# ── Palette ──────────────────────────────────────────────────────────────────

# Table de 16 couleurs bien contrastées, indexée par numéro de poule.
# Les couleurs servent uniquement à l'identification visuelle (en-têtes).
COULEURS: dict[int, colors.Color] = {
    1: colors.HexColor("#E53935"),  # Rouge
    2: colors.HexColor("#1E88E5"),  # Bleu
    3: colors.HexColor("#43A047"),  # Vert
    4: colors.HexColor("#FB8C00"),  # Orange
    5: colors.HexColor("#8E24AA"),  # Violet
    6: colors.HexColor("#00ACC1"),  # Cyan
    7: colors.HexColor("#D81B60"),  # Rose
    8: colors.HexColor("#6D4C41"),  # Brun
    9: colors.HexColor("#9E9D24"),  # Olive
    10: colors.HexColor("#283593"),  # Bleu marine
    11: colors.HexColor("#00695C"),  # Sarcelle
    12: colors.HexColor("#E65100"),  # Orange brûlé
    13: colors.HexColor("#37474F"),  # Gris ardoise
    14: colors.HexColor("#880E4F"),  # Bordeaux
    15: colors.HexColor("#33691E"),  # Vert forêt
    16: colors.HexColor("#4527A0"),  # Indigo
}

# Les noms de poules sont des lettres (A à P).
NOMS_POULES: dict[int, str] = {i: chr(64 + i) for i in range(1, 17)}

_NOIR = colors.black
_BLANC = colors.white
_GRIS_FOND = colors.HexColor("#F0F0F0")
_GRIS_GRILLE = colors.HexColor("#AAAAAA")


# ── Utilitaires ──────────────────────────────────────────────────────────────


def _matches(n: int) -> list[tuple[int, int]]:
    """Toutes les combinaisons de 2 équipes parmi n (ordre croissant)."""
    return list(itertools.combinations(range(1, n + 1), 2))


def _rang(n: int) -> str:
    """Rang ordinal français : 1er, 2e, 3e…"""
    return "1er" if n == 1 else f"{n}e"


def repartition_poules(n_total: int, base: int = 4) -> list[int]:
    """
    Répartit n_total équipes en poules de taille `base` ou `base+1`.

    Priorités (de haut en bas) :
      1. Distribution uniforme en poules de (base+1) si N divisible par base+1.
      2. Distribution uniforme en poules de base si N divisible par base.
      3. Distribution mixte minimisant le nombre total de poules.

    Exemples (base=4) :
      8  → [4, 4]         # divisible par 4
      9  → [5, 4]         # mixte
      12 → [4, 4, 4]      # divisible par 4
      20 → [5, 5, 5, 5]   # divisible par 5
      24 → [4, 4, 4, 4, 4, 4]  # divisible par 4
      32 → [4]*8          # divisible par 4

    Retourne une liste ordonnée (poules de base+1 en premier si mixte).
    """
    # Priorité 1 : distribution uniforme en poules de (base+1)
    if n_total % (base + 1) == 0:
        return [base + 1] * (n_total // (base + 1))
    # Priorité 2 : distribution uniforme en poules de base
    if n_total % base == 0:
        return [base] * (n_total // base)
    # Priorité 3 : distribution mixte minimisant le nombre de poules
    for n_poules in range(max(1, n_total // (base + 1)), n_total + 1):
        x = n_total - n_poules * base  # poules de base+1
        y = n_poules - x  # poules de base
        if 0 <= x <= n_poules and y >= 0:
            return [base + 1] * x + [base] * y
    # Cas dégénéré (non décomposable en poules de base ou base+1)
    n_poules = max(1, n_total // base)
    reste = n_total - n_poules * base
    return [base] * n_poules + ([reste] if reste else [])


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
    coul = COULEURS.get(num_poule, _NOIR)

    if sortie is None:
        sortie = Path(f"poule_{num_poule:02d}.pdf")
    sortie.parent.mkdir(parents=True, exist_ok=True)

    if equipes is None:
        equipes = [(None, "") for _ in range(n_equipes)]

    # ── Dimensions ───────────────────────────────────────────────────────────
    page_w, page_h = landscape(A4)
    marge = 1.0 * cm
    larg = page_w - 2 * marge  # largeur utile du contenu

    # Paramètres typographiques adaptés au nombre d'équipes
    # (tout doit tenir sur une page A4 paysage)
    if n_equipes <= 4:
        h_row = 0.80 * cm  # hauteur de ligne
        fs_body = 10  # taille police corps
        fs_head = 10  # taille police en-têtes
        fs_tit = 20  # taille police titre principal
        esp = 0.28 * cm  # espace entre tableaux
    elif n_equipes <= 5:
        h_row = 0.65 * cm
        fs_body = 9
        fs_head = 9
        fs_tit = 18
        esp = 0.18 * cm
    else:  # n_equipes >= 6 — Poule UNIQUE ou cas dégénéré
        h_row = 0.52 * cm
        fs_body = 8
        fs_head = 8
        fs_tit = 16
        esp = 0.12 * cm

    # ── Styles paragraphes ───────────────────────────────────────────────────

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
        """Sous-en-tête (fond gris)."""
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

    # Style commun pour les cellules de tableau (padding)
    _pad = [
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]

    story: list = []

    # ── Titre principal ───────────────────────────────────────────────────────
    titre = titre_complet or (
        f"Poule\u00a0«\u00a0{nom}\u00a0»\u00a0\u2014\u00a0{n_equipes}\u00a0équipes"
    )
    story.append(Paragraph(titre, st_titre))
    story.append(Spacer(1, fs_tit * 0.6))  # interligne ≈ 1 ligne de titre

    # ════════════════════════════════════════════════════════════════════════
    # Tableau 1 — NOMS – PRÉNOMS  (50 % de la largeur de page)
    # ════════════════════════════════════════════════════════════════════════

    half = larg / 2
    cw1 = [3.0 * cm, 3.2 * cm, half - 6.2 * cm]

    data1 = [
        [
            Paragraph("ÉQUIPE", st_ent()),
            Paragraph("N°\u00a0INSCRIPTION", st_ent()),
            Paragraph("NOMS\u00a0–\u00a0PRÉNOMS", st_ent()),
        ]
    ]
    for i in range(n_equipes):
        num_insc, noms = equipes[i]
        data1.append(
            [
                Paragraph(f"<b>Équipe\u00a0{i + 1}</b>", st_body()),
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
    for r in range(1, len(data1)):
        st1.append(
            ("BACKGROUND", (0, r), (-1, r), _BLANC if r % 2 == 1 else _GRIS_FOND)
        )

    t1 = Table(data1, colWidths=cw1, rowHeights=h_row)
    t1.setStyle(TableStyle(st1))
    t1.hAlign = "LEFT"
    story.append(t1)
    story.append(Spacer(1, esp))

    # ════════════════════════════════════════════════════════════════════════
    # Tableau 2 — Résultats des matches
    # ════════════════════════════════════════════════════════════════════════

    liste_matches = _matches(n_equipes)

    cw_m = 2.3 * cm  # colonne Matchs
    cw_r = 2.8 * cm  # colonne Résultats
    cw_e = (larg - cw_m - cw_r) / n_equipes  # colonne par équipe
    cw2 = [cw_m, cw_r] + [cw_e] * n_equipes

    # En-tête
    data2 = [
        [
            Paragraph("Matchs", st_ent()),
            Paragraph("Résultats", st_ent()),
            *[Paragraph(f"Éq.\u00a0{i}", st_ent()) for i in range(1, n_equipes + 1)],
        ]
    ]

    # Lignes de matches
    for ea, eb in liste_matches:
        # Tiret quadratin centré dans la cellule Résultats (repère pour le score)
        ligne = [
            Paragraph(f"{ea}\u00a0–\u00a0{eb}", st_body()),
            Paragraph("\u2014", st_body()),
        ]
        for eq in range(1, n_equipes + 1):
            ligne.append("" if eq in (ea, eb) else "_NOIR_")  # marqueur temporaire
        data2.append(ligne)

    # Ligne TOTAL
    idx_total = len(data2)  # position dans data2 après ajout de la ligne
    data2.append(
        [Paragraph("<b>TOTAL</b>", st_ent()), ""] + ["" for _ in range(n_equipes)]
    )

    st2 = [
        # En-tête
        ("BACKGROUND", (0, 0), (-1, 0), coul),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, coul),
        # Corps
        ("GRID", (0, 0), (-1, -1), 0.5, _GRIS_GRILLE),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), fs_body),
        # Ligne TOTAL
        ("SPAN", (0, idx_total), (1, idx_total)),
        ("BACKGROUND", (0, idx_total), (1, idx_total), coul),
        ("TEXTCOLOR", (0, idx_total), (1, idx_total), _BLANC),
        ("FONTNAME", (0, idx_total), (-1, idx_total), "Helvetica-Bold"),
        ("FONTSIZE", (0, idx_total), (-1, idx_total), fs_head),
        ("BACKGROUND", (2, idx_total), (-1, idx_total), _GRIS_FOND),
        ("LINEABOVE", (0, idx_total), (-1, idx_total), 1.5, coul),
        *_pad,
    ]

    # Cellules noires pour les équipes absentes d'un match
    for r_idx, (ea, eb) in enumerate(liste_matches):
        row = r_idx + 1  # +1 pour l'en-tête
        for eq in range(1, n_equipes + 1):
            if eq not in (ea, eb):
                col = eq + 1  # 0=Matchs, 1=Résultats, 2..=Équipes
                st2.append(("BACKGROUND", (col, row), (col, row), _NOIR))

    # Remplacer les marqueurs temporaires par ''
    for ligne in data2[1:idx_total]:
        for j, v in enumerate(ligne):
            if v == "_NOIR_":
                ligne[j] = ""

    t2 = Table(data2, colWidths=cw2, rowHeights=h_row)
    t2.setStyle(TableStyle(st2))
    story.append(t2)
    story.append(Spacer(1, esp))

    # ════════════════════════════════════════════════════════════════════════
    # Tableau 3 — Classement
    # ════════════════════════════════════════════════════════════════════════

    cw3 = [2.5 * cm, 7.5 * cm, 2.0 * cm]
    nom_classement = "UNIQUE" if titre_complet else nom
    titre_t3 = f"CLASSEMENT POULE {nom_classement.upper()}"

    data3 = [
        # Titre fusionné sur les 3 colonnes
        [Paragraph(f"<b>{titre_t3}</b>", st_ent()), "", ""],
        # Sous-en-têtes
        [
            Paragraph("Classement", st_sh()),
            Paragraph("Équipe", st_sh()),
            Paragraph("Points", st_sh()),
        ],
    ] + [[Paragraph(_rang(i + 1), st_body()), "", ""] for i in range(n_equipes)]

    st3 = [
        # Titre
        ("SPAN", (0, 0), (2, 0)),
        ("BACKGROUND", (0, 0), (2, 0), coul),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, coul),
        # Sous-en-tête
        ("BACKGROUND", (0, 1), (-1, 1), _GRIS_FOND),
        ("LINEBELOW", (0, 1), (-1, 1), 0.5, _GRIS_GRILLE),
        # Corps
        ("GRID", (0, 0), (-1, -1), 0.5, _GRIS_GRILLE),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 2), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 2), (-1, -1), fs_body),
        *_pad,
    ]
    for r in range(2, len(data3)):
        st3.append(
            ("BACKGROUND", (0, r), (-1, r), _BLANC if r % 2 == 0 else _GRIS_FOND)
        )

    t3 = Table(data3, colWidths=cw3, rowHeights=h_row)
    t3.setStyle(TableStyle(st3))
    story.append(t3)

    # ════════════════════════════════════════════════════════════════════════
    # Construction du PDF
    # ════════════════════════════════════════════════════════════════════════

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
    • poule_{lettre}_{pool_base:02d}eq.pdf  et
      poule_{lettre}_{pool_base+1:02d}eq.pdf
      pour chaque lettre de poule (A, B, C…) jusqu'au maximum nécessaire.
    • poule_unique_{N:02d}eq.pdf  pour chaque N de [teams_min, teams_max]
      non décomposable en poules de pool_base ou pool_base+1 équipes.
    """
    output.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    valides = set(range(pool_base, (pool_base + 1) + 1))  # {base, base+1}

    # ── Cas particuliers : Poule UNIQUE ──────────────────────────────────────
    for n in range(teams_min, teams_max + 1):
        tailles = repartition_poules(n, pool_base)
        if any(t not in valides for t in tailles):
            chemin = output / f"poule_unique_{n:02d}eq.pdf"
            pdf = generer(
                num_poule=1,
                n_equipes=n,
                sortie=chemin,
                logo_data=logo_data,
                titre_complet=f"Poule\u00a0UNIQUE\u00a0de\u00a0{n}\u00a0équipes",
            )
            generated.append(pdf)
            print(f"  {pdf}  [Poule UNIQUE]")

    # ── Cas normaux : un gabarit par (lettre × taille) ───────────────────────
    normaux = [
        n
        for n in range(teams_min, teams_max + 1)
        if all(t in valides for t in repartition_poules(n, pool_base))
    ]
    if normaux:
        max_pools = max(len(repartition_poules(n, pool_base)) for n in normaux)
        for num_poule in range(1, max_pools + 1):
            lettre = NOMS_POULES.get(num_poule, str(num_poule))
            for taille in (pool_base, pool_base + 1):
                chemin = output / f"poule_{lettre}_{taille:02d}eq.pdf"
                pdf = generer(
                    num_poule=num_poule,
                    n_equipes=taille,
                    sortie=chemin,
                    logo_data=logo_data,
                )
                generated.append(pdf)
                print(f"  {pdf}")

    return generated


# ── Chargement du fichier logo ────────────────────────────────────────────────


def _charger_logo_yaml(chemin: Path) -> dict | None:
    """Charge logo.yaml (format JSON, compatible YAML si pyyaml est installé)."""
    try:
        import yaml  # pyyaml, optionnel

        with open(chemin, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        import json

        with open(chemin, encoding="utf-8") as f:
            return json.load(f)


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
        logo_data = _charger_logo_yaml(args.logo_yaml)

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
