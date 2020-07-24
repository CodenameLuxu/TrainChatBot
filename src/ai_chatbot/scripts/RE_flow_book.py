from durable.lang import *
from flask import request
from ai_chatbot.scripts import REDataHeader as Header
from ai_chatbot.scripts import REResponseCode as ResponseCode
import ai_chatbot.scripts.RE_function_booking as rebook
import json
import datetime
import dateparser
from ai_chatbot.scraper.scraper import Scraper

STAGE_INIT = "1"
STAGE_VALIDATION = "2"
STAGE_VERIFICATION = "3"
STAGE_PROCESS = "4"
STAGE_TERMINATE = "5"

bookingJSON = {
    Header.RESPONSE_CODE: ResponseCode.NOT_PROCESS,
    Header.RESPONSE_DATA: 'Not process'
}

with ruleset('booking'):
    @when_all(m.data.Stage == STAGE_INIT)
    def init(c):
        c.m.data.Stage = STAGE_VALIDATION
        c.assert_fact(c.m)


    @when_all(m.data.Stage == STAGE_VALIDATION)
    def validation(c):
        missingData = rebook.missingDataCheck(c.m.data)
        if missingData == 0:
            c.m.data.Stage = STAGE_VERIFICATION
            c.assert_fact(c.m)
        else:
            bookingJSON = {
                Header.RESPONSE_CODE: ResponseCode.MISSING_INPUT,
                Header.RESPONSE_DATA: missingData
            }
            c.m.data[Header.RESPONSE_HEAD] = bookingJSON
            request.data = str(c.m.data).replace("\'", '\"')


    @when_all(m.data.Stage == STAGE_VERIFICATION)
    def verification(c):
        if rebook.verificationCheck(c.m.data) == 0:
            c.m.data.Stage = STAGE_PROCESS
            c.assert_fact(c.m)
        else:
            bookingJSON = {
                Header.RESPONSE_CODE: ResponseCode.VERIFICATION,
                Header.RESPONSE_DATA: {
                    'DEPART': c.m.data[Header.STATIONFROM],
                    'ARRIVAL': c.m.data[Header.STATIONTO],
                    'DATE': c.m.data[Header.DEPARTDATE],
                    'TIME': c.m.data[Header.DEPARTTIME],
                    'SINGLERETURN': c.m.data[Header.SINGLERETURN],
                    'RETURNDATE': c.m.data[Header.RETURNDATE],
                    'RETURNTIME': c.m.data[Header.RETURNTIME]
                }
            }
            c.m.data[Header.RESPONSE_HEAD] = bookingJSON
            request.data = str(c.m.data).replace("\'", '\"')


    @when_all(m.data.Stage == STAGE_PROCESS)
    def process(c):
        try:
            stationFroms = c.m.data.StationFrom.split("-")
            stationTos = c.m.data.StationTo.split("-")
            dateobject = dateparser.parse(c.m.data.DepDate)
            timeobject = dateparser.parse(c.m.data.DepTime)
            dateTimeObj = datetime.datetime.combine(dateobject.date(), timeobject.time())
            scrap = Scraper("../res/chromedriver.exe", 10)
            if c.m.data.ReturnDate != '':
                returndate = dateparser.parse(c.m.data.ReturnDate)
                returntime = dateparser.parse(c.m.data.ReturnTime)
                returndatetime = datetime.datetime.combine(returndate.date(), returntime.time())
                print(dateTimeObj.strftime(Header.FORMAT_DATETIME))
                scrapedArray = scrap.scrape(True, stationFroms[1], stationTos[1], dateTimeObj, returndatetime)
            else:
                print(dateTimeObj.strftime(Header.FORMAT_DATETIME))
                scrapedArray = scrap.scrape(True, stationFroms[1], stationTos[1], dateTimeObj)
            stringedArray = []
            for items in scrapedArray:
                stringedDict = {}
                for key, value in items.items():
                    stringedDict[key.__str__()] = value.__str__()
                stringedArray.append(stringedDict)
            bookingJSON = {
                Header.RESPONSE_CODE: ResponseCode.SUCESS_BOOKING,
                Header.RESPONSE_DATA: {
                    "date": c.m.data.DepDate,
                    "time": c.m.data.DepTime,
                    "result": stringedArray
                }
            }
            print('scapper array - {0}'.format(stringedArray))
            c.m.data[Header.RESPONSE_HEAD] = bookingJSON
            request.data = str(c.m.data).replace("\'", '\"')
            c.m.data.Stage = STAGE_TERMINATE
            c.assert_fact(c.m)
        except Exception as e:
            bookingJSON = {
                Header.RESPONSE_CODE: ResponseCode.NOT_PROCESS,
                Header.RESPONSE_DATA: 'error'
            }
            c.m.data[Header.RESPONSE_HEAD] = bookingJSON
            request.data = str(c.m.data).replace("'", '"')


    @when_all(m.data.Stage == STAGE_TERMINATE)
    def finalize(c):
        c.delete_state()
