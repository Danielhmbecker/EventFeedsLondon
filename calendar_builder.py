import os
from datetime import datetime, timedelta
import uuid

INPUT_FILE = 'data/master_events.txt'
TXT_OUTPUT_DIR = 'output/txt'
ICS_OUTPUT_DIR = 'output/ics'

def parse_event_line(line):
    try:
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 9:
            raise ValueError("Insufficient fields")

        return {
            "date": datetime.strptime(parts[0], "%Y-%m-%d"),
            "title": parts[1],
            "tickets_url": parts[2] if parts[2] else "N/A",
            "area": parts[3],
            "venue": parts[4],
            "capacity": int(parts[5]) if parts[5].isdigit() else 0,
            "doors_open": parts[6],
            "doors_close": parts[7],
            "desc_text": parts[8],
            "status": parts[8].split("Status:")[-1].strip() if "Status:" in parts[8] else "N/A",
            "notes": parts[9] if len(parts) > 9 else "N/A",
            "first_act": parts[10] if len(parts) > 10 else "TBA",
            "busyness_start": parts[11] if len(parts) > 11 else "18:00",
            "busyness_end": parts[12] if len(parts) > 12 else "21:00"
        }
    except Exception as e:
        print(f"❌ Skipping line (parse error): {line}")
        return None

def create_ics_event(event):
    uid = str(uuid.uuid4())

    capacity = event.get("capacity", 0)
    status_lower = event.get("status", "").lower()
    attendance_estimate = 0

    if "sold out" in status_lower:
        attendance_estimate = capacity
        status_line = "🔴 Sold out — Buckle up! Full house, foot traffic stampede, plan extra everything."
    elif "limited" in status_lower or "few" in status_lower:
        attendance_estimate = int(capacity * 0.7)
        status_line = "🟠 Limited tickets — Things heating up! Keep an eye on stock and staff."
    elif "available" in status_lower:
        attendance_estimate = int(capacity * 0.4)
        status_line = "🟢 Tickets available — Chill vibes, no stress on prep."
    else:
        attendance_estimate = 0
        status_line = f"🔥 Status: {event.get('status', 'N/A')}"

    dtstart = datetime.strptime(f"{event['date'].date()} {event['doors_open']}", "%Y-%m-%d %H:%M")
    dtend = datetime.strptime(f"{event['date'].date()} {event['doors_close']}", "%Y-%m-%d %H:%M")

    description = (
        f"📍 Venue: {event['venue']} (Capacity: {capacity})\\n"
        f"🎟 Tickets: {event['tickets_url']}\\n"
        f"{status_line}\\n"
        f"ℹ️ {event['desc_text']}\\n"
        f"📝 Notes: {event['notes']}\\n"
        f"🚪 Doors Open: {event['doors_open']}\\n"
        f"🚪 Doors Close: {event['doors_close']}\\n"
        f"🎤 First Act: {event['first_act']}\\n"
        f"⏰ Expected busy period: {event['busyness_start']} to {event['busyness_end']}\\n"
        f"🎫 Est. Attendance: {attendance_estimate} / {capacity}"
    )

    return f"""BEGIN:VEVENT
UID:{uid}
SUMMARY:{event['title']}
DTSTART:{dtstart.strftime("%Y%m%dT%H%M%S")}
DTEND:{dtend.strftime("%Y%m%dT%H%M%S")}
DESCRIPTION:{description}
LOCATION:{event['venue']}
URL:{event['tickets_url']}
CATEGORIES:master,{event['area'].lower()}
END:VEVENT"""

def write_txt(area, events):
    os.makedirs(TXT_OUTPUT_DIR, exist_ok=True)
    path = os.path.join(TXT_OUTPUT_DIR, f"{area}_Events.txt")
    with open(path, 'w', encoding='utf-8') as f:
        for event in events:
            f.write(event['raw'] + '\n')

def write_ics(area, events):
    os.makedirs(ICS_OUTPUT_DIR, exist_ok=True)
    calendar = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:EventCalendarGenerator"]
    for event in events:
        calendar.append(create_ics_event(event))
    calendar.append("END:VCALENDAR")

    path = os.path.join(ICS_OUTPUT_DIR, f"{area}_Events.ics")
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(calendar))

def main():
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

    # Master ICS with all events combined
    all_events = [e for events in by_area.values() for e in events]
    write_ics("AllLondon", all_events)

if __name__ == "__main__":
    main()
