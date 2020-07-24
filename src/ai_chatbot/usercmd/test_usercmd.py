import pytest
from ai_chatbot.usercmd import UserCmd

def test_UserCmd_all():
    assert usercmd_respond("ABCDEFG", "usercmd:echo:test") == "test"
    assert usercmd_respond("ABCDEFG", "usercmd:asdasd") == "Sorry, the usercmd you put in is unrecognisable. Please try again."

