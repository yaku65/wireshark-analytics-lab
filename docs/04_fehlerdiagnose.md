# 4. Fehlerdiagnose

Dieses Kapitel beschreibt ein systematisches Vorgehen, um typische Netzwerkstörungen mithilfe von Wireshark und ergänzenden Bordmitteln einzugrenzen. Die komplette Checkliste aus diesem Kapitel ist außerdem als Python-Script umgesetzt: [`scripts/detect_issues.py`](../scripts/detect_issues.py) prüft Beispieldaten automatisiert auf genau die Muster, die unten beschrieben sind.

## Vorgehen nach dem Schichtenmodell

Eine bewährte Strategie ist es, sich von unten nach oben durch das OSI-Modell zu arbeiten, da ein Fehler auf einer unteren Schicht sich meist auf alle darüberliegenden Schichten auswirkt:

1. **Physikalische Verbindung prüfen** – Ist das Kabel gesteckt, die WLAN-Verbindung aktiv?
2. **IP-Konfiguration prüfen** – Hat der Host eine gültige IP-Adresse, Subnetzmaske und ein Gateway (`ipconfig` / `ip a`)?
3. **Erreichbarkeit testen** – Antwortet das Gateway oder ein bekannter Zielhost auf `ping`?
4. **Namensauflösung prüfen** – Funktioniert die DNS-Auflösung (`nslookup`, `dig`)?
5. **Anwendungsebene prüfen** – Liefert der Dienst (z. B. HTTP) eine gültige Antwort?

## Typische Fehlerbilder und ihre Signaturen in Wireshark

### Paketverlust

**Symptom:** Anwendungen wirken langsam oder brechen ab.

**Wireshark-Filter:**

```text
tcp.analysis.retransmission
tcp.analysis.duplicate_ack
```

**Interpretation:** Häufige Retransmissions deuten auf eine instabile Verbindung oder überlastete Netzwerkkomponenten hin. Wiederholte Duplicate ACKs können ein Hinweis auf verlorene Pakete sein, die der Empfänger nie erhalten hat.

### DNS-Probleme

**Symptom:** Webseiten lassen sich nicht öffnen, obwohl die Internetverbindung grundsätzlich funktioniert.

**Wireshark-Filter:**

```text
dns && dns.flags.rcode != 0
```

**Interpretation:** Ein von `0` (`NOERROR`) abweichender Response Code zeigt an, dass die Namensauflösung fehlgeschlagen ist, etwa durch einen nicht erreichbaren DNS-Server oder eine nicht existierende Domain. Wird dieselbe Anfrage dazu noch mehrfach wiederholt, ohne je eine Antwort zu bekommen, spricht das eher für einen nicht erreichbaren DNS-Server als für eine einzelne falsche Domain – dieser Fall wird von [`scripts/analyze_dns.py`](../scripts/analyze_dns.py) automatisch markiert.

### Hohe Latenz

**Symptom:** Verbindungen sind grundsätzlich stabil, aber spürbar langsam.

**Wireshark-Filter:**

```text
tcp.time_delta > 0.5
```

**Interpretation:** Große Zeitabstände zwischen zusammenhängenden Paketen einer TCP-Verbindung weisen auf Latenzprobleme hin, etwa durch überlastete Zwischenstationen oder eine hohe geografische Distanz zum Zielserver.

### Verbindungsabbrüche

**Symptom:** Verbindungen werden unerwartet beendet.

**Wireshark-Filter:**

```text
tcp.flags.reset == 1
```

**Interpretation:** Ein `RST`-Flag zeigt einen erzwungenen Verbindungsabbruch an, dieser kann von einer Firewall, einem überlasteten Server oder einer fehlerhaften Anwendung ausgelöst werden.

## Checkliste für die praktische Diagnose

- [ ] Ist das Problem auf einem einzelnen Host oder netzwerkweit reproduzierbar?
- [ ] Tritt der Fehler bei jedem Verbindungsversuch auf oder nur sporadisch?
- [ ] Liegt der Fehler auf Netzwerk-, Namensauflösungs- oder Anwendungsebene?
- [ ] Gibt es auffällige Muster in den Zeitstempeln (Latenz, Timeouts)?
- [ ] Lässt sich der Fehler durch einen minimalen Testfall (z. B. reiner Ping) isolieren?

Der erste Punkt dieser Liste (einzelner Host vs. netzwerkweit) wird von `scripts/detect_issues.py` bereits automatisch grob eingeordnet, indem gezählt wird, wie viele unterschiedliche Gegenstellen von Retransmissions, RST-Paketen oder hoher Latenz betroffen sind.

## Ergänzende Kommandozeilenwerkzeuge

| Werkzeug | Zweck |
| --- | --- |
| `ping` | Grundlegende Erreichbarkeitsprüfung |
| `traceroute` / `tracert` | Sichtbarmachen der Route über einzelne Hops |
| `nslookup` / `dig` | Gezielte Prüfung der DNS-Auflösung |
| `tshark` | Automatisierte, skriptbasierte Auswertung von Mitschnitten auf der Kommandozeile, in diesem Repo als Grundlage für [`scripts/parse_tshark_export.py`](../scripts/parse_tshark_export.py) |

Im abschließenden Kapitel werden die Ergebnisse dieses Labs zusammengefasst und offene Punkte für eine Weiterentwicklung benannt.
