from ai_chatbot.sessions.ChatMessage import ChatMessage


class ChatHistory:
    def __init__(self):
        self.chat_log = []
        self.state = {}

    def add_user_response(self, user_message):
        self.chat_log.append(ChatMessage.ChatMessage("user", user_message))

    def add_bot_response(self, bot_response):
        self.chat_log.append(ChatMessage.ChatMessage("bot", bot_response))

    def return_latest_chat(self):
        return self.chat_log[-1].content

    def set_state(self, newstate):
        self.state = newstate

    def reset_state(self):
        self.state = {}

    def return_all_chat(self):
        return self.chat_log
