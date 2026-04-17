#!/usr/bin/env python3
"""
Génère les feuilles de phases finales au format PDF A4 paysage.

Pour chaque groupe de N équipes partageant le même nombre de poules P :
  1. Répartition en P poules (même algorithme que les feuilles de poule)
  2. Qualifiés : 1er et 2e de chaque poule → 2P équipes
  3. Tableau à élimination directe SANS case bye :
     - Si 2P est une puissance de 2 (r=0) : toutes les équipes en round 1
     - Sinon (r>0) : r matches préliminaires + q-r entrées directes en round 1
       → 2 étages pré-remplis (colonne prél. + entrées directes)
  4. Match pour la 3e place inclus
  5. Un seul PDF par groupe de N (évite les doublons)

Placement anti-intrapoule (best-effort) :
  L'algorithme existant produit des paires anti-intrapoule ; les matches
  préliminaires reprennent les premières paires, les entrées directes sont
  réparties uniformément dans le bracket.

Format : A4 paysage. Si la hauteur de case descend sous MIN_CASE_H, le document
         est produit en 2 pages A4 portrait à assembler en A3 paysage.

Nommage : finales_{N}eq.pdf  /  finales_{N1}-{N2}eq.pdf  /  finales_{N1}_{N2}_...eq.pdf

Usage :
    python python/generate_phases_finales.py \\
        --teams-min 6 --teams-max 32 --pool-base 4 \\
        --output documents/ --logo-yaml logo.yaml
"""

from __future__ import annotations

import math
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import argparse

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas as rl_canvas

from logos import draw_logos

# ── Palette (identique à generate_feuille_poule) ─────────────────────────────

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
NOMS_POULES: dict[int, str] = {i: chr(64 + i) for i in range(1, 17)}

_NOIR = colors.black
_BLANC = colors.white
_GRIS_FOND = colors.HexColor("#F0F0F0")
_GRIS_VIDE = colors.HexColor("#F8F8F8")
_GRIS_TITRE_COL = colors.HexColor("#37474F")

MIN_CASE_H = 6 * mm  # en-dessous : passage en mode A3 (2 pages paysage)

# Overhead vertical total hors cases :
#   0.4 cm (gap en-têtes→cases) + 0.3 cm (gap bracket→3e) + 0.2 cm (gap titre 3e→cases)
_OVERHEAD_LAYOUT = 0.9 * cm

_NOM_TOURS: dict[int, str] = {
    64: "32es de finale",
    32: "16es de finale",
    16: "8es de finale",
    8: "Quarts de finale",
    4: "Demi-finales",
    2: "Finale",
}


def _nom_tour(n: int) -> str:
    return _NOM_TOURS.get(n, f"{n}-finale")


# ── Répartition en poules ─────────────────────────────────────────────────────


def repartition_poules(n_total: int, base: int = 4) -> list[int]:
    """Répartit n_total équipes en poules de taille base ou base+1."""
    if n_total % (base + 1) == 0:
        return [base + 1] * (n_total // (base + 1))
    if n_total % base == 0:
        return [base] * (n_total // base)
    for n_poules in range(max(1, n_total // (base + 1)), n_total + 1):
        x = n_total - n_poules * base
        y = n_poules - x
        if 0 <= x <= n_poules and y >= 0:
            return [base + 1] * x + [base] * y
    n_poules = max(1, n_total // base)
    reste = n_total - n_poules * base
    return [base] * n_poules + ([reste] if reste else [])


# ── Construction du bracket sans bye ─────────────────────────────────────────

# Type d'un slot : (label, num_poule)
Slot = tuple[str, int]


def placer_equipes_sans_bye(p_poules: int) -> dict:
    """
    Construit le bracket sans bye pour P poules.

    2P équipes sont réparties entre :
    - r matches préliminaires (r = 2P - q, avec q = puissance de 2 ≤ 2P)
    - q-r entrées directes au round 1

    Retourne un dict avec :
      q       : taille du bracket principal (puissance de 2)
      r       : nombre de matches préliminaires (0 si 2P est une puissance de 2)
      prelim  : liste de r paires (slot_haut, slot_bas) — matches préliminaires
      round1  : liste de q entrées — Slot (entrée directe) ou None (gagnant prélim)
    """
    n = 2 * p_poules
    q = 1
    while q * 2 <= n:
        q *= 2
    r = n - q  # 0 si n est déjà une puissance de 2

    # Arrangement anti-intrapoule (algorithme existant)
    half = max(1, p_poules // 2)
    all_teams: list[Slot] = []
    for i in range(p_poules):
        num_1 = i + 1
        num_2 = (i + half) % p_poules + 1
        all_teams.append((f"{NOMS_POULES[num_1]}1", num_1))
        all_teams.append((f"{NOMS_POULES[num_2]}2", num_2))

    # r premières paires → matches préliminaires (déjà anti-intrapoule par construction)
    prelim: list[tuple[Slot, Slot]] = [
        (all_teams[2 * i], all_teams[2 * i + 1]) for i in range(r)
    ]
    direct: list[Slot] = all_teams[2 * r :]  # q-r entrées directes

    # Répartition uniforme des positions de gagnants préliminaires dans round1
    # → interleave les None et les entrées directes pour maximiser l'anti-intrapoule
    if r == 0:
        prelim_positions: set[int] = set()
    else:
        step = q / r
        prelim_positions = {round(step * i) for i in range(r)}
        if len(prelim_positions) < r:
            # Fallback si round() produit des doublons (cas rares)
            prelim_positions = set(range(r))

    round1: list[Slot | None] = []
    di = 0
    for pos in range(q):
        if pos in prelim_positions:
            round1.append(None)
        else:
            round1.append(direct[di])
            di += 1

    return {"q": q, "r": r, "prelim": prelim, "round1": round1}


# ── Primitives de dessin ──────────────────────────────────────────────────────


def _draw_case_remplie(
    c,
    x: float,
    y_bot: float,
    w: float,
    h: float,
    label: str,
    num_poule: int,
    fs: float,
) -> None:
    """Case pré-remplie : sous-colonnes poule (fond coloré) / nom / score."""
    wp = w * 0.20
    wn = w * 0.58
    ws = w * 0.22
    coul = COULEURS.get(num_poule, _NOIR)

    c.setFillColor(coul)
    c.setStrokeColor(_NOIR)
    c.setLineWidth(0.5)
    c.rect(x, y_bot, wp, h, fill=True, stroke=True)
    c.setFillColor(_BLANC)
    c.setFont("Helvetica-Bold", fs)
    c.drawCentredString(x + wp / 2, y_bot + h / 2 - fs * 0.38, label)

    c.setFillColor(_BLANC)
    c.rect(x + wp, y_bot, wn, h, fill=True, stroke=True)

    c.setFillColor(_GRIS_FOND)
    c.rect(x + wp + wn, y_bot, ws, h, fill=True, stroke=True)


def _draw_case_vide(
    c,
    x: float,
    y_bot: float,
    w: float,
    h: float,
    fs: float,
) -> None:
    """Case vide (tours suivants) : nom / score."""
    wn = w * 0.78
    ws = w * 0.22

    c.setFillColor(_GRIS_VIDE)
    c.setStrokeColor(_NOIR)
    c.setLineWidth(0.5)
    c.rect(x, y_bot, wn, h, fill=True, stroke=True)

    c.setFillColor(_GRIS_FOND)
    c.rect(x + wn, y_bot, ws, h, fill=True, stroke=True)


def _draw_connector(
    c,
    x_right: float,
    y_center_haut: float,
    y_center_bas: float,
    x_left_out: float,
) -> None:
    """Coude reliant deux cases (haut et bas) à la case gagnant à droite."""
    x_mid = (x_right + x_left_out) / 2
    y_out = (y_center_haut + y_center_bas) / 2

    c.setStrokeColor(_NOIR)
    c.setLineWidth(0.6)
    c.line(x_right, y_center_haut, x_mid, y_center_haut)
    c.line(x_right, y_center_bas, x_mid, y_center_bas)
    c.line(x_mid, y_center_haut, x_mid, y_center_bas)
    c.line(x_mid, y_out, x_left_out, y_out)


# ── Rendu du bracket sur un canvas ───────────────────────────────────────────


def _render_bracket(
    c,
    bracket: dict,
    x0: float,
    y_top: float,
    case_w: float,
    case_h: float,
    conn_w: float,
    fs: float,
    draw_3e: bool,
    y_3e_top: float,
) -> None:
    """
    Dessine le tableau de finales et le match pour la 3e place.

    Toutes les cases (prél., round1, tours suivants, 3e place) ont la même
    hauteur case_h. Les positions des connecteurs sont propagées via y_centers
    pour tenir compte de l'espacement non uniforme dû aux matches préliminaires.

    Structure des colonnes (gauche → droite) :
      [Prél.]  Round1  Round2  …  Gagnant
    La colonne Prél. n'existe que si r > 0.
    """
    q = bracket["q"]
    r = bracket["r"]
    prelim: list[tuple[Slot, Slot]] = bracket["prelim"]
    round1: list[Slot | None] = bracket["round1"]
    has_prelim = r > 0
    n_rounds = int(math.log2(q))

    # x de la colonne round1
    x_r1 = x0 + (case_w + conn_w) if has_prelim else x0

    # ── En-têtes de colonnes ──────────────────────────────────────────────────
    c.setFillColor(_GRIS_TITRE_COL)
    c.setFont("Helvetica-Bold", fs + 0.5)
    if has_prelim:
        c.drawCentredString(x0 + case_w / 2, y_top, "Prél.")
    for col in range(n_rounds + 1):
        x_col = x_r1 + col * (case_w + conn_w)
        label = _nom_tour(q // (2**col)) if col < n_rounds else "Gagnant"
        c.drawCentredString(x_col + case_w / 2, y_top, label)

    y0 = y_top - 0.4 * cm  # haut de la zone des cases

    # ── Prélim. + Round 1 — parcours unique avec y_offset cumulatif ──────────
    # • None dans round1 → match prélim. :
    #     2 cases pré-remplies (case_h chacune) dans la colonne prél.
    #     + 1 case vide round1 centrée dans le span 2×case_h
    # • Slot dans round1 → 1 case pré-remplie de case_h (entrée directe)
    y_offset = 0.0
    round1_y_centers: list[float] = []
    pi = 0

    for pos in range(q):
        slot = round1[pos]
        if slot is None:
            sh, sb = prelim[pi]
            pi += 1

            # Deux cases prél. empilées, hauteur case_h chacune
            yb_h = y0 - y_offset - case_h
            yb_b = y0 - y_offset - 2 * case_h
            _draw_case_remplie(c, x0, yb_h, case_w, case_h, sh[0], sh[1], fs)
            _draw_case_remplie(c, x0, yb_b, case_w, case_h, sb[0], sb[1], fs)

            # Connecteur prél. → round1
            _draw_connector(
                c,
                x0 + case_w,
                yb_h + case_h / 2,
                yb_b + case_h / 2,
                x_r1,
            )

            # Case round1 (gagnant) centrée dans le span 2×case_h
            r1_center = y0 - y_offset - case_h  # milieu du span 2×case_h
            _draw_case_vide(c, x_r1, r1_center - case_h / 2, case_w, case_h, fs)

            round1_y_centers.append(r1_center)
            y_offset += 2 * case_h
        else:
            # Entrée directe : 1 case pré-remplie
            yb = y0 - y_offset - case_h
            _draw_case_remplie(c, x_r1, yb, case_w, case_h, slot[0], slot[1], fs)
            round1_y_centers.append(yb + case_h / 2)
            y_offset += case_h

    # ── Tours suivants : connecteurs et cases calculés depuis y_centers ───────
    round_y_centers = round1_y_centers
    for tour in range(1, n_rounds + 1):
        n_matches = len(round_y_centers) // 2
        x_col = x_r1 + tour * (case_w + conn_w)
        x_prev_right = x_col - conn_w
        next_centers: list[float] = []

        for m in range(n_matches):
            y_h = round_y_centers[2 * m]
            y_b = round_y_centers[2 * m + 1]
            y_center = (y_h + y_b) / 2
            _draw_case_vide(c, x_col, y_center - case_h / 2, case_w, case_h, fs)
            _draw_connector(c, x_prev_right, y_h, y_b, x_col)
            next_centers.append(y_center)

        round_y_centers = next_centers

    # ── Match pour la 3e place ────────────────────────────────────────────────
    if draw_3e:
        x3 = x0
        c.setFillColor(_GRIS_TITRE_COL)
        c.setFont("Helvetica-Bold", fs)
        c.drawString(x3, y_3e_top, "Match pour la 3e place")
        y3 = y_3e_top - 0.2 * cm
        _draw_case_vide(c, x3, y3 - case_h, case_w, case_h, fs)
        _draw_case_vide(c, x3, y3 - 2 * case_h, case_w, case_h, fs)
        x3_res = x3 + case_w + conn_w
        _draw_connector(c, x3 + case_w, y3 - case_h / 2, y3 - 3 * case_h / 2, x3_res)
        _draw_case_vide(c, x3_res, y3 - 3 * case_h / 2, case_w, case_h, fs)


# ── Page d'instructions ───────────────────────────────────────────────────────


def _draw_page_instructions(
    c,
    titre_doc: str,
    bracket: dict,
    logo_data: dict | None,
    page_w: float,
    page_h: float,
    marge: float,
) -> None:
    """
    Dessine la page d'instructions (dernière page du document, paysage A4).

    Explique comment reporter les résultats des poules dans la 1re étape
    du tableau de phases finales.
    """
    q = bracket["q"]
    r = bracket["r"]
    p_poules = (q + r) // 2
    has_prelim = r > 0

    logo_h = (logo_data.get("logo_h_cm", 3.5) * cm) if logo_data else 0
    draw_logos(c, page_w, page_h, marge, logo_data)

    # ── En-tête ───────────────────────────────────────────────────────────────
    y = page_h - marge - logo_h - 0.2 * cm
    c.setFillColor(_GRIS_TITRE_COL)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(marge, y, titre_doc)

    y -= 0.65 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(marge, y, "Remplir la 1re étape — Résultats des poules")

    y -= 0.25 * cm
    c.setStrokeColor(_GRIS_TITRE_COL)
    c.setLineWidth(0.8)
    c.line(marge, y, page_w - marge, y)
    y -= 0.45 * cm

    # ── Texte d'instructions ──────────────────────────────────────────────────
    fs_corps = 10
    fs_num = 10
    line_h = 0.52 * cm
    indent = 0.6 * cm

    def _ligne(num: str, texte: str) -> None:
        nonlocal y
        c.setFillColor(_NOIR)
        if num:
            c.setFont("Helvetica-Bold", fs_num)
            c.drawString(marge, y, num)
        c.setFont("Helvetica", fs_corps)
        c.drawString(marge + indent, y, texte)
        y -= line_h

    def _ligne_suite(texte: str) -> None:
        nonlocal y
        c.setFont("Helvetica", fs_corps)
        c.setFillColor(_NOIR)
        c.drawString(marge + indent, y, texte)
        y -= line_h

    _ligne(
        "1.",
        "À la fin de la phase de poules, relever le classement de chaque poule"
        " (1er et 2e qualifiés).",
    )
    _ligne(
        "2.",
        "Chaque case colorée porte un label indiquant la poule et le rang :",
    )
    _ligne_suite("   A1 = 1er poule A   A2 = 2e poule A   B1 = 1er poule B   …")
    _ligne(
        "3.",
        "Dans chaque case colorée, écrire le nom de l'équipe correspondante.",
    )
    if has_prelim:
        _ligne(
            "4.",
            "Colonne « Prél. » : jouer les matches entre les deux cases colorées",
        )
        _ligne_suite(
            "   superposées, puis inscrire le gagnant dans la case vide à droite."
        )

    y -= 0.15 * cm

    # ── Légende des poules ────────────────────────────────────────────────────
    c.setFillColor(_GRIS_TITRE_COL)
    c.setFont("Helvetica-Bold", fs_corps)
    c.drawString(marge, y, "Correspondance des labels :")
    y -= 0.6 * cm  # espace suffisant sous le titre avant les cases

    # Deux colonnes : qualifiés 1re place à gauche, 2e place à droite
    col_w = (page_w - 2 * marge) / 2 - 0.3 * cm
    box_h = 0.55 * cm
    box_w = 0.8 * cm
    gap_text = 0.2 * cm
    row_h = box_h + 0.25 * cm

    y_legend_start = y
    for p in range(1, p_poules + 1):
        letter = NOMS_POULES[p]
        coul = COULEURS.get(p, _NOIR)
        row = p - 1

        for rank, col_off in ((1, 0), (2, col_w + 0.3 * cm)):
            label = f"{letter}{rank}"
            xi = marge + col_off
            # yi est le bas de la case (les cases descendent depuis y_legend_start)
            yi = y_legend_start - row * row_h - box_h

            # Case colorée miniature
            c.setFillColor(coul)
            c.setStrokeColor(_NOIR)
            c.setLineWidth(0.4)
            c.rect(xi, yi, box_w, box_h, fill=True, stroke=True)
            c.setFillColor(_BLANC)
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(xi + box_w / 2, yi + box_h / 2 - 8 * 0.38, label)

            # Description
            desc = (
                f"{rank}er de la poule {letter}"
                if rank == 1
                else f"2e de la poule {letter}"
            )
            c.setFillColor(_NOIR)
            c.setFont("Helvetica", 9)
            c.drawString(xi + box_w + gap_text, yi + box_h / 2 - 9 * 0.38, desc)


# ── Génération d'un PDF ───────────────────────────────────────────────────────


def generer(
    titre: str,
    bracket: dict,
    sortie: Path,
    logo_data: dict | None,
) -> Path:
    """
    Génère la feuille de phases finales pour le bracket donné.

    Toutes les pages sont en format A4 paysage. Si la hauteur de case descend
    sous MIN_CASE_H, produit 2 pages A4 paysage (montage côte à côte = A3 paysage).
    Une page d'instructions est ajoutée en dernière position.
    """
    sortie.parent.mkdir(parents=True, exist_ok=True)

    q = bracket["q"]
    r = bracket["r"]
    n_bracket = q + r  # hauteur du bracket en nombre de cases (= 2 × p_poules)
    has_prelim = r > 0
    n_rounds = int(math.log2(q))
    # Colonnes : [Prél.] + round1 + round2 + … + Gagnant
    n_cols = n_rounds + 1 + (1 if has_prelim else 0)

    marge = 1.0 * cm
    logo_h = (logo_data.get("logo_h_cm", 3.5) * cm) if logo_data else 0
    titre_h = 1.3 * cm

    pw_l, ph_l = landscape(A4)

    def _compute_widths(page_w: float) -> tuple[float, float]:
        zone_w = page_w - 2 * marge
        coeff = n_cols + 0.22 * (n_cols - 1)
        cw = zone_w / coeff
        return cw, cw * 0.22

    # Hauteur disponible depuis le haut de la zone de cases jusqu'à la marge basse.
    # Elle est partagée entre (n_bracket + 2) cases de hauteur case_h :
    #   n_bracket cases du bracket principal + 2 cases du match pour la 3e place.
    # L'overhead fixe est _OVERHEAD_LAYOUT = 0.4 cm (gap en-tête) +
    #   0.3 cm (gap bracket-3e) + 0.2 cm (gap titre 3e).
    y_top_l = ph_l - marge - logo_h - titre_h
    case_h_l = (y_top_l - marge - _OVERHEAD_LAYOUT) / (n_bracket + 2)
    y0_l = y_top_l - 0.4 * cm
    y_3e_top_l = y0_l - n_bracket * case_h_l - 0.3 * cm

    if case_h_l >= MIN_CASE_H:
        # ── Mode A4 paysage (1 page) ──────────────────────────────────────────
        case_w, conn_w = _compute_widths(pw_l)
        fs = 8 if case_h_l >= 10 * mm else 7

        c = rl_canvas.Canvas(str(sortie), pagesize=(pw_l, ph_l))
        c.setTitle(titre)
        c.setFillColor(_GRIS_TITRE_COL)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(marge, ph_l - marge - 0.75 * cm, titre)
        draw_logos(c, pw_l, ph_l, marge, logo_data)

        _render_bracket(
            c,
            bracket,
            x0=marge,
            y_top=y_top_l,
            case_w=case_w,
            case_h=case_h_l,
            conn_w=conn_w,
            fs=fs,
            draw_3e=True,
            y_3e_top=y_3e_top_l,
        )

    else:
        # ── Mode A3 : 2 pages A4 paysage à assembler côte à côte ─────────────
        # Le bracket s'étend sur 2 largeurs de page ; chaque page en montre la moitié.
        case_h = max(MIN_CASE_H, case_h_l)
        case_w, conn_w = _compute_widths(2 * pw_l)  # bracket sur 2 pages
        y_3e_top_a3 = y0_l - n_bracket * case_h - 0.3 * cm
        fs = 7

        c = rl_canvas.Canvas(str(sortie), pagesize=(pw_l, ph_l))
        c.setTitle(titre)

        for page_idx in range(2):
            sous_titre = f"{titre}  (feuille {page_idx + 1}/2)"
            c.setFillColor(_GRIS_TITRE_COL)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(marge, ph_l - marge - 0.75 * cm, sous_titre)
            if page_idx == 0:
                draw_logos(c, pw_l, ph_l, marge, logo_data)

            # Décalage horizontal : page 2 décale d'une largeur de page entière
            x_offset = -page_idx * pw_l
            _render_bracket(
                c,
                bracket,
                x0=marge + x_offset,
                y_top=y_top_l,
                case_w=case_w,
                case_h=case_h,
                conn_w=conn_w,
                fs=fs,
                draw_3e=(page_idx == 1),
                y_3e_top=y_3e_top_a3,
            )
            if page_idx == 0:
                c.showPage()

    # ── Page d'instructions (dernière page) ───────────────────────────────────
    c.showPage()
    _draw_page_instructions(c, titre, bracket, logo_data, pw_l, ph_l, marge)
    c.save()

    return sortie.resolve()


# ── Formatage des groupes de N ────────────────────────────────────────────────


def _format_ns_fichier(ns: list[int]) -> str:
    """Formate la liste de N pour le nom de fichier."""
    if len(ns) == 1:
        return f"{ns[0]:02d}"
    if all(ns[i] + 1 == ns[i + 1] for i in range(len(ns) - 1)):
        return f"{ns[0]:02d}-{ns[-1]:02d}"
    return "_".join(f"{n:02d}" for n in ns)


def _format_ns_titre(ns: list[int]) -> str:
    """Formate la liste de N pour le titre du document."""
    if len(ns) == 1:
        return f"{ns[0]} équipe{'s' if ns[0] > 1 else ''}"
    if all(ns[i] + 1 == ns[i + 1] for i in range(len(ns) - 1)):
        return f"{ns[0]}–{ns[-1]} équipes"
    return ", ".join(str(n) for n in ns[:-1]) + f" ou {ns[-1]} équipes"


# ── Génération de l'ensemble des feuilles ─────────────────────────────────────


def generer_toutes_finales(
    teams_min: int,
    teams_max: int,
    pool_base: int,
    output: Path,
    logo_data: dict | None,
) -> list[Path]:
    """
    Génère une feuille de phases finales par groupe de N partageant le même P.

    Deux valeurs de N produisent un document identique si et seulement si leur
    répartition en poules donne le même nombre de poules P.
    """
    output.mkdir(parents=True, exist_ok=True)

    # Grouper les N par nombre de poules P
    groups: dict[int, list[int]] = defaultdict(list)
    for n in range(teams_min, teams_max + 1):
        tailles = repartition_poules(n, pool_base)
        p = len(tailles)
        if p >= 2:
            groups[p].append(n)

    generated: list[Path] = []
    for p_poules in sorted(groups.keys()):
        ns = groups[p_poules]
        bracket = placer_equipes_sans_bye(p_poules)
        r = bracket["r"]

        ns_fichier = _format_ns_fichier(ns)
        ns_titre = _format_ns_titre(ns)
        fname = f"finales_{ns_fichier}eq.pdf"
        titre = f"Phases finales — {ns_titre}"
        chemin = output / fname

        generer(titre, bracket, chemin, logo_data)

        etages = "2 étages pré-remplis" if r > 0 else "1 étage pré-rempli"
        info = f"{p_poules} poules, {2 * p_poules} qualifiés, {r} prélim., {etages}"
        if len(ns) > 1:
            info += f", N={ns}"
        print(f"  {chemin}  [{info}]")
        generated.append(chemin)

    return generated


# ── Chargement logo.yaml ──────────────────────────────────────────────────────


def _charger_logo_yaml(chemin: Path) -> dict | None:
    try:
        import yaml

        with open(chemin, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        import json

        with open(chemin, encoding="utf-8") as f:
            return json.load(f)


# ── Interface en ligne de commande ────────────────────────────────────────────


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Génère les feuilles de phases finales au format PDF.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemple :\n"
            "  python python/generate_phases_finales.py \\\n"
            "      --teams-min 6 --teams-max 32 --pool-base 4 \\\n"
            "      --output documents/ --logo-yaml logo.yaml\n"
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

    pdfs = generer_toutes_finales(
        teams_min=args.teams_min,
        teams_max=args.teams_max,
        pool_base=args.pool_base,
        output=args.output,
        logo_data=logo_data,
    )
    print(f"{len(pdfs)} feuille(s) générée(s) dans {args.output}/")


if __name__ == "__main__":
    main()
