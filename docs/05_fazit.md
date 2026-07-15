# 5. Fazit

## Zusammenfassung

Dieses Lab hat den Weg von der Installation von Wireshark bis zur systematischen Fehlerdiagnose anhand von Beispielszenarien nachvollzogen. Dabei wurden folgende Kernpunkte behandelt:

- Grundlegende Einrichtung von Wireshark unter Windows, Linux und macOS
- Der Unterschied zwischen Capture- und Display-Filtern
- Aufbau und Interpretation von ICMP-, DNS- und HTTP-Paketen
- Ein strukturiertes, am OSI-Modell orientiertes Vorgehen zur Eingrenzung von Netzwerkstörungen
- Automatisierte Auswertung von Beispieldaten mit Python (`scripts/`), inklusive einem optionalen Weg über `tshark`-JSON-Exports für echte Mitschnitte

## Lernerfahrungen

Im Verlauf des Labs wurde deutlich, dass die größte Herausforderung selten das reine Auslesen einzelner Paketfelder ist, sondern das **Erkennen von Mustern über mehrere Pakete hinweg**. Ein einzelnes verlorenes Paket ist unauffällig, eine wiederkehrende Kette von Retransmissions über mehrere Sekunden dagegen ein klares Störungssignal. Diese Fähigkeit, von einzelnen Paketen auf ein Gesamtbild zu schließen, lässt sich nur durch praktisches Ausprobieren entwickeln, reines Lesen von Dokumentation reicht dafür nicht aus.

Das hat sich beim Schreiben der Scripts in `scripts/` nochmal bestätigt: die eigentliche Logik (Requests und Replies einander zuordnen, Retransmissions pro Verbindung zählen, unterscheiden zwischen "eine Domain hat einen Fehler" und "mehrere identische Anfragen bleiben unbeantwortet") ist am Ende genau das, was man vorher in Wireshark von Hand gemacht hat – nur eben als Code, der wiederholbar auf denselben Daten läuft.

Ein weiterer Punkt betrifft die Grenzen der Methode. Denn sobald Verkehr über TLS verschlüsselt ist, lassen sich mit Wireshark zwar weiterhin Metadaten wie IP-Adressen, Portnummern und Timing analysieren, die eigentlichen Inhalte bleiben jedoch verborgen. Für eine tiefere Analyse verschlüsselten Verkehrs wären weitergehende Verfahren nötig, etwa das kontrollierte Einspielen von Sitzungsschlüsseln in einer Testumgebung.

## Grenzen dieses Labs

- Es wurden ausschließlich konstruierte Beispielszenarien behandelt, keine Analyse realer, produktiver Netzwerke.
- Verschlüsselter Verkehr (TLS/HTTPS) wurde bewusst ausgeklammert.
- Die Python-Scripts arbeiten auf CSV-Beispieldaten bzw. optional auf `tshark`-JSON-Exports; eine direkte Anbindung an eine laufende Aufzeichnung (Live-Capture) gibt es nicht.
- Bei größeren, echten Mitschnitten würden die aktuell simplen CSV-Auswertungen an ihre Grenzen kommen – dafür wäre eher `pandas` oder direkt `pyshark` sinnvoll (siehe Ausblick).

## Ausblick

Als sinnvolle Erweiterung dieses Labs kämen folgende Themen in Frage:

- Analyse von TLS-Handshakes (ohne Entschlüsselung der Nutzdaten) zur Bewertung von Zertifikaten und Protokollversionen
- Umstieg von CSV-basierten Scripts auf `pyshark` oder direktes Parsen von `.pcapng`-Dateien, um auch mit echten, größeren Mitschnitten arbeiten zu können
- Vergleich von normalem Verkehr mit Beispielen für auffälliges Verhalten (z. B. Portscans) zur Sensibilisierung für sicherheitsrelevante Muster
- Einbindung in ein kleines Monitoring-Setup, um die gelernten Filter dauerhaft auf einer Testinfrastruktur anzuwenden, z. B. indem `scripts/detect_issues.py` regelmäßig gegen frische `tshark`-Exports läuft

## Persönliches Fazit

Für den Bereich IT-Sicherheit ist der Umgang mit Paketanalyse-Werkzeugen eine Grundfertigkeit, vergleichbar mit dem Lesen von Logdateien. Dieses Lab hat dafür eine praktische Grundlage geschaffen, auf der sich weitergehende Themen wie Intrusion Detection oder forensische Netzwerkanalyse aufbauen lassen. Die Python-Scripts waren für mich der Punkt, an dem aus der reinen Dokumentation etwas Anfassbares wurde – nicht nur beschreiben, was man in Wireshark sehen würde, sondern es tatsächlich (auf Beispieldaten) nachbauen.
