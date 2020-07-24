import pytest
from ai_chatbot.sessions.ChatHistory import ChatHistory


def test_ChatHistory_all():
    history = ChatHistory.ChatHistory()
    assert history is not None

    user = "message sample"
    bot = "hello human"
    history.add_user_response(user)
    assert history.return_latest_chat() is user

    history.add_bot_response(bot)
    assert history.return_latest_chat() is bot
