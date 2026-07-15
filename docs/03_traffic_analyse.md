# 3. Beispielhafte Traffic-Analyse

In diesem Kapitel werden drei grundlegende Protokolle anhand konstruierter Beispielszenarien erläutert: ICMP (Ping), DNS und HTTP. Die gezeigten Werte sind exemplarisch und dienen der Veranschaulichung typischer Paketmuster, nicht der Auswertung echter Mitschnitte. Zu jedem Abschnitt gibt es im Ordner [`scripts/`](../scripts) ein passendes Python-Script, das dieselbe Auswertung auf Beispieldaten automatisiert durchführt.

## 3.1 ICMP / Ping-Analyse

### Szenario

Ein einfacher Ping von einem Client zu einem Zielhost soll zeigen, wie Anfrage und Antwort auf Netzwerkebene aussehen.

```bash
ping 8.8.8.8
```

### Relevanter Filter

```text
icmp
```

### Typische Paketstruktur

| Feld | Beschreibung |
| --- | --- |
| `Type 8 / Code 0` | Echo Request (Anfrage vom Client) |
| `Type 0 / Code 0` | Echo Reply (Antwort vom Zielhost) |
| `Identifier` | Kennung, um Anfragen und Antworten einander zuzuordnen |
| `Sequence Number` | Laufende Nummer innerhalb einer Ping-Sequenz |
| `TTL` | Time to Live, sinkt mit jedem durchlaufenen Router |

### Was man daraus lernen kann

- Eine fehlende Echo Reply bei vorhandenem Echo Request deutet auf einen blockierenden Filter (Firewall) oder einen nicht erreichbaren Host hin.
- Die Differenz der Zeitstempel zwischen Request und Reply ergibt die Round-Trip-Time (RTT), ein einfacher Indikator für Latenz.
- Ein auffällig niedriger TTL-Wert in der Antwort kann auf viele Zwischenstationen (Hops) hindeuten.

### Automatisiert mit Python

[`scripts/analyze_icmp.py`](../scripts/analyze_icmp.py) ordnet Request und Reply anhand von `Identifier` und `Sequence Number` einander zu, berechnet die RTT je Ping und zählt Requests ohne Antwort als Paketverlust – also genau das, was man hier von Hand in der Packet List nachvollziehen würde.

## 3.2 DNS-Analyse

### Szenario

Der Client löst einen Domainnamen auf, bevor eine Verbindung zum eigentlichen Webserver aufgebaut wird.

```bash
nslookup example.com
```

### Relevanter Filter

```text
dns
```

### Typische Paketstruktur

| Feld | Beschreibung |
| --- | --- |
| `Transaction ID` | Eindeutige ID zur Zuordnung von Anfrage und Antwort |
| `Query Type` | Art des angefragten Records, z. B. `A` (IPv4), `AAAA` (IPv6), `MX` |
| `Answer RRs` | Anzahl der zurückgegebenen Antwort-Records |
| `Response Code` | z. B. `NOERROR`, `NXDOMAIN` bei nicht existierender Domain |

### Was man daraus lernen kann

- Ein `NXDOMAIN` weist auf einen Tippfehler in der Domain oder ein tatsächlich nicht existierendes Ziel hin.
- Wiederholte identische DNS-Anfragen ohne Antwort deuten auf einen nicht erreichbaren oder blockierten DNS-Server hin.
- Die Zeit zwischen Anfrage und Antwort ist häufig für gefühlte Ladezeiten relevanter als die eigentliche HTTP-Antwortzeit.

### Automatisiert mit Python

[`scripts/analyze_dns.py`](../scripts/analyze_dns.py) führt Anfrage und Antwort über die `Transaction ID` zusammen, zählt Fehlercodes und markiert Domains, die mehrfach angefragt, aber nie beantwortet wurden.

## 3.3 HTTP-Analyse

### Szenario

Nach erfolgreicher DNS-Auflösung fordert der Client eine Webseite per HTTP GET an.

### Relevanter Filter

```text
http
```

### Typische Paketstruktur

| Feld | Beschreibung |
| --- | --- |
| `Request Method` | z. B. `GET`, `POST` |
| `Host` | Angeforderter Hostname |
| `Status Code` | z. B. `200 OK`, `301 Moved Permanently`, `404 Not Found` |
| `Content-Type` | MIME-Type der Antwort, z. B. `text/html` |

### Was man daraus lernen kann

- Statuscode `3xx` zeigt Weiterleitungen an, die die tatsächliche Ladezeit verlängern können.
- Statuscode `4xx`/`5xx` weist auf clientseitige bzw. serverseitige Fehler hin.
- Bei unverschlüsseltem HTTP sind Header und Inhalte im Klartext sichtbar, ein guter Anlass, um im Unterricht auf die Bedeutung von HTTPS/TLS hinzuweisen.

### Automatisiert mit Python

[`scripts/analyze_http.py`](../scripts/analyze_http.py) gruppiert alle Requests nach Statuscode-Klasse (2xx/3xx/4xx/5xx) und markiert Anfragen, deren Antwortzeit über einem einstellbaren Schwellwert liegt.

## Zusammenfassender Vergleich

| Protokoll | Ebene (OSI) | Typischer Zweck | Häufiges Fehlerbild | Auswertung |
| --- | --- | --- | --- | --- |
| ICMP | 3 (Network) | Erreichbarkeitsprüfung | Timeout, Zielhost nicht erreichbar | `scripts/analyze_icmp.py` |
| DNS | 7 (Application) | Namensauflösung | NXDOMAIN, Timeout | `scripts/analyze_dns.py` |
| HTTP | 7 (Application) | Inhaltsübertragung | 4xx/5xx-Statuscodes, lange Ladezeiten | `scripts/analyze_http.py` |

Im nächsten Kapitel werden diese Grundlagen genutzt, um systematisch bei Netzwerkstörungen vorzugehen – inklusive einem Script, das die dortige Checkliste auf TCP-Ebene automatisiert durchgeht.
