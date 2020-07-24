import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

"""
Author: Martin
Version: v0.4

* v0.4 - Selenium used instead (or otherwise im getting nowhere)
* v0.3 - 
* v0.2 - Scrapes lowest valued tickets, gets url
* v0.1 - Minimal viable/alpha version of the scraper
"""

class Scraper():
    """
        location = The path to the chromedriver file is
        timeout = Timeout in seconds on how long the page can load for
        headless = True/False if it should run in headless/no window mode
    """
    def __init__(self, location: str, timeout: int = 3, headless: bool = True):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--test-type")
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})    # Disable image loading
        options.headless = headless                                                                         # headless = Do not run a window/GUI
        if options.headless:
            print("Scraper: Selenium: Chromium/Chrome webdriver running in headless mode. headless=False to disable it.")
        self.driver = webdriver.Chrome(location, options=options)
        self.driver.set_page_load_timeout(timeout)                                                          # Do not wait for loading longer than timeout

    """
    Extract the information of each row of the table:
    params:
        _type: return, single
        info: return, out, ret, single
    returns:
        type: _type
        departureTime: Time of departure in "HH:MM"
        from: Departure station code
        to: Arrival station code
        arrivalTime: Time of arrival in "HH:MM"
        durationTime: How long the journey will take
        fareTotal: Total prices of the ticket
        info: info
    """
    def __getRowInfo(self, row, _type: str, info: str) -> dict:
        try:
            fare = row.find('td', class_='fare').find('div', class_=_type).find('label').get_text().strip()
        except Exception as e:
            fare = None
        if fare == "":
            fare = None
        if fare == None:
            return {'type': None}

        dep = row.find('td', class_='dep').get_text().strip()
        from__ = row.find('td', class_='from').find('abbr').get_text().strip()  # Probably unneeded
        to_ = row.find('td', class_='to').find('abbr').get_text().strip()       # Probably unneeded
        arr = row.find('td', class_='arr').get_text().strip()
        dur = row.find('td', class_='dur').get_text().replace('\n', '').replace('\t', '').replace(' ', '')

        return {'type': _type, 'departureTime': dep, 'from': from__, 'to': to_, 'arrivalTime': arr, 'durationTime': dur, 'fareTotal': fare, 'info': info}

    """
    Turns given parameters into URL string:
        from_: Departure station code
        to: Arrival station code
        date: Departure date
        time: Departure time
        ret_date: Return date
        ret_time: Return time
    """
    def __formUrl(self, from_: str, to: str, date: str, time: str, ret_date: str = "", ret_time: str = "") -> str:
        # If there is not a return date and time given
        if ret_date == "" or ret_time == "":
            return "http://ojp.nationalrail.co.uk/service/timesandfares/"+from_+'/'+to+'/'+date+'/'+time+"/dep"
        else:
            return "http://ojp.nationalrail.co.uk/service/timesandfares/"+from_+'/'+to+'/'+date+'/'+time+"/dep/"+ret_date+'/'+ret_time+"/dep"

    """
    page: Page content
    url: Page URL
    ret: False/True scrape as a return page
    """
    def __page_scrape(self, page: str, url: str, ret: bool = False) -> dict:
        soup = BeautifulSoup(page, 'html.parser')
        result_table_out = soup.find('table', id='oft').tbody.find_all('tr', class_='mtx')
        if ret:
            result_table_ret = soup.find('table', id='ift').tbody.find_all('tr', class_='mtx')
            _type = "return"
        else:
            _type = "single"

        for row in result_table_out:
            yield {**{'url': url}, **self.__getRowInfo(row, _type, _type)}

        if ret:
            try:
                cookies = self.driver.find_element_by_class_name('accept-cookies-button')
                cookies.click()
            except Exception as c:
                print(c)

            try:
                cookies = self.driver.find_element_by_class_name('popup-ok')
                cookies.click()
            except Exception as c:
                print(c)

            driver_ajax = self.driver.find_element_by_id('singleFaresPane')
            driver_ajax.click()

            for row in result_table_out:
                yield {**{'url': url}, **self.__getRowInfo(row, "single", "out")}

            for row in result_table_ret:
                yield {**{'url': url}, **self.__getRowInfo(row, "single", "ret")}

    """
    lowest_only: Return only the lowest of its types/info
    from_code: From/departure station code
    to_code: To/arrival station code
    out_datetime: Outward datetime
    ret_datetime: Return datetime
    """
    def scrape(self, lowest_only: bool, from_code: str, to_code: str, out_datetime: datetime, ret_datetime: datetime = None) -> dict:
        date = out_datetime.strftime("%d%m%y")
        time = out_datetime.strftime("%H%M")

        if ret_datetime is not None:
            ret_date = ret_datetime.strftime("%d%m%Y")
            ret_time = ret_datetime.strftime("%H%M")
            ret = True
        else:
            ret_date = ""
            ret_time = ""
            ret = False

        url = self.__formUrl(from_code, to_code, date, time, ret_date, ret_time)
        try:
            self.driver.get(url)
        except Exception as e:
            print(e)
    
        source = self.driver.page_source

        try:
            if lowest_only:
                lowest = {}
                for row in self.__page_scrape(source, url, ret):
                    _type = row['type']
                    _type_l = _type+'_'+row['info']
                    if _type is not None and \
                            _type_l not in lowest or \
                            (float(row['fareTotal'][1:]) < float(lowest[_type_l]['fareTotal'][1:])):
                        lowest[_type_l] = row

                for name, row in lowest.items():
                    yield row
            else:
                yield from self.__page_scrape(source, url, ret)
        except Exception as e:
            raise Exception('Cannot scrape page error')

if __name__ == "__main__":
    try:
        s = Scraper("drivers/chromedriver_linux", 3)
        for x in s.scrape(True, "NRW", "LUT", datetime.datetime(2020, 2, 3, 15, 30), datetime.datetime(2020, 2, 7, 15, 15)):
            print(x)
    except Exception as e:
        print("error:", e)

