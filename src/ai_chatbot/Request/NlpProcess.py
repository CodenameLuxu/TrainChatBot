import dateparser
from ai_chatbot.nlp.StringProcess import StringProcess
from ai_chatbot.sessions.SessionManager import SessionManager
from ai_chatbot.usercmd.usercmd import UserCmd
from ai_chatbot.nlg.NlgGeneration import NlgGeneration
from ai_chatbot.scripts import ReasoningEngine


class NlpProcess:
    def __init__(self):
        self.sessionManager = SessionManager.SessionManager()
        self.stringProcess = StringProcess.StringProcess()
        self.usercmd = UserCmd()
        self.nlg = NlgGeneration()
        self.re = ReasoningEngine.ReasoningEngine()

    def Run_Chat(self, uuid: str, message: str) -> str:
        # Session manegment
        session = self.sessionManager.get_session(uuid)
        if message == 'usercmd:load':
            if session is None:
                self.sessionManager.add_session(uuid)
                session = self.sessionManager.get_session(uuid)
                greeting = self.nlg.hello_user()
                session.add_bot_response(greeting)
                return greeting
            else:
                return session.return_all_chat()
        elif 'usercmd:' in message:
            # If session is none but not from a browser reload 
            if session is None:
                self.sessionManager.add_session(uuid)
                session = self.sessionManager.get_session(uuid)
            usercmd_resp = self.usercmd.usercmd_respond(uuid, message)
            session.add_bot_response(usercmd_resp)
            print("usercmd_resp:", usercmd_resp)
            return usercmd_resp

        session.add_user_response(message)
        tokens = self.stringProcess.string_tokenizer(message)
        for token in tokens:
            print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
                  token.shape_, token.is_alpha, token.is_stop)
        print([(ent.text, ent.label_, ent.ent_id_) for ent in tokens.ents])

        try:
            response = self.re.process(session, tokens)
        except Exception as e:
            return self.nlg.no_process()

        # get latest bot message
        if response['Code'] == 0:
            bot_response = self.nlg.no_process()
        elif response['Code'] == 101:
            departing = response['ResponseData']['result'][0]['from']
            arrival = response['ResponseData']['result'][0]['to']
            date = response['ResponseData']['date']
            time = response['ResponseData']['result'][0]['departureTime']
            price = response['ResponseData']['result'][0]['fareTotal']
            url = response['ResponseData']['result'][0]['url']
            url_html = "<a href=\""+url+"\">"+"Click Here!"+"</a>"
            bot_response = self.nlg.ticket_display(departing, arrival, date, time, price, url_html)
        elif response['Code'] == 501:
            if response['ResponseData'] == 'StationFrom':
                bot_response = self.nlg.missing_departure()
            elif response['ResponseData'] == 'StationTo':
                bot_response = self.nlg.missing_arrival()
            elif response['ResponseData'] == 'DepDate':
                bot_response = self.nlg.missing_date()
            elif response['ResponseData'] == 'DepTime':
                bot_response = self.nlg.missing_dep_time()
            elif response['ResponseData'] == 'ArrTime':
                bot_response = self.nlg.missing_expected_arrival_time()
            elif response['ResponseData'] == 'StationAt':
                bot_response = self.nlg.missing_intermediate_station()
            elif response['ResponseData'] == 'StationAtTime':
                bot_response = self.nlg.missing_intermediate_station_arrival()
            elif response['ResponseData'] == 'BadDate':
                bot_response = self.nlg.bad_date()
            elif response['ResponseData'] == 'BadTime':
                bot_response = self.nlg.bad_time()
            elif response['ResponseData'] == 'SingleReturn':
                bot_response = self.nlg.missing_single_or_return()
            elif response['ResponseData'] == 'ReturnDate':
                bot_response = self.nlg.missing_return_date()
            elif response['ResponseData'] == 'ReturnTime':
                bot_response = self.nlg.missing_return_time()
            elif response['ResponseData'] == 'ActualDepart':
                bot_response = "Please enter the time you actually left your origin station."
            else:
                bot_response = "There has been an error, please contact the system administrator."
        elif response['Code'] == 103:
            bot_response = response['ResponseData']
        elif response['Code'] == 401:
            bot_response = "I'm sorry, i'm unable to answer that question."
        elif response['Code'] == 301:
            departing = response['ResponseData']['DEPART']
            arrival = response['ResponseData']['ARRIVAL']
            date = dateparser.parse(response['ResponseData']['DATE']).date().__str__()
            time = dateparser.parse(response['ResponseData']['TIME']).time().__str__()
            tickettype = response['ResponseData']['SINGLERETURN']
            if tickettype == 'single':
                type = False
                bot_response = self.nlg.confirm_book_selection(departing, arrival, date, time, tickettype, type, None, None)
            else:
                rtndate = dateparser.parse(response['ResponseData']['RETURNDATE']).date().__str__()
                rtntime = dateparser.parse(response['ResponseData']['RETURNTIME']).time().__str__()
                type = True
                bot_response = self.nlg.confirm_book_selection(departing, arrival, date, time, tickettype, type, rtndate, rtntime)
        elif response['Code'] == 102:
            delay_amount = response['ResponseData']
            bot_response = self.nlg.delay_display(delay_amount)
        elif response['Code'] == 503:
            bot_response = self.nlg.exit_conversation()
        else:
            bot_response = "processed"

        # Add bot response
        session.add_bot_response(bot_response)

        return bot_response
