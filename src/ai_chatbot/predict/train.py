"""
Using this file:
    python train.py {store|load} {store|load} {np|sc|mm} [models...]
        scikit-learn models:
            knrXX       k neighbors regression | XX = nth (EX: 01, 05, 11)
            gpr         Guassian process regression
            dtr         Decision Tree Regression
            svr         Epsilon-Support Vector Regression
            nnr_ras     Artifical neural network (scikit-learn)
            nnr_rad     Deep neural network (scikit-learn)
            sgd         Stochastic Gradient Descent (with squared loss)
            sgdh        ... with huber loss
            sgdei       ... with epsilon insensitive loss
            vr          Voting regressor (knr15, dtr, nnr)

        keras models:
            nnr_kb      Artifical neural network (baseline)
            nnr_kw      Artifical neural network (wide)
            nnr_kd      Deep neural network
            nnr_kdw     Deep neural network (wide)

    First store|load: Stores/loads train data file
    Second store|load: Stores/loads training and test datas
    np|sc|mm: No scaler, StandardScaler, MinMaxScaler
"""

import datetime, csv, sys, json, dill, time
from enum import Enum
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy
from sklearn import preprocessing, metrics
from sklearn.neighbors import KNeighborsRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import SGDRegressor
from sklearn.ensemble import VotingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, median_absolute_error, explained_variance_score
from math import sqrt
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score, KFold

from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor

"""
DARWIN table:
    rid     Train RTTI Train Identifier
    tpl     Location TIPLOC
    pta     Planned Time of Arrival
    ptd     Planned Time of Departure
    wta     Working (staff) Time of Arrival
    wtp     Working Time of Passing
    wtd     Working Time of Departure
    arr_et  Estimated Arrival Time
    arr_wet Working Estimated Time
    arr_atRemoved   True if actual replaced by estimated
    pass_et Estimated Passing Time
    pass_wet    Working Estimated Time
    pass_atRemoved  True if actual replaced by estimated
    dep_et  Estimated Departure
    dep_wet Working Estimated Time
    dep_atRemoved   True if actual replaced by estimated
    arr_at  Recorded Actual Time of Arrival
    pass_at Actual passing time
    dep_at  Actual departure time
    cr_code Cancellation Reason Code
    lr_code Late Running Reason

scikit-learn:
    https://scikit-learn.org/stable/modules/neighbors.html
"""

"""
    keras neural network models

    baseline (artifical neural network)
    wide (wider artifical neural network): double size of input as baseline
    deep (deep neural network)
    deepwide (wider deep neural network): double size of inputs as deep
"""
def baseline_model():
    model = Sequential()
    model.add(Dense(417, input_dim=417, activation='relu'))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mse', optimizer='adam')
    return model

def wide_model():
    model = Sequential()
    model.add(Dense(833, input_dim=417, activation='relu'))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mse', optimizer='adam')
    return model

def deep_model():
    model = Sequential()
    model.add(Dense(417, activation='relu'))
    model.add(Dense(417, activation='relu'))
    model.add(Dense(417, activation='relu'))
    model.add(Dense(417, activation='relu'))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mse', optimizer='adam')
    return model

def deepwide_model():
    model = Sequential()
    model.add(Dense(833, activation='relu'))
    model.add(Dense(833, activation='relu'))
    model.add(Dense(833, activation='relu'))
    model.add(Dense(833, activation='relu'))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mse', optimizer='adam')
    return model


"""
EX:
    Value of 2, max range of 4
    Returns array of:
        [0, 0, 1, 0]

__binaryArray only used by neural network models (keras)
"""
def binaryArray(value: int, max_range: int):
    array = [0] * max_range
    array[value] = 1
    return array

"""
Metrics used to determine the errors and scores of a model by the test/actual y data vs predicted y data
"""
def measurements(y_test, y_pred):
    print("root mean squared error: ", mean_squared_error(y_test, y_pred, squared=False))
    print("mean absolute error: ", mean_absolute_error(y_test, y_pred))
    print("median absolute error: ", median_absolute_error(y_test, y_pred))
    print("r2score ", r2_score(y_test, y_pred))

"""
Seconds from midnight to "HH:MM" string format
"""
def secsmidnight2csvtime(secsmidnight: int) -> str: # static method
    if secsmidnight < 0:
        prefix = '-'
        secsmidnight = -secsmidnight
    else:
        prefix = ''

    m, s = divmod(secsmidnight, 60)
    h, m = divmod(m, 60)
    h = int(h)
    m = int(m)
    return prefix+str(f'{h:02d}:{m:02d}')

"""
"HH:MM" string format to seconds from midnight
"""
def csvtime2secsmidnight(csv_time: str) -> int:
    csv_datetime = datetime.datetime(2020, 1, 1, int(csv_time[0:2]), int(csv_time[3:5]))
    return int((csv_datetime - csv_datetime.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())

"""
Converts RID to date and ID/unique number
EX: 201701037101237
    To:
        Date:   2017-01-03
        ID:     7101237
"""
def csv_date2date_id(csv_date: str) -> dict:
    return {'date': datetime.date(int(csv_date[0:4]), int(csv_date[4:6]), int(csv_date[6:8])),
            'id': csv_date[8:]}

"""
Reads the CSV file and returns a dictionary of a list of all trains rids and all trains journey
"""
def read_csv(csv_path: str) -> dict:
    with open(csv_path, newline='') as csv_file:
        headers = []
        prev_rid: str = ''
        first: bool = True
        full_list = {}
        rid_list = []

        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            if first:
                for h in row:
                    headers.append(h)
                first = False
            else:
                row_dict: dict = dict()

                cur_rid: str = row[0]
                for i in range(1, len(row)):
                    row_dict[headers[i]] = row[i]

                if prev_rid != cur_rid:
                    full_list[cur_rid] = [row_dict]
                    di_dict = csv_date2date_id(cur_rid)
                    rid_list.append({'rid': cur_rid, 'date': di_dict['date'], 'uid': di_dict['id']})
                    prev_rid = cur_rid
                else:
                    full_list[cur_rid].append(row_dict)

        return {'all': full_list, 'rids': rid_list}

"""
Reads the CSV files and put them into a better train dictionary format than read_csv
"""
def multi_csvread(min_ym: dict, max_ym: dict, verbose: bool, src: str = 'a51') -> list:
    cur_ym = min_ym
    running = True
    extracted_data = []
    train_extracted_data = []
    stn_num = 0

    while running:
        if verbose:
            print(cur_ym['y'], cur_ym['m'])
        csv_dict = read_csv('../../../res/train_data/'+src+'/NRCH_LIVST_OD_'+src+'_'+str(cur_ym['y'])+'_'+str(cur_ym['m'])+'_'+str(cur_ym['m'])+'.csv')
        for train in csv_dict['rids']:
            rid = train['rid']
            stn_num = 0
            time_type = 'actual'
            train_extracted_data = []

            for station in csv_dict['all'][rid]:
                # Cancelled train
                if station['cr_code'] != '':
                    time_type = 'cancelled:'+station['cr_code']
                    break

                # Stopping/intermediate stations
                if station['pta'] != '' and station['ptd'] != '':
                    arr_t = station['arr_at']
                    dep_t = station['dep_at']
                    p_arr_t = station['pta']
                    p_dep_t = station['ptd']

                    # Use estimation time if actual time not available
                    if arr_t == '' or dep_t == '':
                        time_type = 'hasestimate'
                        arr_t = station['arr_et']
                        dep_t = station['dep_et']

                        # Discard data if unable to be used
                        if arr_t == '' or dep_t == '':
                            time_type == 'error'
                            break

                # Departure station
                elif station['ptd'] != '' and station['tpl'] == 'NRCH':
                    arr_t = None
                    dep_t = station['dep_at']
                    p_arr_t = None
                    p_dep_t = station['ptd']

                    # Use estimation time if actual time not available
                    if dep_t == '':
                        time_type = 'hasestimate'
                        dep_t = station['dep_et']

                        # Discard data if unable to be used
                        if dep_t == '':
                            time_type == 'error'
                            break

                # Arrival station
                elif station['pta'] != '' and station['tpl'] == 'LIVST':
                    arr_t = station['arr_at']
                    dep_t = None
                    p_arr_t = station['pta']
                    p_dep_t = None

                    # Use estimation time if actual time not available
                    if arr_t == '':
                        time_type = 'hasestimate'
                        arr_t = station['arr_et']

                        # Discard data if unable to be used
                        if arr_t == '':
                            time_type == 'error'
                            break

                # Passing stations, ignore
                else:
                    continue

                #print(stn_num, station['tpl'], p_arr_t, p_dep_t, arr_t, dep_t)
                """
                num: station number
                tpl: station code
                pla_a: Planned Arrival
                pla_d: Planned Departure
                act_a: Actual Arrival
                act_d: Actual Departure
                """
                train_extracted_data.append({
                        'num': stn_num,
                        'tpl': station['tpl'],
                        'pla_a': p_arr_t,
                        'pla_d': p_dep_t,
                        'act_a': arr_t,
                        'act_d': dep_t
                    })
                stn_num += 1

            extracted_data.append({'rid': rid, 'date': train['date'], 'type': time_type, 'stations': train_extracted_data})

        cur_ym['m'] += 1
        if cur_ym['m'] >= 13:
            cur_ym['y'] += 1
            cur_ym['m'] = 1

        # Year month threshold achieved, stop running
        if cur_ym['y'] >= max_ym['y'] and cur_ym['m'] >= max_ym['m']:
            running = False

    return extracted_data

"""
Run this file in order to train the datat
"""
if __name__ == "__main__":
    # MIN: 2017, 1 | MAX: 2019, 5
    min_ym = {'y': 2017, 'm': 1}
    max_ym = {'y': 2019, 'm': 5}
    min_ym2 = {'y': 2017, 'm': 1}
    max_ym2 = {'y': 2018, 'm': 7}

    rel_stations = {
        'NRCH' : 0,
        'DISS' : 1,
        'STWMRKT' : 2,
        'IPSWICH' : 3,
        'MANNGTR' : 4,
        'CLCHSTR' : 5,
        'MRKSTEY' : 6,
        'WITHAME' : 7,
        'CHLMSFD' : 8, 
        'SHENFLD' : 9,
        'STFD' : 10,
        'LIVST' : 11
    }
    
    verbose = False
    modelfit = True
    cont = True

    try: 
        # Create train dump
        if sys.argv[1] == 'store':
            exdata = multi_csvread(min_ym, max_ym, verbose)
            exdata += multi_csvread(min_ym2, max_ym2, verbose, 'rdg')
            with open('traindatadump.dill', 'wb') as ouf:
                dill.dump(exdata, ouf)
        # Load train dump from previous session
        elif sys.argv[1] == 'load':
            with open('traindatadump.dill', 'rb') as inf:
                exdata = dill.load(inf)
    except Exception as e:
        print('specify "load" or "store" csv data')
        sys.exit()

    X = []
    X_preproc_first = []
    X_preproc_second = []
    y = []

    X_bin = []
    y_bin = []

    try:
        arg2 = sys.argv[2]
    except Exception as e:
        print('arg2: state "store" or "load" Xy dump file')
        sys.exit()

    if arg2 == 'store':
        trains_skipped = 0
        trains_num = 0

        for train in exdata:
            if 'cancelled' not in train['type']:
                """
                    times = seconds from midnight

                X:
                    Departure time planned
                    Departure time actual
                    Departure station
                    Arrival time planned
                    Arrival station
                    Day of the week
                    Day of the month
                    Weekday/weekend  as weekend = 0 or 1
                    On-peak/Off-peak as offpeak = 0 or 1
                        (off-peak any time, excluding mornings and late afternoons/early evning weekday)
                        See link for more info:
                        https://www.thetrainline.com/train-times/off-peak 
                    #Hour of the day

                y:
                    Arrival time actual
                """

                date = train['date']
                weekday = date.weekday()
                try:
                    hour = int(train['stations'][0]['act_d'][0:2])
                except Exception as e:
                    trains_skipped += 1
                    break       # skip train
                trains_num += 1
                offpeak = 0

                if weekday < 5:
                    weekend = 0
                    if (hour >= 10 and hour <= 15) or (hour >= 19):
                        offpeak = 1
                else:
                    weekend = 1
                    offpeak = 1

                # Intermediate = passing station
                for x_i in range(0, (len(train['stations']) - 1)):          # Departure station loop
                    for y_i in range(x_i+1, len(train['stations'])):        # Arrival station loop
                        for z_i in range(x_i, y_i - 1):                     # Intermediate station loop (between (or within) departure and arrival)
                            csv_pla_d = train['stations'][x_i]['pla_d']     # Planned departure time
                            csv_act_d = train['stations'][x_i]['act_d']     # Actual departure time
                            csv_pla_a = train['stations'][y_i]['pla_a']     # Planned arrival time
                            csv_act_a = train['stations'][y_i]['act_a']     # Actual arrival time
                            csv_act_i = train['stations'][z_i]['act_d']     # Actual intermediate departure time
                            csv_dep_st = train['stations'][x_i]['tpl']      # Departure station code
                            csv_arr_st = train['stations'][y_i]['tpl']      # Arrival station code
                            csv_int_st = train['stations'][z_i]['tpl']      # Intermediate station code

                            # For other regression models (scikit-learn)
                            pla_d = csvtime2secsmidnight(csv_pla_d)
                            act_d = csvtime2secsmidnight(csv_act_d)
                            pla_a = csvtime2secsmidnight(csv_pla_a)
                            act_a = csvtime2secsmidnight(csv_act_a)
                            act_i = csvtime2secsmidnight(csv_act_i)
                            dep_st = rel_stations[csv_dep_st]
                            arr_st = rel_stations[csv_arr_st]
                            int_st = rel_stations[csv_int_st]

                            # For neural network (keras)
                            pla_d_h = int(csv_pla_d[0:2])
                            pla_d_m = int(csv_pla_d[3:5])
                            act_d_h = int(csv_act_d[0:2])
                            act_d_m = int(csv_act_d[3:5])
                            pla_a_h = int(csv_pla_a[0:2])
                            pla_a_m = int(csv_pla_a[3:5])
                            act_a_h = int(csv_act_a[0:2])
                            act_a_m = int(csv_act_a[3:5])
                            act_i_h = int(csv_act_i[0:2])
                            act_i_m = int(csv_act_i[3:5])

                            if act_a != pla_a:
                                # TEST
                                print([csv_pla_d, csv_act_d, csv_dep_st, csv_act_i, csv_int_st, csv_pla_a, csv_arr_st, weekday, date.day, date.month, weekend, offpeak], csv_act_a)
                                #print([pla_d, act_d, dep_st, act_i, int_st, pla_a, arr_st, weekday, date.day, date.month, weekend, offpeak], act_a)
                                X.append([pla_d, act_d, dep_st, act_i, int_st, pla_a, arr_st, weekday, date.day, date.month, weekend, offpeak])
                                y.append(act_a)

                                #size_range = [24, 60, 24, 60, 12, 24, 60, 12, 24, 60, 12, 7, 32, 13, 2, 2]
                                #new_X_col = [pla_d_h, pla_d_m, act_d_h, act_d_m, dep_st, act_i_h, act_i_m, int_st, pla_a_h, pla_a_m, arr_st, weekday, date.day, date.month, weekend, offpeak]
                                size_range = [24, 60, 24, 60, 12, 24, 60, 12, 24, 60, 12, 32, 13]
                                new_X_col = [pla_d_h, pla_d_m, act_d_h, act_d_m, dep_st, act_i_h, act_i_m, int_st, pla_a_h, pla_a_m, arr_st, date.day, date.month]
                                bin_new_X_col = []

                                for c_i in range(0, len(new_X_col)):
                                    bin_new_X_col += binaryArray(new_X_col[c_i], size_range[c_i])

                                X_bin.append(bin_new_X_col)
                                delay_mins, s = divmod(pla_a - act_a, 60)
                                y_bin.append(delay_mins)

        print('Trains skipped: '+str(trains_skipped))
        print('samples: '+str(len(X)))
        print('trains: '+str(trains_num))

        """
        Split into train and test sets, 80% train, 20% test
        sc = Standard scaler
        mm = Min max scaler
        bin = Binary array (neural network only)
        """
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        X_sc_train, X_sc_test, y_sc_train, y_sc_test = train_test_split(X, y, test_size=0.2)
        X_mm_train, X_mm_test, y_mm_train, y_mm_test = train_test_split(X, y, test_size=0.2)
        X_bin_train, X_bin_test, y_bin_train, y_bin_test = train_test_split(X_bin, y_bin, test_size=0.2)

        # preprocessing
        ss = StandardScaler()
        X_sc_train = ss.fit_transform(X_sc_train)
        X_sc_test = ss.transform(X_sc_test)

        mm = MinMaxScaler()
        X_mm_train = mm.fit_transform(X_mm_train)
        X_mm_test = mm.transform(X_mm_test)

        with open('train_xy_dump.dill', 'wb') as xy_file:
            dill.dump(X_train, xy_file)
            dill.dump(X_test, xy_file)
            dill.dump(y_train, xy_file)
            dill.dump(y_test, xy_file)

            dill.dump(X_sc_train, xy_file)
            dill.dump(X_sc_test, xy_file)
            dill.dump(y_sc_train, xy_file)
            dill.dump(y_sc_test, xy_file)

            dill.dump(X_mm_train, xy_file)
            dill.dump(X_mm_test, xy_file)
            dill.dump(y_mm_train, xy_file)
            dill.dump(y_mm_test, xy_file)

            dill.dump(X_bin_train, xy_file)
            dill.dump(X_bin_test, xy_file)
            dill.dump(y_bin_train, xy_file)
            dill.dump(y_bin_test, xy_file)
    elif arg2 == 'load':
        with open('train_xy_dump.dill', 'rb') as xy_file:
            X_train = dill.load(xy_file)
            X_test = dill.load(xy_file)
            y_train = dill.load(xy_file)
            y_test = dill.load(xy_file)

            X_sc_train = dill.load(xy_file)
            X_sc_test = dill.load(xy_file)
            y_sc_train = dill.load(xy_file)
            y_sc_test = dill.load(xy_file)

            X_mm_train = dill.load(xy_file)
            X_mm_test = dill.load(xy_file)
            y_mm_train = dill.load(xy_file)
            y_mm_test = dill.load(xy_file)

            X_bin_train = dill.load(xy_file)
            X_bin_test = dill.load(xy_file)
            y_bin_train = dill.load(xy_file)
            y_bin_test = dill.load(xy_file)

    plt.title('Model loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    legends = []

    type_pre = sys.argv[3]
    if type_pre != 'sc' and type_pre != 'mm':
        type_pre = 'np'
    regressor = sys.argv[4:]
    if len(regressor) == 0:
        print('arg3+: specify a regressor model list: either: knrXX, gpr, dtr, svr, nnr')
    else:
        # https://scikit-learn.org/stable/supervised_learning.html#supervised-learning
        for i in range(0, len(regressor)):
            print("doing... "+regressor[i])
            timebef = time.time()
            # https://scikit-learn.org/stable/modules/neighbors.html#nearest-neighbors-regression
            if regressor[i][0:3] == 'knr':
                model = KNeighborsRegressor(n_neighbors=int(regressor[i][3:5]))
            # https://scikit-learn.org/stable/modules/gaussian_process.html#gaussian-process-regression-gpr
            elif regressor[i] == 'gpr':
                model = GaussianProcessRegressor()
            # https://scikit-learn.org/stable/modules/tree.html#regression
            elif regressor[i] == 'dtr':
                model = DecisionTreeRegressor()
            # https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVR.html
            # very long to process
            elif regressor[i] == 'svr':
                model = SVR()
            # https://scikit-learn.org/stable/modules/neural_networks_supervised.html#regression
            elif regressor[i] == 'nnr_ras':         # shallow neural network
                model = MLPRegressor(hidden_layer_sizes=(64, 128, 48), activation='relu', solver='adam', max_iter=2000)
            elif regressor[i] == 'nnr_rad':         # deep neural network
                model = MLPRegressor(hidden_layer_sizes=(128, 128, 128, 128, 48), activation='relu', solver='adam', max_iter=4000)
            elif 'nnr_k' in regressor[i]:           # keras regressor
                X_bin_train_np = numpy.array(X_bin_train)
                y_bin_train_np = numpy.array(y_bin_train)
                X_bin_test_np = numpy.array(X_bin_test)
                y_bin_test_np = numpy.array(y_bin_test)

                estimators = []
                if type_pre == 'sc':
                    estimators.append(('standardise', StandardScaler()))

                if regressor[i] == 'nnr_kb':
                    print("base model")
                    #estimators.append(('mlp', KerasRegressor(build_fn=baseline_model, epochs=100, batch_size=100, verbose=True)))
                    model = KerasRegressor(build_fn=baseline_model, epochs=100, batch_size=100, verbose=True)
                elif regressor[i] == 'nnr_kd':
                    print("deep model")
                    #estimators.append(('mlp', KerasRegressor(build_fn=deep_model, epochs=100, batch_size=100, verbose=True)))
                    model = KerasRegressor(build_fn=deep_model, epochs=100, batch_size=100, verbose=True)
                elif regressor[i] == 'nnr_kw':
                    print("wide model")
                    #estimators.append(('mlp', KerasRegressor(build_fn=wide_model, epochs=100, batch_size=100, verbose=True)))
                    model = KerasRegressor(build_fn=wide_model, epochs=100, batch_size=100, verbose=True)
                elif regressor[i] == 'nnr_kdw':
                    print("deep wide model")
                    #estimators.append(('mlp', KerasRegressor(build_fn=deepwide_model, epochs=30, batch_size=100, verbose=True)))
                    model = KerasRegressor(build_fn=deepwide_model, epochs=30, batch_size=100, verbose=True)
                else:
                    print("error, nnr_kb or nnr_kd only")
                    break

                #kfold = KFold(n_splits=2)
                #results = cross_val_score(model, X_bin_train_np, y_bin_train_np, cv=kfold)
                #print("Results: %.2f (%.2f) MSE" % (results.mean(), results.std()))
                print(X_bin_train_np[0])
                print(y_bin_train_np[0])

                history = model.fit(X_bin_train_np, y_bin_train_np)
                y_pred = model.predict(X_bin_test_np) 
                measurements(y_bin_test_np, y_pred)

                # Plot training & validation loss values
                plt.plot(history.history['loss'])
                legends.append(regressor[i])


            # https://scikit-learn.org/stable/modules/sgd.html#regression
            elif regressor[i] == 'sgd':
                model = SGDRegressor()
            elif regressor[i] == 'sgdh':
                model = SGDRegressor(loss="huber", max_iter=50000)
            elif regressor[i] == 'sgdei':
                model = SGDRegressor(loss="epsilon_insensitive", max_iter=10000)
            # https://scikit-learn.org/stable/modules/ensemble.html#voting-regressor
            elif regressor[i] == 'vr':
                model = VotingRegressor(estimators=[('knr', KNeighborsRegressor(n_neighbors=15)), ('dtr', DecisionTreeRegressor()), ('nnr', MLPRegressor())])
            else:
                print(regressor[i], "not found")
                continue

            if 'nnr_k' not in  regressor[i]:
                if type_pre == 'sc':
                    print(regressor[i], "- standardised")
                    model.fit(X_sc_train, y_sc_train)
                    y_sc_pred = model.predict(X_sc_test) 
                    measurements(y_sc_test, y_sc_pred)
                elif type_pre == 'mm':
                    print(regressor[i], "- minmax")
                    model.fit(X_mm_train, y_mm_train)
                    y_mm_pred = model.predict(X_mm_test) 
                    measurements(y_mm_test, y_mm_pred)
                else:
                    print(regressor[i], "- no preprocessing")
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test) 
                    measurements(y_test, y_pred)
                    type_pre = 'np'

            with open('../../../res/models/'+regressor[i]+'_'+type_pre+'_model.dill', 'wb') as model_file:
                dill.dump(model, model_file)
                print("saved as: "+regressor[i]+'_'+type_pre+'_model.dill')
            print("time taken: "+str(time.time()-timebef)+" seconds")

    # Creates the graph as an image
    plt.legend(legends, loc='upper left')
    plt.savefig('nnr_history.png')


