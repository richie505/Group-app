"""Which MCQs are already one-liners (APPSC One-liners): a one-line stem and four short options, none of them a
combination of statements ("1 and 2 only", "Both", "a-iii, b-i", "C, D, B, A") or a count ("Only two")."""
import re

COMBO = re.compile(r"(?i)^\s*(only\s+(one|two|three|four)|all\s+(four|three|of the above)|none of the above|both\b|neither\b|"
                   r"[1-6](\s*(,|and|&|or)\s*[1-6])+(\s*only)?\s*$|[1-6]\s+only\s*$|[a-f]\s*[-–—]\s*[ivx]+|[A-F](\s*,\s*[A-F]){2,}|"
                   r"(A|R)\b.*\b(true|false|explanation)|statement)")


def oneliner(q):
    s = q["s"].strip()
    if "\n" in s or len(s) > 220:
        return False
    if re.search(r"(?i)\b(assertion|reason \(r\)|list[- ]?i\b|statements?\b|following pairs|correctly matched|chronological|arrange)", s):
        return False
    if len(q["o"]) != 4 or any(COMBO.search(o) or len(o) > 90 for o in q["o"]):
        return False
    return True
