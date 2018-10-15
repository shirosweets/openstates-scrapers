import re
import csv
from urllib import parse
import lxml.html
from pupa.scrape import Person, Scraper


class NoDetails(Exception):
    pass

class MTPersonScraper(Scraper):

    def scrape_cell(self, row, css_class):
        if row.xpath('td[contains(@class,"{}")]/a/text()'.format(css_class)):
            td = row.xpath('td[contains(@class,"{}")]/a/text()'.format(css_class))
        elif row.xpath('td[contains(@class,"{}")]/text()'.format(css_class)):
            td = row.xpath('td[contains(@class,"{}")]/text()'.format(css_class))

        if td:
            return td[0].replace("\n", '').strip()
        else:
            return None

    def scrape(self, chamber=None, session=None):
        # TODO: Session selector at the top of the page
        if not session:
            session = self.latest_session()
            self.info('No session specified; using %s', session)

        chambers = [chamber] if chamber else ['upper', 'lower']

        # All members are in the HTML of one page, so just fetch it once
        # and then parse it per chamber(s)

        url = 'https://leg.mt.gov/legislator-information/?session_select=111'

        data = self.get(url).text
        page = lxml.html.fromstring(data)

        for chamber in chambers:
            yield from self.scrape_legislators(page, chamber=chamber)

    def scrape_legislators(self, page, chamber):
        CHAMBER_CODES = {'upper': 'SD', 'lower': 'HD'}
        PARTY_CODES = {'D': 'Democratic', 'R': 'Republican', 'I': 'Independent'}

        rows = page.xpath('//table[@id="reports-table"]/tbody/tr')
        for row in rows:
            chamber_td = self.scrape_cell(row, 'seatCell')

            # If the row isn't for the chamber being scraped, skip it
            if CHAMBER_CODES[chamber] not in chamber_td:
                continue

            name = self.scrape_cell(row, 'nameCell')
            party = self.scrape_cell(row, 'partyCell')
            party = PARTY_CODES[party]

            phone = self.scrape_cell(row, 'phoneCell')
            # TODO: Split phone on <br>

            email = self.scrape_cell(row, 'emailCell')

            print(name, party, phone, email)
            #yield legislator


    def _scrape_details(self, url):
        '''Scrape the member's bio page.

        Things available but not currently scraped are office address,
        and waaay too much contact info, including personal email, phone.
        '''
        pass