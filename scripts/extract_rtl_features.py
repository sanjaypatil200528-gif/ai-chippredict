import re
import csv
from pathlib import Path

RTL_DIR = Path("rtl")
OUT = Path("dataset/rtl_features.csv")

# Longest tokens first to avoid counting parts of multi-character operators.
OPERATORS = {
    "multiply_count": r"(?<!\*)\*(?!\*)",
    "plus_count": r"(?<!\+)\+(?!\+)",
    "minus_count": r"(?<!-)-(?!-)",
    "and_count": r"(?<!&)&(?!&)",
    "or_count": r"(?<!\|)\|(?!\|)",
    "xor_count": r"\^",
    "relational_count": r"<=|>=|<|>",
    "equality_count": r"===|!==|==|!=",
    "shift_count": r">>>|<<|>>",
    "ternary_count": r"\?",
}

def extract_features(path):
    text = path.read_text()
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//.*", "", text)

    # Remove Verilog string literals before counting operators.
    text = re.sub(r'"(?:\\.|[^"\\])*"', '""', text)

    def count_declared_bits(keyword):
        total = 0
        pattern = (
            rf"\b{keyword}\b\s+"
            rf"(?:(?:wire|reg|logic)\s+)?"
            rf"(?:\[(\d+)\s*:\s*(\d+)\]\s*)?"
            rf"[A-Za-z_]\w*"
        )
        for match in re.finditer(pattern, text):
            hi, lo = match.group(1), match.group(2)
            total += abs(int(hi) - int(lo)) + 1 if hi is not None else 1
        return total

    result = {
        "circuit": path.stem,
        "source_lines": len(text.splitlines()),
        "input_bits": count_declared_bits("input"),
        "output_bits": count_declared_bits("output"),
        "wire_bits": count_declared_bits("wire"),
    }

    for name, pattern in OPERATORS.items():
        result[name] = len(re.findall(pattern, text))

    return result

files = sorted(RTL_DIR.glob("*.v"))
if not files:
    raise SystemExit("No Verilog files found in rtl/")

rows = [extract_features(path) for path in files]
OUT.parent.mkdir(parents=True, exist_ok=True)

with OUT.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Extracted RTL features from {len(rows)} circuits.")
print(f"Saved to: {OUT}")
for row in rows:
    print(
        f"{row['circuit']}: inputs={row['input_bits']}, "
        f"outputs={row['output_bits']}, "
        f"relational={row['relational_count']}, "
        f"equality={row['equality_count']}, "
        f"multiplication={row['multiply_count']}"
    )
