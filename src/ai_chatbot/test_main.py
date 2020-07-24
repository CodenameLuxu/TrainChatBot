import pytest

from ai_chatbot.main import id_generator, toJsonValid

def test_main_all():
    id_ = id_generator(12)
    assert len(id_) == 12
    assert toJsonValid("Test\"Test") == "Test\\\"Test"

