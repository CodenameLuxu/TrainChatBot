from ai_chatbot.nlp.PatternRules.PatternMaker import PatternMaker

class StringProcess:
    def __init__(self):
        self.instance = PatternMaker()


    def string_tokenizer(self, message):
        copy = message[:]
        tokens = self.instance.nlp(message)
        return tokens
