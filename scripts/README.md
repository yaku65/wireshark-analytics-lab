# Scripts

Das hier ist der praktische Teil vom Lab. Die `docs/` beschreiben, wonach man in Wireshark manuell Ausschau halten wuerde (Filter, typische Paketmuster, Fehlerbilder) - die Scripts hier machen einen Teil davon automatisch, so wie es im Fazit (`docs/05_fazit.md`) als naechster Schritt angedacht war.

Kurz zur Ausgangslage: echte `.pcapng`-Mitschnitte gehoeren laut Repo-Beschreibung nicht ins Repo (Datenschutz, siehe `docs/02_setup_wireshark.md`). Deswegen gibt's `generate_sample_data.py`, das mir realistisch aussehende, aber komplett erfundene CSV-Daten baut. Wer einen echten Mitschnitt hat, kann stattdessen `parse_tshark_export.py` benutzen (dazu unten mehr).

## Kurz-Setup

Braucht nichts ausser Python selbst (getestet mit 3.10, sollte aber auch mit aelteren 3.x-Versionen laufen), keine externen Pakete noetig.

```bash
cd scripts
python generate_sample_data.py
python analyze_icmp.py
```

Oder alles auf einmal:

```bash
python run_all.py
```

## Was macht welches Script

### `common.py`

Kein eigenstaendiges Script, sondern nur ein paar Helferlein, die ich sonst in jeder Datei doppelt haette (CSV einlesen, Trennlinien fuers Terminal, Prozentrechnung ohne Division-durch-Null-Absturz). Wird von allen anderen Scripts importiert.

### `generate_sample_data.py`

Erzeugt vier CSV-Dateien in `data/`: `icmp_capture.csv`, `dns_capture.csv`, `http_capture.csv` und `tcp_events_capture.csv`. Die Werte sind von Hand konstruiert und orientieren sich an den Szenarien aus `docs/03_traffic_analyse.md` (Ping, DNS-Anfrage, HTTP-Request).

Damit die restlichen Scripts ueberhaupt was zu tun haben, sind ein paar "Stoerungen" eingebaut, quasi die Fehlerbilder aus `docs/04_fehlerdiagnose.md` als Testdaten:

- drei Pings ohne Antwort (Paketverlust)
- eine Domain mit Tippfehler -> NXDOMAIN
- eine Domain, die dreimal angefragt wird, aber nie antwortet (DNS-Server weg)
- eine Weiterleitung, ein 404, ein 500 und eine auffaellig langsame HTTP-Antwort
- eine TCP-Verbindung mit gehaeuften Retransmissions, eine mit hoher Latenz und eine, die per RST beendet wird

Standardmaessig mit festem Seed (`--seed 42`), damit die Ausgabe reproduzierbar bleibt. Mit `--seed 123` (oder jeder anderen Zahl) kriegt man andere Zufallswerte, falls man mal was anderes sehen will.

### `analyze_icmp.py`

Liest `icmp_capture.csv`, ordnet Echo Request und Echo Reply anhand von `identifier` + `seq` einander zu und berechnet daraus die RTT (Round-Trip-Time) pro Ping. Requests ohne passende Reply zaehlen als Paketverlust. Am Ende gibt's Min/Avg/Max-RTT und eine Liste der auffaellig langsamen Antworten (Schwellwert aktuell 300 ms, steht oben im Script als Konstante).

Das ist im Prinzip das, was man in Wireshark mit dem Filter `icmp` sieht, nur dass man die RTT nicht mehr von Hand aus der Paketliste ablesen muss.

### `analyze_dns.py`

Gleiches Prinzip fuer DNS: Anfrage und Antwort werden ueber die `transaction_id` zusammengefuehrt. Ausgewertet wird, wie viele Anfragen beantwortet wurden, welche Fehlercodes vorkamen (z. B. `NXDOMAIN`) und - das fand ich beim Bauen am interessantesten - welche Domains *mehrfach* angefragt wurden, ohne je eine Antwort zu kriegen. Eine einzelne unbeantwortete Anfrage ist meistens Zufall, drei identische Anfragen ohne Antwort deuten eher auf einen nicht erreichbaren DNS-Server hin. Entspricht dem Abschnitt "DNS-Probleme" in `docs/04_fehlerdiagnose.md`.

### `analyze_http.py`

Zaehlt Statuscodes (2xx/3xx/4xx/5xx), listet alle 4xx/5xx-Requests einzeln auf und markiert Anfragen, die laenger als ein Schwellwert gedauert haben. Der Schwellwert ist per `--threshold` einstellbar (Millisekunden, Standard 500):

```bash
python analyze_http.py --threshold 800
```

### `detect_issues.py`

Das ist quasi die Checkliste aus `docs/04_fehlerdiagnose.md` als Code. Liest `tcp_events_capture.csv` und sucht nach den vier dort beschriebenen Mustern:

| Muster | Wireshark-Filter | was das Script macht |
| --- | --- | --- |
| Retransmissions | `tcp.analysis.retransmission` | zaehlt sie pro Verbindung, markiert Verbindungen mit 3+ als auffaellig |
| Duplicate ACKs | `tcp.analysis.duplicate_ack` | zaehlt sie |
| Hohe Latenz | `tcp.time_delta > 0.5` | listet alle Pakete mit zu grossem Zeitabstand |
| Verbindungsabbruch | `tcp.flags.reset == 1` | listet alle RST-Pakete mit betroffener Verbindung |

Am Ende gibt's noch eine kleine Einordnung, ob die Auffaelligkeiten nur eine einzelne Gegenstelle betreffen (eher lokales Problem bei dem einen Server) oder mehrere (eher ein generelleres Problem im eigenen Netzwerkpfad) - angelehnt an die erste Frage der Checkliste in `docs/04_fehlerdiagnose.md`.

### `run_all.py`

Fuehrt alle Scripts der Reihe nach aus. Praktisch zum Vorfuehren, ohne dass man fuenfmal `python irgendwas.py` tippen muss. Mit `--regenerate` werden die Beispieldaten vorher neu erzeugt, sonst werden vorhandene `data/*.csv` weiterverwendet.

### `parse_tshark_export.py` (optional)

Falls jemand das Ganze nicht nur mit den erfundenen Beispieldaten, sondern mit einem echten (selbst aufgezeichneten!) Mitschnitt ausprobieren moechte: dieses Script wandelt einen `tshark -T json`-Export in genau das CSV-Format um, das die Analyse-Scripts erwarten.

```bash
tshark -r meine_aufzeichnung.pcapng -Y icmp -T json > icmp_export.json
python parse_tshark_export.py icmp icmp_export.json
```

Genauso mit `-Y dns`, `-Y http` bzw. `-Y tcp` fuer die anderen drei Dateien. Ich hab das nur gegen die tshark-Feldnamen aus der Doku gebaut, nicht gegen einen echten Mitschnitt getestet (siehe Datenschutz-Hinweis oben) - je nach tshark-Version koennen einzelne Feldnamen leicht abweichen, dann muss man in `get_field()` nachjustieren.

## Warum CSV und nicht z. B. pandas / eine Datenbank

Kurz ueberlegt, dann dagegen entschieden: fuer die Datenmengen hier (ein paar Dutzend Zeilen pro Datei) reicht die eingebaute `csv`-Bibliothek locker, und man muss sich vorher nichts installieren, um das Repo auszuprobieren. Falls das Lab mal auf echte, groessere Mitschnitte skaliert werden soll, waere `pandas` oder direkt `pyshark` der naheliegende naechste Schritt (siehe auch Ausblick in `docs/05_fazit.md`).

## Bekannte Einschraenkungen

- Alle Beispieldaten sind erfunden, keine echten Mitschnitte (Absicht, siehe oben).
- `parse_tshark_export.py` ist ungetestet gegen echte Exports.
- Die Schwellwerte (Latenz, langsame HTTP-Antworten) sind fest im Code bzw. per Argument einstellbar, aber nicht aus einer Config-Datei ladbar. Fuer den Umfang des Labs war mir das nicht wichtig genug.
