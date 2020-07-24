from builtins import int

from datetime import datetime

import dateparser
from ai_chatbot.scripts import REDataHeader as Header
from ai_chatbot.predict.predict import Predict as delay


def delay_say():
    print('Delay')


def printData(data):
    print('Station from : {0}'.format(data[Header.STATIONFROM]))
    print('Station to : {0}'.format(data[Header.STATIONTO]))
    print('departure date : {0}'.format(data[Header.DEPARTDATE]))
    print('departure time  : {0}'.format(data[Header.DEPARTTIME]))
    print('Arrival time  : {0}'.format(data[Header.ARRTIME]))
    print('Station At  : {0}'.format(data[Header.STATIONAT]))
    print('Station At Time  : {0}'.format(data[Header.STATIONATTIME]))


def missingDataCheck(data):
    if data[Header.STATIONFROM] == '':
        return Header.STATIONFROM
    if data[Header.DEPARTTIME] == '':
        return Header.DEPARTTIME
    if data[Header.ACTUALDEPART] == '':
        return Header.ACTUALDEPART
    if data[Header.STATIONTO] == '':
        return Header.STATIONTO
    elif data[Header.ARRTIME] == '':
        return Header.ARRTIME
    elif data[Header.STATIONAT] == '':
        return Header.STATIONAT
    elif data[Header.STATIONATTIME] == '':
        return Header.STATIONATTIME
    else:
        return 0


def delay_predict(data):
    print('Predicting delay for journey :')
    print('\t {0} --> {1}'.format(data[Header.STATIONAT], data[Header.STATIONTO]))
    delayObject = delay('dtr', 'np')
    stationFroms = data[Header.STATIONFROM].split("-")
    stationTos = data[Header.STATIONTO].split("-")
    stationInter = data[Header.STATIONAT].split("-")
    delayAmount = delayObject.predict(
        dateparser.parse(data[Header.DEPARTTIME]).time().__str__(),
        dateparser.parse(data[Header.ACTUALDEPART]).time().__str__(),
        stationFroms[1].upper(),
        dateparser.parse(data[Header.ARRTIME]).time().__str__(),
        stationTos[1].upper(),
        dateparser.parse(data[Header.STATIONATTIME]).time().__str__(),
        stationInter[1].upper(),
        datetime.now()
    )
    print(delayAmount)
    amount = delayObject.diffcsvtime(dateparser.parse(data[Header.ARRTIME]).time().__str__(), delayAmount)
    return amount
