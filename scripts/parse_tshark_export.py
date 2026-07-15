"""
parse_tshark_export.py

Bonus-Script, falls man das Ganze mal mit einem echten Mitschnitt statt den
generierten Beispieldaten ausprobieren will. Wandelt einen tshark-JSON-Export
in genau das CSV-Format um, das analyze_icmp.py / analyze_dns.py /
analyze_http.py / detect_issues.py erwarten.

Wichtig: es ist bewusst KEIN echter Mitschnitt im Repo, siehe Hinweis in
docs/02_setup_wireshark.md (Datenschutz & Ethik). Wer das selbst testen
will, braucht einen eigenen Mitschnitt aus einer eigenen/isolierten
Testumgebung.

So kommt man an die JSON-Exports (Beispiel fuer ICMP):

    tshark -r meine_aufzeichnung.pcapng -Y icmp -T json > icmp_export.json

...und entsprechend mit -Y dns / -Y http / -Y tcp fuer die anderen drei.
Danach:

    python parse_tshark_export.py icmp icmp_export.json
    python parse_tshark_export.py dns dns_export.json
    python parse_tshark_export.py http http_export.json
    python parse_tshark_export.py tcp tcp_export.json

Jeder Aufruf ueberschreibt die entsprechende Datei in data/.

Ich habe das nur gegen die tshark-Dokumentation gebaut und nicht gegen
einen echten Mitschnitt getestet (siehe oben, warum). Je nach
tshark-Version koennen sich Feldnamen leicht unterscheiden, dann muss man
in get_field() nachjustieren. Fuer den Zweck dieses Labs (Demo, kein
Produktivbetrieb) reicht das erstmal so.
"""

import argparse
import csv
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def get_field(layers: dict, key: str, default=""):
    """tshark packt jeden Feldwert in eine Liste, z.B. layers['ip.src'] == ['1.2.3.4'].
    Hier nehme ich einfach den ersten Wert, falls vorhanden."""
    value = layers.get(key)
    if not value:
        return default
    if isinstance(value, list):
        return value[0]
    return value


def load_packets(json_path: Path) -> list[dict]:
    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)
    # tshark -T json liefert eine Liste von Objekten mit "_source" -> "layers"
    return [pkt["_source"]["layers"] for pkt in data]


def convert_icmp(json_path: Path) -> None:
    packets = load_packets(json_path)
    rows = []
    for i, layers in enumerate(packets, start=1):
        rows.append({
            "no": i,
            "timestamp": get_field(layers, "frame.time_relative", "0"),
            "src_ip": get_field(layers, "ip.src"),
            "dst_ip": get_field(layers, "ip.dst"),
            "icmp_type": get_field(layers, "icmp.type"),
            "icmp_code": get_field(layers, "icmp.code"),
            "identifier": get_field(layers, "icmp.ident"),
            "seq": get_field(layers, "icmp.seq"),
            "ttl": get_field(layers, "ip.ttl"),
        })
    write_csv("icmp_capture.csv",
              ["no", "timestamp", "src_ip", "dst_ip", "icmp_type", "icmp_code", "identifier", "seq", "ttl"],
              rows)


def convert_dns(json_path: Path) -> None:
    packets = load_packets(json_path)
    rows = []
    for i, layers in enumerate(packets, start=1):
        is_response = get_field(layers, "dns.flags.response", "0")
        rows.append({
            "no": i,
            "timestamp": get_field(layers, "frame.time_relative", "0"),
            "src_ip": get_field(layers, "ip.src"),
            "dst_ip": get_field(layers, "ip.dst"),
            "transaction_id": get_field(layers, "dns.id"),
            "is_response": is_response,
            "query_name": get_field(layers, "dns.qry.name"),
            "query_type": get_field(layers, "dns.qry.type"),
            "response_code": get_field(layers, "dns.flags.rcode", ""),
            "answer_rrs": get_field(layers, "dns.count.answers", ""),
        })
    write_csv("dns_capture.csv",
              ["no", "timestamp", "src_ip", "dst_ip", "transaction_id", "is_response",
               "query_name", "query_type", "response_code", "answer_rrs"],
              rows)


def convert_http(json_path: Path) -> None:
    packets = load_packets(json_path)
    rows = []
    for i, layers in enumerate(packets, start=1):
        status = get_field(layers, "http.response.code", "")
        if not status:
            continue  # uns interessieren hier nur abgeschlossene Response-Zeilen
        rows.append({
            "no": i,
            "timestamp": get_field(layers, "frame.time_relative", "0"),
            "src_ip": get_field(layers, "ip.src"),
            "dst_ip": get_field(layers, "ip.dst"),
            "method": get_field(layers, "http.request.method", "GET"),
            "host": get_field(layers, "http.host"),
            "uri": get_field(layers, "http.request.uri", "/"),
            "status_code": status,
            "content_type": get_field(layers, "http.content_type"),
            # http.time ist Wiresharks eigene Request/Response-Zeitdifferenz in Sekunden
            "response_time_ms": round(float(get_field(layers, "http.time", "0")) * 1000, 1),
        })
    write_csv("http_capture.csv",
              ["no", "timestamp", "src_ip", "dst_ip", "method", "host", "uri",
               "status_code", "content_type", "response_time_ms"],
              rows)


def convert_tcp(json_path: Path) -> None:
    packets = load_packets(json_path)
    rows = []
    for i, layers in enumerate(packets, start=1):
        analysis = ""
        if get_field(layers, "tcp.analysis.retransmission"):
            analysis = "retransmission"
        elif get_field(layers, "tcp.analysis.duplicate_ack"):
            analysis = "duplicate_ack"

        rows.append({
            "no": i,
            "timestamp": get_field(layers, "frame.time_relative", "0"),
            "src_ip": get_field(layers, "ip.src"),
            "dst_ip": get_field(layers, "ip.dst"),
            "src_port": get_field(layers, "tcp.srcport"),
            "dst_port": get_field(layers, "tcp.dstport"),
            "flags": get_field(layers, "tcp.flags.str", ""),
            "analysis": analysis,
            "time_delta": get_field(layers, "tcp.time_delta", "0"),
        })
    write_csv("tcp_events_capture.csv",
              ["no", "timestamp", "src_ip", "dst_ip", "src_port", "dst_port", "flags", "analysis", "time_delta"],
              rows)


def write_csv(filename: str, fieldnames: list[str], rows: list[dict]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    path = DATA_DIR / filename
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"geschrieben: {path} ({len(rows)} Zeilen)")


CONVERTERS = {
    "icmp": convert_icmp,
    "dns": convert_dns,
    "http": convert_http,
    "tcp": convert_tcp,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("kind", choices=CONVERTERS.keys(), help="welches Protokoll der JSON-Export enthaelt")
    parser.add_argument("json_file", type=Path, help="Pfad zum tshark -T json Export")
    args = parser.parse_args()

    if not args.json_file.exists():
        print(f"[Fehler] {args.json_file} nicht gefunden.")
        return

    CONVERTERS[args.kind](args.json_file)


if __name__ == "__main__":
    main()
