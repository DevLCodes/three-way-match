import pytest
from pydantic import ValidationError

from three_way_match.extract import extract, json_object
from three_way_match.schemas import DocType

VALID = '{"order_id": "1", "lines": [{"product": "Chai", "quantity": 10, "unit_price": 18}], "total": 180}'


def scripted(*replies):
    sent = []

    def chat(messages):
        sent.append([m.copy() for m in messages])
        return replies[len(sent) - 1]

    return chat, sent


def test_strips_chatter_around_json():
    assert json_object("Sure!\n```json\n" + VALID + "\n```") == VALID


def test_valid_first_reply_needs_one_call():
    chat, sent = scripted(VALID)
    assert extract("text", DocType.INVOICE, chat=chat).total == 180
    assert len(sent) == 1
    assert "<document>\ntext\n</document>" in sent[0][0]["content"]


def test_invalid_reply_is_retried_with_the_error():
    chat, sent = scripted('{"order_id": "1", "lines": [{"product": "Chai", "quantity": "ten"}]}', VALID)
    assert extract("text", DocType.INVOICE, chat=chat).lines[0].quantity == 10
    retry = sent[1]
    assert [m["role"] for m in retry] == ["user", "assistant", "user"]
    assert "quantity" in retry[2]["content"]


def test_gives_up_after_attempts():
    chat, _ = scripted("nope", "still nope")
    with pytest.raises(ValidationError):
        extract("text", DocType.INVOICE, chat=chat)
