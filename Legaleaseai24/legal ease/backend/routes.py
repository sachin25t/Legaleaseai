import os

from fastapi import APIRouter, HTTPException, status
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

load_dotenv()
router = APIRouter()


class DocumentRequest(BaseModel):
    document_type: str = Field(min_length=1)
    parties: str = Field(min_length=1)
    terms: str = Field(min_length=1)
    dates: str = Field(min_length=1)

    @field_validator("document_type", "parties", "terms", "dates")
    @classmethod
    def require_non_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("value must not be blank")
        return value


def _fallback_document(request: DocumentRequest) -> str:
    return (
        f"{request.document_type.upper()}\n\n"
        f"Effective date: {request.dates}\n\n"
        f"PARTIES\n{request.parties}\n\n"
        f"TERMS AND CONDITIONS\n{request.terms}\n\n"
        "DISCLAIMER\n"
        "This draft is AI-assisted and should be reviewed by a qualified legal professional."
    )


def _generate_with_gemini(request: DocumentRequest) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return _fallback_document(request)

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        prompt = (
            "Draft a clear legal document using the following information. "
            "Use plain text headings and clauses. Do not provide legal advice.\n\n"
            f"Document type: {request.document_type}\n"
            f"Parties: {request.parties}\n"
            f"Effective date: {request.dates}\n"
            f"Terms: {request.terms}"
        )
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt,
        )
        text = getattr(response, "text", "") or ""
        if text and text.strip():
            return text.strip()
    except ImportError as error:
        raise RuntimeError(
            "Gemini support is unavailable; install the google-genai package."
        ) from error
    except Exception as error:
        raise RuntimeError("Gemini generation failed") from error

    raise RuntimeError("Gemini returned an empty document")


@router.post("/generate")
def generate_document(request: DocumentRequest) -> dict[str, str]:
    try:
        return {"text": _generate_with_gemini(request)}
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error
