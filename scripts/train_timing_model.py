from pathlib import Path
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

DATA = Path("dataset/timing_ml_dataset.csv")
MODEL_DIR = Path("models")
RESULT_DIR = Path("results")

MODEL_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATA)

# Inputs: RTL structure and timing constraints only.
# Exclude circuit name and measured timing results to prevent leakage.
feature_cols = [
    "clock_period_ns",
    "input_delay_ns",
    "output_delay_ns",
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

X = df[feature_cols]
y = df["timing_violation"].astype(int)

# Stratified split keeps both labels represented in train and test.
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=5,
    class_weight="balanced",
    random_state=42
)

model.fit(X_train, y_train)
pred = model.predict(X_test)

print("\n=== AI ChipPredict: Random Forest Baseline ===")
print("Dataset rows:", len(df))
print("Unique circuits:", df["circuit"].nunique())
print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))
print("\nAccuracy :", round(accuracy_score(y_test, pred), 3))
print("Precision:", round(precision_score(y_test, pred, zero_division=0), 3))
print("Recall   :", round(recall_score(y_test, pred, zero_division=0), 3))
print("F1 score :", round(f1_score(y_test, pred, zero_division=0), 3))
print("\nConfusion matrix [ [TN, FP], [FN, TP] ]:")
print(confusion_matrix(y_test, pred, labels=[0, 1]))
print("\nClassification report:")
print(classification_report(
    y_test, pred,
    labels=[0, 1],
    target_names=["Pass", "Violation"],
    zero_division=0
))

joblib.dump(
    {"model": model, "feature_cols": feature_cols},
    MODEL_DIR / "timing_violation_rf.joblib"
)

report = X_test.copy()
report["actual_violation"] = y_test.to_numpy()
report["predicted_violation"] = pred
report["correct"] = (
    report["actual_violation"] == report["predicted_violation"]
)
report.to_csv(RESULT_DIR / "timing_model_test_predictions.csv", index=False)

print("\nSaved model: models/timing_violation_rf.joblib")
print("Saved test predictions: results/timing_model_test_predictions.csv")
print("\nNote: This is an initial prototype. The test set includes")
print("scenarios from circuits also present in training, so the")
print("scores do not prove generalization to unseen circuit designs.")
