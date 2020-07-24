import sys
from durable.lang import *
from flask import request
import json
import ai_chatbot.scripts.RE_function_delay as redelay
from ai_chatbot.scripts import REResponseCode as ResponseCode
from ai_chatbot.scripts import REDataHeader as Header

STAGE_INIT = 1
STAGE_VALIDATION = 2
STAGE_PROCESS = 3
STAGE_TERMINATE = 4

with ruleset('delay'):
    @when_all(m.data.Stage == STAGE_INIT)
    def init(c):
        c.m.data[Header.STAGE] = STAGE_VALIDATION
        c.assert_fact(c.m)


    @when_all(m.data.Stage == STAGE_VALIDATION)
    def validation(c):
        if (redelay.missingDataCheck(c.m.data) == 0):
            c.m.data.Stage = STAGE_PROCESS
            c.assert_fact(c.m)
        else:
            bookingJSON = {
                Header.RESPONSE_CODE: ResponseCode.MISSING_INPUT,
                Header.RESPONSE_DATA: redelay.missingDataCheck(c.m.data)
            }
            print('DEL- validation - missing : {0}'.format(bookingJSON[Header.RESPONSE_DATA]))
            c.m.data[Header.RESPONSE_HEAD] = bookingJSON
            request.data = str(c.m.data).replace("'", '"')


    @when_all(m.data.Stage == STAGE_PROCESS)
    def process(c):
        try:
            response = redelay.delay_predict(c.m.data)
            responseJSON = {
                Header.RESPONSE_CODE: ResponseCode.SUCESS_DELAY,
                Header.RESPONSE_DATA: str(response)
            }
            c.m.data[Header.RESPONSE_HEAD] = responseJSON
            request.data = str(c.m.data).replace("'", '"')
            c.m.data[Header.STAGE] = STAGE_TERMINATE
            c.assert_fact(c.m)
        except Exception as e:
            print("Oops!", sys.exc_info()[0], "occured.")
            bookingJSON = {
                Header.RESPONSE_CODE: ResponseCode.NOT_PROCESS,
                Header.RESPONSE_DATA: 'error'
            }
            c.m.data[Header.RESPONSE_HEAD] = bookingJSON
            request.data = str(c.m.data).replace("'", '"')


    @when_all(m.data.Stage == STAGE_TERMINATE)
    def finalize(c):
        c.delete_state()
