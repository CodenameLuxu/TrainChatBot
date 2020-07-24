import scrapy
from scrapy.crawler import CrawlerProcess
import datetime

class TicketsSpider(scrapy.Spider):
    name = 'trainline'
    start_urls = ['https://www.thetrainline.com/']

    def parse(self, response):
        payload = {
                'from.text': 'Norwich',
                'to.text': 'Luton',
                'journeyType': 'single', # return openReturn
                'page.journeySearchForm.outbound.title': '28-Dec-19',
                'dateType': 'departAfter', # arriveBefore
                'hours': '08', # 00 - 23
                'minutes': '15', # 00, 15, 30, 45
                'page.journeySearchForm.inbound.title': ''
        }
        return scrapy.FormRequest.from_response(response, formdata=payload, callback=self.parse_tickets)

    def parse_tickets(self, response):
        print(response.text)

if __name__ == "__main__":
    process = CrawlerProcess(
        settings = {
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1'
        }
    )
    process.crawl(TicketsSpider)
    process.start()



