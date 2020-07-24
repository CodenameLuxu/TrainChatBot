from flask import Flask, render_template, request, session, make_response
from flask_bootstrap import Bootstrap
import string, random, datetime, os
from ai_chatbot.Request import NlpProcess
from ai_chatbot.sessions.ChatMessage import ChatMessage

app = Flask(__name__)
app.secret_key = b'O\xb2h\xe1\x95\xdb\xde\xe2\x14\x17\x80\xf0\x9b\x06\x93\xca'
Bootstrap(app)
# Init bot here?
expert_system = NlpProcess.NlpProcess()


# Took it from:
# https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits#2257449
def id_generator(size: int = 12, chars: str = (string.ascii_uppercase + string.digits)) -> str:
    return ''.join(random.choice(chars) for _ in range(size))


# The main place for the chatbot to interface with
@app.route('/')
def index():
    resp = make_response(render_template('index.html'))
    if 'chat_session_id' not in request.cookies:
        resp.set_cookie('chat_session_id', id_generator())
    return resp

def toJsonValid(string: str) -> str:
    new_string: str = ""

    for c in string:
        if c == '"':
            new_string += "\\\""
        else:
            new_string += c

    return new_string

@app.route('/get')
def get_bot_responder() -> str:
    inputText = request.args.get('inputText')
    input_datetime = datetime.datetime.now()
    chat_session_id = request.cookies.get('chat_session_id')
    inputText = inputText.strip()
    bot_output = expert_system.Run_Chat(chat_session_id, inputText)

    bot_str_output = "{\"chat_log\":["
    first = True
    if type(bot_output) is not str:
        # Turn it to JSON formatting if getting back session history
        for msg in bot_output:
            if first:
                first = False
            else:
                bot_str_output += ","

            print("msg:", msg)

            bot_str_output += str("{\"type\":\"" + msg.get_type()
                                  + "\",\"content\":\"" + toJsonValid(msg.get_content())
                                  + "\",\"datetime\":\"" + msg.get_datetime() + "\"}")
    else:
        # Turn it to JSON formatting if just an input
        bot_datetime = datetime.datetime.now()
        bot_str_output += str("{\"type\":\"user"
                              + "\",\"content\":\"" + toJsonValid(inputText)
                              + "\",\"datetime\":\"" + str(input_datetime.replace(microsecond=0)) + "\"},")
        bot_str_output += str("{\"type\":\"bot"
                              + "\",\"content\":\"" + toJsonValid(bot_output)
                              + "\",\"datetime\":\"" + str(bot_datetime.replace(microsecond=0)) + "\"}")
    bot_str_output += "]}"
    print("bot_str_output:", bot_str_output)
    return bot_str_output

def main():
    app.run(ssl_context='adhoc')

# Can just run like any other Python program
if __name__ == "__main__":
    main()

