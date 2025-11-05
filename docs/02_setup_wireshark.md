# 2. Setup & Grundlagen von Wireshark

Dieses Kapitel erklärt Installation, Grundkonzept, sichere Aufzeichnung (ohne sensible Daten) und die wichtigsten Filter. Ziel ist, dass du die Begriffe und den Ablauf verstehst – **ohne** lokal etwas auszuführen.

---

## 2.1 Voraussetzungen
- Grundkenntnisse zu IP, TCP/UDP, DNS, HTTP.
- Laptop/PC mit Admin-Rechten (für echte Captures – hier nur theoretisch).
- Optionales CLI-Tool: **tshark** (wird mit Wireshark installiert).

---

## 2.2 Installation (Übersicht)
> Nur zur Vollständigkeit – in diesem Projekt werden **keine** realen Mitschnitte benötigt.

- **Windows:** Wireshark Installer ausführen, Option „TShark“ und „Npcap“ aktiviert lassen.
- **macOS:** via Installer (dmg) oder `brew install wireshark` (Pakete variieren).
- **Linux:** Paketmanager, z. B. `sudo apt install wireshark tshark`.

**Prüfen (optional):**
```bash
tshark -v
