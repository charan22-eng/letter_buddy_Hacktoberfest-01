"""
Letter Buddy – LLM extraction (Phase 2).

Takes raw OCR text, finds deterministic candidates for dates and numbers,
and uses Ollama to extract structured information.
"""

from __future__ import annotations

import json
import re

import httpx
from pydantic import BaseModel, Field

from letterbuddy.config import cfg


class ExtractedLetter(BaseModel):
    sender: str = Field(description="The name of the organization or person sending the letter")
    date: str | None = Field(None, description="The date the letter was sent")
    subject: str | None = Field(None, description="The main subject or reference of the letter")
    summary: str = Field(description="A 1-2 sentence simple summary of what the letter is about")
    action_required: bool = Field(description="True if the recipient needs to do something")
    action_deadline: str | None = Field(None, description="The deadline for the action, if any")
    severity: str = Field(description="Must be one of: 'info', 'warning', 'critical'")
    payment_amount: str | None = Field(None, description="Any payment amount required, e.g., '12,500'")
    needs_person: bool = Field(False, description="True if court/tax/loan/medical document")
    is_scam: bool = Field(False, description="True if there are scam signals (threats, urgent OTP requests)")
    prescription_doses: str | None = Field(None, description="If prescription, exact verbatim text of the doses")


def _extract_candidates(ocr_text: str) -> dict[str, str]:
    """Extract deterministic candidates and map to IDs."""
    candidates = {}

    date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b'
    dates = list(set(re.findall(date_pattern, ocr_text, flags=re.IGNORECASE)))
    for i, d in enumerate(dates):
        candidates[f"D{i}"] = d

    amount_pattern = r'(?:Rs\.?|₹|INR|\$)?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
    amounts = []
    for amt in re.findall(amount_pattern, ocr_text):
        if len(amt.replace(',', '')) > 2 or '.' in amt:
            amounts.append(amt)
    for i, a in enumerate(list(set(amounts))):
        candidates[f"A{i}"] = a

    contact_pattern = r'([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})'
    contacts = list(set(re.findall(contact_pattern, ocr_text)))
    for i, c in enumerate(contacts):
        candidates[f"C{i}"] = c

    return candidates

def extract_info(ocr_text: str) -> ExtractedLetter:
    candidates = _extract_candidates(ocr_text)
    candidate_lines = "\n".join([f"{k}: {v}" for k, v in candidates.items()])

    prompt = f"""
You are a highly accurate assistant that extracts structured data from official letters.
Read the following OCR text from a letter and extract the requested fields.

RULES:
1. You MUST use candidate IDs (e.g. D0, A1, C2) for sender, date, action_deadline, and payment_amount. Do not write the actual text, ONLY the ID. If none apply, output null.
2. The summary should be extremely simple, as if explaining to an elderly person.
3. Severity must be strictly one of: "info", "warning", "critical". 
4. Set needs_person=true if it involves court, tax, loans, or medical prescriptions.
5. Set is_scam=true if there are threats of arrest, account suspension, or urgent OTP requests.

CANDIDATES (Use these IDs):
{candidate_lines}

OCR TEXT:
{ocr_text}

Respond ONLY with a valid JSON object matching this schema:
{{
  "sender": "string (C# ID or null)",
  "date": "string (D# ID or null)",
  "subject": "string or null",
  "summary": "string",
  "action_required": boolean,
  "action_deadline": "string (D# ID or null)",
  "severity": "string",
  "payment_amount": "string (A# ID or null)",
  "needs_person": boolean,
  "is_scam": boolean,
  "prescription_doses": "string or null"
}}
"""

    model = cfg.llm.primary
    host = "http://127.0.0.1:11434"

    try:
        response = httpx.post(
            f"{host}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False, "format": "json"},
            timeout=120.0
        )
        response.raise_for_status()
        data = json.loads(response.json()["response"])

        # Resolve IDs and enforce restrictions
        def resolve_id(val):
            if not val: return None
            if val in candidates: return candidates[val]
            raise ValueError(f"Unknown candidate ID used: {val}")

        data["sender"] = resolve_id(data.get("sender")) or "Unknown"
        data["date"] = resolve_id(data.get("date"))
        data["action_deadline"] = resolve_id(data.get("action_deadline"))
        data["payment_amount"] = resolve_id(data.get("payment_amount"))

        # Flag ambiguous dates (V-EXT-2)
        def flag_ambiguous(val):
            if val and re.match(r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$', val):
                parts = re.split(r'[/-]', val)
                if int(parts[0]) <= 12 and int(parts[1]) <= 12:
                    return f"{val} (Ambiguous DD/MM vs MM/DD)"
            return val

        data["date"] = flag_ambiguous(data["date"])
        data["action_deadline"] = flag_ambiguous(data["action_deadline"])

        # Check this number for low confidence (V-FAITH-4)
        if data["payment_amount"] and "(low confidence)" in data["payment_amount"].lower():
             data["payment_amount"] += " ⚠️ CHECK THIS NUMBER"

        # Hallucination check (V-FAITH-1/2/3/5): ensure no extra digits in summary not present in OCR
        summary_digits = set(filter(str.isdigit, data.get("summary", "")))
        ocr_digits = set(filter(str.isdigit, ocr_text))
        if summary_digits - ocr_digits:
            raise ValueError(f"Hallucination detected: summary contains digits {summary_digits - ocr_digits} not in OCR.")

        letter = ExtractedLetter(**data)

        # Safety must not depend on LLM alone (V-SAFE)
        from letterbuddy.safety import is_high_stakes_deterministic, is_scam_deterministic
        if is_scam_deterministic(ocr_text):
            letter.is_scam = True
            letter.severity = "critical"
        if is_high_stakes_deterministic(ocr_text):
            letter.needs_person = True

        return letter

    except Exception as e:
        letter = ExtractedLetter(
            sender="Unknown",
            date=None,
            subject=None,
            summary=f"Extraction failed/rejected: {str(e)}",
            action_required=False,
            action_deadline=None,
            severity="warning",
            payment_amount=None,
            needs_person=False,
            is_scam=False,
            prescription_doses=None
        )
        
        from letterbuddy.safety import is_scam_deterministic, is_high_stakes_deterministic
        if is_scam_deterministic(ocr_text):
            letter.is_scam = True
            letter.severity = "critical"
        if is_high_stakes_deterministic(ocr_text):
            letter.needs_person = True
            
        return letter
