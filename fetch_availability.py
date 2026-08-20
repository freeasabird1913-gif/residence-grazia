#!/usr/bin/env python3
"""
Fetches iCal feeds from Airbnb and Booking.com and generates availability.json.
Run automatically by GitHub Actions every hour.
"""

import urllib.request
import json
from datetime import datetime, timezone

# ── CONFIGURA QUI I TUOI FEED iCAL ───────────────────────────────────────────
# Per ogni appartamento, incolla l'URL iCal da Airbnb e/o Booking.com.
# Puoi mettere più URL per appartamento (es. uno Airbnb + uno Booking).
# Lascia la lista vuota [] se l'appartamento non è su quella piattaforma.
#
# Come trovare l'URL iCal:
#   Airbnb:  Annuncio → Disponibilità → Sincronizza calendari → Esporta calendario
#   Booking: Extranet → Calendario → Sincronizza → Esporta (.ics)
# ─────────────────────────────────────────────────────────────────────────────

FEEDS = {
    "Appartamento Blu": [
        "https://ical.booking.com/v1/export?t=3bcaf5a7-7140-4fa0-b310-c87efb8bb790",
        "https://www.airbnb.co.uk/calendar/ical/1181690743610446492.ics?t=66039f05e08a49efb110704aca0a513b",
    ],
    "Appartamento Girasole": [
        "https://ical.booking.com/v1/export?t=22f1e2ac-fa31-4c78-a093-b0b6fd476af3",
        "https://www.airbnb.co.uk/calendar/ical/1181697209682651095.ics?t=a61bbe97a609489e9189e242bdf40678",
    ],
    "Appartamento Perla": [
        "https://ical.booking.com/v1/export?t=9ad8a252-16aa-42cb-8ddf-d3b0e4bfabcf",
        "https://www.airbnb.co.uk/calendar/ical/1183344791474677071.ics?t=d028dc08a9f64309b484d32df5ad99ee",
    ],
    "Appartamento Salvia": [
        "https://ical.booking.com/v1/export?t=386a19ba-7ca6-4cf8-9bbc-e577bc58376a",
        "https://www.airbnb.co.uk/calendar/ical/1183355228740068625.ics?t=087f18bbb75f47a29e3ec4d5a8767e65",
    ],
    "Appartamento Turchese": [
        "https://ical.booking.com/v1/export?t=129f144a-fc06-4550-8917-e64800a6144d",
        "https://www.airbnb.co.uk/calendar/ical/1179009389016521979.ics?t=77973b89206e4ca0b59ff0ffa3949d74",
    ],
    "Appartamento Corallo": [
        "https://ical.booking.com/v1/export?t=c6e1a998-7a0d-4356-991e-203be3535ae4",
        "https://www.airbnb.co.uk/calendar/ical/1179035053755959407.ics?t=8ef755184dc04d559da4c2b388311b62",
    ],
    "Appartamento Terrazza": [
        "https://admin.booking.com/hotel/hoteladmin/ical.html?t=265d91b0-5ef5-4de1-8718-b6b01f1b08cd",
        "https://www.airbnb.co.uk/calendar/ical/880865505669393035.ics?t=03e8070b1f6b452c92b31eb6f32e4f96",
    ],
    "Appartamento Conchiglia": [
        "https://ical.booking.com/v1/export?t=7a67dd28-3cc5-4ac8-9bcb-015912ac9a2c",
        "https://www.airbnb.co.uk/calendar/ical/1686954100181905676.ics?t=117d7e5e528345c1b2b876893e694645",
    ],
    "Appartamento Brezza": [
        "https://ical.booking.com/v1/export?t=538a0049-d3e0-493a-aaf2-ff1a6f75db1d",
        "https://www.airbnb.co.uk/calendar/ical/1690368488636541074.ics?t=5d14c787df984691b21b3559f5a8077f",
    ],
    "Appartamento Marea": [
        "https://ical.booking.com/v1/export?t=4b784bad-ac85-4404-8297-2ce816a8403d",
        "https://www.airbnb.co.uk/calendar/ical/1692033319433531827.ics?t=c2c78b5eb819470c8f27078ee2a837ee",
    ],
    "Appartamento Onda": [
        "https://ical.booking.com/v1/export?t=02446c16-4e06-402e-8f29-395c6dc49d5d",
        "https://www.airbnb.co.uk/calendar/ical/1692038922154224946.ics?t=b7f3d48a0c464e768cd1d0519c7d3e5e",
    ],
    "Appartamento Duna": [
        "https://ical.booking.com/v1/export?t=5a682ac7-be8f-4880-b35c-995912bd7e9c",
        "https://www.airbnb.co.uk/calendar/ical/1692043383800200662.ics?t=38d47bf5e6ce4e979da2bcc0b66bd866",
    ],
    "Appartamento Faro": [
        "https://ical.booking.com/v1/export?t=0d4aac39-366c-4904-a093-285ca48fd703",
        "https://www.airbnb.co.uk/calendar/ical/1692046333955078263.ics?t=1b4e39d80e454e2da022d06146494b13",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────

def parse_date(s):
    s = s.strip()
    try:
        return datetime.strptime(s[:8], '%Y%m%d').strftime('%Y-%m-%d')
    except Exception:
        return None

def fetch_ical(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            content = r.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"    Errore fetch: {e}")
        return []

    events = []
    in_event = False
    dtstart = dtend = None

    for line in content.splitlines():
        line = line.strip()
        if line == 'BEGIN:VEVENT':
            in_event, dtstart, dtend = True, None, None
        elif line == 'END:VEVENT':
            if in_event and dtstart and dtend:
                events.append({'start': dtstart, 'end': dtend})
            in_event = False
        elif in_event:
            if line.upper().startswith('DTSTART'):
                dtstart = parse_date(line.split(':', 1)[-1])
            elif line.upper().startswith('DTEND'):
                dtend = parse_date(line.split(':', 1)[-1])

    return events

result = {}
today = datetime.now(timezone.utc).strftime('%Y-%m-%d')

for name, urls in FEEDS.items():
    print(f"→ {name}")
    all_events = []
    for url in urls:
        events = fetch_ical(url)
        all_events.extend(events)
    # Mantieni solo prenotazioni future
    future = [e for e in all_events if e.get('end', '') >= today]
    # Rimuovi duplicati
    seen = set()
    unique = []
    for e in future:
        key = (e['start'], e['end'])
        if key not in seen:
            seen.add(key)
            unique.append(e)
    result[name] = unique
    print(f"   {len(unique)} prenotazioni future")

output = {
    'updated': datetime.now(timezone.utc).isoformat(),
    'apartments': result
}

with open('availability.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nDone — availability.json aggiornato.")
