from ai_chatbot.scripts.StateManager.RE_State import RE_State

class StateManager:
    def __init__(self):
        self.sessions = {}

    def add_session(self, uuid: str, state):
        self.sessions[uuid] = RE_State.RE_State()

    # Everything in python is a pointer so this is fine
    def get_session(self, uuid: str):
        for key, value in self.sessions.items():
            if key == uuid:
                return value
