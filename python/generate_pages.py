#!/usr/bin/env python3
"""
Génère le site de documentation statique dans pages/.

Combine les spécifications (PBOULE.md), une section «Documents créés»
(liste des PDF avec liens) et le CHANGELOG.md en un unique index.html,
puis copie les PDF dans pages/.

Usage :
    python python/generate_pages.py
    python python/generate_pages.py --docs-dir documents/ --output-dir pages/
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

# ── Feuille de style ──────────────────────────────────────────────────────────

_CSS = """\
/* Pétanque — Documentation */
body {
    max-width: 960px;
    margin: 0 auto;
    padding: 1rem 2rem;
    font-family: system-ui, "Segoe UI", sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #333;
}
h1 {
    font-size: 1.8em;
    color: #1565C0;
    border-bottom: 2px solid #1565C0;
    padding-bottom: 0.3em;
}
h2 {
    font-size: 1.4em;
    color: #1565C0;
    border-bottom: 1px solid #BBDEFB;
    padding-bottom: 0.2em;
}
h3 { font-size: 1.1em; color: #1565C0; }
/* Conteneur TOC + logos côte à côte */
.toc-logos-wrapper {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 2rem;
    margin-bottom: 2rem;
}
#TOC {
    background: #F8F8F8;
    border: 1px solid #DDD;
    border-radius: 4px;
    padding: 0.8rem 1.5rem;
    display: inline-block;
    min-width: 280px;
    flex-shrink: 0;
}
/* Dans le wrapper, la marge basse du TOC est gérée par le conteneur */
.toc-logos-wrapper #TOC { margin-bottom: 0; }
/* TOC hors wrapper (si logos absents) */
#TOC:not(.toc-logos-wrapper #TOC) { margin-bottom: 2rem; }
#TOC ul { margin: 0.3em 0; padding-left: 1.5em; }
#TOC a { color: #1565C0; text-decoration: none; }
#TOC a:hover { text-decoration: underline; }
/* Bloc logos */
.logo-block { flex-shrink: 0; }
.logo-inner { position: relative; display: inline-block; }
.logo-main  { display: block; }
.logo-secondary {
    position: absolute;
    bottom: 0;
    left: 0;
}
table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
th {
    background: #1565C0;
    color: #FFF;
    padding: 0.5rem 0.8rem;
    text-align: left;
}
td { border: 1px solid #CCC; padding: 0.4rem 0.8rem; }
tr:nth-child(even) td { background: #F5F5F5; }
code {
    background: #F0F0F0;
    padding: 0.1em 0.35em;
    border-radius: 3px;
    font-size: 0.9em;
}
pre {
    background: #F0F0F0;
    padding: 1rem;
    border-radius: 4px;
    overflow-x: auto;
}
pre code { background: none; padding: 0; }
a { color: #1565C0; }
a:hover { color: #0D47A1; }
blockquote {
    border-left: 4px solid #BBDEFB;
    margin: 0;
    padding: 0.5rem 1rem;
    color: #555;
}
.pdf-link {
    display: inline-block;
    margin: 0.2rem 0.3rem;
    padding: 0.25rem 0.6rem;
    background: #E3F2FD;
    border: 1px solid #90CAF9;
    border-radius: 4px;
    text-decoration: none;
    font-size: 0.9em;
}
.pdf-link:hover { background: #BBDEFB; }
"""


# ── Logos ─────────────────────────────────────────────────────────────────────

_SCREEN_DPI = 96  # résolution écran de référence pour la conversion cm → px


def _load_logo_data(logo_yaml: Path | None) -> dict | None:
    """Charge les données des logos depuis logo.yaml."""
    if logo_yaml is None or not logo_yaml.exists():
        return None
    try:
        with open(logo_yaml, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _build_logo_html(logo_data: dict) -> str:
    """
    Génère le fragment HTML du bloc logos.

    Disposition identique aux PDF :
      • logo principal en taille pleine
      • logo secondaire superposé en bas à gauche, à 1/3 de la hauteur
    """
    logo_h_cm = logo_data.get("logo_h_cm", 3.5)
    logo_h_px = round(logo_h_cm / 2.54 * _SCREEN_DPI)
    pet_h_px = round(logo_h_px / 3)

    cof = logo_data.get("logo_main")
    pet = logo_data.get("logo_petanque")

    if not cof and not pet:
        return ""

    parts = ['<div class="logo-block"><div class="logo-inner">']

    if cof and cof.get("path"):
        fname = Path(cof["path"]).name
        parts.append(
            f'<img src="{fname}" class="logo-main"'
            f' style="height:{logo_h_px}px" alt="Logo COF Montlaur" />'
        )

    if pet and pet.get("path"):
        fname = Path(pet["path"]).name
        parts.append(
            f'<img src="{fname}" class="logo-secondary"'
            f' style="height:{pet_h_px}px" alt="Logo pétanque" />'
        )

    parts.append("</div></div>")
    return "\n".join(parts)


def _inject_logos(html_path: Path, logo_html: str) -> None:
    """
    Enveloppe le <nav id="TOC"> et le bloc logos dans un conteneur flex.

    Avant :  <nav id="TOC">…</nav>
    Après  : <div class="toc-logos-wrapper">
               <nav id="TOC">…</nav>
               <div class="logo-block">…</div>
             </div>
    """
    content = html_path.read_text(encoding="utf-8")
    toc_re = re.compile(r'(<nav id="TOC".*?</nav>)', re.DOTALL)

    def wrap(m: re.Match) -> str:
        return (
            '<div class="toc-logos-wrapper">\n'
            + m.group(1)
            + "\n"
            + logo_html
            + "\n</div>"
        )

    new_content, n = toc_re.subn(wrap, content, count=1)
    if n:
        html_path.write_text(new_content, encoding="utf-8")


# ── Section «Documents créés» ─────────────────────────────────────────────────


def _pdf_link(p: Path) -> str:
    return f'<a class="pdf-link" href="{p.name}">{p.name}</a>'


def _section_documents(docs_dir: Path) -> str:
    """Génère le markdown de la section «Documents créés»."""
    pdfs = sorted(p for p in docs_dir.glob("*.pdf") if p.name != "pboule.pdf")
    if not pdfs:
        return "# Documents créés\n\n*Aucun document disponible.*\n"

    parts: list[str] = [
        "# Documents créés",
        "",
        "Gabarits PDF disponibles en téléchargement pour cette version.",
        "",
    ]

    # Feuille d'inscription
    inscription = [p for p in pdfs if p.name.startswith("feuille_")]
    if inscription:
        parts += ["## Feuille d'inscription", ""]
        parts += [_pdf_link(p) for p in inscription]
        parts.append("")

    # Poules uniques (cas particuliers)
    uniques = sorted(p for p in pdfs if p.name.startswith("poule_unique_"))
    if uniques:
        parts += ["## Poules uniques (cas particuliers)", ""]
        parts += [_pdf_link(p) for p in uniques]
        parts.append("")

    # Feuilles de poule standard — groupées par taille
    standards = sorted(
        p
        for p in pdfs
        if p.name.startswith("poule_") and not p.name.startswith("poule_unique_")
    )
    if standards:
        parts += ["## Feuilles de poule", ""]
        sizes: dict[str, list[Path]] = {}
        for p in standards:
            tokens = p.stem.split("_")  # ["poule", "A", "04eq"]
            size = tokens[2] if len(tokens) >= 3 else "?"
            sizes.setdefault(size, []).append(p)
        for size, group in sorted(sizes.items()):
            n = int(size.replace("eq", ""))
            parts += [f"### {n} équipes", ""]
            parts += [_pdf_link(p) for p in group]
            parts.append("")

    return "\n".join(parts) + "\n"


# ── Générateur principal ──────────────────────────────────────────────────────


def generer(
    docs_dir: Path,
    output_dir: Path,
    pboule_md: Path,
    changelog_md: Path,
    logo_creation_md: Path | None = None,
    logo_yaml: Path | None = None,
) -> None:
    """Génère le site statique dans output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Feuille de style
    (output_dir / "style.css").write_text(_CSS, encoding="utf-8")

    # Section «Documents créés» → fichier temporaire
    docs_section = _section_documents(docs_dir)
    tmp_docs: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(docs_section)
            tmp_docs = Path(tmp.name)

        # Pandoc : PBOULE.md [+ logo-creation] + docs + CHANGELOG → index.html
        sources = [str(pboule_md)]
        if logo_creation_md is not None and logo_creation_md.exists():
            sources.append(str(logo_creation_md))
        sources += [str(tmp_docs), str(changelog_md)]

        cmd = [
            "pandoc",
            *sources,
            "--standalone",
            "--toc",
            "--toc-depth=3",
            "-t",
            "html5",
            "--metadata",
            "title=Compétition de Pétanque — Documentation",
            "--metadata",
            "lang=fr",
            "--css",
            "style.css",
            "-o",
            str(output_dir / "index.html"),
        ]
        subprocess.run(cmd, check=True)

    finally:
        if tmp_docs is not None:
            tmp_docs.unlink(missing_ok=True)

    # Logos : copie des fichiers image + injection dans index.html
    logo_data = _load_logo_data(logo_yaml)
    if logo_data:
        for key in ("logo_main", "logo_petanque"):
            info = logo_data.get(key)
            if info and info.get("path"):
                src = Path(info["path"])
                if src.exists():
                    shutil.copy2(src, output_dir / src.name)

        logo_html = _build_logo_html(logo_data)
        if logo_html:
            _inject_logos(output_dir / "index.html", logo_html)

    # Copie des PDF
    copied = 0
    for pdf in sorted(docs_dir.glob("*.pdf")):
        if pdf.name == "pboule.pdf":
            continue
        shutil.copy2(pdf, output_dir / pdf.name)
        copied += 1

    print(f"  → {output_dir / 'index.html'} ({copied} PDF copiés)")


# ── Interface en ligne de commande ────────────────────────────────────────────


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Génère le site de documentation statique dans pages/.",
    )
    ap.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("documents"),
        metavar="DIR",
        help="Dossier contenant les PDF (défaut : documents/)",
    )
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=Path("pages"),
        metavar="DIR",
        help="Dossier de sortie (défaut : pages/)",
    )
    ap.add_argument(
        "--pboule-md",
        type=Path,
        default=Path("PBOULE.md"),
        metavar="FILE",
        help="Fichier de spécifications (défaut : PBOULE.md)",
    )
    ap.add_argument(
        "--changelog",
        type=Path,
        default=Path("CHANGELOG.md"),
        metavar="FILE",
        help="Fichier de changelog (défaut : CHANGELOG.md)",
    )
    ap.add_argument(
        "--logo-creation-md",
        type=Path,
        default=None,
        metavar="FILE",
        help="Documentation de création du logo (optionnel)",
    )
    ap.add_argument(
        "--logo-yaml",
        type=Path,
        default=None,
        metavar="FILE",
        help="Cache des caractéristiques des logos, logo.yaml (optionnel)",
    )
    args = ap.parse_args()
    generer(
        args.docs_dir,
        args.output_dir,
        args.pboule_md,
        args.changelog,
        args.logo_creation_md,
        args.logo_yaml,
    )


if __name__ == "__main__":
    main()
