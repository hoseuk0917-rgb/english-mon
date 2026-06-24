from pathlib import Path
import json
import re
import random
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"

MASTER_V02 = DATA / "word_master_v0_2.json"
QBANK_V02 = DATA / "question_bank_v0_2.json"

QBANK_V03 = DATA / "question_bank_v0_3.json"
AUDIT = DOCS / "question_bank_audit_v0_3.md"
LOCK = DOCS / "definition_writing_pack_lock_v0_3.md"

SEED = 20260624
rng = random.Random(SEED)

master = json.loads(MASTER_V02.read_text(encoding="utf-8"))
qbank_v02 = json.loads(QBANK_V02.read_text(encoding="utf-8"))

words = master["words"]
base_questions = qbank_v02["questions"]

stopwords = {
    "a", "an", "the", "to", "of", "in", "on", "at", "for", "with", "and", "or",
    "that", "which", "who", "when", "where", "what", "your", "you", "it", "is",
    "are", "be", "as", "by", "from", "into", "up", "out", "not", "than", "etc",
    "something", "someone", "anything", "else"
}

def clean_token(token):
    return re.sub(r"[^A-Za-z]", "", token)

def choose_blank_word(definition):
    tokens = definition.split()
    candidates = []

    for idx, token in enumerate(tokens):
        cleaned = clean_token(token)
        if len(cleaned) < 4:
            continue
        if cleaned.lower() in stopwords:
            continue
        candidates.append((idx, token, cleaned))

    if not candidates:
        for idx, token in enumerate(tokens):
            cleaned = clean_token(token)
            if cleaned:
                candidates.append((idx, token, cleaned))

    if not candidates:
        return definition, ""

    candidates.sort(key=lambda x: len(x[2]), reverse=True)
    idx, original_token, answer = candidates[0]

    masked_tokens = tokens[:]
    masked_tokens[idx] = "_" * len(answer)

    return " ".join(masked_tokens), answer

def make_question_id(word_id, qtype):
    suffix = {
        "definition_one_blank": "OB",
        "definition_full_input": "FI",
    }[qtype]
    return f"Q-{word_id}-{suffix}"

def make_definition_one_blank(w):
    masked, answer = choose_blank_word(w["definition_en"])
    return {
        "question_id": make_question_id(w["word_id"], "definition_one_blank"),
        "type": "definition_one_blank",
        "word_id": w["word_id"],
        "unit": w["unit"],
        "prompt": {
            "word": w["word"],
            "pos": w["pos"],
            "definition_masked": masked,
            "definition_en": w["definition_en"],
            "instruction": "Fill one blank in the English definition from the PDF."
        },
        "answer": answer,
        "answer_text": answer,
        "full_definition": w["definition_en"],
        "skill": ["definition", "writing", "partial_recall"],
        "difficulty": 3
    }

def make_definition_full_input(w):
    return {
        "question_id": make_question_id(w["word_id"], "definition_full_input"),
        "type": "definition_full_input",
        "word_id": w["word_id"],
        "unit": w["unit"],
        "prompt": {
            "word": w["word"],
            "pos": w["pos"],
            "instruction": "Type the full English definition from the PDF."
        },
        "answer": w["definition_en"],
        "answer_text": w["definition_en"],
        "skill": ["definition", "writing", "full_recall"],
        "difficulty": 5
    }

new_questions = []
for w in words:
    new_questions.append(make_definition_one_blank(w))
    new_questions.append(make_definition_full_input(w))

questions = base_questions + new_questions

expected_types = [
    "definition_sniper",
    "cipher_blank",
    "typo_repair",
    "boss_input",
    "definition_one_blank",
    "definition_full_input",
]

errors = []

if len(words) != 100:
    errors.append(f"words expected 100, actual {len(words)}")

if len(base_questions) != 400:
    errors.append(f"base questions expected 400, actual {len(base_questions)}")

if len(new_questions) != 200:
    errors.append(f"new questions expected 200, actual {len(new_questions)}")

if len(questions) != 600:
    errors.append(f"total questions expected 600, actual {len(questions)}")

type_counts = Counter(q["type"] for q in questions)
for qtype in expected_types:
    if type_counts[qtype] != 100:
        errors.append(f"{qtype} expected 100, actual {type_counts[qtype]}")

word_counts = Counter(q["word_id"] for q in questions)
for w in words:
    if word_counts[w["word_id"]] != 6:
        errors.append(f"{w['word_id']} expected 6 questions, actual {word_counts[w['word_id']]}")

qid_counts = Counter(q["question_id"] for q in questions)
dupes = [k for k, v in qid_counts.items() if v > 1]
if dupes:
    errors.append(f"duplicate question_id: {dupes}")

for q in questions:
    if not str(q.get("answer", "")).strip():
        errors.append(f"blank answer: {q.get('question_id')}")

    if q["type"] == "definition_one_blank":
        masked = q["prompt"].get("definition_masked", "")
        if "_" not in masked:
            errors.append(f"definition_one_blank has no blank: {q['question_id']}")

if errors:
    print("=== V0.3 BUILD FAILED ===")
    for e in errors:
        print("- " + e)
    raise SystemExit(1)

qbank_v03 = {
    "schema_version": "englishmon.question_bank.v0.3",
    "title": "EnglishMon Question Bank v0.3 - Definition Writing Modes",
    "source_master": "data/word_master_v0_2.json",
    "source_previous_bank": "data/question_bank_v0_2.json",
    "seed": SEED,
    "summary": {
        "word_count": len(words),
        "question_count": len(questions),
        "study_target": "PDF English definitions",
        "question_types": expected_types,
        "questions_per_word": 6
    },
    "questions": questions
}

QBANK_V03.write_text(json.dumps(qbank_v03, ensure_ascii=False, indent=2), encoding="utf-8")

unit_counts = Counter(q["unit"] for q in questions)

audit = []
audit.append("# EnglishMon Question Bank Audit v0.3")
audit.append("")
audit.append("## Summary")
audit.append("")
audit.append("- Study target: PDF English definitions")
audit.append(f"- Word count: {len(words)}")
audit.append(f"- Question count: {len(questions)}")
audit.append("- Questions per word: 6")
audit.append("")
audit.append("## Type Counts")
audit.append("")
for qtype in expected_types:
    audit.append(f"- {qtype}: {type_counts[qtype]}")
audit.append("")
audit.append("## Unit Counts")
audit.append("")
for unit in [4, 6, 7, 8, 10]:
    audit.append(f"- Unit {unit}: {unit_counts[unit]}")
audit.append("")
audit.append("## Added in v0.3")
audit.append("")
audit.append("- definition_one_blank: word -> fill one blank in English definition")
audit.append("- definition_full_input: word -> type full English definition")
audit.append("")
AUDIT.write_text("\n".join(audit) + "\n", encoding="utf-8")

lock = []
lock.append("# EnglishMon Definition Writing Pack Lock v0.3")
lock.append("")
lock.append("## Locked Files")
lock.append("")
lock.append("- data/question_bank_v0_3.json")
lock.append("- docs/question_bank_audit_v0_3.md")
lock.append("")
lock.append("## Validation")
lock.append("")
lock.append(f"- Words: {len(words)}")
lock.append(f"- Questions: {len(questions)}")
lock.append("- Every word has 6 questions: OK")
lock.append("- definition_one_blank: 100")
lock.append("- definition_full_input: 100")
lock.append("")
lock.append("## Study Target")
lock.append("")
lock.append("The student must memorize and write the English definition beside each word in the PDF.")
lock.append("")
LOCK.write_text("\n".join(lock) + "\n", encoding="utf-8")

print("=== DEFINITION WRITING PACK V0.3 CREATED ===")
print(f"QBANK: {QBANK_V03}")
print(f"AUDIT: {AUDIT}")
print(f"LOCK : {LOCK}")
print(f"QUESTIONS: {len(questions)}")
for qtype in expected_types:
    print(f"{qtype}: {type_counts[qtype]}")
