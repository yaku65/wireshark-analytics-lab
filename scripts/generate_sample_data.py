"""
generate_sample_data.py

Baut vier CSV-Dateien in data/, die so aussehen wie eine (stark vereinfachte)
Wireshark/tshark-Exportdatei fuer ICMP, DNS, HTTP und ein paar TCP-Events.

Warum keine echten .pcapng-Mitschnitte? Weil das Repo laut README bewusst
keine echten Netzwerkdaten enthaelt (siehe docs/02_setup_wireshark.md,
Abschnitt Datenschutz & Ethik). Die Werte hier sind von Hand konstruiert,
orientieren sich aber an den Szenarien aus docs/03_traffic_analyse.md und
docs/04_fehlerdiagnose.md - inklusive ein paar absichtlich eingebauten
"Stoerungen" (Paketverlust, NXDOMAIN, Retransmissions, RST, ...), damit die
Analyse-Scripts auch tatsaechlich was zu finden haben.

Mit --seed kann man andere Zufallswerte erzeugen, Standard ist ein fester
Seed, damit die Ausgabe reproduzierbar bleibt (gut fuer Screenshots in der
README oder falls man das Ganze nochmal vorfuehren muss).
"""

import argparse
import csv
import random
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

CLIENT_IP = "192.168.1.10"
GATEWAY_IP = "192.168.1.1"


def write_csv(filename: str, fieldnames: list[str], rows: list[dict]) -> None:
    path = DATA_DIR / filename
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  geschrieben: {path.relative_to(DATA_DIR.parent)}  ({len(rows)} Zeilen)")


def gen_icmp(rng: random.Random) -> list[dict]:
    """Simuliert 'ping 8.8.8.8', angelehnt an docs/03_traffic_analyse.md 3.1.

    Zwei Zeilen pro Ping (Request + Reply), bei drei Sequenznummern lasse
    ich die Reply absichtlich weg -> Paketverlust zum Ueben.
    """
    rows = []
    no = 1
    t = 0.0
    dropped_seqs = {6, 13, 17}  # hier "geht" die Antwort verloren
    for seq in range(1, 21):
        # Echo Request
        rows.append({
            "no": no, "timestamp": f"{t:.6f}", "src_ip": CLIENT_IP, "dst_ip": "8.8.8.8",
            "icmp_type": 8, "icmp_code": 0, "identifier": 1, "seq": seq, "ttl": 64,
        })
        no += 1

        if seq in dropped_seqs:
            t += 1.0  # Timeout, bevor der naechste Request rausgeht
            continue

        # RTT: meistens 20-70ms, einmal ein Ausreisser fuer die Latenz-Demo
        rtt = rng.uniform(0.020, 0.070)
        if seq == 10:
            rtt = 0.612  # deutlich zu langsam, soll spaeter auffallen
        t += rtt

        rows.append({
            "no": no, "timestamp": f"{t:.6f}", "src_ip": "8.8.8.8", "dst_ip": CLIENT_IP,
            "icmp_type": 0, "icmp_code": 0, "identifier": 1, "seq": seq, "ttl": 51,
        })
        no += 1
        t += rng.uniform(0.3, 0.6)  # Pause bis zum naechsten Ping

    return rows


def gen_dns(rng: random.Random) -> list[dict]:
    """Simuliert ein paar nslookup-Anfragen, angelehnt an docs/03 3.2.

    query_1 - query_10 sind normale Abfragen, dazwischen ein Tippfehler
    (NXDOMAIN) und eine Domain, deren DNS-Server offenbar nicht antwortet
    (3x dieselbe Anfrage, nie eine Response -> siehe docs/04, Abschnitt
    DNS-Probleme).
    """
    domains = [
        "example.com", "wikipedia.org", "github.com", "python.org",
        "duckduckgo.com", "wikipedia.org", "github.com",
    ]
    rows = []
    no = 1
    t = 0.0
    tid = 1000

    for domain in domains:
        rows.append({
            "no": no, "timestamp": f"{t:.6f}", "src_ip": CLIENT_IP, "dst_ip": "192.168.1.1",
            "transaction_id": tid, "is_response": 0, "query_name": domain,
            "query_type": "A", "response_code": "", "answer_rrs": "",
        })
        no += 1
        t += rng.uniform(0.01, 0.05)
        rows.append({
            "no": no, "timestamp": f"{t:.6f}", "src_ip": "192.168.1.1", "dst_ip": CLIENT_IP,
            "transaction_id": tid, "is_response": 1, "query_name": domain,
            "query_type": "A", "response_code": "NOERROR", "answer_rrs": 1,
        })
        no += 1
        t += rng.uniform(0.2, 0.5)
        tid += 1

    # Tippfehler in der Domain -> NXDOMAIN
    rows.append({
        "no": no, "timestamp": f"{t:.6f}", "src_ip": CLIENT_IP, "dst_ip": "192.168.1.1",
        "transaction_id": tid, "is_response": 0, "query_name": "examlpe.com",
        "query_type": "A", "response_code": "", "answer_rrs": "",
    })
    no += 1
    t += 0.02
    rows.append({
        "no": no, "timestamp": f"{t:.6f}", "src_ip": "192.168.1.1", "dst_ip": CLIENT_IP,
        "transaction_id": tid, "is_response": 1, "query_name": "examlpe.com",
        "query_type": "A", "response_code": "NXDOMAIN", "answer_rrs": 0,
    })
    no += 1
    t += 0.3
    tid += 1

    # DNS-Server antwortet nicht -> dreimal dieselbe Anfrage, keine Response
    for _ in range(3):
        rows.append({
            "no": no, "timestamp": f"{t:.6f}", "src_ip": CLIENT_IP, "dst_ip": "192.168.1.1",
            "transaction_id": tid, "is_response": 0, "query_name": "intranet.local",
            "query_type": "A", "response_code": "", "answer_rrs": "",
        })
        no += 1
        t += 2.0  # Client wartet und fragt nochmal
        tid += 1

    return rows


def gen_http(rng: random.Random) -> list[dict]:
    """Simuliert ein paar HTTP-Requests, angelehnt an docs/03 3.3.

    Eine Weiterleitung (301 -> 200), ein 404, ein 500 und eine auffaellig
    langsame Antwort sind absichtlich mit drin.
    """
    rows = []
    no = 1
    t = 0.0

    requests = [
        ("example.com", "/", 200, "text/html", rng.uniform(0.05, 0.2)),
        ("example.com", "/about", 200, "text/html", rng.uniform(0.05, 0.2)),
        ("example.com", "/old-page", 301, "text/html", rng.uniform(0.03, 0.1)),
        ("example.com", "/new-page", 200, "text/html", rng.uniform(0.05, 0.2)),
        ("example.com", "/style.css", 200, "text/css", rng.uniform(0.02, 0.08)),
        ("example.com", "/nicht-vorhanden", 404, "text/html", rng.uniform(0.03, 0.1)),
        ("api.example.com", "/v1/status", 200, "application/json", rng.uniform(0.05, 0.15)),
        ("api.example.com", "/v1/report", 500, "application/json", rng.uniform(0.1, 0.3)),
        ("example.com", "/bilder/banner.jpg", 200, "image/jpeg", 2.184),  # langsam
        ("example.com", "/kontakt", 200, "text/html", rng.uniform(0.05, 0.2)),
    ]

    for host, uri, status, ctype, resp_time in requests:
        method = "GET"
        rows.append({
            "no": no, "timestamp": f"{t:.6f}", "src_ip": CLIENT_IP, "dst_ip": "93.184.216.34",
            "method": method, "host": host, "uri": uri, "status_code": status,
            "content_type": ctype, "response_time_ms": round(resp_time * 1000, 1),
        })
        no += 1
        t += resp_time + rng.uniform(0.2, 1.0)

    return rows


def gen_tcp_events(rng: random.Random) -> list[dict]:
    """Simuliert ein paar TCP-Verbindungen mit den Mustern aus
    docs/04_fehlerdiagnose.md: Retransmissions, Duplicate ACKs, hohe
    time_delta-Werte (Latenz) und ein Verbindungsabbruch per RST.
    """
    rows = []
    no = 1
    t = 0.0

    def add(src, dst, sport, dport, flags, analysis="", delta=None):
        nonlocal no, t
        if delta is None:
            delta = rng.uniform(0.001, 0.05)
        t += delta
        rows.append({
            "no": no, "timestamp": f"{t:.6f}", "src_ip": src, "dst_ip": dst,
            "src_port": sport, "dst_port": dport, "flags": flags,
            "analysis": analysis, "time_delta": f"{delta:.6f}",
        })
        no += 1

    # Stream 1: ganz normale Verbindung, nix zu melden
    add(CLIENT_IP, "93.184.216.34", 51001, 443, "SYN")
    add("93.184.216.34", CLIENT_IP, 443, 51001, "SYN,ACK")
    add(CLIENT_IP, "93.184.216.34", 51001, 443, "ACK")
    add(CLIENT_IP, "93.184.216.34", 51001, 443, "PSH,ACK")
    add("93.184.216.34", CLIENT_IP, 443, 51001, "ACK")
    add("93.184.216.34", CLIENT_IP, 443, 51001, "FIN,ACK")
    add(CLIENT_IP, "93.184.216.34", 51001, 443, "ACK")

    # Stream 2: haeufige Retransmissions -> Paketverlust-Muster
    add(CLIENT_IP, "198.51.100.20", 51002, 443, "SYN")
    add("198.51.100.20", CLIENT_IP, 443, 51002, "SYN,ACK")
    add(CLIENT_IP, "198.51.100.20", 51002, 443, "ACK")
    add(CLIENT_IP, "198.51.100.20", 51002, 443, "PSH,ACK")
    for _ in range(5):
        add(CLIENT_IP, "198.51.100.20", 51002, 443, "PSH,ACK", analysis="retransmission",
            delta=rng.uniform(0.15, 0.4))
    add("198.51.100.20", CLIENT_IP, 443, 51002, "ACK", analysis="duplicate_ack")
    add("198.51.100.20", CLIENT_IP, 443, 51002, "ACK", analysis="duplicate_ack")
    add("198.51.100.20", CLIENT_IP, 443, 51002, "ACK", analysis="duplicate_ack")

    # Stream 3: hohe Latenz zwischendrin (time_delta > 0.5), sonst unauffaellig
    add(CLIENT_IP, "203.0.113.5", 51003, 443, "SYN")
    add("203.0.113.5", CLIENT_IP, 443, 51003, "SYN,ACK", delta=0.842)
    add(CLIENT_IP, "203.0.113.5", 51003, 443, "ACK")
    add(CLIENT_IP, "203.0.113.5", 51003, 443, "PSH,ACK")
    add("203.0.113.5", CLIENT_IP, 443, 51003, "ACK", delta=0.977)
    add("203.0.113.5", CLIENT_IP, 443, 51003, "FIN,ACK")
    add(CLIENT_IP, "203.0.113.5", 51003, 443, "ACK")

    # Stream 4: Verbindung wird per RST abgewuergt (z.B. Firewall)
    add(CLIENT_IP, "198.51.100.77", 51004, 8080, "SYN")
    add("198.51.100.77", CLIENT_IP, 8080, 51004, "SYN,ACK")
    add(CLIENT_IP, "198.51.100.77", 51004, 8080, "ACK")
    add(CLIENT_IP, "198.51.100.77", 51004, 8080, "PSH,ACK")
    add("198.51.100.77", CLIENT_IP, 8080, 51004, "RST")

    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Erzeugt Beispieldaten (CSV) fuer die Analyse-Scripts in diesem Ordner."
    )
    parser.add_argument("--seed", type=int, default=42,
                         help="Zufalls-Seed, Standard 42 fuer reproduzierbare Ergebnisse.")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    DATA_DIR.mkdir(exist_ok=True)

    print(f"Erzeuge Beispieldaten (seed={args.seed}) in {DATA_DIR}/ ...")

    write_csv(
        "icmp_capture.csv",
        ["no", "timestamp", "src_ip", "dst_ip", "icmp_type", "icmp_code", "identifier", "seq", "ttl"],
        gen_icmp(rng),
    )
    write_csv(
        "dns_capture.csv",
        ["no", "timestamp", "src_ip", "dst_ip", "transaction_id", "is_response",
         "query_name", "query_type", "response_code", "answer_rrs"],
        gen_dns(rng),
    )
    write_csv(
        "http_capture.csv",
        ["no", "timestamp", "src_ip", "dst_ip", "method", "host", "uri",
         "status_code", "content_type", "response_time_ms"],
        gen_http(rng),
    )
    write_csv(
        "tcp_events_capture.csv",
        ["no", "timestamp", "src_ip", "dst_ip", "src_port", "dst_port", "flags", "analysis", "time_delta"],
        gen_tcp_events(rng),
    )

    print("\nFertig. Die Analyse-Scripts (analyze_icmp.py, analyze_dns.py, "
          "analyze_http.py, detect_issues.py) koennen jetzt drauf losgelassen werden.")


if __name__ == "__main__":
    main()
