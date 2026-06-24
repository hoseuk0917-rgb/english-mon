from pathlib import Path
import json
import random
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"

MASTER = DATA / "word_master_v0_1.json"
OUT_JSON = DATA / "question_bank_v0_1.json"
OUT_AUDIT = DOCS / "question_bank_audit_v0_1.md"

SEED = 20260624
rng = random.Random(SEED)

payload = json.loads(MASTER.read_text(encoding="utf-8"))
words = payload["words"]

EXPECTED_WORDS = 100
QUESTION_TYPES = [
    "meaning_sniper",
    "cipher_blank",
    "typo_repair",
    "boss_input",
]

def make_question_id(word_id, qtype):
    suffix = {
        "meaning_sniper": "MS",
        "cipher_blank": "CB",
        "typo_repair": "TR",
        "boss_input": "BI",
    }[qtype]
    return f"Q-{word_id}-{suffix}"

def choose_distractors(target, all_words, count=3):
    same_unit = [
        w for w in all_words
        if w["unit"] == target["unit"] and w["word_id"] != target["word_id"]
    ]
    other = [
        w for w in all_words
        if w["unit"] != target["unit"] and w["word_id"] != target["word_id"]
    ]

    pool = same_unit[:]
    rng.shuffle(pool)

    selected = pool[:count]

    if len(selected) < count:
        rng.shuffle(other)
        selected.extend(other[:count - len(selected)])

    return selected[:count]

def make_meaning_sniper(w):
    distractors = choose_distractors(w, words, 3)
    options = [
        {
            "option_id": "A",
            "text": w["meaning_ko"],
            "is_answer": True,
        }
    ]

    for d in distractors:
        options.append({
            "option_id": "",
            "text": d["meaning_ko"],
            "is_answer": False,
        })

    rng.shuffle(options)

    for idx, opt in enumerate(options):
        opt["option_id"] = chr(ord("A") + idx)

    answer = next(opt["option_id"] for opt in options if opt["is_answer"])

    return {
        "question_id": make_question_id(w["word_id"], "meaning_sniper"),
        "type": "meaning_sniper",
        "word_id": w["word_id"],
        "unit": w["unit"],
        "prompt": {
            "word": w["word"],
            "instruction": "Choose the Korean meaning."
        },
        "options": options,
        "answer": answer,
        "answer_text": w["meaning_ko"],
        "skill": ["meaning", "recognition"],
        "difficulty": 1
    }

def mask_word(word):
    chars = list(word)
    alpha_positions = [i for i, c in enumerate(chars) if c.isalpha()]

    if len(alpha_positions) <= 3:
        k = 1
    elif len(alpha_positions) <= 6:
        k = 2
    elif len(alpha_positions) <= 9:
        k = 3
    else:
        k = 4

    protected = {0, len(chars) - 1}
    candidates = [i for i in alpha_positions if i not in protected]

    if len(candidates) < k:
        candidates = alpha_positions[:]

    selected = sorted(rng.sample(candidates, k))
    blanks = []

    for i in selected:
        blanks.append({
            "index": i,
            "letter": chars[i]
        })
        chars[i] = "_"

    return "".join(chars), blanks

def make_cipher_blank(w):
    masked, blanks = mask_word(w["word"])

    return {
        "question_id": make_question_id(w["word_id"], "cipher_blank"),
        "type": "cipher_blank",
        "word_id": w["word_id"],
        "unit": w["unit"],
        "prompt": {
            "meaning_ko": w["meaning_ko"],
            "masked_word": masked,
            "instruction": "Fill the missing letters."
        },
        "answer": w["word"],
        "blanks": blanks,
        "skill": ["spelling", "letter_position"],
        "difficulty": 2
    }

def make_typo(word):
    chars = list(word)

    repeated = []
    for i in range(1, len(chars)):
        if chars[i].lower() == chars[i - 1].lower() and chars[i].isalpha():
            repeated.append(i)

    if repeated:
        i = repeated[0]
        typo = "".join(chars[:i] + chars[i + 1:])
        if typo != word:
            return typo, "missing_double_letter"

    vowels = "aeiou"
    for i, c in enumerate(chars):
        if c.lower() in vowels:
            replacement = {
                "a": "e",
                "e": "a",
                "i": "e",
                "o": "a",
                "u": "o",
            }.get(c.lower(), "a")

            new_chars = chars[:]
            new_chars[i] = replacement.upper() if c.isupper() else replacement
            typo = "".join(new_chars)
            if typo != word:
                return typo, "vowel_confusion"

    for i in range(len(chars) - 1):
        if chars[i].isalpha() and chars[i + 1].isalpha():
            new_chars = chars[:]
            new_chars[i], new_chars[i + 1] = new_chars[i + 1], new_chars[i]
            typo = "".join(new_chars)
            if typo != word:
                return typo, "letter_swap"

    return word + "e", "extra_letter"

def make_typo_repair(w):
    typo, pattern = make_typo(w["word"])

    return {
        "question_id": make_question_id(w["word_id"], "typo_repair"),
        "type": "typo_repair",
        "word_id": w["word_id"],
        "unit": w["unit"],
        "prompt": {
            "meaning_ko": w["meaning_ko"],
            "typo_word": typo,
            "instruction": "Repair the typo."
        },
        "answer": w["word"],
        "typo_pattern": pattern,
        "skill": ["spelling", "error_detection"],
        "difficulty": 2
    }

def make_boss_input(w):
    return {
        "question_id": make_question_id(w["word_id"], "boss_input"),
        "type": "boss_input",
        "word_id": w["word_id"],
        "unit": w["unit"],
        "prompt": {
            "meaning_ko": w["meaning_ko"],
            "pos": w["pos"],
            "instruction": "Type the full English word."
        },
        "answer": w["word"],
        "skill": ["meaning", "spelling", "recall"],
        "difficulty": 3
    }

questions = []

for w in words:
    questions.append(make_meaning_sniper(w))
    questions.append(make_cipher_blank(w))
    questions.append(make_typo_repair(w))
    questions.append(make_boss_input(w))

errors = []

if len(words) != EXPECTED_WORDS:
    errors.append(f"word count expected {EXPECTED_WORDS}, actual {len(words)}")

expected_questions = EXPECTED_WORDS * len(QUESTION_TYPES)
if len(questions) != expected_questions:
    errors.append(f"question count expected {expected_questions}, actual {len(questions)}")

word_question_counts = Counter(q["word_id"] for q in questions)
for w in words:
    if word_question_counts[w["word_id"]] != len(QUESTION_TYPES):
        errors.append(
            f"word question count mismatch: {w['word_id']} / {word_question_counts[w['word_id']]}"
        )

type_counts = Counter(q["type"] for q in questions)
for qtype in QUESTION_TYPES:
    if type_counts[qtype] != EXPECTED_WORDS:
        errors.append(f"type count mismatch: {qtype} / {type_counts[qtype]}")

question_ids = [q["question_id"] for q in questions]
dupe_qids = [k for k, v in Counter(question_ids).items() if v > 1]
if dupe_qids:
    errors.append(f"duplicate question_id: {dupe_qids}")

for q in questions:
    if not str(q.get("answer", "")).strip():
        errors.append(f"blank answer: {q['question_id']}")

    if q["type"] == "meaning_sniper":
        if len(q.get("options", [])) != 4:
            errors.append(f"bad option count: {q['question_id']}")
        if sum(1 for opt in q["options"] if opt["is_answer"]) != 1:
            errors.append(f"bad answer option count: {q['question_id']}")

    if q["type"] == "cipher_blank":
        if "_" not in q["prompt"]["masked_word"]:
            errors.append(f"no blank in cipher: {q['question_id']}")

    if q["type"] == "typo_repair":
        if q["prompt"]["typo_word"] == q["answer"]:
            errors.append(f"typo same as answer: {q['question_id']}")

if errors:
    print("=== QUESTION BANK VALIDATION FAILED ===")
    for e in errors:
        print("- " + e)
    raise SystemExit(1)

question_bank = {
    "schema_version": "englishmon.question_bank.v0.1",
    "title": "EnglishMon Question Bank v0.1",
    "source_master": "data/word_master_v0_1.json",
    "seed": SEED,
    "summary": {
        "word_count": len(words),
        "question_count": len(questions),
        "question_types": QUESTION_TYPES,
        "questions_per_word": len(QUESTION_TYPES)
    },
    "questions": questions
}

OUT_JSON.write_text(
    json.dumps(question_bank, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

unit_counts = Counter(q["unit"] for q in questions)

audit = []
audit.append("# EnglishMon Question Bank Audit v0.1")
audit.append("")
audit.append("## Summary")
audit.append("")
audit.append(f"- Source master: data/word_master_v0_1.json")
audit.append(f"- Word count: {len(words)}")
audit.append(f"- Question count: {len(questions)}")
audit.append(f"- Questions per word: {len(QUESTION_TYPES)}")
audit.append(f"- Seed: {SEED}")
audit.append("")
audit.append("## Type Counts")
audit.append("")
for qtype in QUESTION_TYPES:
    audit.append(f"- {qtype}: {type_counts[qtype]}")
audit.append("")
audit.append("## Unit Counts")
audit.append("")
for unit in [4, 6, 7, 8, 10]:
    audit.append(f"- Unit {unit}: {unit_counts[unit]}")
audit.append("")
audit.append("## Coverage")
audit.append("")
audit.append("- Every word has 4 questions: OK")
audit.append("- Duplicate question_id: 0")
audit.append("- Blank answer: 0")
audit.append("- Meaning sniper option count: OK")
audit.append("- Cipher blanks: OK")
audit.append("- Typo repair: OK")
audit.append("")
audit.append("## Question Types")
audit.append("")
audit.append("- meaning_sniper: English word -> choose Korean meaning")
audit.append("- cipher_blank: Korean meaning + masked spelling -> fill letters")
audit.append("- typo_repair: Korean meaning + wrong spelling -> repair typo")
audit.append("- boss_input: Korean meaning -> type full English word")
audit.append("")

OUT_AUDIT.write_text("\n".join(audit) + "\n", encoding="utf-8")

print("=== QUESTION BANK CREATED ===")
print(f"JSON : {OUT_JSON}")
print(f"AUDIT: {OUT_AUDIT}")
print(f"WORDS: {len(words)}")
print(f"QUESTIONS: {len(questions)}")
for qtype in QUESTION_TYPES:
    print(f"{qtype}: {type_counts[qtype]}")
