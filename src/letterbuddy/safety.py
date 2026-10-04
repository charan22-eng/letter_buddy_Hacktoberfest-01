"""Letter Buddy – Safety checks and scam detection (Phase 4)."""

def is_scam_deterministic(ocr_text: str) -> bool:
    ocr_lower = ocr_text.lower()
    signals = [
        "otp", "pin", "cvv", "password",
        "avoid arrest", "account suspended",
        "bit.ly", "tinyurl", "click the link"
    ]
    return any(s in ocr_lower for s in signals)

def is_high_stakes_deterministic(ocr_text: str) -> bool:
    ocr_lower = ocr_text.lower()
    signals = ["court", "legal", "tax demand", "loan default", "prescription"]
    return any(s in ocr_lower for s in signals)
