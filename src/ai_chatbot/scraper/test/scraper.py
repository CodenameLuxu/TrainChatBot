import requests, os, datetime
import time as mtime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

"""
Author: Martin
Version: v0.3

* v0.3 - 
* v0.2 - Scrapes lowest valued tickets, gets url
* v0.1 - Minimal viable/alpha version of the scraper
"""

def getRowInfo(row, outward: bool) -> dict:
    dep = row.find('td', class_='dep').get_text().strip()
    from__ = row.find('td', class_='from').find('abbr').get_text().strip()  # Probably unneeded
    to_ = row.find('td', class_='to').find('abbr').get_text().strip()       # Probably unneeded
    arr = row.find('td', class_='arr').get_text().strip()
    dur = row.find('td', class_='dur').get_text().replace('\n', '').replace('\t', '').replace(' ', '')
    fare = row.find('td', class_='fare').find('label').get_text().strip()
    return {'outward': outward, 'depatureTime': dep, 'from': from__, 'to': to_, 'arrivalTime': arr, 'durationTime': dur, 'fareTotal': fare}

def formUrl(from_: str, to: str, date: str, time: str, ret_date: str = "", ret_time: str = "") -> str:
    # If there is not a return date and time given
    if ret_date == "" or ret_time == "":
        return "http://ojp.nationalrail.co.uk/service/timesandfares/"+from_+'/'+to+'/'+date+'/'+time+"/dep"
    else:
        return "http://ojp.nationalrail.co.uk/service/timesandfares/"+from_+'/'+to+'/'+date+'/'+time+"/dep/"+ret_date+'/'+ret_time+"/dep"

def page_scrape(page: str, url: str, from_: str, to: str, date: str, time_: str, ret_date: str = "", ret_time: str = "") -> dict:
    soup = BeautifulSoup(page, 'html.parser')
    result_table_out = soup.find('table', id='oft').tbody.find_all('tr', class_='mtx')
    """
    if ret_date is not "":
        result_table_ret = soup.find('table', id='ift').tbody.find_all('tr', class_='mtx')
    """

    for row in result_table_out:
        yield {**{'url': url}, **getRowInfo(row, True)}

    """ Not working properly at the moment
    if ret_date is not "":
        for row in result_table_ret:
            yield getRowInfo(row, False)
    """

class Scraper():
    def __init__(self, path: str=""):
        """
        if path is not "":
            #os.environ['MOZ_HEADLESS'] = '1'       # Will not pop up a window of Firefox
            #self.driver = webdriver.Firefox(executable_path=path)
            #self.driver = webdriver.PhantomJS()
        """

    # Format:
    #   date: string: "today", "tomorrow", "DDMMYY" (others)
    #   time: int: HHMM
    def scrape(self, from_: str, to: str, date: str, time_: str, ret_date: str = "", ret_time: str = "") -> dict:
        url = formUrl(from_, to, date, time_, ret_date, ret_time)

        page = requests.get(url)
        yield from page_scrape(page.content, url, from_, to, date, time_, ret_date, ret_time)

    def scrapeLowest(self, from_: str, to: str, date: str, time_: str, ret_date: str = "", ret_time: str = "") -> dict:
        lowest: float = -1
        url = formUrl(from_, to, date, time, ret_date, ret_time)
        ret_dict: dict = {'url': url, 'results': []}
        for n in self.scrape(from_, to, date, time, ret_date, ret_time):
            if lowest == -1 or (float(n['fareTotal'][1:]) <= lowest):
                # Override previous result if is lower than that, otherwise append to it if equals
                if (float(n['fareTotal'][1:]) == lowest):
                    ret_dict['results'].append(n)
                else:
                    ret_dict['results'] = [n]
                lowest = float(n['fareTotal'][1:])
        return ret_dict

    def selenium_scrape(self):
        self.driver.get('http://www.nationalrail.co.uk/')

        full_from_ = 'Norwich'
        full_to = 'Luton'
        full_date = '29/11/2019'

        from_ = 'NRW'
        to = 'LUT'
        date = '29112019'
        hour = '07'
        sec = '15'
        time_str = str(hour)+str(sec)

        driver_from_ = self.driver.find_element_by_name('from.searchTerm')
        driver_to = self.driver.find_element_by_name('to.searchTerm')
        driver_date = self.driver.find_element_by_name('timeOfOutwardJourney.monthDay')
        driver_form = self.driver.find_element_by_id("journeyPlannerForm")

        driver_from_.send_keys(full_from_)
        driver_to.send_keys(full_to)
        driver_date.clear()
        driver_date.send_keys(full_date)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//select[@id='sltHours']/option[text()='"+hour+"']"))).click()
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//select[@id='sltMins']/option[text()='"+sec+"']"))).click()
        driver_form.submit()

        url = self.driver.current_url
        for i in page_scrape(self.driver.page_source, url, from_, to, date, time_str):
            print(i)

    def new_scrape(self, from_: str, from_full: str, to: str, to_full: str, out_datetime: datetime, ret_datetime: datetime = None) -> dict:
        """
        from_ = 'NRW'
        from_full = "Norwich"
        to = 'LUT'
        to_full = "Luton"
        """

        date: str = out_datetime.strftime('%d%m%y')
        time_: str = out_datetime.strftime('%H%M')

        date_fmt: str = out_datetime.strftime('%d/%m/%y')
        hour: str = str(out_datetime.hour)
        mins: str = str(out_datetime.minute)

        ret_date: str = ""
        ret_time: str = ""
        ret_date_fmt: str = ""
        ret_hour: str = ""
        ret_mins: str = ""

        if ret_datetime != None:
            ret_date = ret_datetime.strftime('%d%m%y')
            ret_time = ret_datetime.strftime('%H%M')

            ret_date_fmt = ret_datetime.strftime('%d/%m/%y')
            ret_hour = str(ret_datetime.hour)
            ret_mins = str(ret_datetime.minute)

        payload = {"commandName":"journeyPlannerCommand","jpState":"10ngle",
                "from.searchTerm":from_full,
                "to.searchTerm":to_full,
                "timeOfOutwardJourney.arrivalOrDeparture":"DEPART",
                "timeOfOutwardJourney.monthDay":date_fmt,
                "timeOfOutwardJourney.hour": hour,
                "timeOfOutwardJourney.minute": mins}

        if ret_datetime != None:
            payload.update({"checkbox":"true","_checkbox":"on",
                    "timeOfReturnJourney.arrivalOrDeparture":"DEPART",
                    "timeOfReturnJourney.monthDay":ret_date_fmt,
                    "timeOfReturnJourney.hour":ret_hour,
                    "timeOfReturnJourney.minute":ret_mins})

        payload.update({"numberOfAdults":"1","numberOfChildren":"0",
                "firstClass":"true","_firstClass":"on",
                "standardClass":"true","_standardClass":"on",
                "railcardCodes":"","numberOfEachRailcard":"0",
                "oldRailcardCodes":"",
                "viaMode":"VIA","via.searchTerm":"Station","via1Mode":"VIA","via1.searchTerm":"Station","via2Mode":"VIA","via2.searchTerm":"Station","offSetOption":"0","operator.code":"","_reduceTransfers":"on","_lookForSleeper":"on","_directTrains":"on","_showFastestTrainsOnly":"on"})


        cookie_payload = {'expand-disruptions': 'no',
        'jpRemember': '{"commandName":"journeyPlannerCommand","jpState":"10ngle",'
                +'"from.searchTerm":"'+from_full+'",'
                +'"to.searchTerm":"'+to_full+'",'
                +'"timeOfOutwardJourney.arrivalOrDeparture":"DEPART",'
                +'"timeOfOutwardJourney.monthDay":"'+date_fmt+'",'
                +'"timeOfOutwardJourney.hour":"'+hour+'",'
                +'"timeOfOutwardJourney.minute":"'+mins+'",'}

        if ret_datetime != None:
            cookie_payload['jpRemember'] += str('"checkbox":"true","_checkbox":"on",'
                    +'"timeOfReturnJourney.arrivalOrDeparture":"DEPART",'
                    +'"timeOfReturnJourney.monthDay":"'+ret_date_fmt+'",'
                    +'"timeOfReturnJourney.hour":"'+ret_hour+'",'
                    +'"timeOfReturnJourney.minute":"'+ret_mins+'",')

        cookie_payload['jpRemember'] += str('"numberOfAdults":"1","numberOfChildren":"0",'
                +'"firstClass":"true","_firstClass":"on",'
                +'"standardClass":"true","_standardClass":"on",'
                +'"railcardCodes":"","numberOfEachRailcard":"0",'
                +'"oldRailcardCodes":"",'
                +'"viaMode":"VIA","via.searchTerm":"Station","via1Mode":"VIA","via1.searchTerm":"Station","via2Mode":"VIA","via2.searchTerm":"Station","offSetOption":"0","operator.code":"","_reduceTransfers":"on","_lookForSleeper":"on","_directTrains":"on","_showFastestTrainsOnly":"on"}')

        s = requests.Session()
        url = formUrl(from_, to, date, time_, ret_date, ret_time)
        #print(url)
        r = s.post("https://ojp.nationalrail.co.uk/service/planjourney/plan", data=payload, allow_redirects=False)
        #print('JSESSIONID: ', requests.utils.dict_from_cookiejar(s.cookies), r.status_code)
        s.cookies.set_cookie(requests.cookies.create_cookie('expand-disruptions', cookie_payload['expand-disruptions']))
        s.cookies.set_cookie(requests.cookies.create_cookie('jpRemember', cookie_payload['jpRemember']))
        r = s.get(url)
        yield from page_scrape(r.content, url, from_, to, date, time_, ret_date, ret_time)

# For testing purpose
if __name__ == "__main__":
    s = Scraper()
    for n in s.new_scrape('NRW', 'Norwich', 'LUT', 'Luton', datetime.datetime(2019, 11, 23, 19, 15)):
        print(n['url'], n['depatureTime'], n['arrivalTime'], n['durationTime'], n['fareTotal'])
    """
    for n in s.scrape("NRW", "LST", "101119", "2145", "111119", "2345"):
        print(n['url'], n['depatureTime'], n['arrivalTime'], n['durationTime'], n['fareTotal'])
    """

