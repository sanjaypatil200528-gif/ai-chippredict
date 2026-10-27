import pandas as pd
import joblib
from pathlib import Path

model_path = Path("models/timing_violation_rf.joblib")
features_path = Path("dataset/rtl_features.csv")

if not model_path.exists():
    raise FileNotFoundError("Train the model first.")

saved = joblib.load(model_path)
model = saved["model"]
feature_cols = saved["feature_cols"]
features = pd.read_csv(features_path)

print("\n=== AI ChipPredict: Timing Predictor ===")
print("\nAvailable circuits:")

for i, name in enumerate(features["circuit"], start=1):
    print(f"{i}. {name}")

choice = int(input("\nChoose circuit number: "))
if choice < 1 or choice > len(features):
    raise ValueError("Invalid circuit number.")

circuit_features = features.iloc[[choice - 1]].copy()

period = float(input("Enter clock period in ns (example: 5): "))
input_delay = float(input("Enter input delay in ns (example: 1): "))
output_delay = float(input("Enter output delay in ns (example: 1): "))

if period <= 0 or input_delay < 0 or output_delay < 0:
    raise ValueError("Period must be positive; delays cannot be negative.")

circuit_features["clock_period_ns"] = period
circuit_features["input_delay_ns"] = input_delay
circuit_features["output_delay_ns"] = output_delay

X = circuit_features[feature_cols]
prediction = int(model.predict(X)[0])
probabilities = model.predict_proba(X)[0]
violation_probability = probabilities[list(model.classes_).index(1)]

print("\n--- Prediction ---")
print("Circuit:", circuit_features.iloc[0]["circuit"])
print(f"Clock period: {period:.2f} ns")
print("Predicted result:",
      "TIMING VIOLATION" if prediction else "TIMING PASS")
print(f"Model-estimated violation probability: {violation_probability:.1%}")
