"""
detect_issues.py

Das hier ist im Grunde die Checkliste aus docs/04_fehlerdiagnose.md als
Code: es liest tcp_events_capture.csv und sucht nach genau den vier
Mustern, die dort beschrieben sind.

  - Retransmissions        -> tcp.analysis.retransmission
  - Duplicate ACKs         -> tcp.analysis.duplicate_ack
  - hohe Zeitabstaende      -> tcp.time_delta > 0.5
  - erzwungene Abbrueche    -> tcp.flags.reset == 1

Ich haette das genauso gut in analyze_icmp/dns/http mit reinpacken koennen,
aber dann waere das Script ziemlich unuebersichtlich geworden. Getrennt
nach Protokoll ist es leichter nachzuvollziehen, welcher Filter zu welchem
Befund gehoert.
"""

from collections import defaultdict

from common import load_csv, section

LATENCY_THRESHOLD = 0.5  # Sekunden, siehe docs/04_fehlerdiagnose.md


def main() -> None:
    rows = load_csv("tcp_events_capture.csv")

    retransmissions = [r for r in rows if r["analysis"] == "retransmission"]
    duplicate_acks = [r for r in rows if r["analysis"] == "duplicate_ack"]
    resets = [r for r in rows if "RST" in r["flags"]]
    high_latency = [r for r in rows if float(r["time_delta"]) > LATENCY_THRESHOLD]

    section("Fehlerdiagnose (TCP-Events)")

    print(f"Retransmissions:  {len(retransmissions)}")
    print(f"Duplicate ACKs:   {len(duplicate_acks)}")
    print(f"RST-Pakete:       {len(resets)}")
    print(f"Hohe Latenz (>{LATENCY_THRESHOLD}s): {len(high_latency)}")

    # Retransmissions nach Verbindung gruppieren, das war fuer mich der
    # interessanteste Teil: ein einzelnes verlorenes Paket ist normal,
    # eine ganze Kette auf derselben Verbindung nicht (siehe docs/05_fazit.md,
    # Abschnitt Lernerfahrungen).
    if retransmissions:
        by_stream = defaultdict(int)
        for r in retransmissions:
            stream = f"{r['src_ip']}:{r['src_port']} -> {r['dst_ip']}:{r['dst_port']}"
            by_stream[stream] += 1

        print("\nRetransmissions pro Verbindung:")
        for stream, count in by_stream.items():
            note = "  <- gehaeuft, sieht nach Paketverlust aus" if count >= 3 else ""
            print(f"  {stream}: {count}x{note}")

    if resets:
        print("\nVerbindungen mit RST:")
        for r in resets:
            print(f"  {r['src_ip']}:{r['src_port']} -> {r['dst_ip']}:{r['dst_port']}  "
                  f"(t={r['timestamp']})")

    if high_latency:
        print(f"\nAuffaellige Zeitabstaende (> {LATENCY_THRESHOLD}s):")
        for r in high_latency:
            print(f"  {r['src_ip']}:{r['src_port']} -> {r['dst_ip']}:{r['dst_port']}  "
                  f"delta={float(r['time_delta']):.3f}s")

    # Kurzer Abgleich mit der Checkliste aus docs/04_fehlerdiagnose.md:
    # ist das Problem auf einen einzelnen Host beschraenkt oder netzwerkweit?
    affected_hosts = {r["dst_ip"] for r in retransmissions + resets + high_latency}
    section("Kurze Einordnung")
    if len(affected_hosts) == 0:
        print("Keine Auffaelligkeiten gefunden, Verbindungen sehen sauber aus.")
    elif len(affected_hosts) == 1:
        print(f"Auffaelligkeiten betreffen nur eine Gegenstelle ({next(iter(affected_hosts))}), "
              "eher kein grundsaetzliches Netzwerkproblem, sondern moeglicherweise "
              "ein Problem bei diesem einen Server/Pfad.")
    else:
        print(f"Auffaelligkeiten verteilen sich auf {len(affected_hosts)} verschiedene "
              "Gegenstellen, das kann auf ein allgemeineres Problem im eigenen "
              "Netzwerkpfad hindeuten (z.B. ueberlasteter Router, instabile Verbindung).")


if __name__ == "__main__":
    main()
