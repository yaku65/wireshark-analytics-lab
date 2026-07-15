"""
analyze_http.py

Auswertung von http_capture.csv, angelehnt an docs/03_traffic_analyse.md 3.3.
Zeigt die Verteilung der Statuscodes und markiert:
  - 4xx / 5xx Antworten (Client- bzw. Serverfehler)
  - 3xx Weiterleitungen
  - ungewoehnlich langsame Antworten

Der Schwellwert fuer "langsam" laesst sich per --threshold anpassen, falls
die 500 ms Standardwert nicht passen (z.B. bei API-Traffic will man
vielleicht strenger sein).
"""

import argparse
from collections import Counter

from common import load_csv, section


def status_group(code: int) -> str:
    return f"{code // 100}xx"


def main() -> None:
    parser = argparse.ArgumentParser(description="Wertet die HTTP-Beispieldaten aus.")
    parser.add_argument("--threshold", type=float, default=500.0,
                         help="Schwellwert in ms, ab dem eine Antwort als langsam gilt (Standard: 500)")
    args = parser.parse_args()

    rows = load_csv("http_capture.csv")

    status_counts = Counter()
    group_counts = Counter()
    slow_requests = []
    error_requests = []

    for r in rows:
        status = int(r["status_code"])
        status_counts[status] += 1
        group_counts[status_group(status)] += 1

        resp_time = float(r["response_time_ms"])
        if resp_time >= args.threshold:
            slow_requests.append((r["host"] + r["uri"], resp_time))

        if status >= 400:
            error_requests.append((r["host"] + r["uri"], status))

    section("HTTP-Auswertung")
    print(f"Anzahl Requests: {len(rows)}")

    print("\nStatuscodes:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}x")

    print("\nGruppiert nach Klasse:")
    for group in ["2xx", "3xx", "4xx", "5xx"]:
        if group in group_counts:
            print(f"  {group}: {group_counts[group]}x")

    if error_requests:
        print(f"\nFehlerhafte Requests (4xx/5xx):")
        for url, status in error_requests:
            print(f"  {status}  {url}")

    if slow_requests:
        print(f"\nLangsame Requests (>= {args.threshold:.0f} ms):")
        for url, t in slow_requests:
            print(f"  {t:.0f} ms  {url}")

    print()
    if group_counts.get("3xx"):
        print("Hinweis: Weiterleitungen (3xx) verlaengern die gefuehlte "
              "Ladezeit, auch wenn jede einzelne Antwort fuer sich schnell ist.")
    if slow_requests:
        print("Hinweis: bei durchgehend langsamen Antworten lohnt sich ein "
              "Blick auf tcp.time_delta im zugehoerigen TCP-Stream "
              "(siehe detect_issues.py).")


if __name__ == "__main__":
    main()
