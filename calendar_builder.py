import os
from datetime import datetime
import uuid

INPUT_FILE = 'data/master_events.txt'
TXT_OUTPUT_DIR = 'output/txt'
ICS_OUTPUT_DIR = 'output/ics'

def parse_event_line(line):
    try:
        parts = [p.strip() for p in line.split('|')]
        date_str, title, ticket, area, venue, capacity, doors, end, desc_status = parts
        return {
            "date": datetime.strptime(date_str, "%Y-%m-%d"),
            "title": title,
            "ticket": ticket,
            "area": area,
            "venue": venue,
            "capacity": capacity,
            "doors": doors,
            "end": end,
            "desc_status": desc_status
        }
    except Exception as e:
        print(f"❌ Skipping line (parse error): {line}")
        return None

def to_ics_event(event):
    dtstart = datetime.strptime(f"{event['date'].date()} {event['doors']}", "%Y-%m-%d %H:%M")
    dtend = datetime.strptime(f"{event['date'].date()} {event['end']}", "%Y-%m-%d %H:%M")
    uid = str(uuid.uuid4())

    description = (
        f"📍 Venue: {event['venue']} (Capacity: {event['capacity']})\\n"
        f"🎟 Tickets: {event['ticket']}\\n"
        f"ℹ️ {event['desc_status']}"
    )

    return f"""BEGIN:VEVENT
UID:{uid}
SUMMARY:{event['title']}
DTSTART:{dtstart.strftime("%Y%m%dT%H%M%S")}
DTEND:{dtend.strftime("%Y%m%dT%H%M%S")}
DESCRIPTION:{description}
LOCATION:{event['venue']}
URL:{event['ticket']}
CATEGORIES:master,{event['area'].lower()}
END:VEVENT"""

def write_txt(area, events):
    path = os.path.join(TXT_OUTPUT_DIR, f"{area}_Events.txt")
    with open(path, 'w', encoding='utf-8') as f:
        for event in events:
            f.write(event['raw'] + '\n')

def write_ics(area, events):
    calendar = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:EventCalendarGenerator"]
    for event in events:
        calendar.append(to_ics_event(event))
    calendar.append("END:VCALENDAR")

    path = os.path.join(ICS_OUTPUT_DIR, f"{area}_Events.ics")
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(calendar))

def main():
    os.makedirs(TXT_OUTPUT_DIR, exist_ok=True)
    os.makedirs(ICS_OUTPUT_DIR, exist_ok=True)

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        raw_lines = [l.strip() for l in f.readlines() if l.strip()]

    by_area = {}
    for line in raw_lines:
        event = parse_event_line(line)
        if not event:
            continue
        event['raw'] = line
        area = event['area']
        if area not in by_area:
            by_area[area] = []
        by_area[area].append(event)

    for area, events in by_area.items():
        write_txt(area, events)
        write_ics(area, events)

    # Make master .ics
    all_events = [e for events in by_area.values() for e in events]
    write_ics("AllLondon", all_events)

if __name__ == "__main__":
    main()
