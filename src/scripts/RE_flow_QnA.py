from durable.lang import *
from flask import request
from scripts import REDataHeader as Header
from scripts import REResponseCode as ResponseCode
from scripts.QuestionDomain.QuestionTree import QuestionTree
import json

STAGE_INIT = "1"
STAGE_VALIDATION = "2"
STAGE_VERIFICATION = "3"
STAGE_PROCESS = "4"
STAGE_TERMINATE = "5"

responseJSON = {
       Header.RESPONSE_CODE : ResponseCode.NOT_PROCESS,
       Header.RESPONSE_DATA : 'Not process'
}

with ruleset('question'):

    @when_all(m.data.Stage == STAGE_INIT)
    def init(c): 
        c.m.data.Stage = STAGE_VALIDATION
        c.assert_fact(c.m)

    @when_all(m.data.Stage == STAGE_VALIDATION)
    def validation(c):
        print('QnA - Validation')
        c.m.data.Stage = STAGE_PROCESS
        c.assert_fact(c.m)


    @when_all(m.data.Stage == STAGE_PROCESS)
    def process(c):
        print('QnA - Process')
        try:
            tree = QuestionTree()
            tree.loadTree()
            answer = tree.searchfor(c.m.data[Header.QUESTION])
            responseJSON = {
                Header.RESPONSE_CODE: ResponseCode.SUCESS_QUESTION,
                Header.RESPONSE_DATA: answer
            }
            c.m.data[Header.RESPONSE_HEAD] = responseJSON
            c.m.data[Header.RESPONSE_HEAD] = responseJSON
            request.data = str(c.m.data).replace("'",'"')
            c.m.data.Stage = STAGE_TERMINATE
            c.assert_fact(c.m)
        except:
            responseJSON = {
                Header.RESPONSE_CODE: ResponseCode.QUESTION_NOTFOUND,
                Header.RESPONSE_DATA: 'error'
            }
            c.m.data[Header.RESPONSE_HEAD] = responseJSON
            request.data = str(c.m.data).replace("'", '"')
            c.m.data.Stage = STAGE_TERMINATE
            c.assert_fact(c.m)

    @when_all( m.data.Stage == STAGE_TERMINATE)
    def finalize(c):
        print('QnA - finalize')
        c.assert_fact(c.m)







