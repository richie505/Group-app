"""Where a PYQ was asked (from its source line): "g2" APPSC Group 2 paper, "ap" another APPSC paper, "up" UPSC,
"ot" other exams; and its year when the source names one (for the trend view)."""
import re

G2 = re.compile(r"APPSC.*Group[- ]?(II|2)\b(?!.*Panchayat)|^Group[- ]?II (Screening|Mains|Prelims)", re.I)
UP = re.compile(r"\b(UPSC|IAS|CSE|Civil Services)\b", re.I)


def tier(q):
    s = q.get("src") or ""
    if G2.search(s) and not re.search(r"TSPSC|Telangana", s, re.I):
        return "g2"
    if q.get("ap") or "APPSC" in s.upper():
        return "ap"
    if UP.search(s):
        return "up"
    return "ot"


def year(q):
    m = re.findall(r"(19[6-9]\d|20[0-3]\d)", q.get("src") or "")
    return int(m[-1]) if m else 0
