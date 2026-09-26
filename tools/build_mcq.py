#!/usr/bin/env python3
"""Build the app's MCQ files from the PYQ Bank (Syllabus-Ordered) .docx files and the
CDI "AP History Group 2 PYQs 2025-2000 With Explanations" PDF.

Questions are attached to notes rows (Sections) through the row codes in the bank headings
(B-1, M1-B-2, S3-10 ...). CDI questions are matched to the same question in the bank (and
add their explanation to it); CDI questions not in the bank are filed under the closest
History & Culture row by text similarity.

Usage: python3 tools/build_mcq.py <mcq_src_dir> <assets_dir>
Writes <assets_dir>/mcq1.json .. mcq6.json and prints a summary.
"""
import hashlib
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import docx
import pymupdf
from docx.table import Table
from docx.text.paragraph import Paragraph

sys.path.insert(0, str(Path(__file__).parent))
from ocr_clean import Cleaner  # noqa: E402

HEAD_RE = re.compile(r"^([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+)\s+(.*?)(?:\s+\(\d+\))?\s*(?:—\s*NO PYQ)?$")
QSTART_RE = re.compile(r"^(\d+)\.\s+(.*)")
OPT_RE = re.compile(r"^\((\d)\)\s*(.*)")
ANS_RE = re.compile(r"^ANS\.\s*(?:\((\d)\))?\s*(.*)")


def norm(text):
    t = text.lower()
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def qid(stem, options):
    key = norm(stem)[:300] + "|" + "|".join(norm(o)[:60] for o in options)
    return hashlib.sha1(key.encode()).hexdigest()[:12]


# ---------------------------------------------------------------- PYQ bank (.docx)

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
W_PSTYLE = f".//{W}pStyle"
W_VAL = f"{W}val"

def parse_bank_file(path):
    d = docx.Document(path)
    out = []
    code = None
    unit = None
    q = None
    state = None  # stem / opts / ans

    def finish():
        nonlocal q
        if q:
            cancelled = "cancel" in (q.get("ans", "") + " " + q["src"]).lower()
            if cancelled and q["o"]:
                q["k"] = "u"  # cancelled by APPSC: practice only, unscored
                q["cx"] = 1
                out.append(q)
            elif cancelled:
                pass
            elif q["o"] and q["a"] is not None:
                out.append(q)
            elif not q["o"] and q.get("ans"):
                q["k"] = "f"  # answer-only: flashcard
                out.append(q)
            elif q["o"]:
                q["k"] = "u"  # no official key: unscored
                out.append(q)
        q = None

    for el in d.element.body.iterchildren():
        if el.tag.endswith("}tbl"):
            if q is not None and state == "stem":
                t = Table(el, d)
                rows = []
                for r in t.rows:
                    cells = []
                    for c in r.cells:
                        txt = re.sub(r"\s+", " ", c.text).strip()
                        if not cells or cells[-1] != txt:  # merged cells repeat
                            cells.append(txt)
                    if any(cells):
                        rows.append(cells)
                if rows:
                    q["t"] = rows
            continue
        if not el.tag.endswith("}p"):
            continue
        p = Paragraph(el, d)
        text = re.sub(r"\s+", " ", p.text).strip()
        if not text:
            continue
        ps = el.find(W_PSTYLE)
        style = ps.get(W_VAL).replace("Heading", "Heading ") if ps is not None else ""
        bold = any(r.bold for r in p.runs if r.text.strip())

        if style.startswith("Heading 2"):
            finish()
            unit = text
            code = None
            continue
        if style.startswith("Heading 3"):
            finish()
            m = HEAD_RE.match(text)
            code = m.group(1) if m else ("GENERAL" if text.startswith("General") else None)
            continue
        if code is None:
            continue

        m = QSTART_RE.match(text)
        if m and bold and state in (None, "src", "ans"):
            finish()
            q = {"code": code, "unit": unit, "s": m.group(2), "o": [], "a": None, "src": ""}
            state = "stem"
            continue
        if q is None:
            continue
        m = OPT_RE.match(text)
        if m and state in ("stem", "opts") and not bold:
            q["o"].append(m.group(2))
            state = "opts"
            continue
        m = ANS_RE.match(text)
        if m and state in ("stem", "opts"):
            q["ans"] = m.group(2).strip()
            if m.group(1):
                idx = int(m.group(1)) - 1
                q["a"] = idx if 0 <= idx < len(q["o"]) else None
            state = "ans"
            continue
        if state == "ans":
            q["src"] = text
            state = "src"
            finish()
            continue
        if state == "stem":
            q["s"] += "\n" + text
    finish()
    return out


def clean_source(src):
    """'Group 2 · 2025  answer not from APPSC key' -> ('Group 2 · 2025', appsc?)"""
    notes = r"(read from page image|text repaired by model|answer not from APPSC key|answer-only in source|" \
            r"options rebuilt|translated from Telugu|cancelled by APPSC|answer not available|State PSC|UPSC)"
    flags = src
    label = re.sub(r"\s+", " ", re.sub(notes, " ", src)).strip(" ·")
    m = re.match(r"^(.*?·\s*\d{4})", label)  # exam · year; drop extraction notes after it
    if m:
        label = m.group(1)
    appsc = not any(k in flags for k in ("State PSC", "UPSC"))
    return label, appsc


# ---------------------------------------------------------------- CDI PDF

def parse_cdi(path):
    doc = pymupdf.open(path)
    lines = []
    for p in doc:
        for b in p.get_text("blocks", sort=False):
            for ln in b[4].split("\n"):
                t = ln.strip()
                if not t or t.startswith("WWW.CARPEDIEMIAS") or "AP HISTORY GROUP II PYQS" in t or re.fullmatch(r"\d+", t):
                    continue
                lines.append(t)
    text = " ".join(lines)
    text = re.sub(r"\s+", " ", text)
    # exam headers
    exam_re = re.compile(r"(APPSC GROUP 2(?: MAINS| PRELIMS)?(?: \d{4})? (?:Held on: [\d.\-A-Za-z ]+?\d{4}|Exam Year: \d{4}))")
    chunks = exam_re.split(text)
    qs = []
    exam = ""
    for ch in chunks:
        if exam_re.fullmatch(ch or ""):
            yr = re.findall(r"(\d{4})", ch)
            exam = f"APPSC Group 2 · {yr[-1]}" if yr else "APPSC Group 2"
            continue
        if not exam:
            continue
        for part in re.split(r"(?=\bQ\d+\.\s)", ch):
            m = re.match(r"Q(\d+)\.\s+(.*)", part)
            if not m:
                continue
            body = m.group(2)
            ans_m = re.search(r"\bAnswer:\s*", body)
            if not ans_m:
                continue
            qpart, rest = body[: ans_m.start()], body[ans_m.end():]
            # options: (1) .. (4)  or  1. .. 4.
            opt_m = list(re.finditer(r"(?:^|\s)\(([1-4])\)\s", qpart))
            if len(opt_m) < 4:
                opt_m = list(re.finditer(r"(?:^|\s)([1-4])\.\s", qpart))
                # take the last run of 1..4
                seq = []
                for o in opt_m:
                    if o.group(1) == "1":
                        seq = [o]
                    elif seq and int(o.group(1)) == len(seq) + 1:
                        seq.append(o)
                opt_m = seq if len(seq) == 4 else []
            else:
                opt_m = opt_m[-4:] if [o.group(1) for o in opt_m[-4:]] == ["1", "2", "3", "4"] else []
            if len(opt_m) != 4:
                continue
            stem = qpart[: opt_m[0].start()].strip()
            opts = []
            for i, o in enumerate(opt_m):
                end = opt_m[i + 1].start() if i < 3 else len(qpart)
                opts.append(qpart[o.end():end].strip())
            am = re.match(r"\(?([1-4])\)?", rest.strip())
            if not am:
                continue
            answer = int(am.group(1)) - 1
            expl, note = "", ""
            em = re.search(r"Explanation:\s*(.*?)(?:Exam Note:\s*(.*))?$", rest)
            if em:
                expl = (em.group(1) or "").strip()
                note = (em.group(2) or "").strip()
            qs.append({"s": stem, "o": opts, "a": answer, "src": exam, "x": expl, "n": note})
    return qs


def tidy_expl(text):
    text = re.sub(r"\s+", " ", text).strip()
    # paragraph breaks before "Option (n)", "Statement", "Hence", "Therefore"
    text = re.sub(r"\s(?=(Option \(\d\)|Assertion \(A\):|Reason \(R\):|Statement \(?[A-Z12]\)?:|Hence,|Therefore,|Thus,))", "\n", text)
    return text


def tidy_note(text):
    items = [re.sub(r"\s+", " ", t).strip(" •") for t in text.split("•")]
    return [t for t in items if t]


# ---------------------------------------------------------------- similarity

def tokens(text):
    stop = {"the", "of", "and", "in", "a", "to", "is", "which", "following", "was", "by", "for", "with",
            "on", "as", "an", "are", "were", "it", "its", "that", "this", "from", "at", "be", "who", "what",
            "correct", "statements", "statement", "given", "below", "select", "answer", "using", "codes",
            "code", "incorrect", "not", "one", "only", "both", "neither", "nor", "true", "false", "his", "her"}
    return [w for w in norm(text).split() if len(w) > 2 and w not in stop and not w.isdigit()]


class Tfidf:
    def __init__(self, docs):
        self.df = Counter()
        for d in docs:
            self.df.update(set(d))
        self.n = len(docs)
        self.vecs = [self.vec(d) for d in docs]

    def vec(self, toks):
        tf = Counter(toks)
        v = {w: (1 + math.log(c)) * math.log(1 + self.n / (1 + self.df.get(w, 0))) for w, c in tf.items()}
        norm_ = math.sqrt(sum(x * x for x in v.values())) or 1
        return {w: x / norm_ for w, x in v.items()}

    def best(self, toks):
        v = self.vec(toks)
        scores = [(sum(v.get(w, 0) * x for w, x in dv.items()), i) for i, dv in enumerate(self.vecs)]
        return max(scores)


# ---------------------------------------------------------------- main

def block_text(bl):
    x = bl.get("x")
    if isinstance(x, str):
        return x
    if isinstance(x, list):
        return "".join(t for t, _ in x)
    if bl.get("k") == "t":
        cells = []
        for row in [bl.get("h", [])] + bl.get("r", []):
            for c in row:
                cells.append(c if isinstance(c, str) else "".join(t for t, _ in c))
        return " ".join(cells)
    return ""


AI_PLACEMENTS = Path(__file__).parent / "data" / "ai_subsections.json"
REHOME_ITEMS = Path(__file__).parent / "data" / "rehome_items.json"
REHOME_REJECTS = Path(__file__).parent / "data" / "review_rejects.txt"
APH_PREV = Path(__file__).parent / "data" / "aph_prev.txt"  # hand-cleaned AP History one-liners (Q || A)
GS_EXTRA = Path(__file__).parent / "data" / "appsc_gs_extra.json"  # GS questions from APPSC key PDFs not in the bank
PYQ_FIXES = Path(__file__).parent / "data" / "pyq_fixes.json"  # hand-checked text for scan-damaged questions
BROKEN_OUT = Path(__file__).parent / "data" / "broken_pyqs.json"
SECTION_ITEMS = Path(__file__).parent / "data" / "section_rehome_items.json"
SECTION_ACCEPTS = Path(__file__).parent / "data" / "section_review_accepts.txt"


def load_rehomes():
    """Hand-reviewed moves for questions the bank filed under the wrong row:
    [(book, row, qid, (to_book, to_row, to_sec))], minus the proposals rejected on review."""
    if not REHOME_ITEMS.exists():
        return []
    rejected = set()
    if REHOME_REJECTS.exists():
        for line in REHOME_REJECTS.read_text().splitlines():
            if ":" in line:
                rejected |= {int(x) for x in line.split(":", 1)[1].split()}
    items = json.loads(REHOME_ITEMS.read_text())  # review numbers are 1-based positions
    return [(b, r, i, tuple(t)) for n, (b, r, i, t) in enumerate(items, 1) if n not in rejected]


def load_section_moves():
    """Second pass, for questions no subsection fitted: hand-accepted moves to a better
    section as a whole, [(book, row, qid, (to_book, to_row))]."""
    if not SECTION_ITEMS.exists() or not SECTION_ACCEPTS.exists():
        return []
    accepted = set()
    for line in SECTION_ACCEPTS.read_text().splitlines():
        if ":" in line:
            accepted |= {int(x) for x in line.split(":", 1)[1].split()}
    items = json.loads(SECTION_ITEMS.read_text())  # review numbers are 1-based positions
    return [(b, r, i, tuple(t)) for n, (b, r, i, t) in enumerate(items, 1) if n in accepted]


def assign_subsections(book_no, book, rows_q, min_score=0.02, forced=None):
    """For each row's question list, the index of the closest subsection (■ heading), or -1.
    Questions the text match cannot place use tools/data/ai_subsections.json when present."""
    ai = json.loads(AI_PLACEMENTS.read_text()) if AI_PLACEMENTS.exists() else {}
    forced = forced or {}
    all_rows = [r for u in book["units"] for r in u["rows"]]
    docs, where = [], []
    for ri, r in enumerate(all_rows):
        for si, sec in enumerate(r["secs"]):
            text = (sec["t"] + " ") * 3 + " ".join(block_text(b) for b in sec["b"])
            docs.append(tokens(text))
            where.append((ri, si))
    tf = Tfidf(docs)
    by_row = defaultdict(list)
    for k, (ri, si) in enumerate(where):
        by_row[ri].append((si, tf.vecs[k]))
    out = {}
    for key, qs in rows_q.items():
        cands = by_row.get(int(key), [])
        res = []
        for q in qs:
            if (int(key), q["id"]) in forced:
                res.append(forced[(int(key), q["id"])])
                continue
            text = q["s"] + " " + " ".join(q["o"]) + " " + q.get("at", "")
            if 0 <= q.get("a", -1) < len(q["o"]):
                text += " " + q["o"][q["a"]] * 2  # the correct option says most about the topic
            v = tf.vec(tokens(text))
            best, best_si = 0.0, -1
            for si, dv in cands:
                sc = sum(x * dv.get(w, 0) for w, x in v.items())
                if sc > best:
                    best, best_si = sc, si
            si = best_si if best >= min_score else -1
            if si < 0:
                si = ai.get(f"{book_no}:{key}:{q['id']}", -1)
            res.append(si)
        out[key] = res
    return out


def main():
    src, assets = Path(sys.argv[1]), Path(sys.argv[2])

    # notes rows: code -> [(book, row)], unit code -> (book, unit)
    code_rows = defaultdict(list)
    row_unit = {}
    unit_of = {}
    books = {}
    for n in range(1, 7):
        b = json.loads((assets / f"book{n}.json").read_text())
        books[n] = b
        seq = 0
        for ui, u in enumerate(b["units"]):
            if u["code"]:
                unit_of[u["code"]] = (n, ui)
            for r in u["rows"]:
                for c in r["codes"]:
                    code_rows[c].append((n, seq))
                row_unit[(n, seq)] = ui
                seq += 1

    per_row = defaultdict(dict)   # (book,row) -> {qid: q}
    per_unit = defaultdict(dict)  # (book,unit) -> {qid: q}
    all_q = {}
    stats = Counter()

    bank = []
    for f in sorted(src.glob("*.docx")):
        cache = f.with_suffix(".parsed3.json")
        if cache.exists() and cache.stat().st_mtime > f.stat().st_mtime:
            qs = json.loads(cache.read_text())
        else:
            qs = parse_bank_file(f)
            cache.write_text(json.dumps(qs, ensure_ascii=False))
        for q in qs:
            q["file"] = f.name
        bank += qs
    # bank unit (file, heading) -> notes unit, by majority of its questions' rows
    votes = defaultdict(Counter)
    for q in bank:
        for t in code_rows.get(q["code"], []):
            bk, r = t
            votes[(q["file"], q["unit"])][(bk, row_unit[t])] += 1
    unit_target = {k: v.most_common(1)[0][0] for k, v in votes.items()}
    if True:
        qs = bank
        stats["bank_parsed"] += len(qs)
        for q in qs:
            label, appsc = clean_source(q["src"])
            kind = q.get("k")
            item = {"s": q["s"], "o": q["o"], "a": q["a"] if q["a"] is not None else -1, "src": label}
            if kind:
                item["k"] = kind
            if q.get("cx"):
                item["cx"] = 1
            if kind == "f":
                item["at"] = q["ans"]
            if appsc:
                item["ap"] = 1
            if "t" in q:
                item["t"] = q["t"]
            i = qid(q["s"], q["o"])
            item["id"] = i
            all_q.setdefault(i, item)
            item = all_q[i]
            if q["code"] == "GENERAL":
                m = re.match(r"UNIT\s+(\S+)", q["unit"] or "")
                target = unit_of.get(m.group(1)) if m else None
                target = target or unit_target.get((q["file"], q["unit"]))
                if target:
                    per_unit[target][i] = item
                    stats["general_to_unit"] += 1
                else:
                    stats["general_dropped"] += 1
                continue
            targets = code_rows.get(q["code"])
            if not targets:
                stats["unmapped_code"] += 1
                continue
            for t in targets:
                per_row[t][i] = item
            stats["mapped"] += 1

    # candidate rows for AP history: book 1 rows
    b1_rows = []
    for ui, u in enumerate(books[1]["units"]):
        for r in u["rows"]:
            text = r["title"] + " " + " ".join(s["t"] for s in r["secs"])
            body = []
            for s in r["secs"]:
                for bl in s["b"]:
                    x = bl.get("x")
                    if isinstance(x, str):
                        body.append(x)
                    elif isinstance(x, list):
                        body.append("".join(t for t, _ in x))
            b1_rows.append(tokens(text * 3) + tokens(" ".join(body))[:4000])
    tf = Tfidf(b1_rows)
    # ---- CDI: merge explanations into bank questions, file the rest by similarity
    cdi_path = next(src.glob("*Cdi*AP-History*.pdf"), None)
    if cdi_path:
        cdi = parse_cdi(cdi_path)
        stats["cdi_parsed"] = len(cdi)
        by_norm = {}
        for i, q in all_q.items():
            by_norm.setdefault(norm(q["s"])[:120], i)
        # fuzzy: token sets of APPSC bank questions, looked up through an inverted index
        qtok = {i: set(tokens(q["s"] + " " + " ".join(q["o"]))) for i, q in all_q.items() if q.get("ap")}
        inv = defaultdict(set)
        for i, ts in qtok.items():
            for w in ts:
                inv[w].add(i)

        def trigrams(t):
            t = norm(t)
            return {t[k:k + 3] for k in range(len(t) - 2)}

        def jac(a, b):
            return len(a & b) / max(1, len(a | b))

        # same Group 2 paper (year) in the bank: compare stem trigrams + option words
        by_year = defaultdict(list)
        for i, q in all_q.items():
            m = re.match(r"Group 2 · (\d{4})", q["src"])
            if m:
                by_year[m.group(1)].append((trigrams(q["s"]), set(tokens(" ".join(q["o"]))), i))

        def same_paper(c):
            st, ot = trigrams(c["s"]), set(tokens(" ".join(c["o"])))
            best, best_i = 0.0, None
            for bs, bo, i in by_year.get(c["src"][-4:], []):
                sc = 0.5 * jac(st, bs) + 0.5 * jac(ot, bo)
                if sc > best:
                    best, best_i = sc, i
            return best_i if best >= 0.4 else None

        def fuzzy(c):
            ts = set(tokens(c["s"] + " " + " ".join(c["o"])))
            if len(ts) < 3:
                return None
            cand = Counter()
            for w in ts:
                if len(inv[w]) < 400:
                    cand.update(inv[w])
            best, best_i = 0.0, None
            for i, _ in cand.most_common(30):
                j = len(ts & qtok[i]) / len(ts | qtok[i])
                if j > best:
                    best, best_i = j, i
            return best_i if best >= 0.6 else None
        row_of_q = defaultdict(set)
        for key, qd in per_row.items():
            for i in qd:
                row_of_q[i].add(key)
        for c in cdi:
            i = by_norm.get(norm(c["s"])[:120]) or same_paper(c) or fuzzy(c)
            expl = tidy_expl(c["x"])
            note = tidy_note(c["n"])
            if i and i in all_q:
                all_q[i]["x"] = expl
                if note:
                    all_q[i]["n"] = note
                stats["cdi_matched_bank"] += 1
                if i in row_of_q:
                    continue
            item = {"s": c["s"], "o": c["o"], "a": c["a"], "src": c["src"], "ap": 1, "x": expl}
            if note:
                item["n"] = note
            item["id"] = i or qid(c["s"], c["o"])
            score, ri = tf.best(tokens(c["s"] + " " + " ".join(c["o"]) + " " + " ".join(note)))
            per_row[(1, ri)][item["id"]] = item
            stats["cdi_added_by_similarity"] += 1

    # ---- AP History one-liners ("previous papers.pdf"): recall cards for the ones not already in the bank
    if APH_PREV.exists():
        ap_tok = {i: set(tokens(q["s"] + " " + " ".join(q["o"]) + " " + q.get("at", ""))) for i, q in all_q.items()}
        ap_inv = defaultdict(set)
        for i, ts in ap_tok.items():
            for w in ts:
                ap_inv[w].add(i)
        part = "pyq"
        for line in APH_PREV.read_text().splitlines():
            if line.startswith("## "):
                part = line[3:].strip()
                continue
            if "||" not in line or line.startswith("#"):
                continue
            cue, ans = (x.strip() for x in line.split("||", 1))
            ts = set(tokens(cue + " " + ans))
            cand = Counter()
            for w in ts:
                if len(ap_inv[w]) < 400:
                    cand.update(ap_inv[w])
            same = [i for i, _ in cand.most_common(20) if ts and len(ts & ap_tok[i]) / len(ts) >= 0.75]
            if same:
                q = all_q[same[0]]
                if not q["o"] and not q.get("at"):  # bank has the question but no answer: take the PDF's
                    q.update(k="f", at=ans, a=-1)
                    stats["aph_prev_answered_bank_q"] += 1
                stats["aph_prev_already_in_bank"] += 1
                continue
            item = {"s": cue, "o": [], "a": -1, "k": "f", "at": ans, "id": qid(cue, [])}
            if part == "pyq":
                item.update(src="AP History PYQs 1983-2024 (one-liners)", ap=1)
            else:
                item["src"] = "AP History one-liner notes"
            score, ri = tf.best(tokens(cue + " " + ans))
            per_row[(1, ri)][item["id"]] = item
            all_q.setdefault(item["id"], item)
            stats["aph_prev_added"] += 1

    # ---- extra APPSC GS questions from the official key PDFs (mental ability left out), filed by similarity
    if GS_EXTRA.exists():
        all_rows, where = [], []
        for bk in sorted(books):
            flat = 0
            for u in books[bk]["units"]:
                for r in u["rows"]:
                    body = []
                    for sec in r["secs"]:
                        for bl in sec["b"]:
                            x = bl.get("x")
                            body.append(x if isinstance(x, str) else "".join(t for t, _ in x) if isinstance(x, list) else "")
                    all_rows.append(tokens((r["title"] + " " + " ".join(sec["t"] for sec in r["secs"])) * 3) + tokens(" ".join(body))[:4000])
                    where.append((bk, flat)); flat += 1
        tf_all = Tfidf(all_rows)
        for q in json.loads(GS_EXTRA.read_text()):
            item = {"s": q["s"], "o": q["o"], "a": q["a"], "src": q["src"], "ap": 1}
            if not q["o"]:
                item.update(k="f", at=q["at"], a=-1)
            item["id"] = qid(q["s"], q["o"])
            if item["id"] in all_q:
                continue
            score, ri = tf_all.best(tokens(q["s"] + " " + " ".join(q["o"]) + " " + q.get("at", "")))
            per_row[where[ri]][item["id"]] = item
            all_q[item["id"]] = item
            stats["gs_extra_added"] += 1

    # ---- reviewed re-homes: move misfiled questions to the row and subsection they belong to
    forced = defaultdict(dict)
    for bk, r, i, (tb, tr, ts) in load_rehomes():
        item = per_row.get((bk, r), {}).pop(i, None)
        if item is None:
            stats["rehome_missing"] += 1
            continue
        per_row[(tb, tr)][i] = item
        forced[tb][(tr, i)] = ts
        stats["rehomed"] += 1
    for bk, r, i, (tb, tr) in load_section_moves():
        item = per_row.get((bk, r), {}).pop(i, None)
        if item is None:
            stats["section_move_missing"] += 1
            continue
        if i not in per_row[(tb, tr)]:
            forced[tb][(tr, i)] = -1  # reviewed at section level only: keep under "Other"
        per_row[(tb, tr)][i] = item
        stats["section_moved"] += 1
    for key in [k for k, v in per_row.items() if not v]:
        del per_row[key]

    # ---- trim OCR junk left by scanned papers; list what is still too broken to fix here
    uniq = {}
    for d in list(per_row.values()) + list(per_unit.values()):
        for i, q in d.items():
            uniq[id(q)] = q
    texts = []
    for b in books.values():
        for u in b["units"]:
            for r in u["rows"]:
                texts.append(r["title"])
                for sec in r["secs"]:
                    texts.append(sec["t"])
                    texts += [block_text(x) for x in sec["b"]]
    texts += [q["s"] + " " + " ".join(q["o"]) for q in uniq.values()]
    fixes = json.loads(PYQ_FIXES.read_text()) if PYQ_FIXES.exists() else {}
    for q in uniq.values():
        f = fixes.get(q["id"])
        if f and not f.get("ok") and not f.get("drop"):
            q["s"], q["o"], q["a"] = f["s"], f["o"], f["a"]
            if "at" in f:
                q["at"] = f["at"]
            stats["hand_fixed"] += 1
    # questions whose content was lost in the scan (charts, missing options) are left out
    dropped = {i for i, f in fixes.items() if f.get("drop")}
    for d in list(per_row.values()) + list(per_unit.values()):
        for i in [i for i in d if i in dropped]:
            del d[i]
            stats["dropped_unrecoverable"] += 1
    uniq = {k: q for k, q in uniq.items() if q["id"] not in dropped}
    cleaner = Cleaner(texts)
    broken = []
    for q in uniq.values():
        stats["ocr_trimmed"] += cleaner.clean_question(q)
        lv = cleaner.level(q)
        if lv and q["id"] not in fixes:  # everything in the fixes file was checked by hand
            broken.append({"level": lv, "id": q["id"], "src": q["src"], "s": q["s"], "o": q["o"]})
    stats["ocr_badly_broken"] = sum(1 for b in broken if b["level"] == 2)
    stats["ocr_partly_broken"] = sum(1 for b in broken if b["level"] == 1)
    broken.sort(key=lambda b: (b["src"], -b["level"]))
    BROKEN_OUT.write_text(json.dumps(broken, ensure_ascii=False, indent=1))

    # ---- write one file per book: rows -> questions, units -> general questions
    for n in range(1, 7):
        rows = {str(r): list(qd.values()) for (bk, r), qd in sorted(per_row.items()) if bk == n}
        units = {str(u): list(qd.values()) for (bk, u), qd in sorted(per_unit.items()) if bk == n}
        # APPSC questions first, then the rest
        for d in (rows, units):
            for k in d:
                d[k].sort(key=lambda q: ({"f": 1, "u": 2}.get(q.get("k"), 0), 0 if q.get("ap") else 1))
        subs = assign_subsections(n, books[n], rows, forced=forced[n])
        stats[f"book{n}_sub_assigned"] = sum(1 for v in subs.values() for x in v if x >= 0)
        (assets / f"mcq{n}.json").write_text(
            json.dumps({"rows": rows, "units": units, "subs": subs}, ensure_ascii=False, separators=(",", ":")))
        print(f"mcq{n}: rows={len(rows)} q_in_rows={sum(len(v) for v in rows.values())} "
              f"unit_general={sum(len(v) for v in units.values())}")
    print(dict(stats), "unique", len(all_q), "kinds", Counter(q.get("k", "scored") for q in all_q.values()))
    index_path = assets / "index.json"
    index = json.loads(index_path.read_text())
    for b in index["books"]:
        for ri, r in enumerate(b["rows"]):
            r["q"] = len(per_row.get((b["id"], ri), {}))
        b["uq"] = {str(u): len(qd) for (bk, u), qd in per_unit.items() if bk == b["id"]}
    index_path.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
