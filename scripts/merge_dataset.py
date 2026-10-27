import csv
from pathlib import Path

rtl_path = Path("dataset/rtl_features.csv")
measured_path = Path("dataset/measured_results.csv")
output_path = Path("dataset/chippredict_dataset.csv")

with rtl_path.open(newline="") as f:
    rtl_rows = list(csv.DictReader(f))

with measured_path.open(newline="") as f:
    measured_rows = list(csv.DictReader(f))

measured_by_circuit = {
    row["circuit"]: row for row in measured_rows
}

merged = []
missing = []

for rtl in rtl_rows:
    circuit = rtl["circuit"]

    if circuit not in measured_by_circuit:
        missing.append(circuit)
        continue

    row = dict(rtl)
    row.update(measured_by_circuit[circuit])
    merged.append(row)

if not merged:
    raise SystemExit("No matching circuits found. Check the CSV circuit names.")

output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=merged[0].keys())
    writer.writeheader()
    writer.writerows(merged)

print(f"Merged circuits: {len(merged)}")
print(f"Saved dataset: {output_path}")

if missing:
    print("Missing measured results:", ", ".join(missing))

print("\nCircuit | RTL features | Area | Estimated cell delay | Violation")
for row in merged:
    print(
        f"{row['circuit']} | "
        f"{row['source_lines']} source lines | "
        f"{row['cell_area']} | "
        f"{row['estimated_cell_path_delay_ns']} ns | "
        f"{row['timing_violation']}"
    )
