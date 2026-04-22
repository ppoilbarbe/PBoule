"""Domaine pétanque : répartition des équipes en poules, couleurs et noms."""

from __future__ import annotations

from reportlab.lib import colors

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


def repartition_poules(n_total: int, base: int = 4) -> list[int]:
    """
    Répartit n_total équipes en poules de taille `base` ou `base+1`.

    Priorités (de haut en bas) :
      1. Distribution uniforme en poules de base si N divisible par base.
      2. Distribution uniforme en poules de (base+1) si N divisible par base+1.
      3. Distribution mixte : poules de base en tête, surplus de (base+1) en fin.
    """
    if n_total % base == 0:
        return [base] * (n_total // base)
    if n_total % (base + 1) == 0:
        return [base + 1] * (n_total // (base + 1))
    for n_poules in range(max(1, n_total // (base + 1)), n_total + 1):
        x = n_total - n_poules * base
        y = n_poules - x
        if 0 <= x <= n_poules and y >= 0:
            return [base] * y + [base + 1] * x
    n_poules = max(1, n_total // base)
    reste = n_total - n_poules * base
    return [base] * n_poules + ([reste] if reste else [])
