"""
analyze_icmp.py

Wertet icmp_capture.csv aus und macht im Prinzip von Hand das, was man in
Wireshark mit dem Filter `icmp` sehen und dann selbst zusammenzaehlen wuerde
(siehe docs/03_traffic_analyse.md, Abschnitt 3.1).

Was das Script macht:
  1. Echo Request und Echo Reply anhand von identifier+seq zusammensuchen
  2. daraus die Round-Trip-Time (RTT) je Ping berechnen
  3. Requests ohne Antwort als Paketverlust zaehlen
  4. kurze Statistik ausgeben (min/avg/max RTT, Verlustrate)

Aufruf einfach: python analyze_icmp.py
"""

import statistics

from common import load_csv, section, pct

# ab wann eine RTT als "auffaellig hoch" gilt (in Sekunden)
LATENCY_THRESHOLD = 0.3


def main() -> None:
    rows = load_csv("icmp_capture.csv")

    requests = {}
    replies = {}
    for row in rows:
        key = (row["identifier"], row["seq"])
        t = float(row["timestamp"])
        if row["icmp_type"] == "8":
            requests[key] = t
        elif row["icmp_type"] == "0":
            replies[key] = t

    rtts = []
    lost = []
    high_latency = []

    for key, req_time in requests.items():
        if key in replies:
            rtt = replies[key] - req_time
            rtts.append(rtt)
            if rtt > LATENCY_THRESHOLD:
                high_latency.append((key[1], rtt))  # seq, rtt
        else:
            lost.append(key[1])  # nur die seq-Nummer merken

    section("ICMP / Ping-Auswertung")
    print(f"Anzahl Requests:        {len(requests)}")
    print(f"Beantwortet:            {len(rtts)}")
    print(f"Verloren (keine Reply): {len(lost)}  ({pct(len(lost), len(requests))})")

    if lost:
        print(f"  -> fehlende Antworten bei seq: {sorted(lost)}")

    if rtts:
        print(f"\nRTT min/avg/max: "
              f"{min(rtts)*1000:.1f} ms / "
              f"{statistics.mean(rtts)*1000:.1f} ms / "
              f"{max(rtts)*1000:.1f} ms")

    if high_latency:
        print(f"\nAuffaellig langsame Antworten (> {LATENCY_THRESHOLD*1000:.0f} ms):")
        for seq, rtt in high_latency:
            print(f"  seq={seq}: {rtt*1000:.1f} ms")

    # kleine Einordnung, angelehnt an docs/03_traffic_analyse.md
    print()
    if lost:
        print("Hinweis: fehlende Echo Replies koennen auf einen blockierenden "
              "Filter (Firewall) oder einen kurzzeitig nicht erreichbaren "
              "Host hindeuten.")
    if high_latency:
        print("Hinweis: einzelne stark erhoehte RTT-Werte sind meist kein "
              "Drama, treten sie aber gehaeuft auf, lohnt sich ein Blick auf "
              "die Route (traceroute) oder die Auslastung der Gegenstelle.")


if __name__ == "__main__":
    main()
