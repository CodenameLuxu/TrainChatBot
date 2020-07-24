from builtins import Exception

from durable.lang import *
from flask import request
from ai_chatbot.scripts import REDataHeader as Header
from ai_chatbot.scripts import REResponseCode as ResponseCode
from ai_chatbot.scripts.QuestionDomain.QuestionTree import QuestionTree
import json
import traceback

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
        """try:
            print('QnA - Process')
            print('Question --> {0} \n \t >{1}'.format(c.m.data[Header.QUESTION],c.m.data[Header.QUESTIONSEARCHING]))
            answer = ''
            if (c.m.data[Header.QUESTIONSEARCHING] == 0 ):
                c.m.data[Header.QUESTIONSEARCHING] = 1
                c.assert_fact(c.m)

                tree = QuestionTree()
                tree.loadTree()
                # print(tree.getAllTreeTags())
                answer = tree.searchfor(c.m.data[Header.QUESTION])
                print()
            responseJSON = {
                Header.RESPONSE_CODE: ResponseCode.SUCESS_QUESTION,
                Header.RESPONSE_DATA: answer
            }
            c.m.data[Header.RESPONSE_HEAD] = responseJSON
            c.m.data[Header.RESPONSE_HEAD] = responseJSON
            request.data = str(c.m.data).replace("'",'"')
            c.m.data.Stage = STAGE_TERMINATE
            c.assert_fact(c.m)
        except Exception as e:
            traceback.print_exc()"""
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







