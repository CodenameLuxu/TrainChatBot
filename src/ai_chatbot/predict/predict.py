import dill, json, datetime, os
import numpy
from sklearn.preprocessing import StandardScaler, MinMaxScaler

"""
Predicts train arrival time at last station
__init__: model_name and data_type (see /res/models/*.dill)
            EX: knr01_np_model.dill = knr01, np
"""
class Predict():
    def __init__(self, model_name: str = 'knr01', data_type: str = 'np'):
        """
        cwd_name = os.getcwd().split('/')[-1]
        cwd_win_name = os.getcwd().split('\\')[-1]
        # If opened in src directory, move up by one
        if cwd_name == 'src' or cwd_win_name == 'src':
            on_root = '../'
        else:
            on_root = ''
        """

        self.data_type = data_type
        self.nn_mode = False

        with open('../res/models/' + model_name + '_' + data_type + '_model.dill', 'rb') as model_file:
            self.model = dill.load(model_file)

            if 'nnr_k' in model_name:
                self.nn_mode = True

        self.rel = {
            'NRW': 0,
            'DIS': 1,
            'SMK': 2,
            'IPS': 3,
            'MNG': 4,
            'COL': 5,
            'MKT': 6,
            'WTM': 7,
            'CHM': 8,
            'SNF': 9,
            'SRA': 10,
            'LST': 11
        }

    """
        times = seconds from midnight
        station = numerical order of station

        neural network version:
            times = split into binary array of hour and minutes
            station = binary array of station position

    X:
        Departure time planned
        Departure time actual
        Departure station
        Arrival time planned
        Arrival station
        Day of the week
        Day of the month
        Weekday/weekend  as weekend = 0 or 1        (Not used in neural network model)
        On-peak/Off-peak as offpeak = 0 or 1        (Not used in neural network model)
            (off-peak any time, excluding mornings and late afternoons/early evning weekday)
            See link for more info:
            https://www.thetrainline.com/train-times/off-peak 

    y:
        Arrival time actual

    parameters:
        departure_planned: str: Departure (Planned) time
        departure_actual: str: Departure (Actual) time
        departure_station: str:
        arrival_planned: str: Arrival (Planned) time
        arrival_station: str:
        intermediate_actual: str: Passing (Actual) time
        intermediate_station: str:
        date: datetime.datetime: The date (in YEAR/MM/DD) of the train running
    """

    """
    EX:
        Value of 2, max range of 4
        Returns array of:
            [0, 0, 1, 0]

    __binaryArray only used by neural network models (keras)
    """
    def __binaryArray(value: int, max_range: int):
        array = [0] * max_range
        array[value] = 1
        return array

    """
        Times in stringed format: "HH:MM"
        Stations are in three letter station code format: EX: "COL"
        Datetime: YYYY-MM-DD HH:MM must be all given in datetime.datetime class
    """
    def predict_nn(self,
            departure_planned: str,
            departure_actual: str,
            departure_station: str,
            arrival_planned: str,
            arrival_station: str,
            intermediate_actual: str,
            intermediate_station: str,
            date: datetime.datetime):

        departure_planned_h = int(departure_planned[0:2])
        departure_planned_m = int(departure_planned[3:5])
        departure_actual_h = int(departure_actual[0:2])
        departure_actual_m = int(departure_actual[3:5])
        arrival_planned_h = int(arrival_planned[0:2])
        arrival_planned_m = int(arrival_planned[3:5])
        intermediate_actual_h = int(intermediate_actual[0:2])
        intermediate_actual_m = int(intermediate_actual[3:5])

        alt_departure_station = self.rel[departure_station]
        alt_arrival_station = self.rel[arrival_station]
        alt_intermediate_station = self.rel[intermediate_station]

        hour = int(str(departure_actual)[0:2])
        dateparse = datetime.datetime.now()
        weekday = dateparse.weekday()
        day = dateparse.day
        month = dateparse.month

        offpeak = 0

        if weekday < 5:  # If it is in a Monday-Friday
            weekend = 0
            # 10:00-15:00 or 19:00-23:59
            if (hour >= 10 and hour <= 15) or (hour >= 19):
                offpeak = 1
        else:  # If it is a Saturday or Sunday
            weekend = 1
            offpeak = 1

        size_range = [24, 60, 24, 60, 12, 24, 60, 12, 24, 60, 12, 32, 13]
        new_X_col = [departure_planned_h, departure_planned_m,
                departure_actual_h, departure_actual_m,
                alt_departure_station,
                intermediate_actual_h, intermediate_actual_m,
                alt_intermediate_station,
                arrival_planned_h, arrival_planned_m,
                alt_arrival_station,
                date.day, date.month]
        bin_X = []

        # Uses __binaryArray to convert from integer to array of binary/booleans
        for c_i in range(0, len(new_X_col)):
            bin_X += Predict.__binaryArray(new_X_col[c_i], size_range[c_i])

        # Requires to convert from vertical array to horizontal
        bin_X = numpy.expand_dims(bin_X, axis=0)

        return self.model.predict([bin_X])

    """
        Times in stringed format: "HH:MM"
        Stations are in three letter station code format: EX: "COL"
        Datetime: YYYY-MM-DD HH:MM must be all given in datetime.datetime class
    """
    def predict(self,
            departure_planned: str,
            departure_actual: str,
            departure_station: str,
            arrival_planned: str,
            arrival_station: str,
            intermediate_actual: str,
            intermediate_station: str,
            date: datetime.datetime):

        # Ignores rest of this predict method and just use predict_nn if a neural network model
        if self.nn_mode:
            return self.predict_nn(departure_planned, departure_actual, departure_station, arrival_planned, arrival_station, intermediate_actual, intermediate_station, date)

        alt_departure_planned = Predict.csvtime2secsmidnight(departure_planned)
        alt_departure_actual = Predict.csvtime2secsmidnight(departure_actual)
        alt_departure_station = self.rel[departure_station]
        alt_arrival_planned = Predict.csvtime2secsmidnight(arrival_planned)
        alt_arrival_station = self.rel[arrival_station]
        alt_intermediate_actual = Predict.csvtime2secsmidnight(intermediate_actual)
        alt_intermediate_station = self.rel[intermediate_station]

        hour = int(str(departure_actual)[0:2])
        dateparse = datetime.datetime.now()
        weekday = dateparse.weekday()
        day = dateparse.day
        month = dateparse.month

        offpeak = 0

        if weekday < 5:  # If it is in a Monday-Friday
            weekend = 0
            # 10:00-15:00 or 19:00-23:59
            if (hour >= 10 and hour <= 15) or (hour >= 19):
                offpeak = 1
        else:  # If it is a Saturday or Sunday
            weekend = 1
            offpeak = 1

        X_data = [[alt_departure_planned,
                alt_departure_actual, alt_arrival_station,
                alt_intermediate_actual, alt_intermediate_station,
                alt_arrival_planned, alt_arrival_station,
                weekday, day, month, weekend, offpeak]]

        if self.data_type == 'sc':
            X_data = StandardScaler().fit_transform(X_data)
        elif self.data_type == 'mm':
            X_data = MinMaxScaler().fit_transform(X_data)

        return self.model.predict(X_data)[0]

    # Converts csv string time to seconds from midnight
    def csvtime2secsmidnight(csv_time: str) -> int:  # static method
        csv_datetime = datetime.datetime(2020, 1, 1, int(csv_time[0:2]), int(csv_time[3:5]))
        return int((csv_datetime - csv_datetime.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())

    def secsmidnight2csvtime(secsmidnight: int) -> str:  # static method
        if secsmidnight < 0:
            prefix = '-'
            secsmidnight = -secsmidnight
        else:
            prefix = ''

        m, s = divmod(secsmidnight, 60)
        h, m = divmod(m, 60)
        h = int(h)
        m = int(m)
        return prefix + str(f'{h:02d}:{m:02d}')

    # Gives differences in CSV time
    def diffcsvtime(self, arrival_planned: str, predicted_secsmidnight: int) -> str:
        from_midnight_arrival_planned = Predict.csvtime2secsmidnight(arrival_planned)
        print(str(from_midnight_arrival_planned) + ' => ' + str(predicted_secsmidnight))
        print('DIFF: ' + str(predicted_secsmidnight - from_midnight_arrival_planned))
        return Predict.secsmidnight2csvtime(predicted_secsmidnight - from_midnight_arrival_planned)


if __name__ == "__main__":
    pass
