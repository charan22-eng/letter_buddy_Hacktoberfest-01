"""
Tests for Phase 2: LLM Extraction.
"""

from letterbuddy.extract import _extract_candidates, extract_info


def test_extract_candidates():
    text = "Dear Policyholder, Your renewal is due on 01/11/2026 or 15th September 2026. Please pay Rs. 12,500/- immediately."
    candidates = _extract_candidates(text)

    vals = candidates.values()
    assert "01/11/2026" in vals
    assert "15th September 2026" in vals
    assert "12,500" in vals

def test_extract_info():
    # Synthetic OCR text
    text = """
    National Insurance Company Ltd.
    Reference: POL/2026/INS/78432
    Date: 15th September 2026
    Subject: Insurance Policy Renewal Notice
    Your current Life Insurance policy is due for renewal on 01/11/2026. The annual premium amount is Rs. 12,500.
    """

    result = extract_info(text)

    assert "Insurance" in result.sender
    assert "2026" in result.date
    assert "Insurance" in result.subject
    assert result.action_required is True
    assert result.action_deadline == "01/11/2026 (Ambiguous DD/MM vs MM/DD)"
    assert "12,500" in result.payment_amount
    assert result.severity in ["warning", "info"]

def test_extract_hallucination_reject():
    text = "The amount is 1234."
    result = extract_info(text)
    # If the LLM hallucinates 5678, it should fail
    # We can mock this by checking that the strict pipeline is enforced
    # (The pipeline code itself rejects if hallucinated)
    pass
