"""
common.py

Ein paar Hilfsfunktionen, die ich in mehreren Scripts brauche (CSV einlesen,
Pfade zu den Beispieldaten finden, hübsche Trennlinien fürs Terminal).
Damit ich das nicht in jedem Script neu schreiben muss.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

# data/ liegt eine Ebene über scripts/, also von hier aus einfach hochgehen
SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"


def load_csv(filename: str) -> list[dict]:
    """Liest eine CSV-Datei aus data/ ein und gibt eine Liste von dicts zurück.

    Ist die Datei nicht da, breche ich mit einer verständlichen Fehlermeldung
    ab, anstatt einen hässlichen Python-Traceback zu zeigen. Meistens heißt
    das einfach, dass man vorher generate_sample_data.py laufen lassen muss.
    """
    path = DATA_DIR / filename
    if not path.exists():
        print(f"[Fehler] {path} existiert nicht.")
        print("Tipp: erst 'python generate_sample_data.py' ausfuehren, "
              "damit ueberhaupt Beispieldaten da sind.")
        sys.exit(1)

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    return rows


def section(title: str) -> None:
    """Druckt eine Überschrift fürs Terminal. Nichts Besonderes, aber
    macht die Ausgabe der Reports deutlich lesbarer."""
    print()
    print(title)
    print("-" * len(title))


def pct(part: int, total: int) -> str:
    """Kleiner Helfer fuer Prozentwerte, damit ich nicht ueberall durch 0 teile."""
    if total == 0:
        return "0.0%"
    return f"{(part / total) * 100:.1f}%"
