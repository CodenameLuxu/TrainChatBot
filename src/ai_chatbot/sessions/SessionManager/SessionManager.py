from ai_chatbot.sessions.ChatHistory import ChatHistory


class SessionManager:
    def __init__(self):
        self.sessions = {}

    def add_session(self, uuid: str):
        self.sessions[uuid] = ChatHistory.ChatHistory()

    # Everything in python is a pointer so this is fine
    def get_session(self, uuid: str):
        for key, value in self.sessions.items():
            if key == uuid:
                return value
