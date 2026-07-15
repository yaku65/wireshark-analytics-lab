# 2. Setup von Wireshark

## Voraussetzungen

Bevor Wireshark sinnvoll genutzt werden kann, sollten folgende Punkte geklärt sein:

- Administrator- bzw. Root-Rechte für die Installation des Capture-Treibers
- Ein Netzwerkinterface, das tatsächlich Verkehr sieht (Ethernet oder WLAN)
- Auf Linux: Mitgliedschaft in der Gruppe `wireshark`, damit `dumpcap` ohne dauerhafte Root-Rechte laufen kann

## Installation

### Windows

1. Installer von der offiziellen Wireshark-Seite herunterladen.
2. Bei der Installation die Option **Npcap** aktivieren, da dies der zugrunde liegende Capture-Treiber ist.
3. Optional: **USBPcap** installieren, falls USB-Verkehr analysiert werden soll (für dieses Lab nicht erforderlich).

### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install wireshark
sudo usermod -aG wireshark $USER
```

Nach dem Hinzufügen zur Gruppe ist ein Neustart der Sitzung notwendig, damit die Gruppenmitgliedschaft wirksam wird.

### macOS

Installation über Homebrew:

```bash
brew install --cask wireshark
```

## Erste Schritte nach der Installation

1. Wireshark starten, es erscheint die Startseite mit einer Liste verfügbarer Schnittstellen.
2. Die Schnittstelle mit sichtbarer Verkehrsaktivität auswählen (kleine Graphen neben jedem Interface-Namen).
3. Mit einem Doppelklick auf die Schnittstelle die Aufzeichnung starten.
4. Über **Capture → Stop** oder das rote Quadrat in der Symbolleiste die Aufzeichnung beenden.

## Aufbau der Benutzeroberfläche

Wireshark gliedert sich in drei zentrale Bereiche:

| Bereich | Inhalt |
| --- | --- |
| **Packet List** | Chronologische Liste aller aufgezeichneten Pakete mit Zeitstempel, Quelle, Ziel und Protokoll |
| **Packet Details** | Baumartige Aufschlüsselung eines ausgewählten Pakets nach OSI-Schichten |
| **Packet Bytes** | Rohdarstellung des Pakets in Hexadezimal- und ASCII-Form |

## Capture-Filter vs. Display-Filter

Ein häufiger Anfängerfehler ist, beide Filterarten zu verwechseln:

- **Capture-Filter** werden vor dem Start der Aufzeichnung gesetzt und bestimmen, welche Pakete überhaupt mitgeschnitten werden (Syntax basiert auf `libpcap`, z. B. `host 192.168.0.1`).
- **Display-Filter** wirken nachträglich auf bereits aufgezeichnete Pakete und blenden nur bestimmte Einträge in der Packet List ein oder aus (z. B. `dns`, `http.response.code == 404`).

Für die Beispiele in diesem Lab werden ausschließlich Display-Filter verwendet, da diese für die nachträgliche Analyse besser geeignet sind.

## Nützliche Display-Filter für den Einstieg

```text
icmp                        # nur ICMP-Verkehr (Ping)
dns                         # nur DNS-Anfragen und -Antworten
http                        # nur HTTP-Verkehr
tcp.analysis.retransmission # erkannte TCP-Retransmissions
ip.addr == 192.168.0.10     # Verkehr von/zu einer bestimmten Adresse
```

Genau diese Filter tauchen in Kapitel 3 und 4 wieder auf – und liegen auch den Python-Scripts in [`scripts/`](../scripts) zugrunde, nur eben automatisiert statt manuell in der Packet List angeschaut.

## Von der Aufzeichnung zu tshark und weiter zu Python

`tshark` ist das Kommandozeilen-Pendant zu Wireshark und kann Mitschnitte unter anderem als JSON exportieren:

```bash
tshark -r aufzeichnung.pcapng -Y icmp -T json > icmp_export.json
```

Dieses JSON lässt sich mit [`scripts/parse_tshark_export.py`](../scripts/parse_tshark_export.py) in das CSV-Format umwandeln, das die Analyse-Scripts in diesem Repo erwarten. Für dieses Lab reicht das nur als Bonus-Pfad, standardmäßig arbeiten die Scripts mit generierten Beispieldaten (siehe [`scripts/README.md`](../scripts/README.md)).

## Hinweise zu Datenschutz und Ethik

Da Wireshark sämtlichen sichtbaren Verkehr eines Interfaces mitschneiden kann, gilt für dieses Lab ausnahmslos:

- Es wird ausschließlich in isolierten Testumgebungen oder mit selbst erzeugtem Testverkehr gearbeitet.
- Es werden keine Mitschnitte aus produktiven oder fremden Netzwerken verwendet.
- Aufzeichnungen (`.pcapng`-Dateien) werden nicht im Repository abgelegt. Das Gleiche gilt für `tshark`-JSON-Exports aus echten Mitschnitten, falls jemand `parse_tshark_export.py` mit eigenen Daten ausprobiert.

Im nächsten Kapitel werden anhand von Beispiel-Szenarien typische Protokolle (ICMP, DNS, HTTP) analysiert.
