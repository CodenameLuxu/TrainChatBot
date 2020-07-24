import requests

"""
timeOfOutwardJourney.arrivalOrDeparture
    DEPART
    ARRIVE
    FIRST
    LAST
timeOfOutwardJourney.monthDay
    Today
    DD/MM/YYYY
timeOfOutwardJourney.hour
    Range: 00 - 23
timeOfOutwardJourney.minute
    0 15 30 45


# Return section:

checkbox
    true/false
timeOfReturnJourney.arrivalOrDeparture
    DEPART
    ARRIVE
    FIRST
    LAST
timeOfReturnJourney.monthDay
    Today
    DD/MM/YYYY
timeOfReturnJourney.hour
    Range: 00 - 23
timeOfReturnJourney.minute
    0 15 30 45


# "More options, railcards & passengers" section

showFastestTrainsOnly
    true/false

## Passengers section
numberOfAdults
    0 to 8
numberOfChildren
    0 to 8
firstClass
    true/false
standardClass
    true/false
rcards
        Select a railcard (empty string)
    TSU 16-17 Saver 
    YNG 16-25 Railcard 
    TST 26-30 Railcard 
    NGC Annual Gold (Network Gold / South East) 
    DCR Devon &amp; Cornwall Railcard 
    DCG Devon &amp; Cornwall Gold Card 
    DIS Disabled Persons Railcard 
    FAM Family &amp; Friends Railcard 
    HRC Highland Railcard 
    HMF HM Forces Railcard 
    NDC JobCentre Plus Travel Discount Card 
    NDJ New Deal Photocard Scotland 
    NEW Network Railcard 
    SRN Senior Railcard 
    2TR Two Together Railcard 
numberOfEachRailcard
    0 to 8


## Journey section
offSetOption
    0   Use recommended
    1   1/2 hour extra
    2   1 hour extra
    3   1 hour 30 minutes extra
    4   2 hours extra
operator.code
       All Train Operators (empty string)
    CC c2c 
    CS Caledonian Sleeper 
    CH Chiltern Railways 
    XC CrossCountry 
    EM East Midlands Railway 
    ES Eurostar 
    GX Gatwick Express 
    GC Grand Central 
    GN Great Northern 
    GW Great Western Railway 
    LE Greater Anglia 
    HX Heathrow Express 
    HT Hull Trains 
    IL Island Line Trains 
    GR London North Eastern Railway                     
    LN London Northwestern Railway 
    LO London Overground 
    ME Merseyrail 
    NT Northern 
    SR ScotRail 
    SW South Western Railway 
    SE Southeastern 
    SN Southern 
    SX Stansted Express 
    XR TfL Rail 
    TP TransPennine Express 
    AW Transport for Wales                     
    TL Thameslink 
    VT Virgin Trains 
    WM West Midlands Railway 
reduceTransfers
    true/false
lookForSleeper
    true/false
directTrains
    true/false
"""

session = requests.Session()
params = { 
        'from.searchTerm' : 'Norwich', 'to.searchTerm' : 'Luton',
        'timeOfOutwardJourney.arrivalOrDeparture' : 'DEPART',
        'directTrains' : 'Today',
        'timeOfOutwardJourney.hour' : '07',
        'timeOfOutwardJourney.minute' : '15',
        'checkbox' : False
}

r1 = session.post("https://ojp.nationalrail.co.uk/service/planjourney/plan", data=params, allow_redirects=False)
if r1.status_code == 302:
    jar = r1.cookies
    r2_url = r1.headers['Location']
    r2 = session.get(r2_url, cookies=jar, allow_redirects=False)
    print(r2.text)

