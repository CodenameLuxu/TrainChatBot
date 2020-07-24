from ai_chatbot.scraper.scraper import Scraper
import re, datetime

"""
usercmd is just to test the functions of the chatbot, currently:
    usercmd:fetch|fetchl|fetchr|fetchrl:... to test the scraper
    usercmd:echo:... to test the chatbot message
"""
class UserCmd:
    def usercmd_respond(self, chat_session_id: str, inputText: str) -> str:
        if 'usercmd:' in inputText:
            if 'fetch:' in inputText or 'fetchl:' in inputText or 'fetchr:' in inputText or 'fetchrl:' in inputText:
                ret_str: str = ''
                """
                EX:
                    usercmd:fetch:NRW:LUT:2020-02-02 15:15
                    usercmd:fetchl:NRW:LUT:2020-02-02 15:15
                    usercmd:fetchr:NRW:LUT:2020-02-02 15:15|2020-02-05 15:15
                    usercmd:fetchrl:NRW:LUT:2020-02-02 15:15|2020-02-05 15:15
                """
                if ((re.search('usercmd:fetch:(\w{3}):(\w{3}):(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})', inputText) is not None) or
                        (re.search('usercmd:fetchl:(\w{3}):(\w{3}):(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})', inputText) is not None) or
                        (re.search('usercmd:fetchr:(\w{3}):(\w{3}):(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})|(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})', inputText) is not None) or
                        (re.search('usercmd:fetchrl:(\w{3}):(\w{3}):(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})|(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})', inputText) is not None)):
                    try:
                        from_, to_ = re.findall('([A-Z]{3})', inputText)
                        dates_times = re.findall('(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})', inputText)

                        print(dates_times)
                        date_split = dates_times[0]
                        out_datetime = datetime.datetime(int(date_split[0]), int(date_split[1]), int(date_split[2]), int(date_split[3]), int(date_split[4]))
                        try:
                            date_split = dates_times[1]
                            ret_datetime = datetime.datetime(int(date_split[0]), int(date_split[1]), int(date_split[2]), int(date_split[3]), int(date_split[4]))
                        except:
                            ret_datetime = None
                    except Exception as e:
                        print(e)
                        return "Sorry, the format given is wrong. It should be: 'FRO:TOO:YYYY-MM-DD HH:MM' or 'FRO:TOO:YYYY-MM-DD HH:MM|YYYY-MM-DD HH:MM' for return"
                else:
                    return "Sorry, the format given is wrong. It should be: 'FRO:TOO:YYYY-MM-DD HH:MM' or 'FRO:TOO:YYYY-MM-DD HH:MM|YYYY-MM-DD HH:MM' for return"

                s = Scraper("drivers/chromedriver_linux")
                for n in s.scrape(False, from_, to_, out_datetime, ret_datetime):
                    ret_str += '<br>'+n['depatureTime']+' '+n['arrivalTime']+' '+n['durationTime']+' '+n['fareTotal']
                ret_str += '<br><a href=\"'+res_dict['url']+'\">Link</a>'\
                            '<br>'+str(len(res_dict['results']))+' lowest priced tickets found'
                return ret_str
            elif 'echo:' in inputText:
                """
                Example: "usercmd:echo:Test 1 2 3 4"
                returns: "Test 1 2 3 4"
                """
                print("echo: ", inputText[13:])
                return inputText[13:]
            else:
                return "Sorry, the usercmd you put in is unrecognisable. Please try again."
        elif inputText == '':
            return "Sorry, you did not say anything. Try again."
        return "ERROR"

