"""Letter Buddy – Safety checks and scam detection (Phase 4)."""

import re

def is_scam_deterministic(ocr_text: str) -> bool:
    ocr_lower = ocr_text.lower()
    signals = [
        "otp", "pin", "cvv", "password",
        "avoid arrest", "account suspended",
        "bit.ly", "tinyurl", "click the link",
        "urgent payment", "personal bank account", "upi",
        "transfer immediately", "credentials", "verify your identity"
    ]
    if any(s in ocr_lower for s in signals):
        return True
        
    url_pattern = r'(https?://(?:bit\.ly|tinyurl\.com|t\.co|ow\.ly)/[a-zA-Z0-9]+)'
    if re.search(url_pattern, ocr_text, flags=re.IGNORECASE):
        return True
        
    fake_authority = ["police warrant", "income tax department will arrest", "cbi inquiry"]
    if any(s in ocr_lower for s in fake_authority):
        return True
        
    return False

def is_high_stakes_deterministic(ocr_text: str) -> bool:
    ocr_lower = ocr_text.lower()
    signals = ["court", "legal", "tax demand", "loan default", "prescription", "medical", "diagnosis"]
    return any(s in ocr_lower for s in signals)
