import csv
import numpy as np
from pathlib import Path

DATASET = Path("dataset/measured_results.csv")

with DATASET.open(newline="") as f:
    rows = list(csv.DictReader(f))

if len(rows) < 3:
    raise SystemExit("Need at least 3 circuit samples.")

# Features available before physical implementation:
# mapped cell count is used here only as a baseline feature.
# For a genuine early-RTL predictor, replace it with RTL-derived features.
X = np.array(
    [[float(row["cell_count"])] for row in rows],
    dtype=float
)
y = np.array(
    [float(row["cell_area"]) for row in rows],
    dtype=float
)

# Fit a simple linear regression model using NumPy.
X_design = np.column_stack([np.ones(len(X)), X])
coefficients, *_ = np.linalg.lstsq(X_design, y, rcond=None)

predictions = X_design @ coefficients
mae = np.mean(np.abs(y - predictions))
rmse = np.sqrt(np.mean((y - predictions) ** 2))

print("AI ChipPredict: Area Prediction Baseline")
print("----------------------------------------")
print(f"Training samples: {len(rows)}")
print(f"Intercept: {coefficients[0]:.4f}")
print(f"Area per cell: {coefficients[1]:.4f}")
print(f"Training MAE: {mae:.4f} area units")
print(f"Training RMSE: {rmse:.4f} area units")
print()
print("Circuit                  Actual area    Predicted area")
for row, actual, predicted in zip(rows, y, predictions):
    print(
        f"{row['circuit']:<24} "
        f"{actual:>12.4f} "
        f"{predicted:>16.4f}"
    )

print()
print("WARNING: These are training-set metrics, not test-set accuracy.")
print("Cell count is a synthesis-stage feature, not a pure RTL-only feature.")
