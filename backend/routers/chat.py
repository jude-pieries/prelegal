import os
from dataclasses import dataclass, field
from typing import Optional

import litellm
from fastapi import APIRouter, HTTPException
from litellm import acompletion
from pydantic import BaseModel, create_model

litellm.ssl_verify = False

router = APIRouter()

MODEL = "openrouter/openai/gpt-oss-120b"
EXTRA_BODY = {"provider": {"order": ["cerebras"]}}


@dataclass
class FieldDef:
    name: str
    description: str


@dataclass
class DocumentConfig:
    name: str
    template_file: str
    fields: list[FieldDef] = field(default_factory=list)

    def make_system_prompt(self, supported_docs: list[str]) -> str:
        field_list = "\n".join(f"- {f.name}: {f.description}" for f in self.fields)
        n = len(self.fields)
        others = ", ".join(d for d in supported_docs if d != self.name)
        return f"""You are a legal assistant helping users draft a {self.name}.

Your job is to conduct a friendly interview to collect all required information, one question at a time.

RULES — follow these exactly:
1. Every single response MUST end with a question asking about the next unconfirmed field.
2. After the user answers, confirm the value in field_updates, then immediately ask the NEXT field on the remaining list.
3. NEVER say the document is complete or set is_complete to true unless every one of the {n} fields below has a confirmed value.
4. Do NOT summarise, congratulate, or wrap up until all {n} fields are confirmed.
5. If a user's answer covers multiple fields at once, capture them all in field_updates and ask about the next uncovered field.
6. If the user asks about a different document type, explain this tool covers the {self.name} and mention we also support: {others}.

Fields to collect ({n} total):
{field_list}

Response format:
- message: a short, friendly sentence acknowledging the last answer (if any) followed by your next question
- field_updates: only fields confirmed in this turn
- is_complete: true ONLY when ALL {n} fields above are confirmed, false otherwise"""

    def make_field_updates_model(self):
        return create_model(
            "FieldUpdates",
            **{f.name: (Optional[str], None) for f in self.fields},
        )

    def make_llm_response_model(self):
        fu = self.make_field_updates_model()
        return create_model(
            "LLMResponse",
            message=(str, ...),
            field_updates=(fu, fu()),
            is_complete=(bool, False),
        )


DOCUMENT_CONFIGS: dict[str, DocumentConfig] = {
    "cloud-service-agreement": DocumentConfig(
        name="Cloud Service Agreement",
        template_file="templates/CSA.md",
        fields=[
            FieldDef("customer", "Full legal name of the customer"),
            FieldDef("provider", "Full legal name of the cloud service provider"),
            FieldDef("effectiveDate", "Agreement effective date (YYYY-MM-DD)"),
            FieldDef("governingLaw", "Governing US state law (e.g. 'Delaware')"),
            FieldDef("chosenCourts", "Courts for dispute resolution (e.g. 'courts in Delaware')"),
            FieldDef("subscriptionPeriod", "Subscription duration (e.g. '1 year', '12 months')"),
            FieldDef("technicalSupport", "Level of technical support (e.g. 'email support during business hours')"),
            FieldDef("generalCapAmount", "General liability cap (e.g. 'fees paid in the 12 months before the claim')"),
            FieldDef("increasedCapAmount", "Increased liability cap for certain claims (e.g. '2x fees paid in prior 12 months')"),
            FieldDef("increasedClaims", "Claims triggering the increased cap (e.g. 'data breaches, IP infringement')"),
            FieldDef("unlimitedClaims", "Claims with unlimited liability (e.g. 'gross negligence, willful misconduct, fraud')"),
            FieldDef("providerCoveredClaims", "What the provider indemnifies against (e.g. 'third-party IP infringement claims')"),
            FieldDef("customerCoveredClaims", "What the customer indemnifies against (e.g. 'claims arising from customer data')"),
        ],
    ),
    "design-partner-agreement": DocumentConfig(
        name="Design Partner Agreement",
        template_file="templates/design-partner-agreement.md",
        fields=[
            FieldDef("provider", "Full legal name of the provider"),
            FieldDef("partner", "Full legal name of the design partner"),
            FieldDef("effectiveDate", "Agreement effective date (YYYY-MM-DD)"),
            FieldDef("term", "Duration of the partnership (e.g. '6 months', '1 year')"),
            FieldDef("fees", "Fees payable, if any (e.g. 'No fees' or '$5,000')"),
            FieldDef("programDescription", "Brief description of the design partner program"),
            FieldDef("governingLaw", "Governing US state law"),
            FieldDef("chosenCourts", "Courts for dispute resolution"),
            FieldDef("providerNoticeAddress", "Provider's email or postal address for legal notices"),
            FieldDef("partnerNoticeAddress", "Partner's email or postal address for legal notices"),
        ],
    ),
    "service-level-agreement": DocumentConfig(
        name="Service Level Agreement",
        template_file="templates/sla.md",
        fields=[
            FieldDef("provider", "Full legal name of the service provider"),
            FieldDef("customer", "Full legal name of the customer"),
            FieldDef("subscriptionPeriod", "Period covered by this SLA (e.g. '1 year from effective date')"),
            FieldDef("targetUptime", "Uptime commitment percentage (e.g. '99.9%')"),
            FieldDef("targetResponseTime", "Target support response time (e.g. '4 business hours for P1 issues')"),
            FieldDef("supportChannel", "How to reach support (e.g. 'email support@company.com')"),
            FieldDef("scheduledDowntime", "Maintenance window (e.g. 'Sundays 2–4am UTC')"),
            FieldDef("uptimeCredit", "Service credit for uptime failures (e.g. '5% of monthly fee per 0.1% below target')"),
            FieldDef("responseTimeCredit", "Service credit for response time failures (e.g. '5% of monthly fee')"),
        ],
    ),
    "professional-services-agreement": DocumentConfig(
        name="Professional Services Agreement",
        template_file="templates/psa.md",
        fields=[
            FieldDef("customer", "Full legal name of the customer"),
            FieldDef("provider", "Full legal name of the services provider"),
            FieldDef("effectiveDate", "Agreement effective date (YYYY-MM-DD)"),
            FieldDef("governingLaw", "Governing US state law"),
            FieldDef("chosenCourts", "Courts for dispute resolution"),
            FieldDef("generalCapAmount", "General liability cap"),
            FieldDef("deliverables", "Description of what will be delivered"),
            FieldDef("fees", "Fee amount and structure (e.g. '$10,000 fixed fee' or '$200/hour')"),
            FieldDef("paymentPeriod", "Invoice payment terms (e.g. 'Net 30 days')"),
            FieldDef("sowTerm", "Duration of the statement of work (e.g. '90 days')"),
            FieldDef("rejectionPeriod", "Days customer has to review and reject deliverables (e.g. '10 business days')"),
        ],
    ),
    "data-processing-agreement": DocumentConfig(
        name="Data Processing Agreement",
        template_file="templates/DPA.md",
        fields=[
            FieldDef("customer", "Full legal name of the data controller (customer)"),
            FieldDef("provider", "Full legal name of the data processor (provider)"),
            FieldDef("parentAgreement", "Reference to the main agreement this DPA supplements (e.g. 'Cloud Service Agreement dated 2025-01-01')"),
            FieldDef("categoriesOfPersonalData", "Types of personal data to be processed (e.g. 'names, email addresses, IP addresses')"),
            FieldDef("categoriesOfDataSubjects", "Who the data subjects are (e.g. 'customer employees and end users')"),
            FieldDef("specialCategoryData", "Any sensitive/special category data (e.g. 'None' or 'health records')"),
            FieldDef("frequencyOfTransfer", "How often personal data is transferred (e.g. 'Continuously during service use')"),
            FieldDef("purposeOfProcessing", "Why personal data is processed (e.g. 'To provide cloud software features')"),
            FieldDef("durationOfProcessing", "How long data is processed (e.g. 'For the duration of the main agreement plus 30 days')"),
            FieldDef("governingMemberState", "EU supervisory authority member state (e.g. 'Ireland', 'Germany')"),
        ],
    ),
    "software-license-agreement": DocumentConfig(
        name="Software License Agreement",
        template_file="templates/Software-License-Agreement.md",
        fields=[
            FieldDef("customer", "Full legal name of the customer/licensee"),
            FieldDef("provider", "Full legal name of the provider/licensor"),
            FieldDef("effectiveDate", "Agreement effective date (YYYY-MM-DD)"),
            FieldDef("governingLaw", "Governing US state law"),
            FieldDef("generalCapAmount", "General liability cap"),
            FieldDef("subscriptionPeriod", "License term (e.g. '1 year', 'perpetual')"),
            FieldDef("permittedUses", "What the customer can do with the software (e.g. 'internal business use only')"),
            FieldDef("licenseLimits", "Usage or seat limits (e.g. 'up to 50 named users')"),
            FieldDef("warrantyPeriod", "Software warranty period (e.g. '90 days from delivery')"),
        ],
    ),
    "partnership-agreement": DocumentConfig(
        name="Partnership Agreement",
        template_file="templates/Partnership-Agreement.md",
        fields=[
            FieldDef("company", "Full legal name of the company"),
            FieldDef("partner", "Full legal name of the partner"),
            FieldDef("effectiveDate", "Agreement effective date (YYYY-MM-DD)"),
            FieldDef("endDate", "Agreement end date (YYYY-MM-DD)"),
            FieldDef("obligations", "Partner's key obligations (e.g. 'resell products in EMEA and provide first-line support')"),
            FieldDef("territory", "Geographic territory (e.g. 'United Kingdom and Ireland')"),
            FieldDef("governingLaw", "Governing US state law"),
            FieldDef("chosenCourts", "Courts for dispute resolution"),
            FieldDef("generalCapAmount", "General liability cap"),
            FieldDef("paymentProcess", "How fees are paid (e.g. 'quarterly via bank transfer')"),
            FieldDef("paymentSchedule", "Payment timing (e.g. 'within 30 days of quarter end')"),
        ],
    ),
    "pilot-agreement": DocumentConfig(
        name="Pilot Agreement",
        template_file="templates/Pilot-Agreement.md",
        fields=[
            FieldDef("customer", "Full legal name of the customer"),
            FieldDef("provider", "Full legal name of the provider"),
            FieldDef("effectiveDate", "Pilot start date (YYYY-MM-DD)"),
            FieldDef("pilotPeriod", "Duration of the pilot (e.g. '90 days', '3 months')"),
            FieldDef("generalCapAmount", "General liability cap (e.g. 'fees paid during the pilot')"),
            FieldDef("governingLaw", "Governing US state law"),
            FieldDef("chosenCourts", "Courts for dispute resolution"),
            FieldDef("providerNoticeAddress", "Provider's email or postal address for legal notices"),
            FieldDef("customerNoticeAddress", "Customer's email or postal address for legal notices"),
        ],
    ),
    "business-associate-agreement": DocumentConfig(
        name="Business Associate Agreement",
        template_file="templates/BAA.md",
        fields=[
            FieldDef("provider", "Full legal name of the business associate (provider)"),
            FieldDef("company", "Full legal name of the covered entity (company)"),
            FieldDef("baaEffectiveDate", "BAA effective date (YYYY-MM-DD)"),
            FieldDef("parentAgreement", "Reference to the main agreement (e.g. 'Cloud Service Agreement dated 2025-01-01')"),
            FieldDef("phiLimitations", "Limitations on how PHI may be used (e.g. 'Only for providing the services in the main agreement')"),
            FieldDef("breachNotificationPeriod", "Days to report a PHI breach (e.g. '30 days')"),
        ],
    ),
    "ai-addendum": DocumentConfig(
        name="AI Addendum",
        template_file="templates/AI-Addendum.md",
        fields=[
            FieldDef("customer", "Full legal name of the customer"),
            FieldDef("provider", "Full legal name of the AI service provider"),
            FieldDef("trainingDataAllowed", "Is customer data allowed for AI model training? ('yes' or 'no')"),
            FieldDef("trainingPurposes", "If training is allowed, for what purposes? (e.g. 'improving model accuracy and safety')"),
            FieldDef("trainingRestrictions", "Restrictions on training use (e.g. 'PII must be anonymized' or 'None')"),
            FieldDef("improvementRestrictions", "Restrictions on using outputs for product improvement (e.g. 'None' or specific limits)"),
        ],
    ),
}

MNDA_SYSTEM_PROMPT = """You are a legal assistant helping users draft a Mutual Non-Disclosure Agreement (Mutual NDA).

Your job is to conduct a friendly interview to collect all required information, one question at a time.

RULES — follow these exactly:
1. Every single response MUST end with a question asking about the next unconfirmed field.
2. After the user answers, confirm the value in field_updates, then immediately ask the NEXT field on the remaining list.
3. NEVER say the document is complete or set is_complete to true unless every one of the 16 fields below has a confirmed value.
4. Do NOT summarise, congratulate, or wrap up until all 16 fields are confirmed.
5. If a user's answer covers multiple fields at once, capture them all in field_updates and ask about the next uncovered field.

Fields to collect (16 total):
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

Response format:
- message: a short friendly sentence acknowledging the last answer (if any) followed by your next question
- field_updates: only fields confirmed in this turn
- is_complete: true ONLY when ALL 16 fields above are confirmed, false otherwise"""


class MndaFieldUpdates(BaseModel):
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


class MndaLLMResponse(BaseModel):
    message: str
    field_updates: MndaFieldUpdates
    is_complete: bool


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    current_fields: dict = {}
    document_type: str = "mutual-non-disclosure-agreement"


def _get_supported_doc_names() -> list[str]:
    return ["Mutual Non-Disclosure Agreement"] + [c.name for c in DOCUMENT_CONFIGS.values()]


@router.post("/message")
async def chat_message(req: ChatRequest):
    doc_type = req.document_type

    if doc_type in ("mutual-non-disclosure-agreement", "mutual-nda-cover-page"):
        known = {k: v for k, v in req.current_fields.items() if v is not None}
        system = MNDA_SYSTEM_PROMPT
        if known:
            remaining = [
                f for f in [
                    "purpose", "effectiveDate", "mndaTermType", "mndaTermYears",
                    "confidentialityTermType", "confidentialityTermYears", "governingLaw",
                    "jurisdiction", "party1Name", "party1Title", "party1Company",
                    "party1NoticeAddress", "party2Name", "party2Title", "party2Company",
                    "party2NoticeAddress",
                ]
                if f not in known
            ]
            system += f"\n\nAlready confirmed fields (do not ask about these again): {known}"
            if remaining:
                system += f"\n\nRemaining fields still needed: {remaining}"

        llm_messages = [{"role": "system", "content": system}]
        for msg in req.messages:
            llm_messages.append({"role": msg.role, "content": msg.content})

        try:
            response = await acompletion(
                model=MODEL,
                messages=llm_messages,
                response_format=MndaLLMResponse,
                extra_body=EXTRA_BODY,
                api_key=os.getenv("OPENROUTER_API_KEY"),
            )
            result = MndaLLMResponse.model_validate_json(response.choices[0].message.content)
            # Safety: prevent premature completion if fields are still missing
            if result.is_complete:
                all_fields = [
                    "purpose", "effectiveDate", "mndaTermType", "mndaTermYears",
                    "confidentialityTermType", "confidentialityTermYears", "governingLaw",
                    "jurisdiction", "party1Name", "party1Title", "party1Company",
                    "party1NoticeAddress", "party2Name", "party2Title", "party2Company",
                    "party2NoticeAddress",
                ]
                now_known = {**known, **{k: v for k, v in result.field_updates.model_dump().items() if v is not None}}
                still_missing = [f for f in all_fields if f not in now_known]
                if still_missing:
                    result = MndaLLMResponse(
                        message=result.message,
                        field_updates=result.field_updates,
                        is_complete=False,
                    )
            return result.model_dump(exclude_none=True)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"AI service error: {exc}")

    config = DOCUMENT_CONFIGS.get(doc_type)
    if not config:
        supported = ", ".join(
            ["mutual-non-disclosure-agreement"] + list(DOCUMENT_CONFIGS.keys())
        )
        raise HTTPException(
            status_code=404,
            detail=f"Document type '{doc_type}' is not supported. Supported types: {supported}",
        )

    field_names = [f.name for f in config.fields]
    known = {k: v for k, v in req.current_fields.items() if v is not None and k in field_names}
    remaining = [f for f in field_names if f not in known]

    supported_names = _get_supported_doc_names()
    system = config.make_system_prompt(supported_names)
    if known:
        system += f"\n\nAlready confirmed fields (do not ask about these again): {known}"
    if remaining:
        system += f"\n\nRemaining fields still needed (ask about these next): {remaining}"

    llm_messages = [{"role": "system", "content": system}]
    for msg in req.messages:
        llm_messages.append({"role": msg.role, "content": msg.content})

    llm_response_model = config.make_llm_response_model()

    try:
        response = await acompletion(
            model=MODEL,
            messages=llm_messages,
            response_format=llm_response_model,
            extra_body=EXTRA_BODY,
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        result = llm_response_model.model_validate_json(response.choices[0].message.content)
        # Safety: prevent premature completion if fields are still missing
        if result.is_complete:
            now_known = {**known, **{k: v for k, v in result.field_updates.model_dump().items() if v is not None}}
            still_missing = [f for f in field_names if f not in now_known]
            if still_missing:
                result = llm_response_model(
                    message=result.message,
                    field_updates=result.field_updates,
                    is_complete=False,
                )
        return result.model_dump(exclude_none=True)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}")
