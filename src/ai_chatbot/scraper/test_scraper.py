import pytest

from ai_chatbot.scraper.scraper import Scraper
import datetime

def test_scraper_all():
    happend = False

    s = Scraper("drivers/chromedriver_linux", 3)
    for x in s.scrape(True, "NRW", "LUT", datetime.datetime(2020, 2, 3, 15, 30), datetime.datetime(2020, 2, 7, 15, 15)):
        happend = True

    assert happend is True

