import csv
import numpy as np

DATASET = "dataset/chippredict_dataset.csv"

# Only RTL-derived features: do not use post-synthesis cell count.
FEATURES = [
    "source_lines",
    "input_bits",
    "output_bits",
    "wire_bits",
    "multiply_count",
    "plus_count",
    "minus_count",
    "and_count",
    "or_count",
    "xor_count",
    "relational_count",
    "equality_count",
    "shift_count",
    "ternary_count",
]

TARGET = "cell_area"
ALPHA = 1.0  # Ridge regularization strength

with open(DATASET, newline="") as f:
    rows = list(csv.DictReader(f))

if len(rows) < 3:
    raise SystemExit("Need at least 3 circuit samples.")

X = np.array(
    [[float(row[name]) for name in FEATURES] for row in rows],
    dtype=float,
)
y = np.array([float(row[TARGET]) for row in rows])

def fit_ridge(X_train, y_train, X_test, alpha=ALPHA):
    # Standardize features using training data only.
    mean = X_train.mean(axis=0)
    std = X_train.std(axis=0)
    std[std == 0] = 1.0

    A = (X_train - mean) / std
    B = (X_test - mean) / std

    # Center target so the intercept is not regularized.
    y_mean = y_train.mean()
    centered_y = y_train - y_mean

    weights = np.linalg.solve(
        A.T @ A + alpha * np.eye(A.shape[1]),
        A.T @ centered_y,
    )
    return B @ weights + y_mean

# Leave-one-out cross-validation: test each circuit separately.
predictions = []

for i in range(len(rows)):
    train_idx = np.array([j for j in range(len(rows)) if j != i])
    prediction = fit_ridge(
        X[train_idx],
        y[train_idx],
        X[i:i + 1],
    )[0]
    predictions.append(prediction)

predictions = np.array(predictions)
errors = predictions - y

mae = np.mean(np.abs(errors))
rmse = np.sqrt(np.mean(errors ** 2))

print("AI ChipPredict - RTL Area Prediction Baseline")
print("=" * 52)
print("Dataset samples:", len(rows))
print("RTL features:", ", ".join(FEATURES))
print("Evaluation: leave-one-out cross-validation")
print("Model: Ridge regression")
print()
print(f"Cross-validation MAE:  {mae:.2f} area units")
print(f"Cross-validation RMSE: {rmse:.2f} area units")
print()
print(f"{'Circuit':25s} {'Actual':>12s} {'Predicted':>12s} {'Abs error':>12s}")

for row, actual, predicted, error in zip(
    rows, y, predictions, np.abs(errors)
):
    print(
        f"{row['circuit']:25s} "
        f"{actual:12.2f} "
        f"{predicted:12.2f} "
        f"{error:12.2f}"
    )

print()
print("Note: Only six circuits are available.")
print("Treat these results as an experimental baseline, not validated accuracy.")
