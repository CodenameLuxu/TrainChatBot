import pytest

from predict import Predict
import datetime

def test_predict():
    for nm in ['nnr_k']:
        p = Predict(nm, 'np')
        departure_planned = '08:17'
        departure_actual = '08:17'
        departure_station = 'DIS'
        intermediate_actual = '09:02'
        intermediate_station = 'COL'
        arrival_planned = '10:05'
        arrival_actual = '10:11'
        arrival_station = 'LST'

        for m in range(1, 13):
            arrival_predict = p.predict(departure_planned, departure_actual, departure_station,
                    arrival_planned, arrival_station,
                    intermediate_actual, intermediate_station,
                    datetime.datetime(2020, m, 1))
        print(arrival_predict)
        #print(nm, Predict.secsmidnight2csvtime(arrival_predict), arrival_actual)

if __name__ == "__main__":
    test_predict()

