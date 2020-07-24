import re
from bs4 import BeautifulSoup
from ai_chatbot.nlp.Locations.Location import Location
import urllib3


def scrape_wiki_station(url):
    webpage = make_soup(url)
    if "_A" in url:
        locations = scrape_ABC(webpage)
    elif "_B" in url:
        locations = scrape_ABC(webpage)
    elif "_C" in url:
        locations = scrape_ABC(webpage)
    else:
        locations = scrape_else(webpage)

    return locations


def scrape_ABC(webpage):
    locations = []
    results = webpage.find_all("tr", class_="vcard")
    rgx = re.compile("\s\([^)]+\)")
    for result in results:
        try:
            name = result.find("span", class_="org").a.string.strip()
            name = rgx.sub('', name)
            postcode = result.find("span", class_="postal-code").a.string.strip()
            stationcode = result.find("span", class_="nickname").a.string.strip()
            locations.append(Location(name, postcode, stationcode))
        except:
            pass

    return locations


def scrape_else(webpage):
    locations = []
    results = webpage.find("table", class_="wikitable").findChildren("tr")
    results.pop(0)
    rgx = re.compile("\s\([^)]+\)")
    for result in results:
        contents = result.findChildren("a")
        try:
            name = contents[0].string.strip()
            name = rgx.sub('', name)
            postcode = contents[1].string.strip()
            stationcode = contents[2].string[0:3].strip()
            locations.append(Location(name, postcode, stationcode))
        except:
            pass

    return locations


def make_soup(url):
    urllib3.disable_warnings()
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    r = http.request("GET", url)
    return BeautifulSoup(r.data, 'lxml')
