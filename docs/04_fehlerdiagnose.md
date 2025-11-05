# 4. Fehlerdiagnose im Netzwerk

### Beispiel 1: Paketverlust
Ein Ping-Test zeigt 20% Paketverlust.  
→ Mit Wireshark erkennt man, dass einige ICMP-Echo-Replies fehlen.  
→ Mögliche Ursachen:
- WLAN-Interferenzen
- Firewall blockiert ICMP

### Beispiel 2: DNS-Auflösung schlägt fehl
→ Wireshark zeigt wiederholte DNS-Requests ohne Antwort.  
→ Der DNS-Server ist möglicherweise nicht erreichbar.

### Beispiel 3: Langsamer Seitenaufbau
→ TCP Retransmissions in Wireshark sichtbar.  
→ Ursache: Überlastetes Netzwerk oder Paketverlust.
