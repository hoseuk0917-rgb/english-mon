from pathlib import Path
import json
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"

MASTER = DATA / "word_master_v0_1.json"
QBANK = DATA / "question_bank_v0_1.json"
LOCK = DOCS / "question_bank_lock_v0_1.md"

master = json.loads(MASTER.read_text(encoding="utf-8"))
qbank = json.loads(QBANK.read_text(encoding="utf-8"))

words = master.get("words", [])
questions = qbank.get("questions", [])

word_ids = {w["word_id"] for w in words}
expected_types = ["meaning_sniper", "cipher_blank", "typo_repair", "boss_input"]

errors = []

if len(words) != 100:
    errors.append(f"master words expected 100, actual {len(words)}")

if len(questions) != 400:
    errors.append(f"questions expected 400, actual {len(questions)}")

qid_counts = Counter(q.get("question_id") for q in questions)
dupe_qids = [k for k, v in qid_counts.items() if v > 1]
if dupe_qids:
    errors.append(f"duplicate question_id: {dupe_qids}")

type_counts = Counter(q.get("type") for q in questions)
for t in expected_types:
    if type_counts[t] != 100:
        errors.append(f"type {t} expected 100, actual {type_counts[t]}")

word_question_counts = Counter(q.get("word_id") for q in questions)
for wid in word_ids:
    if word_question_counts[wid] != 4:
        errors.append(f"{wid} expected 4 questions, actual {word_question_counts[wid]}")

for q in questions:
    qid = q.get("question_id", "")
    wid = q.get("word_id", "")
    qtype = q.get("type", "")

    if wid not in word_ids:
        errors.append(f"unknown word_id in question: {qid} / {wid}")

    if qtype not in expected_types:
        errors.append(f"unknown question type: {qid} / {qtype}")

    if not str(q.get("answer", "")).strip():
        errors.append(f"blank answer: {qid}")

    if qtype == "meaning_sniper":
        options = q.get("options", [])
        if len(options) != 4:
            errors.append(f"meaning_sniper option count != 4: {qid}")
        if sum(1 for o in options if o.get("is_answer") is True) != 1:
            errors.append(f"meaning_sniper answer option count != 1: {qid}")

    if qtype == "cipher_blank":
        masked = q.get("prompt", {}).get("masked_word", "")
        if "_" not in masked:
            errors.append(f"cipher_blank has no blank: {qid}")

    if qtype == "typo_repair":
        typo = q.get("prompt", {}).get("typo_word", "")
        answer = q.get("answer", "")
        if typo == answer:
            errors.append(f"typo_repair typo equals answer: {qid}")

if errors:
    print("=== QUESTION BANK VALIDATION FAILED ===")
    for e in errors:
        print("- " + e)
    raise SystemExit(1)

unit_counts = Counter(q.get("unit") for q in questions)

lines = []
lines.append("# EnglishMon Question Bank Lock v0.1")
lines.append("")
lines.append("## Locked Files")
lines.append("")
lines.append("- data/question_bank_v0_1.json")
lines.append("- docs/question_bank_audit_v0_1.md")
lines.append("")
lines.append("## Validation Result")
lines.append("")
lines.append(f"- Master words: {len(words)}")
lines.append(f"- Questions: {len(questions)}")
for t in expected_types:
    lines.append(f"- {t}: {type_counts[t]}")
lines.append("")
lines.append("## Unit Question Counts")
lines.append("")
for unit in [4, 6, 7, 8, 10]:
    lines.append(f"- Unit {unit}: {unit_counts[unit]}")
lines.append("")
lines.append("## Coverage")
lines.append("")
lines.append("- Every word has 4 questions: OK")
lines.append("- Duplicate question_id: 0")
lines.append("- Blank answer: 0")
lines.append("- Meaning sniper options: OK")
lines.append("- Cipher blanks: OK")
lines.append("- Typo repair: OK")
lines.append("")

LOCK.write_text("\n".join(lines), encoding="utf-8")

print("=== QUESTION BANK LOCKED ===")
print(f"MASTER   : {MASTER}")
print(f"QUESTION : {QBANK}")
print(f"LOCK     : {LOCK}")
print(f"QUESTIONS: {len(questions)}")
for t in expected_types:
    print(f"{t}: {type_counts[t]}")
