import pytest
from ai_chatbot.sessions.SessionManager import SessionManager


def test_SessionManager_init():
    sessions = SessionManager.SessionManager()
    assert sessions is not None


def test_SessionManager_AddSession():
    sessions = SessionManager.SessionManager()
    session_name = "unique"
    sessions.add_session(session_name)
    session = sessions.get_session(session_name)
    assert sessions is not None
    assert session is not None
