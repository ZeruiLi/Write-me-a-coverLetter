from langdetect import detect


def detect_lang(text: str) -> str:
    try:
        lang = detect(text or "")
        return "zh" if lang.startswith("zh") else "en"
    except Exception:
        return "en"

