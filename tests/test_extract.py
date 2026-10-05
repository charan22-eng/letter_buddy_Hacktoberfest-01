"""
Tests for Phase 2: LLM Extraction.
"""

from letterbuddy.extract import _extract_candidates, extract_info


def test_extract_candidates():
    text = "Dear Policyholder, Your renewal is due on 01/11/2026 or 15th September 2026. Please pay Rs. 12,500/- immediately."
    candidates = _extract_candidates(text)

    vals = [c["value"] for c in candidates.values()]
    assert "01/11/2026" in vals
    assert "15th September 2026" in vals
    assert "Rs. 12,500" in vals

def test_extract_specific_candidates():
    text = "01/02/2026 05/10/2026 5th Oct 2026 2026-10-05 ₹2,500.50 Rs. 750/- 1,00,000 +91 98765 43210 email@example.com https://example.com REF-12345 POLICY-88991"
    candidates = _extract_candidates(text)
    vals = [c["value"] for c in candidates.values()]
    assert "01/02/2026" in vals
    assert "05/10/2026" in vals
    assert "5th Oct 2026" in vals
    assert "2026-10-05" in vals
    assert "₹2,500.50" in vals
    assert "Rs. 750" in vals
    assert "1,00,000" in vals
    assert "+91 98765 43210" in vals
    assert "email@example.com" in vals
    assert "https://example.com" in vals
    assert "REF-12345" in vals
    assert "POLICY-88991" in vals

def test_extract_info(monkeypatch):
    import httpx
    class MockResponse:
        def raise_for_status(self): pass
        def json(self):
            return {"response": '{"sender": "C0", "date": "D0", "action_deadline": "D1", "payment_amount": "A0", "summary": "Insurance policy 2026 12,500", "severity": "warning", "action_required": true, "needs_person": false, "is_scam": false}'}
    def mock_post(*args, **kwargs):
        return MockResponse()
    monkeypatch.setattr(httpx, "post", mock_post)

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
    assert result.action_required is True
    assert result.action_deadline == "01/11/2026 (Ambiguous DD/MM vs MM/DD)"
    assert "12,500" in result.payment_amount
    assert result.severity in ["warning", "info"]

def test_ambiguous_date_parsing(monkeypatch):
    import httpx
    class MockResponse:
        def raise_for_status(self): pass
        def json(self):
            return {"response": '{"sender": null, "date": "D0", "summary": "Test", "severity": "info", "action_required": false, "needs_person": false, "is_scam": false}'}
    def mock_post(*args, **kwargs):
        return MockResponse()
    monkeypatch.setattr(httpx, "post", mock_post)

    result = extract_info("01/02/2026")
    assert result.date == "01/02/2026 (Ambiguous DD/MM vs MM/DD)"

def test_extract_hallucination_reject(monkeypatch):
    import httpx
    class MockResponse:
        def raise_for_status(self): pass
        def json(self):
            return {"response": '{"sender": null, "summary": "Test 1234", "severity": "info", "action_required": false, "needs_person": false, "is_scam": false}'}
    def mock_post(*args, **kwargs):
        return MockResponse()
    monkeypatch.setattr(httpx, "post", mock_post)

    result = extract_info("The amount is 5678.")
    assert "Extraction failed/rejected: Hallucination detected" in result.summary

def test_candidate_id_validation(monkeypatch):
    import httpx
    class MockResponse:
        def raise_for_status(self): pass
        def json(self):
            return {"response": '{"sender": "X99", "summary": "Test", "severity": "info", "action_required": false, "needs_person": false, "is_scam": false}'}
    def mock_post(*args, **kwargs):
        return MockResponse()
    monkeypatch.setattr(httpx, "post", mock_post)
    result = extract_info("Some text")
    assert "Extraction failed/rejected" in result.summary

def test_fake_candidates(monkeypatch):
    import httpx
    class MockResponse:
        def raise_for_status(self): pass
        def json(self):
            return {"response": '{"sender": null, "date": "D99", "payment_amount": "A99", "phone": "P99", "url": "U99", "reference": "R99", "summary": "Test", "severity": "info", "action_required": false, "needs_person": false, "is_scam": false}'}
    def mock_post(*args, **kwargs):
        return MockResponse()
    monkeypatch.setattr(httpx, "post", mock_post)
    result = extract_info("Valid text 01/01/2026")
    assert "Extraction failed/rejected" in result.summary
