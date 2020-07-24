from durable.lang import *
from ai_chatbot.scripts import REResponseCode as ResponseCode
from ai_chatbot.scripts import REDataHeader as Header
from ai_chatbot.scripts import RE_flow_book
from ai_chatbot.scripts import RE_flow_delay
from ai_chatbot.scripts import RE_flow_QnA
from flask import request
import json
from ai_chatbot.scripts import RE_function_booking as bkfunc
from ai_chatbot.scripts.StateManager import StateManager
from dateutil import parser
from datetime import date
from ai_chatbot.scripts.RE_flow_book import STAGE_VERIFICATION
from ai_chatbot.scripts.QuestionDomain.QuestionTree import QuestionTree


class ReasoningEngine:
    action = {
        'BOK': 'booking',
        'DEL': 'delay',
        'QUE': 'question'
    }

    def __init__(self):
        print('Initilizing RE')

    def tokenToData(self, current, tokens):
        data = {
            Header.ACTION: '',  # type of transaction
            Header.STAGE: 1,  # stage
            Header.STATIONFROM: '',  # departure station
            Header.STATIONTO: '',  # destination station
            Header.DEPARTDATE: '',  # departure date
            Header.DEPARTTIME: '',  # departure time
            Header.ARRTIME: '',
            Header.STATIONAT: '',
            Header.STATIONATTIME: '',
            Header.CONFIRMED: '',
            Header.SINGLERETURN: '',
            Header.RETURNDATE: '',
            Header.RETURNTIME: '',
            Header.QUESTION : '' ,
            Header.QUESTIONSEARCHING : 0,
            Header.QUESTIONTREE : '',
            Header.ACTUALDEPART: '',
            Header.RESPONSE_HEAD: {
                Header.RESPONSE_CODE: 0,
                Header.RESPONSE_DATA: ''
            }
        }

        if not Header.STAGE in current:
            current = data

        for ent in tokens.ents:
            print(' {0} - {1} - {2}'.format(ent.label_, ent.text, ent.ent_id_))
            if (ent.label_ == 'BOK') or (ent.label_ == 'DEL') or (ent.label_ == 'QUE'):
                data[Header.ACTION] = ent.label_
                if data[Header.ACTION] == 'DEL':
                    data[Header.DEPARTDATE] = date.today().__str__().replace('-', '/')
                elif ent.label_ == 'QUE':
                    mergedtokens = [token.text for token in tokens]
                    data[Header.QUESTION] = ' '.join(mergedtokens)
            elif (ent.label_ == 'DEP'):
                data[Header.STATIONFROM] = ent.text + '-' + ent.ent_id_
            elif (ent.label_ == 'ARR'):
                data[Header.STATIONTO] = ent.text + '-' + ent.ent_id_
            elif (ent.label_ == 'STN'):
                if current[Header.STATIONFROM] == '' and data[Header.STATIONFROM] == '':
                    data[Header.STATIONFROM] = ent.text + '-' + ent.ent_id_
                elif current[Header.STATIONTO] == '' and current[Header.STATIONFROM] != ent.text:
                    data[Header.STATIONTO] = ent.text + '-' + ent.ent_id_
                elif current[Header.ACTION] == 'DEL' or data[Header.ACTION] == 'DEL':
                    if ent.ent_id_ != "lst" or ent.ent_id_ != "nrw":
                        data[Header.STATIONAT] = ent.text + '-' + ent.ent_id_
            elif ent.label_ == 'TICKET':
                data[Header.SINGLERETURN] = ent.ent_id_
            elif ent.label_ == 'DATE':
                if current[Header.DEPARTDATE] == '':
                    data[Header.DEPARTDATE] = self.strip_datetime_string(ent.text)
                elif current[Header.ACTION] == 'BOK' and current[Header.RETURNDATE] == '':
                    data[Header.RETURNDATE] = self.strip_datetime_string(ent.text)
            elif ent.label_ == 'TIME':
                if (current[Header.DEPARTTIME] == ''):
                    data[Header.DEPARTTIME] = ent.text
                elif (current[Header.ACTION] == 'DEL') or (data[Header.ACTION] == 'DEL'):
                    if current[Header.ACTUALDEPART] == '':
                        data[Header.ACTUALDEPART] = ent.text
                    elif (current[Header.ARRTIME] == ''):
                        data[Header.ARRTIME] = ent.text
                    else:
                        data[Header.STATIONATTIME] = ent.text
                elif current[Header.ACTION] == 'BOK' and current[Header.RETURNTIME] == '':
                    data[Header.RETURNTIME] = ent.text
            elif ent.label_ == 'EXT':
                current[Header.STAGE] = Header.STATUS_EXIT
            elif ent.label_ == 'TRUE' and current[Header.STAGE] == STAGE_VERIFICATION:
                data[Header.CONFIRMED] = 'true'
            elif ent.label_ == 'FALSE' and current[Header.STAGE] == STAGE_VERIFICATION:
                current[Header.STAGE] = Header.STATUS_INVALID
        return [current, data]

    def overwriteJSON(self, jsn1, jsn2):
        rst = jsn1
        for key, value in rst.items():
            if rst[key] == '':
                rst[key] = jsn2[key]
        return rst

    def process(self, session, tokens):
        # extract data from token into JSON
        if len(tokens.ents) < 1:
            return {
                Header.RESPONSE_CODE: ResponseCode.NOT_PROCESS,
                Header.RESPONSE_DATA: 'Unknown Statement'
            }

        currentData = session.state
        data = self.tokenToData(currentData, tokens)
        data = self.overwriteJSON(data[0], data[1])

        if (data[Header.STAGE] == Header.STATUS_EXIT):
            session.reset_state()
            return {
                Header.RESPONSE_CODE: ResponseCode.NEW_CONVERSATION,
                Header.RESPONSE_DATA: 'Reset'
            }

        if (data[Header.ACTION] == ''):
            session.set_state(data)
            return {
                Header.RESPONSE_CODE: ResponseCode.MISSING_INPUT,
                Header.RESPONSE_DATA: 'ACTION'
            }

        if (data[Header.STAGE] == Header.STATUS_INVALID):
            new_data = {
                Header.ACTION: data[Header.ACTION],  # type of transaction
                Header.STAGE: 2,  # stage
                Header.STATIONFROM: '',  # departure station
                Header.STATIONTO: '',  # destination station
                Header.DEPARTDATE: '',  # departure date
                Header.DEPARTTIME: '',  # departure time
                Header.ARRTIME: '',
                Header.STATIONAT: '',
                Header.STATIONATTIME: '',
                Header.CONFIRMED: '',
                Header.RESPONSE_HEAD: {
                    Header.RESPONSE_CODE: ResponseCode.MISSING_INPUT,
                    Header.RESPONSE_DATA: 'StationFrom'
                }
            }
            session.set_state(new_data)
            return {
                Header.RESPONSE_CODE: ResponseCode.MISSING_INPUT,
                Header.RESPONSE_DATA: 'StationFrom'
            }

        post(self.action[data[Header.ACTION]], {'data': data})
        responseJSON = json.loads(request.data)
        # save current state post-processing.
        session.set_state(responseJSON)
        # if success the reset state
        resetconditions = [ResponseCode.SUCESS_BOOKING,ResponseCode.SUCESS_DELAY,ResponseCode.QUESTION_NOTFOUND,ResponseCode.SUCESS_QUESTION]
        if (int(responseJSON[Header.RESPONSE_HEAD][Header.RESPONSE_CODE]) in resetconditions):
            session.reset_state()
        print('return to nlp - {0}'.format(responseJSON[Header.RESPONSE_HEAD]))
        return responseJSON[Header.RESPONSE_HEAD]

    def addbotResponse(self, session, response):
        session.add_bot_response(response)

    def addUserResponse(self, session, response):
        session.add_user_response(response)

    def strip_datetime_string(self, string):
        datetext = string.lower()
        datetext = datetext.replace('the', '')
        datetext = datetext.replace('th', '')
        datetext = datetext.replace('nd', '')
        datetext = datetext.replace('st', '')
        datetext = datetext.replace(' of', '')
        datetext = datetext.strip()
        return datetext
