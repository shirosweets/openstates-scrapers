import re
import pytz

from pupa.scrape import Scraper, Event
from icalendar import Calendar


class DCEventScraper(Scraper):
    _tz = pytz.timezone('US/Eastern')

    def scrape(self):
        url = 'http://dccouncil.us/events/month/?ical=1&tribe_display=month'
        cal = self.get(url, verify=False).content

        gcal = Calendar.from_ical(cal)
        for component in gcal.walk():
            if component.name == "VEVENT":
                start_date = component.get('dtstart').dt
                end_date = component.get('dtend').dt
                location = component.get('location')
                description = component.get('description').strip()

                name = component.get('summary').strip()

                lat = component.get('geo').latitude
                lon = component.get('geo').longitude

                event = Event(
                    start_date=start_date,
                    end_date=end_date,
                    name=name,
                    location_name=location,
                    description=description
                )

                event.location = {
                    'name': location,
                    'coordinates': {
                        'latitude': str(lat),
                        'longitude': str(lon)
                    }
                }

                event.add_source('http://dccouncil.us/events/month/')

                related_bills = re.findall(r'PR\d{2}-\d+', description)
                related_bills = set(related_bills)

                # hack: we can't add bills directly to an event,
                # so add a stub agenda item
                if related_bills:
                    agenda_item = event.add_agenda_item('Bills under consideration')
                    for bill in related_bills:
                        agenda_item.add_bill(bill)

                yield event
