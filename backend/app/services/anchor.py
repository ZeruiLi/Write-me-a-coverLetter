from __future__ import annotations

import hashlib
import re


def normalize_text(text: str) -> str:
    t = text.replace('\r\n', '\n').replace('\r', '\n')
    t = re.sub(r"[\t\x0b\x0c]", " ", t)
    t = re.sub(r" +", " ", t)
    return t


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def find_span(anchor_text: str, quote: str) -> tuple[int, int]:
    if not quote:
        raise ValueError("empty quote")
    idx = anchor_text.find(quote)
    if idx < 0:
        raise ValueError("quote_not_found")
    return idx, idx + len(quote)

