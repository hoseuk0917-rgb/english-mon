from pathlib import Path
import json
import re
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "word_master_v0_1.json"
DOCS = ROOT / "docs"

payload = json.loads(MASTER.read_text(encoding="utf-8"))
words = payload.get("words", [])

errors = []

expected_units = {4: 20, 6: 20, 7: 20, 8: 20, 10: 20}
expected_total = 100

if len(words) != expected_total:
    errors.append(f"TOTAL expected {expected_total}, actual {len(words)}")

unit_counts = Counter(w.get("unit") for w in words)
for unit, expected in expected_units.items():
    actual = unit_counts.get(unit, 0)
    if actual != expected:
        errors.append(f"Unit {unit} expected {expected}, actual {actual}")

for field in ["word_id", "word"]:
    dupes = [k for k, v in Counter(w.get(field) for w in words).items() if v > 1]
    if dupes:
        errors.append(f"duplicate {field}: {dupes}")

for w in words:
    wid = w.get("word_id", "")
    unit = w.get("unit")

    if not re.match(r"^U(04|06|07|08|10)-\d{3}$", wid):
        errors.append(f"bad word_id format: {wid}")

    for field in ["word", "meaning_ko", "pos"]:
        if not str(w.get(field, "")).strip():
            errors.append(f"blank {field}: {wid}")

    if unit not in expected_units:
        errors.append(f"unexpected unit: {wid} / {unit}")

if errors:
    print("=== VALIDATION FAILED ===")
    for e in errors:
        print("- " + e)
    raise SystemExit(1)

lock = []
lock.append("# EnglishMon Word Master Lock v0.1")
lock.append("")
lock.append("## Locked Files")
lock.append("")
lock.append("- data/word_master_v0_1.json")
lock.append("- docs/word_master_audit_v0_1.md")
lock.append("")
lock.append("## Validation Result")
lock.append("")
lock.append(f"- Total words: {len(words)}")
for unit in [4, 6, 7, 8, 10]:
    lock.append(f"- Unit {unit}: {unit_counts[unit]}")
lock.append("- Duplicate word_id: 0")
lock.append("- Duplicate word: 0")
lock.append("- Blank word: 0")
lock.append("- Blank meaning_ko: 0")
lock.append("- word_id format: OK")
lock.append("")
lock.append("## Rule")
lock.append("")
lock.append("Do not edit the word master manually without running validate_word_master_v0_1.py.")

out = DOCS / "word_master_lock_v0_1.md"
out.write_text("\n".join(lock) + "\n", encoding="utf-8")

print("=== WORD MASTER LOCKED ===")
print(f"MASTER: {MASTER}")
print(f"LOCK  : {out}")
print(f"TOTAL : {len(words)}")
for unit in [4, 6, 7, 8, 10]:
    print(f"Unit {unit}: {unit_counts[unit]}")
