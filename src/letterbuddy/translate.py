"""
Letter Buddy – Translation (Phase 3).

Translates the simplified summary into the user's native language using Ollama.
"""

import re

import httpx

from letterbuddy.config import cfg
from letterbuddy.extract import ExtractedLetter


def translate_summary(letter: ExtractedLetter) -> str:
    """Translate the summary into the target language."""
    # Safety: Advice phrase blocklist
    blocklist = [r"\bi recommend\b", r"\bmy advice\b", r"\bsuggest you\b", r"\bmedical advice\b", r"\bfinancial advice\b"]
    summary_lower = letter.summary.lower()
    for phrase in blocklist:
        if re.search(phrase, summary_lower):
            letter.summary += " [NOTE: Ignore any advice above, consult a professional.]"
            break

    target_lang = cfg.language.target
    if target_lang == "en":
        return letter.summary

    prompt = f"""
Translate the following simple summary into {target_lang}.
Ensure the tone is respectful, simple, and clear for an elderly person to understand.
Do not add any extra commentary or introductory text. Reply ONLY with the translated text.

TEXT TO TRANSLATE:
{letter.summary}
"""

    model = cfg.llm.primary
    host = "http://127.0.0.1:11434"

    try:
        response = httpx.post(
            f"{host}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120.0
        )
        response.raise_for_status()
        result = response.json()
        translated = result["response"].strip()

        # Safety: Digit preservation check (V-FAITH-6)
        orig_digits = set(filter(str.isdigit, letter.summary))
        trans_digits = set(filter(str.isdigit, translated))
        if orig_digits - trans_digits:
            raise ValueError("Translation dropped or altered numbers")

        return translated
    except Exception as e:
        return f"{letter.summary}\n(గమనిక: {str(e)})"
