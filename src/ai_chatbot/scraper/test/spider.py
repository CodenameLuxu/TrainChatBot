import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
import datetime

class TicketsSpider(scrapy.Spider):
    name = 'tickets-spider'
    start_urls = ['https://www.nationalrail.co.uk/']

    def parse(self, response):
        from_ = "NRW"
        from_full = "Norwich"
        to = "LUT"
        to_full = "Luton"
        out_datetime = datetime.datetime(2020, 1, 1, 10, 15)
        ret_datetime = None
        """
        from_ = 'NRW'
        from_full = "Norwich"
        to = 'LUT'
        to_full = "Luton"
        """
        num_adults = 1

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

        payload.update({"numberOfAdults":str(num_adults),"numberOfChildren":"0",
                "firstClass":"true","_firstClass":"on",
                "standardClass":"true","_standardClass":"on",
                "railcardCodes":"","numberOfEachRailcard":"0",
                "oldRailcardCodes":"",
                "viaMode":"VIA","via.searchTerm":"Station","via1Mode":"VIA","via1.searchTerm":"Station","via2Mode":"VIA","via2.searchTerm":"Station","offSetOption":"0","operator.code":"","_reduceTransfers":"on","_lookForSleeper":"on","_directTrains":"on","_showFastestTrainsOnly":"on"})

        return scrapy.FormRequest.from_response(response, formdata=payload, callback=self.parse_tickets)

    def parse_tickets(self, response):
        print(response.text)

# For testing purpose
if __name__ == "__main__":
    process = CrawlerProcess(
        settings = {
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1'
        }
    )
    process.crawl(TicketsSpider)
    process.start()




