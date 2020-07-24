from ai_chatbot.scripts import REDataHeader as Header
import dateparser
import datetime


def printData(data):
    print('Station from : {0}'.format(data[Header.STATIONFROM]))
    print('Station to : {0}'.format(data[Header.STATIONTO]))
    print('departure date : {0}'.format(data[Header.DEPARTDATE]))
    print('departure time  : {0}'.format(data[Header.DEPARTTIME]))

def datecheck(date):
    now = datetime.datetime.now()
    dateobject = dateparser.parse(date)
    if dateobject > now:
        return 0
    else:
        return 1

def returndatecheck(date, returndate):
    dateobject = dateparser.parse(date)
    returndateobject = dateparser.parse(returndate)
    if dateobject < returndateobject:
        return 0
    else:
        return 1

def timecheck(date, time):
    now = datetime.datetime.now()
    dateobject = dateparser.parse(date)
    timeobject = dateparser.parse(time)
    fullobject = datetime.datetime.combine(dateobject.date(), timeobject.time())
    if fullobject > now:
        return 0
    else:
        return 1

def missingDataCheck(data):
    if data[Header.STATIONFROM] == '':
        return Header.STATIONFROM
    elif data[Header.STATIONTO] == '':
        return Header.STATIONTO
    elif data[Header.DEPARTDATE] == '':
        return Header.DEPARTDATE
    elif datecheck(data[Header.DEPARTDATE]) == 1:
        data[Header.DEPARTDATE] = ''
        return Header.BADDATE
    elif data[Header.DEPARTTIME] == '':
        return Header.DEPARTTIME
    elif timecheck(data[Header.DEPARTDATE], data[Header.DEPARTTIME]) == 1:
        data[Header.DEPARTDATE] = ''
        data[Header.DEPARTTIME] = ''
        return Header.BADTIME
    elif data[Header.SINGLERETURN].lower() == '':
        return Header.SINGLERETURN
    elif data[Header.SINGLERETURN].lower() == 'return':
        if data[Header.RETURNDATE] == '':
            return Header.RETURNDATE
        elif returndatecheck(data[Header.DEPARTDATE], data[Header.RETURNDATE]) == 1:
            data[Header.RETURNDATE] = ''
            return Header.BADDATE
        elif data[Header.RETURNTIME] == '':
            return Header.RETURNTIME
        return 0
    else:
        return 0


def verificationCheck(data):
    if data[Header.CONFIRMED] == 'true':
        return 0
    return 1


def getURL(data):
    # call function in scraper/scraper.py
    print('Getting URL for...')
    print('\t {0} --> {1}'.format(data.stationFrom, data.stationTo))
    print('\t Departure date : {0}'.format(data.DepDate))
    print('\t Departure time : {0}'.format(data.DepTime))
