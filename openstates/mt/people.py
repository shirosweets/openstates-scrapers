import re
import lxml.html
from pupa.scrape import Person, Scraper


class NoDetails(Exception):
    pass


class MTPersonScraper(Scraper):
    listing_url = ''

    def scrape_cell(self, row, css_class):
        if row.xpath('td[contains(@class,"{}")]/a/text()'.format(css_class)):
            td = row.xpath(
                'td[contains(@class,"{}")]/a/text()'.format(css_class))
        elif row.xpath('td[contains(@class,"{}")]/text()'.format(css_class)):
            td = row.xpath(
                'td[contains(@class,"{}")]/text()'.format(css_class))

        if td:
            content = re.sub(r'\s+', ' ', td[0].replace("\n", '').strip())
            return content
        else:
            return None

    def scrape_cell_link(self, row, css_class):
        if row.xpath('td[contains(@class,"{}")]/a/@href'.format(css_class)):
            td = row.xpath(
                'td[contains(@class,"{}")]/a/@href'.format(css_class))
            return td[0].strip().replace('mailto:', '')
        return None

    def scrape(self, chamber=None, session=None):
        # TODO: Session selector at the top of the page
        if not session:
            session = self.latest_session()
            self.info('No session specified; using %s', session)

        chambers = [chamber] if chamber else ['upper', 'lower']

        # All members are in the HTML of one page, so just fetch it once
        # and then parse it per chamber(s)

        self.listing_url = 'https://leg.mt.gov/legislator-information/?session_select=111'

        data = self.get(self.listing_url).text
        page = lxml.html.fromstring(data)
        page.make_links_absolute(self.listing_url)

        for chamber in chambers:
            yield from self.scrape_legislators(page, chamber=chamber)

    def scrape_legislators(self, page, chamber):
        CHAMBER_CODES = {'upper': 'SD', 'lower': 'HD'}
        PARTY_CODES = {'D': 'Democratic',
                       'R': 'Republican', 'I': 'Independent'}

        rows = page.xpath('//table[@id="reports-table"]/tbody/tr')
        for row in rows:
            chamber_td = self.scrape_cell(row, 'seatCell')

            # If the row isn't for the chamber being scraped, skip it
            if CHAMBER_CODES[chamber] not in chamber_td:
                continue

            chamber_parts = chamber_td.split(" ")
            print(chamber_parts)
            district = int(chamber_parts[1])

            name = self.scrape_cell(row, 'nameCell')
            person_url = self.scrape_cell_link(row, 'nameCell')

            party = self.scrape_cell(row, 'partyCell')
            party = PARTY_CODES[party]

            phone = self.scrape_cell(row, 'phoneCell')
            # TODO: Split phone on <br>

            email = self.scrape_cell_link(row, 'emailCell')

            print(name, party, phone, email, person_url)

            legislator = Person(primary_org=chamber,
                                district=district,
                                name=name,
                                party=party)

            legislator.add_link(person_url, note="legislator page")
            legislator.add_source(
                self.listing_url, note="legislator list page")

            # if address:
            #     leg.add_contact_detail(type='address', value=address, note='Capitol Office')
            if phone:
                legislator.add_contact_detail(
                    type='voice', value=phone, note='Capitol Office')
            if email:
                legislator.add_contact_detail(type='email', value=email)

            yield legislator

    def _scrape_details(self, url):
        '''Scrape the member's bio page.

        Things available but not currently scraped are office address,
        and waaay too much contact info, including personal email, phone.
        '''
        pass
