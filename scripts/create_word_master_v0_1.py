from pathlib import Path
import json
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"
DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

SOURCE_FILE = "2_1_final_english.pdf"

raw_words = [
    ("U04-001", 4, 20, "biography", "n.", "\uc804\uae30, \uc77c\ub300\uae30"),
    ("U04-002", 4, 20, "brilliant", "adj.", "\ub9e4\uc6b0 \ub611\ub611\ud55c, \uc7ac\ub2a5 \uc788\ub294, \ud6cc\ub96d\ud55c"),
    ("U04-003", 4, 20, "calendar", "n.", "\ub2ec\ub825, \uc77c\uc815\ud45c"),
    ("U04-004", 4, 20, "coupon", "n.", "\ucfe0\ud3f0, \ud560\uc778\uad8c"),
    ("U04-005", 4, 20, "crossword", "n.", "\uc2ed\uc790\ub9d0\ud480\uc774"),
    ("U04-006", 4, 20, "crush", "v.", "\uc73c\uae68\ub2e4, \ucc0c\uadf8\ub7ec\ub728\ub9ac\ub2e4"),
    ("U04-007", 4, 20, "differ", "v.", "\ub2e4\ub974\ub2e4, \ucc28\uc774\uac00 \ub098\ub2e4"),
    ("U04-008", 4, 20, "organic", "adj.", "\uc720\uae30\ub18d\uc758, \ud654\ud559\ubb3c\uc9c8\uc744 \uc4f0\uc9c0 \uc54a\uc740"),
    ("U04-009", 4, 20, "pea", "n.", "\uc644\ub450\ucf69"),
    ("U04-010", 4, 20, "reputation", "n.", "\ud3c9\ud310, \uba85\uc131"),
    ("U04-011", 4, 22, "bargain", "n.", "\uc2f8\uac8c \uc0b0 \ubb3c\uac74, \ud2b9\uac00\ud488"),
    ("U04-012", 4, 22, "basically", "adv.", "\uae30\ubcf8\uc801\uc73c\ub85c, \ub300\uccb4\ub85c"),
    ("U04-013", 4, 22, "caffeine", "n.", "\uce74\ud398\uc778"),
    ("U04-014", 4, 22, "carton", "n.", "\uc885\uc774 \uc0c1\uc790, \uc74c\ub8cc \ud329"),
    ("U04-015", 4, 22, "deposit", "v.", "\uc785\uae08\ud558\ub2e4, \ub9e1\uae30\ub2e4"),
    ("U04-016", 4, 22, "forbid", "v.", "\uae08\uc9c0\ud558\ub2e4"),
    ("U04-017", 4, 22, "pickle", "v.", "\uc808\uc774\ub2e4, \ud53c\ud074\ub85c \ub9cc\ub4e4\ub2e4"),
    ("U04-018", 4, 22, "pork", "n.", "\ub3fc\uc9c0\uace0\uae30"),
    ("U04-019", 4, 22, "suburb", "n.", "\uad50\uc678, \uadfc\uad50"),
    ("U04-020", 4, 22, "whereas", "conj.", "\ubc18\uba74\uc5d0, ~\uc778 \ubc18\uba74"),

    ("U06-001", 6, 32, "asteroid", "n.", "\uc18c\ud589\uc131"),
    ("U06-002", 6, 32, "cable", "n.", "\ucf00\uc774\ube14, \uc804\uc120"),
    ("U06-003", 6, 32, "circumstance", "n.", "\uc0c1\ud669, \ud658\uacbd, \uc0ac\uc815"),
    ("U06-004", 6, 32, "crater", "n.", "\ubd84\ud654\uad6c, \uc6b4\uc11d \uad6c\ub369\uc774"),
    ("U06-005", 6, 32, "defense", "n.", "\ubc29\uc5b4, \uc218\ube44, \ubc29\uc704"),
    ("U06-006", 6, 32, "emit", "v.", "\ub0b4\ubf5c\ub2e4, \ubc29\ucd9c\ud558\ub2e4"),
    ("U06-007", 6, 32, "galaxy", "n.", "\uc740\ud558"),
    ("U06-008", 6, 32, "incident", "n.", "\uc0ac\uac74, \uc0ac\uace0"),
    ("U06-009", 6, 32, "launch", "v.", "\ubc1c\uc0ac\ud558\ub2e4, \uc2dc\uc791\ud558\ub2e4"),
    ("U06-010", 6, 32, "massive", "adj.", "\uac70\ub300\ud55c, \ub300\uaddc\ubaa8\uc758"),
    ("U06-011", 6, 34, "authority", "n.", "\uad8c\ud55c, \uad8c\uc704"),
    ("U06-012", 6, 34, "clone", "v.", "\ubcf5\uc81c\ud558\ub2e4"),
    ("U06-013", 6, 34, "comet", "n.", "\ud61c\uc131"),
    ("U06-014", 6, 34, "diagram", "n.", "\ub3c4\ud45c, \uadf8\ub9bc, \ub3c4\uc2dd"),
    ("U06-015", 6, 34, "encounter", "v.", "\ub9c8\uc8fc\uce58\ub2e4, \uacaa\ub2e4"),
    ("U06-016", 6, 34, "geology", "n.", "\uc9c0\uc9c8\ud559"),
    ("U06-017", 6, 34, "lens", "n.", "\ub80c\uc988"),
    ("U06-018", 6, 34, "originate", "v.", "\ube44\ub86f\ub418\ub2e4, \uc720\ub798\ud558\ub2e4"),
    ("U06-019", 6, 34, "spacecraft", "n.", "\uc6b0\uc8fc\uc120"),
    ("U06-020", 6, 34, "steel", "n.", "\uac15\ucca0"),

    ("U07-001", 7, 36, "Aboriginal", "adj.", "\ud638\uc8fc \uc6d0\uc8fc\ubbfc\uc758"),
    ("U07-002", 7, 36, "campfire", "n.", "\ucea0\ud504\ud30c\uc774\uc5b4, \ubaa8\ub2e5\ubd88"),
    ("U07-003", 7, 36, "chronological", "adj.", "\uc2dc\uac04 \uc21c\uc11c\uc758, \uc5f0\ub300\uc21c\uc758"),
    ("U07-004", 7, 36, "footstep", "n.", "\ubc1c\uc18c\ub9ac, \ubc1c\uc790\uad6d"),
    ("U07-005", 7, 36, "gear", "n.", "\uc7a5\ube44, \uc6a9\ud488"),
    ("U07-006", 7, 36, "inhabit", "v.", "\uc0b4\ub2e4, \uc11c\uc2dd\ud558\ub2e4"),
    ("U07-007", 7, 36, "migrate", "v.", "\uc774\ub3d9\ud558\ub2e4, \uc774\uc8fc\ud558\ub2e4"),
    ("U07-008", 7, 36, "priority", "n.", "\uc6b0\uc120\uc21c\uc704"),
    ("U07-009", 7, 36, "shrink", "v.", "\uc904\uc5b4\ub4e4\ub2e4, \uc624\uadf8\ub77c\ub4e4\ub2e4"),
    ("U07-010", 7, 36, "vast", "adj.", "\uad11\ub300\ud55c, \uac70\ub300\ud55c"),
    ("U07-011", 7, 38, "alert", "adj.", "\uae30\ubbfc\ud55c, \uc815\uc2e0\uc744 \ubc14? \ucc28\ub9b0"),
    ("U07-012", 7, 38, "canyon", "n.", "\ud611\uace1"),
    ("U07-013", 7, 38, "conquer", "v.", "\uc815\ubcf5\ud558\ub2e4, \uadf9\ubcf5\ud558\ub2e4"),
    ("U07-014", 7, 38, "controversial", "adj.", "\ub17c\ub780\uc774 \ub9ce\uc740"),
    ("U07-015", 7, 38, "dawn", "n.", "\uc0c8\ubcbd, \ub3d9\ud2c0 \ubb34\ub835"),
    ("U07-016", 7, 38, "harmony", "n.", "\uc870\ud654, \ud654\ud569"),
    ("U07-017", 7, 38, "inhabitant", "n.", "\uc8fc\ubbfc, \uc11c\uc2dd \ub3d9\ubb3c"),
    ("U07-018", 7, 38, "nevertheless", "adv.", "\uadf8\ub7fc\uc5d0\ub3c4 \ubd88\uad6c\ud558\uace0"),
    ("U07-019", 7, 38, "occupy", "v.", "\ucc28\uc9c0\ud558\ub2e4, \uc810\uc720\ud558\ub2e4"),
    ("U07-020", 7, 38, "paddle", "v.", "\ub178\ub97c \uc813\ub2e4"),

    ("U08-001", 8, 40, "hacker", "n.", "\ud574\ucee4"),
    ("U08-002", 8, 40, "harsh", "adj.", "\uac00\ud639\ud55c, \ud639\ub3c5\ud55c"),
    ("U08-003", 8, 40, "industrial", "adj.", "\uc0b0\uc5c5\uc758, \uacf5\uc5c5\uc758"),
    ("U08-004", 8, 40, "lottery", "n.", "\ubcf5\uad8c, \ucd94\ucca8"),
    ("U08-005", 8, 40, "millionaire", "n.", "\ubc31\ub9cc\uc7a5\uc790, \ubd80\uc790"),
    ("U08-006", 8, 40, "obtain", "v.", "\uc5bb\ub2e4, \ud68d\ub4dd\ud558\ub2e4"),
    ("U08-007", 8, 40, "resort", "n.", "\ud734\uc591\uc9c0, \ub9ac\uc870\ud2b8"),
    ("U08-008", 8, 40, "skyscraper", "n.", "\uace0\uce35 \uac74\ubb3c, \ub9c8\ucc9c\ub8e8"),
    ("U08-009", 8, 40, "tempt", "v.", "\uc720\ud639\ud558\ub2e4, \ud558\uace0 \uc2f6\uac8c \ub9cc\ub4e4\ub2e4"),
    ("U08-010", 8, 40, "virtual", "adj.", "\uac00\uc0c1\uc758, \ucef4\ud4e8\ud130\uc0c1\uc758"),
    ("U08-011", 8, 42, "inspector", "n.", "\uac80\uc0ac\uad00, \uc870\uc0ac\uad00"),
    ("U08-012", 8, 42, "invest", "v.", "\ud22c\uc790\ud558\ub2e4"),
    ("U08-013", 8, 42, "luxury", "adj.", "\uace0\uae09\uc758, \uc0ac\uce58\uc2a4\ub7ec\uc6b4"),
    ("U08-014", 8, 42, "motorcycle", "n.", "\uc624\ud1a0\ubc14\uc774"),
    ("U08-015", 8, 42, "orphan", "n.", "\uace0\uc544"),
    ("U08-016", 8, 42, "slope", "n.", "\uacbd\uc0ac\uba74, \ube44\ud0c8"),
    ("U08-017", 8, 42, "snowboard", "v.", "\uc2a4\ub178\ubcf4\ub4dc\ub97c \ud0c0\ub2e4"),
    ("U08-018", 8, 42, "snowman", "n.", "\ub208\uc0ac\ub78c"),
    ("U08-019", 8, 42, "terrific", "adj.", "\uc544\uc8fc \uba4b\uc9c4, \ud6cc\ub96d\ud55c"),
    ("U08-020", 8, 42, "tire", "n.", "\ud0c0\uc774\uc5b4"),

    ("U10-001", 10, 48, "aerobic", "adj.", "\uc720\uc0b0\uc18c\uc758, \uc0b0\uc18c\ub97c \ud544\uc694\ub85c \ud558\ub294"),
    ("U10-002", 10, 48, "devoted", "adj.", "\ud5cc\uc2e0\uc801\uc778, \ucda9\uc2e4\ud55c"),
    ("U10-003", 10, 48, "fitness", "n.", "\uccb4\ub825, \uac74\uac15 \uc0c1\ud0dc"),
    ("U10-004", 10, 48, "glance", "v.", "\ud790\ub057 \ubcf4\ub2e4"),
    ("U10-005", 10, 48, "gymnastics", "n.", "\uccb4\uc870"),
    ("U10-006", 10, 48, "hesitate", "v.", "\ub9dd\uc124\uc774\ub2e4, \uc8fc\uc800\ud558\ub2e4"),
    ("U10-007", 10, 48, "melody", "n.", "\uba5c\ub85c\ub514, \uc120\uc728"),
    ("U10-008", 10, 48, "register", "v.", "\ub4f1\ub85d\ud558\ub2e4"),
    ("U10-009", 10, 48, "sleeve", "n.", "\uc18c\ub9e4"),
    ("U10-010", 10, 48, "specialize", "v.", "\uc804\ubb38\uc73c\ub85c \ud558\ub2e4, \uc804\uacf5\ud558\ub2e4"),
    ("U10-011", 10, 50, "occasionally", "adv.", "\uac00\ub054, \ub54c\ub54c\ub85c"),
    ("U10-012", 10, 50, "pure", "adj.", "\uc21c\uc218\ud55c, \uc11e\uc774\uc9c0 \uc54a\uc740"),
    ("U10-013", 10, 50, "raw", "adj.", "\ub0a0\uac83\uc758, \uc775\ud788\uc9c0 \uc54a\uc740"),
    ("U10-014", 10, 50, "reject", "v.", "\uac70\uc808\ud558\ub2e4, \ubc1b\uc544\ub4e4\uc774\uc9c0 \uc54a\ub2e4"),
    ("U10-015", 10, 50, "rumor", "n.", "\uc18c\ubb38"),
    ("U10-016", 10, 50, "sunrise", "n.", "\ud574\ub3cb\uc774, \uc77c\ucd9c"),
    ("U10-017", 10, 50, "tobacco", "n.", "\ub2f4\ubc30, \ub2f4\ubc43\uc78e"),
    ("U10-018", 10, 50, "vegetarian", "adj.", "\ucc44\uc2dd\uc8fc\uc758\uc758, \ucc44\uc2dd\uc758"),
    ("U10-019", 10, 50, "workout", "n.", "\uc6b4\ub3d9, \uc2e0\uccb4 \ud6c8\ub828"),
    ("U10-020", 10, 50, "zipper", "n.", "\uc9c0\ud37c"),
]

words = []
for word_id, unit, book_page, word, pos, meaning_ko in raw_words:
    words.append({
        "word_id": word_id,
        "unit": unit,
        "book_page": book_page,
        "word": word,
        "pos": pos,
        "meaning_ko": meaning_ko,
        "source_file": SOURCE_FILE,
        "mastery": {
            "meaning": 0,
            "spelling": 0,
            "sentence": 0,
            "boss": 0
        }
    })

errors = []

if len(words) != 100:
    errors.append(f"total word count expected 100, actual {len(words)}")

expected_unit_counts = {4: 20, 6: 20, 7: 20, 8: 20, 10: 20}
unit_counts = Counter(w["unit"] for w in words)
for unit, expected in expected_unit_counts.items():
    actual = unit_counts.get(unit, 0)
    if actual != expected:
        errors.append(f"Unit {unit} expected {expected}, actual {actual}")

for field in ["word_id", "word"]:
    dupes = [k for k, v in Counter(w[field] for w in words).items() if v > 1]
    if dupes:
        errors.append(f"duplicate {field}: {', '.join(dupes)}")

for field in ["word", "meaning_ko"]:
    blanks = [w["word_id"] for w in words if not str(w[field]).strip()]
    if blanks:
        errors.append(f"blank {field}: {', '.join(blanks)}")

if errors:
    print("=== WORD MASTER VALIDATION FAILED ===")
    for e in errors:
        print("- " + e)
    raise SystemExit(1)

payload = {
    "schema_version": "englishmon.word_master.v0.1",
    "title": "EnglishMon Word Master v0.1",
    "source": {
        "file": SOURCE_FILE,
        "original_file_note": "Uploaded source was 2_1 Korean final English PDF. ASCII filename is used to avoid Windows encoding issues.",
        "units": [4, 6, 7, 8, 10],
        "total_words": 100
    },
    "validation": {
        "expected_total_words": 100,
        "expected_unit_counts": {
            "unit_4": 20,
            "unit_6": 20,
            "unit_7": 20,
            "unit_8": 20,
            "unit_10": 20
        }
    },
    "words": words
}

json_path = DATA / "word_master_v0_1.json"
json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

audit_lines = []
audit_lines.append("# EnglishMon Word Master Audit v0.1")
audit_lines.append("")
audit_lines.append("## Validation")
audit_lines.append("")
audit_lines.append(f"- Total words: {len(words)}")
for unit in [4, 6, 7, 8, 10]:
    audit_lines.append(f"- Unit {unit}: {unit_counts[unit]}")
audit_lines.append("- Duplicate word_id: 0")
audit_lines.append("- Duplicate word: 0")
audit_lines.append("- Blank word: 0")
audit_lines.append("- Blank meaning_ko: 0")
audit_lines.append("")
audit_lines.append("## Word List")
audit_lines.append("")

for unit in [4, 6, 7, 8, 10]:
    audit_lines.append(f"### Unit {unit}")
    audit_lines.append("")
    for w in [x for x in words if x["unit"] == unit]:
        audit_lines.append(f"- {w['word_id']} / {w['word']} / {w['meaning_ko']}")
    audit_lines.append("")

audit_path = DOCS / "word_master_audit_v0_1.md"
audit_path.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")

print("=== WORD MASTER CREATED ===")
print(f"JSON : {json_path}")
print(f"AUDIT: {audit_path}")
print(f"TOTAL: {len(words)}")
for unit in [4, 6, 7, 8, 10]:
    print(f"Unit {unit}: {unit_counts[unit]}")
