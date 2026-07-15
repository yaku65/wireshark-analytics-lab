"""
run_all.py

Fuehrt einfach alle Schritte hintereinander aus: erst Beispieldaten
erzeugen (falls noch nicht vorhanden oder --regenerate gesetzt ist), dann
alle vier Analyse-Scripts der Reihe nach. Praktisch, wenn man nicht jedes
Script einzeln von Hand starten will, z.B. beim Vorfuehren.

    python run_all.py            # nutzt vorhandene data/*.csv, generiert bei Bedarf
    python run_all.py --regenerate   # erzeugt die Beispieldaten neu
"""

import argparse
import runpy
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

STEPS = [
    "generate_sample_data.py",
    "analyze_icmp.py",
    "analyze_dns.py",
    "analyze_http.py",
    "detect_issues.py",
]


def data_exists() -> bool:
    required = ["icmp_capture.csv", "dns_capture.csv", "http_capture.csv", "tcp_events_capture.csv"]
    return all((DATA_DIR / f).exists() for f in required)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fuehrt alle Scripts nacheinander aus.")
    parser.add_argument("--regenerate", action="store_true",
                         help="Beispieldaten neu erzeugen, auch wenn schon welche da sind.")
    args = parser.parse_args()

    steps = STEPS.copy()
    if not args.regenerate and data_exists():
        print("Beispieldaten sind schon vorhanden, ueberspringe generate_sample_data.py "
              "(mit --regenerate kann man das erzwingen).\n")
        steps = steps[1:]

    for i, step in enumerate(steps, start=1):
        print("=" * 70)
        print(f"[{i}/{len(steps)}] {step}")
        print("=" * 70)
        # Argumente fuer den Unterschritt zuruecksetzen, sonst faengt sich
        # z.B. analyze_http.py unsere --regenerate-Flag ein
        old_argv = sys.argv
        sys.argv = [step]
        try:
            runpy.run_path(str(Path(__file__).resolve().parent / step), run_name="__main__")
        finally:
            sys.argv = old_argv
        print()


if __name__ == "__main__":
    main()
