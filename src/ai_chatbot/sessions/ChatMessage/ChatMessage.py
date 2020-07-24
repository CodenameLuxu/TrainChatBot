import datetime


class ChatMessage:
    def __init__(self, _type, message):
        self.type = _type
        self.content = message
        self.datetime = str(datetime.datetime.utcnow()).split('.')[0]

    def get_type(self):
        return self.type

    def get_content(self):
        return self.content

    def get_datetime(self):
        return self.datetime
