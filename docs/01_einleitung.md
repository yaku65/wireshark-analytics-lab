# 1. Einleitung

## Motivation

Netzwerke sind die Grundlage nahezu jeder IT-Infrastruktur, gleichzeitig sind sie für viele Einsteiger eine Blackbox: Daten verschwinden in einem Kabel oder einer WLAN-Verbindung und kommen scheinbar von selbst wieder an. Wireshark macht diesen Prozess sichtbar. Dieses Projekt dokumentiert, wie man mit Wireshark und dem dazugehörigen Kommandozeilenwerkzeug `tshark` Netzwerkverkehr systematisch beobachten, einordnen und für die Fehlersuche nutzen kann.

## Zielsetzung

Ziel dieser Dokumentation ist es, den Ablauf einer beispielhaften Netzwerkanalyse mit Wireshark nachvollziehbar zu beschreiben. Diese Analyse dient als theoretisches Beispiel für Netzwerküberwachung, Fehlersuche und Sicherheitsbewertung und soll folgende Fragen beantworten:

- Wie richtet man Wireshark korrekt ein und wählt die passende Schnittstelle aus?
- Welche Informationen stecken in typischen Protokollen wie ICMP, DNS und HTTP?
- Wie erkennt man anhand von Paketmustern häufige Netzwerkstörungen?
- Welche Grenzen hat eine rein paketbasierte Analyse?
- Wie lässt sich ein Teil dieser Auswertung automatisieren, statt jedes Paket manuell durchzugehen?

Der letzte Punkt wird in `docs/05_fazit.md` als Ausblick genannt und im Ordner [`scripts/`](../scripts) tatsächlich umgesetzt: ein paar kleine Python-Scripts werten Beispieldaten aus, die an die Szenarien aus diesem Lab angelehnt sind.

## Abgrenzung

Dieses Lab ist bewusst als **Lernprojekt** angelegt und nicht als Produktionswerkzeug. Es werden ausschließlich Beispiel- und Demonstrationsszenarien beschrieben, es werden **keine echten, personenbezogenen Netzwerkdaten aufgezeichnet oder veröffentlicht**. Alle in `03_traffic_analyse.md` und `04_fehlerdiagnose.md` gezeigten Paketmuster sind didaktisch konstruiert, um typische Sachverhalte zu illustrieren. Das gilt auch für die CSV-Beispieldaten, mit denen die Scripts in `scripts/` arbeiten – diese werden von `scripts/generate_sample_data.py` erzeugt und enthalten ebenfalls keine echten Mitschnitte.

## Zielgruppe

Die Dokumentation richtet sich an Studierende und Einsteiger im Bereich IT-Sicherheit und Netzwerktechnik, die:

- ein grundlegendes Verständnis von TCP/IP mitbringen,
- erste praktische Erfahrung mit Paketanalyse sammeln möchten,
- oder sich auf Prüfungen bzw. Praktika mit Netzwerkbezug vorbereiten.

## Aufbau des Projekts

| Bereich | Inhalt |
| --- | --- |
| [`docs/02_setup_wireshark.md`](02_setup_wireshark.md) | Installation, Berechtigungen und erste Schritte in Wireshark |
| [`docs/03_traffic_analyse.md`](03_traffic_analyse.md) | Beispielhafte Analyse von Ping-, DNS- und HTTP-Verkehr |
| [`docs/04_fehlerdiagnose.md`](04_fehlerdiagnose.md) | Systematisches Vorgehen bei typischen Netzwerkstörungen |
| [`docs/05_fazit.md`](05_fazit.md) | Zusammenfassung, Lernerfahrungen und Ausblick |
| [`scripts/`](../scripts) | Python-Scripts, die Teile der Analyse aus Kapitel 3 und 4 automatisieren (eigene [README](../scripts/README.md)) |
| [`data/`](../data) | Generierte Beispieldaten (CSV), Grundlage für die Scripts |

## Verwendete Umgebung

Die Beispiele in dieser Dokumentation wurden mit folgender Testumgebung konzipiert:

- **Betriebssystem:** Windows 11 bzw. Linux (Ubuntu) als gleichwertige Alternativen
- **Wireshark-Version:** aktuelle Stable-Version aus dem offiziellen Download-Bereich
- **Zusatzwerkzeuge:** `ping`, `nslookup`/`dig`, `tracert`/`traceroute`
- **Für die Scripts:** Python 3.10+, keine externen Pakete nötig (nur Standardbibliothek)

Im nächsten Kapitel folgt die Installation und Grundkonfiguration von Wireshark.
