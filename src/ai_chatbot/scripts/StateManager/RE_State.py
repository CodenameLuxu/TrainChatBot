class RE_State:
    def __init__(self):
        self.data = {
            'uuid': '',  # cookie id
            'action': 'BOK',  # type of transaction
            'stage': 1,  # stage
            'stationFrom': '',  # departure station
            'stationTo': '',  # destination station
            'DepDate': '',  # departure date
            'DepTime': '',  # departure time
            'Response': ''
        } # Bot response