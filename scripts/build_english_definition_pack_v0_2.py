from pathlib import Path
import json
import random
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"

MASTER_V01 = DATA / "word_master_v0_1.json"
MASTER_V02 = DATA / "word_master_v0_2.json"
QBANK_V02 = DATA / "question_bank_v0_2.json"
AUDIT_MASTER = DOCS / "word_master_audit_v0_2.md"
AUDIT_QBANK = DOCS / "question_bank_audit_v0_2.md"
LOCK = DOCS / "english_definition_pack_lock_v0_2.md"

SEED = 20260624
rng = random.Random(SEED)

definition_map = {
    "biography": "a book about a person's life",
    "brilliant": "extremely smart or talented",
    "calendar": "a chart that shows the days, weeks, or months of a year",
    "coupon": "a note that allows you to get something for free or at a discount",
    "crossword": "a word game in a pattern of black and white squares",
    "crush": "to press something so that its shape is destroyed",
    "differ": "to be unlike another or others",
    "organic": "grown without artificial chemicals",
    "pea": "a round green seed, eaten as a vegetable",
    "reputation": "the general opinion people have about someone or something",
    "bargain": "something on sale at a lower price than usual",
    "basically": "used when referring to the main or most important characteristic of something",
    "caffeine": "a chemical found in tea and coffee that affects your body and brain",
    "carton": "a cardboard container in which food or drink is stored",
    "deposit": "to put money in a bank",
    "forbid": "to say that something must not be done",
    "pickle": "to preserve food in salt or vinegar",
    "pork": "the flesh of a pig",
    "suburb": "an area on the edge of a town or city",
    "whereas": "compared with the fact that; but",

    "asteroid": "a large rock that floats in space",
    "cable": "a set of wires wrapped in plastic",
    "circumstance": "a situation or condition",
    "crater": "a large hole in the ground caused by an explosion or something hitting it",
    "defense": "the act or power of standing up against harm or danger",
    "emit": "to produce and send out",
    "galaxy": "a very large group of stars and planets",
    "incident": "something that happens, often unpleasant",
    "launch": "to send something out, such as a new ship",
    "massive": "very large",
    "authority": "the power to make decisions and tell people what to do",
    "clone": "to produce an identical copy of a living thing",
    "comet": "a bright object with a long tail that travels around the sun",
    "diagram": "a simple drawing to explain something",
    "encounter": "to experience something; to meet someone",
    "geology": "the study of the substances that make up the earth's surface",
    "lens": "a curved piece of glass or plastic that makes things look smaller or bigger",
    "originate": "to come from a particular place, time, etc.",
    "spacecraft": "a rocket or other vehicle that can travel in space",
    "steel": "a strong metal made of iron mixed with other metals",

    "Aboriginal": "of the native peoples of Australia",
    "campfire": "an outdoor fire when camping",
    "chronological": "arranged in the time order that events happened",
    "footstep": "the sound of someone's foot hitting the ground",
    "gear": "the equipment and clothes used for a particular activity",
    "inhabit": "to live in a certain place",
    "migrate": "to travel to a different place, usually when the season changes",
    "priority": "something to receive attention before others",
    "shrink": "to become smaller",
    "vast": "great in size or number",
    "alert": "quick to see, understand, and act",
    "canyon": "a long, narrow valley with steep sides",
    "conquer": "to defeat an enemy, problem, fear, etc.",
    "controversial": "causing discussion and debate",
    "dawn": "the time of day when light first appears in the sky",
    "harmony": "a situation in which people are peaceful and agree with each other",
    "inhabitant": "a person or animal who lives in a certain place",
    "nevertheless": "in spite of that; however",
    "occupy": "to fill, exist in, or use a place or time",
    "paddle": "to move a boat through water with an oar",

    "hacker": "a person who breaks into computer systems",
    "harsh": "unpleasant or severe",
    "industrial": "related to industry or manufacturing",
    "lottery": "a game of chance in which people buy numbered tickets",
    "millionaire": "a rich person with at least $1,000,000 worth of money or property",
    "obtain": "to get; to achieve",
    "resort": "a place where people go for rest or leisure",
    "skyscraper": "a very tall building",
    "tempt": "to make someone want to have or do something",
    "virtual": "able to be done or seen using a computer",
    "inspector": "a person whose job is to make sure people are obeying regulations",
    "invest": "to put time, effort, or money into something to obtain a profit or benefit",
    "luxury": "expensive and of high quality",
    "motorcycle": "a two-wheeled vehicle with an engine",
    "orphan": "a child whose parents are dead",
    "slope": "a straight surface with one end higher than the other",
    "snowboard": "to ride a board down a snowy slope",
    "snowman": "a model of a person made of snow",
    "terrific": "amazing",
    "tire": "a rubber ring that fits around the wheel of a car or bike",

    "aerobic": "requiring oxygen",
    "devoted": "extremely loving and loyal",
    "fitness": "the condition of being physically strong and healthy",
    "glance": "to take a quick look",
    "gymnastics": "physical activities intended to increase strength and flexibility",
    "hesitate": "to pause before acting or speaking",
    "melody": "a tune",
    "register": "to put your name on an official list",
    "sleeve": "the part of clothing that covers the arm",
    "specialize": "to become knowledgeable about a particular subject or job",
    "occasionally": "sometimes, but not regularly",
    "pure": "not mixed with anything else",
    "raw": "uncooked",
    "reject": "to refuse to accept or use",
    "rumor": "gossip that is not based on proven facts",
    "sunrise": "the time in the morning when the sun starts to rise in the sky",
    "tobacco": "a substance made from dried leaves that people smoke",
    "vegetarian": "consisting only of vegetables or fruit",
    "workout": "a period of physical exercise",
    "zipper": "a device for opening and closing clothes and bags",
}

master = json.loads(MASTER_V01.read_text(encoding="utf-8"))
words = master["words"]

errors = []

if len(words) != 100:
    errors.append(f"word count expected 100, actual {len(words)}")

for w in words:
    word = w["word"]
    if word not in definition_map:
        errors.append(f"missing definition_en: {w['word_id']} / {word}")

if len(definition_map) != 100:
    errors.append(f"definition_map expected 100, actual {len(definition_map)}")

if errors:
    print("=== V0.2 BUILD FAILED ===")
    for e in errors:
        print("- " + e)
    raise SystemExit(1)

words_v02 = []
for w in words:
    item = dict(w)
    item["definition_en"] = definition_map[w["word"]]
    item["study_target"] = "definition_en"
    words_v02.append(item)

master_v02 = dict(master)
master_v02["schema_version"] = "englishmon.word_master.v0.2"
master_v02["title"] = "EnglishMon Word Master v0.2 - English Definition Target"
master_v02["source"]["study_target"] = "PDF English definitions beside each word"
master_v02["words"] = words_v02

MASTER_V02.write_text(json.dumps(master_v02, ensure_ascii=False, indent=2), encoding="utf-8")

QUESTION_TYPES = ["definition_sniper", "cipher_blank", "typo_repair", "boss_input"]

def make_question_id(word_id, qtype):
    suffix = {
        "definition_sniper": "DS",
        "cipher_blank": "CB",
        "typo_repair": "TR",
        "boss_input": "BI",
    }[qtype]
    return f"Q-{word_id}-{suffix}"

def choose_distractors(target, all_words, count=3):
    same_unit = [w for w in all_words if w["unit"] == target["unit"] and w["word_id"] != target["word_id"]]
    other = [w for w in all_words if w["unit"] != target["unit"] and w["word_id"] != target["word_id"]]
    rng.shuffle(same_unit)
    rng.shuffle(other)
    selected = same_unit[:count]
    if len(selected) < count:
        selected.extend(other[:count - len(selected)])
    return selected[:count]

def make_definition_sniper(w):
    distractors = choose_distractors(w, words_v02, 3)
    options = [{"option_id": "A", "text": w["definition_en"], "is_answer": True}]
    for d in distractors:
        options.append({"option_id": "", "text": d["definition_en"], "is_answer": False})
    rng.shuffle(options)
    for idx, opt in enumerate(options):
        opt["option_id"] = chr(ord("A") + idx)
    answer = next(opt["option_id"] for opt in options if opt["is_answer"])
    return {
        "question_id": make_question_id(w["word_id"], "definition_sniper"),
        "type": "definition_sniper",
        "word_id": w["word_id"],
        "unit": w["unit"],
        "prompt": {
            "word": w["word"],
            "instruction": "Choose the English definition from the PDF."
        },
        "options": options,
        "answer": answer,
        "answer_text": w["definition_en"],
        "skill": ["definition", "recognition"],
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
        blanks.append({"index": i, "letter": chars[i]})
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
            "definition_en": w["definition_en"],
            "meaning_ko": w["definition_en"],
            "masked_word": masked,
            "instruction": "Fill the missing letters using the English definition."
        },
        "answer": w["word"],
        "blanks": blanks,
        "skill": ["spelling", "definition"],
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
            replacement = {"a": "e", "e": "a", "i": "e", "o": "a", "u": "o"}.get(c.lower(), "a")
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
            "definition_en": w["definition_en"],
            "meaning_ko": w["definition_en"],
            "typo_word": typo,
            "instruction": "Repair the typo using the English definition."
        },
        "answer": w["word"],
        "typo_pattern": pattern,
        "skill": ["spelling", "error_detection", "definition"],
        "difficulty": 2
    }

def make_boss_input(w):
    return {
        "question_id": make_question_id(w["word_id"], "boss_input"),
        "type": "boss_input",
        "word_id": w["word_id"],
        "unit": w["unit"],
        "prompt": {
            "definition_en": w["definition_en"],
            "meaning_ko": w["definition_en"],
            "pos": w["pos"],
            "instruction": "Type the full English word using the English definition."
        },
        "answer": w["word"],
        "skill": ["definition", "spelling", "recall"],
        "difficulty": 3
    }

questions = []
for w in words_v02:
    questions.append(make_definition_sniper(w))
    questions.append(make_cipher_blank(w))
    questions.append(make_typo_repair(w))
    questions.append(make_boss_input(w))

type_counts = Counter(q["type"] for q in questions)
unit_counts = Counter(q["unit"] for q in questions)
word_question_counts = Counter(q["word_id"] for q in questions)

errors = []

if len(questions) != 400:
    errors.append(f"question count expected 400, actual {len(questions)}")

for qtype in QUESTION_TYPES:
    if type_counts[qtype] != 100:
        errors.append(f"{qtype} expected 100, actual {type_counts[qtype]}")

for w in words_v02:
    if word_question_counts[w["word_id"]] != 4:
        errors.append(f"{w['word_id']} expected 4 questions, actual {word_question_counts[w['word_id']]}")

if errors:
    print("=== QUESTION BANK V0.2 FAILED ===")
    for e in errors:
        print("- " + e)
    raise SystemExit(1)

qbank_v02 = {
    "schema_version": "englishmon.question_bank.v0.2",
    "title": "EnglishMon Question Bank v0.2 - English Definition Target",
    "source_master": "data/word_master_v0_2.json",
    "seed": SEED,
    "summary": {
        "word_count": len(words_v02),
        "question_count": len(questions),
        "study_target": "definition_en",
        "question_types": QUESTION_TYPES,
        "questions_per_word": 4
    },
    "questions": questions
}

QBANK_V02.write_text(json.dumps(qbank_v02, ensure_ascii=False, indent=2), encoding="utf-8")

master_audit = []
master_audit.append("# EnglishMon Word Master Audit v0.2")
master_audit.append("")
master_audit.append("- Study target: English definitions from PDF")
master_audit.append(f"- Total words: {len(words_v02)}")
for unit in [4, 6, 7, 8, 10]:
    master_audit.append(f"- Unit {unit}: {sum(1 for w in words_v02 if w['unit'] == unit)}")
master_audit.append("- Missing definition_en: 0")
master_audit.append("")
master_audit.append("## Word List")
master_audit.append("")
for unit in [4, 6, 7, 8, 10]:
    master_audit.append(f"### Unit {unit}")
    master_audit.append("")
    for w in [x for x in words_v02 if x["unit"] == unit]:
        master_audit.append(f"- {w['word_id']} / {w['word']} / {w['definition_en']}")
    master_audit.append("")
AUDIT_MASTER.write_text("\n".join(master_audit) + "\n", encoding="utf-8")

qbank_audit = []
qbank_audit.append("# EnglishMon Question Bank Audit v0.2")
qbank_audit.append("")
qbank_audit.append("- Study target: English definitions from PDF")
qbank_audit.append(f"- Word count: {len(words_v02)}")
qbank_audit.append(f"- Question count: {len(questions)}")
qbank_audit.append("- Questions per word: 4")
qbank_audit.append("")
qbank_audit.append("## Type Counts")
qbank_audit.append("")
for qtype in QUESTION_TYPES:
    qbank_audit.append(f"- {qtype}: {type_counts[qtype]}")
qbank_audit.append("")
qbank_audit.append("## Unit Counts")
qbank_audit.append("")
for unit in [4, 6, 7, 8, 10]:
    qbank_audit.append(f"- Unit {unit}: {unit_counts[unit]}")
qbank_audit.append("")
AUDIT_QBANK.write_text("\n".join(qbank_audit) + "\n", encoding="utf-8")

lock = []
lock.append("# EnglishMon English Definition Pack Lock v0.2")
lock.append("")
lock.append("## Locked Files")
lock.append("")
lock.append("- data/word_master_v0_2.json")
lock.append("- data/question_bank_v0_2.json")
lock.append("- docs/word_master_audit_v0_2.md")
lock.append("- docs/question_bank_audit_v0_2.md")
lock.append("")
lock.append("## Validation")
lock.append("")
lock.append(f"- Words: {len(words_v02)}")
lock.append(f"- Questions: {len(questions)}")
lock.append("- Missing English definitions: 0")
lock.append("- Every word has 4 questions: OK")
lock.append("")
lock.append("## Study Target")
lock.append("")
lock.append("The student studies the English definition beside each word in the PDF, not the Korean meaning.")
lock.append("")
LOCK.write_text("\n".join(lock), encoding="utf-8")

print("=== ENGLISH DEFINITION PACK V0.2 CREATED ===")
print(f"MASTER : {MASTER_V02}")
print(f"QBANK  : {QBANK_V02}")
print(f"WORDS  : {len(words_v02)}")
print(f"QUESTIONS: {len(questions)}")
for qtype in QUESTION_TYPES:
    print(f"{qtype}: {type_counts[qtype]}")
