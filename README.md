# Wireshark Analytics Lab

Dieses Projekt dokumentiert den Ablauf einer beispielhaften **Netzwerküberwachung und Fehleranalyse** mit Wireshark und ergänzt das Ganze um Python-Scripts, die einen Teil dieser Analyse automatisieren.
Es zeigt, wie man typische Aufgaben aus dem IT-Support oder Netzwerkbetrieb analysieren könnte – **ohne echte Daten aufzuzeichnen**.

## Ziele

- Verständnis für den Aufbau und die Überwachung eines Netzwerks
- Beispielhafte Analyse von Netzwerkverkehr mit Wireshark
- Dokumentation typischer Fehlerbilder (z. B. Paketverlust, DNS-Probleme)
- Automatisierte Auswertung dieser Fehlerbilder mit Python, statt jedes Paket manuell durchzugehen

## Projektstruktur

| Pfad | Beschreibung |
| --- | --- |
| `docs/01_einleitung.md` | Überblick & Zielsetzung |
| `docs/02_setup_wireshark.md` | Installation & Grundlagen von Wireshark |
| `docs/03_traffic_analyse.md` | Beispielhafte Analysen (Ping, DNS, HTTP) |
| `docs/04_fehlerdiagnose.md` | Vorgehen bei Netzwerkstörungen |
| `docs/05_fazit.md` | Zusammenfassung & Lernerfahrungen |
| `scripts/` | Python-Scripts zur automatisierten Auswertung, siehe [scripts/README.md](scripts/README.md) |
| `data/` | Generierte CSV-Beispieldaten (Grundlage für die Scripts) |

## Schnellstart

```bash
cd scripts
python generate_sample_data.py   # erzeugt Beispieldaten in data/
python run_all.py                # oder: alles auf einmal
```

Details zu den einzelnen Scripts stehen in [scripts/README.md](scripts/README.md).

## Verwendete Tools

- **Wireshark / Tshark**
- **Ping / nslookup / tracert**
- **Python 3** (nur Standardbibliothek, keine externen Pakete nötig)
- **Markdown für Dokumentation**

---

> ⚠️ Hinweis: Dieses Repository enthält **keine echten Netzwerkdaten**. Sowohl die Dokumentation in `docs/` als auch die CSV-Dateien in `data/` sind konstruierte Beispiele und dienen ausschließlich zu Demonstrations- und Lernzwecken.
