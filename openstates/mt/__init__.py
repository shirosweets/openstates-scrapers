from pupa.scrape import Jurisdiction, Organization
from .people import MTPersonScraper
from .committees import MTCommitteeScraper
from .bills import MTBillScraper


# MT has pretty aggressive scraper blocking
settings = {
    'SCRAPELIB_RPM': 20
}

class Montana(Jurisdiction):
    division_id = "ocd-division/country:us/state:mt"
    classification = "government"
    name = "Montana"
    url = "http://leg.mt.gov/"
    scrapers = {
        'people': MTPersonScraper,
        'committees': MTCommitteeScraper,
        'bills': MTBillScraper,
    }
    legislative_sessions = [
        {
            "_scraped_name": "2011 Regular Session",
            "identifier": "2011",
            "name": "2011 Regular Session"
        },
        {
            "_scraped_name": "2013 Regular Session",
            "identifier": "2013",
            "name": "2013 Regular Session"
        },
        {
            "_scraped_name": "2015 Regular Session",
            "identifier": "2015",
            "name": "2015 Regular Session"
        },
        {
            "_scraped_name": "2017 Regular Session",
            "identifier": "2017",
            "name": "2017 Regular Session",
            "start_date": "2017-01-02",
            "end_date": "2017-04-28"
        },
    ]
    ignored_scraped_sessions = [
        "2017 Special Session",
        "2009 Regular Session",
        "2007 Special Sessions",
        "2007 Regular Session",
        "2005 Special Sessions",
        "2005 Regular Session",
        "2003 Regular Session",
        "2002 Special Sessions",
        "2001 Regular Session",
        "2000 Special Sessions",
        "1999 Special Sessions",
        "1999 Regular Session",
        "1997 Regular Session",
    ]

    def get_organizations(self):
        legislature_name = "Montana Legislature"
        lower_chamber_name = "House"
        lower_seats = 100
        lower_title = "Representative"
        upper_chamber_name = "Senate"
        upper_seats = 50
        upper_title = "Senator"

        legislature = Organization(name=legislature_name,
                                   classification="legislature")
        upper = Organization(upper_chamber_name, classification='upper',
                             parent_id=legislature._id)
        lower = Organization(lower_chamber_name, classification='lower',
                             parent_id=legislature._id)

        for n in range(1, upper_seats+1):
            upper.add_post(
                label=str(n), role=upper_title,
                division_id='{}/sldu:{}'.format(self.division_id, n))
        for n in range(1, lower_seats+1):
            lower.add_post(
                label=str(n), role=lower_title,
                division_id='{}/sldl:{}'.format(self.division_id, n))

        yield legislature
        yield upper
        yield lower

    def get_session_list(self):
        from openstates.utils.lxmlize import url_xpath
        return url_xpath('https://leg.mt.gov/session/',
                         "//button[contains(@class,'js-accordionButton')]/text()")
