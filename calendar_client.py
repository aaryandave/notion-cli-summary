"""Module to get today's events from an iCal URL.
"""
from datetime import datetime, timedelta
import json
from icalendar import Calendar
import requests

def get_days_events(url: str, req_date: datetime=datetime.now()) -> list[dict]:
    """Get the events for a specific date from an iCal URL

    Args:
        url (str): The URL of the iCal file
        req_date (datetime, optional): The date to get the events for. Defaults to datetime.now().

    Returns:
        list[dict]: List of events for the specified date
    """
    response = requests.get(url, timeout=10)
    calendar = Calendar.from_ical(response.text)
    today = req_date.date()
    events = []

    for event in calendar.walk("vevent"):
        start = event.get("dtstart").dt
        end = event.get("dtend").dt

        # Ensure the start and end dates are datetime.date objects
        if isinstance(start, datetime):
            start_time = start.time()
        else:
            start = datetime.combine(start, datetime.min.time())
            start_time = start.time()

        if isinstance(end, datetime):
            end_time = end.time()
        else:
            end = datetime.combine(end, datetime.min.time())
            end_time = end.time()

        if start.date() <= today <= end.date():
            event_info = {
                "name": event.get("name"),
                "dtstart": start.isoformat(),
                "start_time": start_time.strftime("%H:%M"),
                "dtend": end.isoformat(),
                "end_time": end_time.strftime("%H:%M"),
                "description": event.get("description"),
                "location": event.get("location"),
                "summary": event.get("summary")
            }
            events.append(event_info)

    # Sort events in descending order by start date and time
    events.sort(key=lambda x: (x["dtstart"], x["dtend"]), reverse=False)
    return events

def get_event_strings(events: list[dict]) -> list[str]:
    """Get the event strings from the events dictionary

    Args:
        events (list[dict]): List of events

    Returns:
        list[str]: List of event strings
    """
    event_strings = []
    for event in events:
        event_str = ""
        event_str += f"{event['summary']}, " if event.get("summary") else ""
        event_str += f"a {event['description']} " if event.get("description") else ""
        if event.get("dtstart"):
            event_str += f"from {event['start_time']} to {event['end_time']} "
        event_str += f"at {event['location']} " if event.get("location") else ""
        event_strings.append(event_str)
    return event_strings

def main() -> None:
    """Main function to get today's events from the iCal URLs
    """
    with open(".config.json", encoding="utf-8") as f:
        config = json.load(f)
        urls = config["CALENDAR_URLS"]
        print("Events for today:")
        print("---------------")
        for url in urls:
            events = get_days_events(url)
            print("\n".join(get_event_strings(events)))

        print("---------------")
        print("Events for yesterday:")
        print("---------------")
        for url in urls:
            events = get_days_events(url, req_date=datetime.now()-timedelta(days=1))
            print("\n".join(get_event_strings(events)))

if __name__ == "__main__":
    main()
