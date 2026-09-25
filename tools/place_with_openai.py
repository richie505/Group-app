#!/usr/bin/env python3
"""Place the PYQs that build_mcq.py could not match to a subsection, using the OpenAI API.

For every section (notes row), the unplaced questions are sent in batches together with
that section's numbered subsection titles; the model answers with the best subsection
number for each question, or 0 when none fits (those stay in "Other PYQs of this section").

Answers are cached in tools/data/ai_subsections.json ("book:row:question_id" -> subsection
index or -1), so a re-run only asks about questions not yet answered. build_mcq.py applies
this file on its next run.

Usage:
    OPENAI_API_KEY=... python3 tools/place_with_openai.py app/src/main/assets [--dry-run] [--limit N]
Environment: OPENAI_MODEL (default gpt-4o-mini).
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

CACHE = Path(__file__).parent / "data" / "ai_subsections.json"
BATCH = 20
API_URL = "https://api.openai.com/v1/chat/completions"


def question_text(q):
    parts = [q["s"].strip()]
    for row in q.get("t", []):
        parts.append(" | ".join(row))
    for i, o in enumerate(q["o"]):
        parts.append(f"({i + 1}) {o}")
    if q.get("k") == "f":
        parts.append(f"Answer: {q.get('at', '')}")
    elif 0 <= q.get("a", -1) < len(q["o"]):
        parts.append(f"Answer: ({q['a'] + 1}) {q['o'][q['a']]}")
    return "\n".join(parts)[:1500]


def ask(model, key, section, subsections, batch):
    subs = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(subsections))
    qs = "\n\n".join(f"Q{n + 1}:\n{question_text(q)}" for n, q in enumerate(batch))
    prompt = (
        f"Study-notes section: {section}\n\nIts subsections:\n{subs}\n\n"
        "For each exam question below, give the number of the ONE subsection whose topic the "
        "question tests. Use 0 only if the question is not about any of these subsections.\n\n"
        f"{qs}\n\n"
        'Reply with JSON only: {"answers": [n1, n2, ...]} with exactly one number per question, in order.'
    )
    body = json.dumps({
        "model": model,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": "You classify exam questions into study-note subsections. Reply with JSON only."},
            {"role": "user", "content": prompt},
        ],
    }).encode()
    for attempt in range(5):
        req = urllib.request.Request(API_URL, data=body, headers={
            "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.load(r)
            answers = json.loads(data["choices"][0]["message"]["content"])["answers"]
            if len(answers) != len(batch):
                raise ValueError(f"expected {len(batch)} answers, got {len(answers)}")
            usage = data.get("usage", {})
            return [int(a) for a in answers], usage
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                sys.exit(f"OpenAI refused the key (HTTP {e.code}). Check OPENAI_API_KEY.")
            wait = 2 ** attempt * (5 if e.code == 429 else 2)
            print(f"  HTTP {e.code}, retrying in {wait}s", flush=True)
            time.sleep(wait)
        except (ValueError, KeyError, json.JSONDecodeError, urllib.error.URLError, TimeoutError) as e:
            wait = 2 ** attempt * 2
            print(f"  {type(e).__name__}: {e}; retrying in {wait}s", flush=True)
            time.sleep(wait)
    return None, {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("assets")
    ap.add_argument("--dry-run", action="store_true", help="count work and show one prompt; no API calls")
    ap.add_argument("--limit", type=int, default=0, help="stop after this many questions (for a test run)")
    args = ap.parse_args()
    assets = Path(args.assets)
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key and not args.dry_run:
        sys.exit("OPENAI_API_KEY is not set.")

    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    jobs = []  # (book, row, section title, subsection titles, [questions])
    for n in range(1, 7):
        book = json.loads((assets / f"book{n}.json").read_text())
        rows = [r for u in book["units"] for r in u["rows"]]
        mcq = json.loads((assets / f"mcq{n}.json").read_text())
        for key_row, qs in mcq["rows"].items():
            ri = int(key_row)
            subs = mcq.get("subs", {}).get(key_row, [])
            todo = [q for q, s in zip(qs, subs) if s < 0 and f"{n}:{ri}:{q['id']}" not in cache]
            if todo and rows[ri]["secs"]:
                jobs.append((n, ri, rows[ri]["title"], [s["t"] for s in rows[ri]["secs"]], todo))

    total = sum(len(j[4]) for j in jobs)
    print(f"{total} questions to place across {len(jobs)} sections (model {model}); {len(cache)} already cached")
    if args.dry_run:
        if jobs:
            n, ri, title, subs, todo = jobs[0]
            print("\n--- example batch ---")
            print(f"Section: {title}\nSubsections: {len(subs)}\nFirst question:\n{question_text(todo[0])}")
        return

    done = placed = 0
    tokens_in = tokens_out = 0
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    for n, ri, title, subs, todo in jobs:
        for b in range(0, len(todo), BATCH):
            batch = todo[b:b + BATCH]
            answers, usage = ask(model, key, title, subs, batch)
            if answers is None:
                print(f"  giving up on a batch in book {n} row {ri}; it stays unplaced", flush=True)
                continue
            tokens_in += usage.get("prompt_tokens", 0)
            tokens_out += usage.get("completion_tokens", 0)
            for q, a in zip(batch, answers):
                idx = a - 1 if 1 <= a <= len(subs) else -1
                cache[f"{n}:{ri}:{q['id']}"] = idx
                placed += idx >= 0
            done += len(batch)
            CACHE.write_text(json.dumps(cache, separators=(",", ":")))
            print(f"{done}/{total} done, {placed} placed  (tokens in {tokens_in}, out {tokens_out})", flush=True)
            if args.limit and done >= args.limit:
                print("limit reached")
                return
    print(f"finished: {placed} of {done} placed in a subsection; the rest stay in 'Other PYQs'")


if __name__ == "__main__":
    main()
