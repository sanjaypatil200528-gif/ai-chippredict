import csv
from pathlib import Path

path = Path("dataset/measured_results.csv")

with path.open(newline="") as f:
    rows = list(csv.DictReader(f))

print("Dataset:", path)
print("Number of circuits:", len(rows))
print("Columns:", ", ".join(rows[0].keys()))

areas = [float(r["cell_area"]) for r in rows]
delays = [float(r["estimated_cell_path_delay_ns"]) for r in rows]
labels = [int(r["timing_violation"]) for r in rows]

print(f"\nAverage cell area: {sum(areas) / len(areas):.4f}")
print(f"Minimum cell area: {min(areas):.4f}")
print(f"Maximum cell area: {max(areas):.4f}")
print(f"Average estimated cell-path delay: {sum(delays) / len(delays):.4f} ns")
print("Timing violation examples:", sum(labels))
print("Timing passing examples:", len(labels) - sum(labels))

if len(set(labels)) < 2:
    print("\nWARNING: Timing classifier cannot learn both classes yet.")
