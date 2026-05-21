import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def _mock_completion_response(message: str, field_updates: dict = None, is_complete: bool = False):
    """Build a mock litellm acompletion response with structured output."""
    payload = {
        "message": message,
        "field_updates": field_updates or {},
        "is_complete": is_complete,
    }
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps(payload)
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response


<<<<<<< feature/kan-5-all-document-types
def _post_chat(messages=None, current_fields=None, document_type: str = "mutual-non-disclosure-agreement"):
=======
def _post_chat(messages=None, current_fields=None):
>>>>>>> main
    return client.post(
        "/api/chat/message",
        json={
            "messages": messages or [{"role": "user", "content": "Hello"}],
            "current_fields": current_fields or {},
<<<<<<< feature/kan-5-all-document-types
            "document_type": document_type,
=======
>>>>>>> main
        },
    )


class TestChatMessageSuccess:
    @patch("routers.chat.acompletion", new_callable=AsyncMock)
    def test_returns_message_and_empty_field_updates(self, mock_llm):
        mock_llm.return_value = _mock_completion_response("What is the purpose of this NDA?")
        res = _post_chat()
        assert res.status_code == 200
        data = res.json()
        assert data["message"] == "What is the purpose of this NDA?"
        assert data["field_updates"] == {}
        assert data["is_complete"] is False

    @patch("routers.chat.acompletion", new_callable=AsyncMock)
    def test_returns_field_updates_when_confirmed(self, mock_llm):
        mock_llm.return_value = _mock_completion_response(
            "Got it. What date should the agreement take effect?",
            field_updates={"purpose": "Evaluating a business partnership"},
        )
        res = _post_chat(messages=[{"role": "user", "content": "Evaluating a business partnership"}])
        assert res.status_code == 200
        data = res.json()
        assert data["field_updates"]["purpose"] == "Evaluating a business partnership"

    @patch("routers.chat.acompletion", new_callable=AsyncMock)
    def test_is_complete_true_when_all_fields_confirmed(self, mock_llm):
<<<<<<< feature/kan-5-all-document-types
        all_fields = {
            "purpose": "Partnership evaluation",
            "effectiveDate": "2026-01-01",
            "mndaTermType": "expires",
            "mndaTermYears": 1,
            "confidentialityTermType": "years",
            "confidentialityTermYears": 2,
            "governingLaw": "Delaware",
            "jurisdiction": "courts in Delaware",
            "party1Name": "Alice Smith",
            "party1Title": "CEO",
            "party1Company": "Acme Inc",
            "party1NoticeAddress": "alice@acme.com",
            "party2Name": "Bob Jones",
            "party2Title": "CTO",
            "party2Company": "Beta Corp",
        }
=======
>>>>>>> main
        mock_llm.return_value = _mock_completion_response(
            "Your NDA is ready to download!",
            field_updates={"party2NoticeAddress": "legal@acme.com"},
            is_complete=True,
        )
<<<<<<< feature/kan-5-all-document-types
        res = _post_chat(current_fields=all_fields)
=======
        res = _post_chat()
>>>>>>> main
        assert res.status_code == 200
        assert res.json()["is_complete"] is True

    @patch("routers.chat.acompletion", new_callable=AsyncMock)
    def test_known_fields_appended_to_system_prompt(self, mock_llm):
        mock_llm.return_value = _mock_completion_response("Next question")
        _post_chat(current_fields={"purpose": "Partnership evaluation"})
        call_args = mock_llm.call_args
        system_message = call_args.kwargs["messages"][0]["content"]
        assert "Partnership evaluation" in system_message
        assert "do not ask about these again" in system_message

    @patch("routers.chat.acompletion", new_callable=AsyncMock)
    def test_empty_current_fields_does_not_append_to_system_prompt(self, mock_llm):
        mock_llm.return_value = _mock_completion_response("Hello")
        _post_chat(current_fields={})
        system_message = mock_llm.call_args.kwargs["messages"][0]["content"]
        assert "do not ask about these again" not in system_message

    @patch("routers.chat.acompletion", new_callable=AsyncMock)
    def test_conversation_history_forwarded_to_llm(self, mock_llm):
        mock_llm.return_value = _mock_completion_response("Next")
        messages = [
            {"role": "assistant", "content": "What's the purpose?"},
            {"role": "user", "content": "Partnership"},
        ]
        _post_chat(messages=messages)
        llm_messages = mock_llm.call_args.kwargs["messages"]
        roles = [m["role"] for m in llm_messages]
        assert roles == ["system", "assistant", "user"]


class TestChatMessageErrors:
    @patch("routers.chat.acompletion", new_callable=AsyncMock)
    def test_llm_exception_returns_502(self, mock_llm):
        mock_llm.side_effect = Exception("OpenRouter timeout")
        res = _post_chat()
        assert res.status_code == 502
        assert "AI service error" in res.json()["detail"]

    @patch("routers.chat.acompletion", new_callable=AsyncMock)
    def test_malformed_llm_json_returns_502(self, mock_llm):
        mock_choice = MagicMock()
        mock_choice.message.content = "not valid json {"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_llm.return_value = mock_response
        res = _post_chat()
        assert res.status_code == 502

    @patch("routers.chat.acompletion", new_callable=AsyncMock)
    def test_empty_choices_returns_502(self, mock_llm):
        mock_response = MagicMock()
        mock_response.choices = []
        mock_llm.return_value = mock_response
        res = _post_chat()
        assert res.status_code == 502

    def test_missing_messages_field_returns_422(self):
        res = client.post("/api/chat/message", json={"current_fields": {}})
        assert res.status_code == 422

    def test_empty_messages_list_accepted(self):
        with patch("routers.chat.acompletion", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = _mock_completion_response("Hello! What's the purpose?")
            res = _post_chat(messages=[])
            assert res.status_code == 200
<<<<<<< feature/kan-5-all-document-types


class TestMultiDocumentType:
    def test_unknown_document_type_returns_404(self):
        res = _post_chat(document_type="shareholder-agreement")
        assert res.status_code == 404
        assert "not supported" in res.json()["detail"]

    @patch("routers.chat.acompletion", new_callable=AsyncMock)
    def test_cloud_service_agreement_returns_200(self, mock_llm):
        mock_llm.return_value = _mock_completion_response(
            "Let's start your Cloud Service Agreement. What is the full legal name of the customer?",
            field_updates={},
            is_complete=False,
        )
        res = _post_chat(
            messages=[{"role": "user", "content": "Hello"}],
            document_type="cloud-service-agreement",
        )
        assert res.status_code == 200
        data = res.json()
        assert "message" in data

    @patch("routers.chat.acompletion", new_callable=AsyncMock)
    def test_design_partner_agreement_returns_200(self, mock_llm):
        mock_llm.return_value = _mock_completion_response(
            "Let's start your Design Partner Agreement. What is the full legal name of the provider?",
            field_updates={},
            is_complete=False,
        )
        res = _post_chat(
            messages=[{"role": "user", "content": "Hello"}],
            document_type="design-partner-agreement",
        )
        assert res.status_code == 200
        data = res.json()
        assert "message" in data
=======
>>>>>>> main
