import os
from typing import Optional

import litellm
from fastapi import APIRouter, HTTPException
from litellm import acompletion
from pydantic import BaseModel

litellm.ssl_verify = False

router = APIRouter()

MODEL = "openrouter/openai/gpt-oss-120b"
EXTRA_BODY = {"provider": {"order": ["cerebras"]}}

SYSTEM_PROMPT = """You are a legal assistant helping users draft a Mutual Non-Disclosure Agreement (Mutual NDA).

Your job is to have a friendly, conversational chat to collect all the required information. Ask one question at a time in a natural, professional tone. Do not ask multiple questions at once.

The fields you need to collect are:
- purpose: What is the NDA for? How will confidential information be used?
- effectiveDate: When does the agreement take effect? (format: YYYY-MM-DD, e.g. "2026-05-20")
- mndaTermType: Does the NDA have a fixed term ("expires") or continue until terminated ("continues")?
- mndaTermYears: If it expires, how many years? (integer, only needed if mndaTermType is "expires")
- confidentialityTermType: After the NDA ends, do confidentiality obligations last for a set number of years ("years") or in perpetuity ("perpetuity")?
- confidentialityTermYears: How many years? (integer, only needed if confidentialityTermType is "years")
- governingLaw: Which US state's law governs the agreement? (e.g. "Delaware")
- jurisdiction: Where should disputes be resolved? (e.g. "courts located in New Castle, DE")
- party1Name: Full legal name of Party 1's signatory
- party1Title: Job title of Party 1's signatory
- party1Company: Legal company name of Party 1
- party1NoticeAddress: Email or postal address for legal notices to Party 1
- party2Name: Full legal name of Party 2's signatory
- party2Title: Job title of Party 2's signatory
- party2Company: Legal company name of Party 2
- party2NoticeAddress: Email or postal address for legal notices to Party 2

Instructions:
1. Ask questions one at a time in a logical order.
2. In field_updates, include any fields you now have confirmed values for based on the conversation so far.
3. Only include a field in field_updates if you are confident about its value — do not guess.
4. Set is_complete to true only when all 16 fields have been confirmed.
5. Be concise and friendly. Keep responses short."""


class Message(BaseModel):
    role: str
    content: str


class FieldUpdates(BaseModel):
    purpose: Optional[str] = None
    effectiveDate: Optional[str] = None
    mndaTermType: Optional[str] = None
    mndaTermYears: Optional[int] = None
    confidentialityTermType: Optional[str] = None
    confidentialityTermYears: Optional[int] = None
    governingLaw: Optional[str] = None
    jurisdiction: Optional[str] = None
    party1Name: Optional[str] = None
    party1Title: Optional[str] = None
    party1Company: Optional[str] = None
    party1NoticeAddress: Optional[str] = None
    party2Name: Optional[str] = None
    party2Title: Optional[str] = None
    party2Company: Optional[str] = None
    party2NoticeAddress: Optional[str] = None


class ChatRequest(BaseModel):
    messages: list[Message]
    current_fields: FieldUpdates = FieldUpdates()


class LLMResponse(BaseModel):
    message: str
    field_updates: FieldUpdates
    is_complete: bool


@router.post("/message", response_model=LLMResponse, response_model_exclude_none=True)
async def chat_message(req: ChatRequest):
    known = {k: v for k, v in req.current_fields.model_dump().items() if v is not None}

    system = SYSTEM_PROMPT
    if known:
        system += f"\n\nAlready confirmed fields (do not ask about these again): {known}"

    llm_messages = [{"role": "system", "content": system}]
    for msg in req.messages:
        llm_messages.append({"role": msg.role, "content": msg.content})

    try:
        response = await acompletion(
            model=MODEL,
            messages=llm_messages,
            response_format=LLMResponse,
            reasoning_effort="low",
            extra_body=EXTRA_BODY,
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        return LLMResponse.model_validate_json(response.choices[0].message.content)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}")
