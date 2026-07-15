"""
analyze_dns.py

Auswertung von dns_capture.csv. Entspricht ungefaehr dem, was man in
Wireshark mit dem Filter `dns` bzw. `dns && dns.flags.rcode != 0` sehen
wuerde (docs/03_traffic_analyse.md 3.2 und docs/04_fehlerdiagnose.md,
Abschnitt DNS-Probleme).

Gesucht wird nach drei Dingen:
  - Anfragen mit Fehlercode (z.B. NXDOMAIN)
  - Anfragen, die nie beantwortet wurden
  - Domains, die mehrfach angefragt wurden, ohne je eine Antwort zu kriegen
    (typisches Zeichen fuer einen nicht erreichbaren DNS-Server)
"""

from collections import Counter

from common import load_csv, section, pct


def main() -> None:
    rows = load_csv("dns_capture.csv")

    queries = [r for r in rows if r["is_response"] == "0"]
    responses = {r["transaction_id"]: r for r in rows if r["is_response"] == "1"}

    answered = 0
    error_codes = Counter()
    unanswered_domains = Counter()

    for q in queries:
        resp = responses.get(q["transaction_id"])
        if resp is None:
            unanswered_domains[q["query_name"]] += 1
            continue

        answered += 1
        code = resp["response_code"]
        if code != "NOERROR":
            error_codes[code] += 1

    section("DNS-Auswertung")
    print(f"Anzahl Anfragen:     {len(queries)}")
    print(f"Beantwortet:         {answered}  ({pct(answered, len(queries))})")
    print(f"Ohne Antwort:        {len(queries) - answered}")

    if error_codes:
        print("\nFehlercodes in den Antworten:")
        for code, count in error_codes.most_common():
            print(f"  {code}: {count}x")

    if unanswered_domains:
        print("\nDomains ohne jegliche Antwort:")
        for domain, count in unanswered_domains.most_common():
            flag = "  <- mehrfach angefragt, DNS-Server evtl. nicht erreichbar" if count > 1 else ""
            print(f"  {domain}: {count}x{flag}")

    # kurze Einordnung
    print()
    if any(c > 1 for c in unanswered_domains.values()):
        print("Hinweis: wiederholte identische Anfragen ohne Antwort deuten "
              "eher auf einen nicht erreichbaren/blockierten DNS-Server hin "
              "als auf eine einzelne falsche Domain.")
    if "NXDOMAIN" in error_codes:
        print("Hinweis: NXDOMAIN heisst meistens Tippfehler in der Domain, "
              "seltener eine tatsaechlich abgelaufene/geloeschte Domain.")


if __name__ == "__main__":
    main()
