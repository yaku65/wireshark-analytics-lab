# 3. Beispielhafte Traffic-Analyse

### ICMP (Ping)
Ein **Ping-Test** sendet ICMP-Echo-Requests.  
Mit Wireshark kann man prüfen:
- Ob Antworten (Echo Reply) eintreffen
- Wie hoch die Round-Trip-Time (RTT) ist
- Ob Paketverlust besteht

### DNS
Beim Öffnen einer Webseite (z. B. *example.com*) sendet der Client DNS-Requests.  
Wireshark zeigt:
- Anfrage an DNS-Server (Port 53)
- Antwortzeit (`dns.time`)
- mögliche Fehler (z. B. NXDOMAIN)

### HTTP
Ein Webaufruf erzeugt mehrere TCP- und HTTP-Pakete.  
Man kann analysieren:
- HTTP-GET-Requests
- Antwortcodes (200, 404)
- Größe der übertragenen Dateien
