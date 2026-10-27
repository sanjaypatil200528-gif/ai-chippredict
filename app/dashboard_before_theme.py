import streamlit as st
import pandas as pd
import joblib
import time
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score
)

MODEL_PATH = Path("models/timing_violation_rf.joblib")
FEATURES_PATH = Path("dataset/rtl_features.csv")
DATASET_PATH = Path("dataset/timing_ml_dataset.csv")
STA_PATH = Path("results/timing_sweep/all_circuits_timing_sweep.csv")
RESULTS_DIR = Path("results/model_comparison")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="AI ChipPredict | Model Benchmark",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ AI ChipPredict")
st.subheader("AI-Based Timing Violation Prediction in RTL-to-GDS Flow")
st.caption("Six-model benchmark • Performance analytics • OpenSTA validation")

if not all(p.exists() for p in [
    MODEL_PATH, FEATURES_PATH, DATASET_PATH, STA_PATH
]):
    st.error("A required model or dataset file is missing.")
    st.stop()

saved = joblib.load(MODEL_PATH)
feature_cols = saved["feature_cols"]

features = pd.read_csv(FEATURES_PATH)
dataset = pd.read_csv(DATASET_PATH)
sta = pd.read_csv(STA_PATH)

models = {
    "Random Forest": RandomForestClassifier(
        n_estimators=200, max_depth=5,
        class_weight="balanced", random_state=42
    ),
    "Decision Tree": DecisionTreeClassifier(
        max_depth=5, class_weight="balanced", random_state=42
    ),
    "Logistic Regression": make_pipeline(
        StandardScaler(),
        LogisticRegression(
            class_weight="balanced", max_iter=2000, random_state=42
        )
    ),
    "SVM": make_pipeline(
        StandardScaler(),
        SVC(probability=True, class_weight="balanced", random_state=42)
    ),
    "KNN": make_pipeline(
        StandardScaler(),
        KNeighborsClassifier(n_neighbors=5)
    ),
    "Gradient Boosting": GradientBoostingClassifier(random_state=42)
}

recommended_for = {
    "Random Forest": "Strong general-purpose baseline; nonlinear patterns",
    "Decision Tree": "Simple, interpretable decision rules",
    "Logistic Regression": "Fast baseline; approximately linear patterns",
    "SVM": "Small datasets with complex decision boundaries",
    "KNN": "Similarity-based baseline on scaled features",
    "Gradient Boosting": "Learning complex patterns from sequential trees"
}

# Keep a fixed, shared test split for a fair preliminary comparison.
X = dataset[feature_cols].copy()
y = dataset["timing_violation"].astype(int)

if y.nunique() != 2 or y.value_counts().min() < 2:
    st.error("The dataset needs examples from both timing classes.")
    st.stop()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

@st.cache_data
def benchmark_models(X_train, X_test, y_train, y_test):
    results = []

    for name, estimator in models.items():
        model = estimator

        start = time.perf_counter()
        model.fit(X_train, y_train)
        training_seconds = time.perf_counter() - start

        # Average per-sample inference time over repeated test-batch predictions.
        repeats = 100
        start = time.perf_counter()
        for _ in range(repeats):
            predictions = model.predict(X_test)
        inference_ms_per_sample = (
            (time.perf_counter() - start)
            / (repeats * len(X_test)) * 1000
        )

        probabilities = model.predict_proba(X_test)[:, 
            list(model.classes_).index(1)
        ]
        predictions = model.predict(X_test)

        results.append({
            "Model": name,
            "Accuracy": accuracy_score(y_test, predictions),
            "Precision": precision_score(
                y_test, predictions, zero_division=0
            ),
            "Recall": recall_score(
                y_test, predictions, zero_division=0
            ),
            "F1-Score": f1_score(
                y_test, predictions, zero_division=0
            ),
            "AUC-ROC": roc_auc_score(y_test, probabilities),
            "Training Time (s)": training_seconds,
            "Inference Time (ms/sample)": inference_ms_per_sample,
            "Recommended For": recommended_for[name]
        })

    return pd.DataFrame(results)

with st.spinner("Training and evaluating all six models..."):
    summary = benchmark_models(
        X_train, X_test, y_train, y_test
    )

# Rank by F1 first, then violation recall, then AUC.
summary = summary.sort_values(
    ["F1-Score", "Recall", "AUC-ROC"],
    ascending=False
).reset_index(drop=True)

best_model_name = summary.iloc[0]["Model"]

st.success(
    f"Current best model by F1-Score, then Recall and AUC-ROC: "
    f"{best_model_name}"
)

st.caption(
    "Metrics use one shared random stratified holdout split. "
    "Because multiple timing scenarios come from the same six circuits, "
    "these scores do not establish performance on unseen circuit designs."
)

# ---------------- PERFORMANCE SUMMARY ----------------
st.header("1. Performance Results Summary")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Models Evaluated", len(summary))
m2.metric("Test Samples", len(X_test))
m3.metric("Top Model", best_model_name)
m4.metric("Dataset Scenarios", len(dataset))

display_summary = summary.copy()
metric_cols = [
    "Accuracy", "Precision", "Recall", "F1-Score", "AUC-ROC"
]
display_summary[metric_cols] = (
    display_summary[metric_cols] * 100
).round(2)
display_summary["Training Time (s)"] = display_summary[
    "Training Time (s)"
].round(6)
display_summary["Inference Time (ms/sample)"] = display_summary[
    "Inference Time (ms/sample)"
].round(6)

st.caption("Classification metrics are displayed as percentages.")
st.dataframe(display_summary, hide_index=True, width="stretch")

# Export the full-precision benchmark table.
summary_csv = summary.to_csv(index=False)
(RESULTS_DIR / "performance_summary.csv").write_text(summary_csv)

st.download_button(
    "Download Complete Performance Summary CSV",
    data=summary_csv,
    file_name="chippredict_performance_summary.csv",
    mime="text/csv",
    width="stretch"
)

# ---------------- GRAPHS ----------------
st.header("2. Graphical Model Comparison")

st.subheader("Classification Metrics")
chart_metrics = summary.set_index("Model")[
    ["Accuracy", "Precision", "Recall", "F1-Score", "AUC-ROC"]
]
st.bar_chart(chart_metrics, y_label="Score (0 to 1)")

st.subheader("Training Time")
training_chart = summary.set_index("Model")[["Training Time (s)"]]
st.bar_chart(training_chart, y_label="Seconds")

st.subheader("Inference Time")
inference_chart = summary.set_index("Model")[[
    "Inference Time (ms/sample)"
]]
st.bar_chart(inference_chart, y_label="Milliseconds per sample")

st.subheader("Best Model by Evaluation Ranking")
st.write(
    f"**{best_model_name}** ranks first on this test split under the "
    "F1-Score → Recall → AUC-ROC tie-break rule. This ranking may change "
    "with more circuits or a different validation strategy."
)

st.subheader("Recommendations by Model")
st.dataframe(
    summary[["Model", "Recommended For"]],
    hide_index=True,
    width="stretch"
)

# ---------------- LIVE PREDICTION ----------------
st.divider()
st.header("3. Live Timing Prediction")

left, right = st.columns(2)

with left:
    model_name = st.selectbox(
        "Choose model for prediction",
        list(models.keys()),
        index=list(models.keys()).index(best_model_name)
    )

    circuit = st.selectbox(
        "Select RTL circuit",
        features["circuit"].tolist()
    )

    period = st.number_input(
        "Clock period (ns)", min_value=0.1,
        max_value=1000.0, value=5.0, step=0.5
    )
    input_delay = st.number_input(
        "Input delay (ns)", min_value=0.0,
        max_value=1000.0, value=1.0, step=0.5
    )
    output_delay = st.number_input(
        "Output delay (ns)", min_value=0.0,
        max_value=1000.0, value=1.0, step=0.5
    )
    predict = st.button(
        "Predict and Compare with OpenSTA",
        type="primary",
        width="stretch"
    )

with right:
    st.subheader("Prediction Output")

    if predict:
        selected_model = models[model_name]
        # Refit the selected model on all currently available labeled data.
        selected_model.fit(X, y)

        row = features.loc[
            features["circuit"] == circuit
        ].iloc[[0]].copy()
        row["clock_period_ns"] = period
        row["input_delay_ns"] = input_delay
        row["output_delay_ns"] = output_delay

        prediction = int(selected_model.predict(row[feature_cols])[0])
        probabilities = selected_model.predict_proba(row[feature_cols])[0]
        classes = list(selected_model.classes_)
        violation_probability = float(probabilities[classes.index(1)])

        if prediction:
            st.error("⚠️ AI PREDICTION: TIMING VIOLATION")
        else:
            st.success("✅ AI PREDICTION: TIMING PASS")

        st.metric(
            "Estimated Violation Probability",
            f"{violation_probability:.1%}"
        )

        actual = sta[
            (sta["circuit"] == circuit)
            & ((sta["clock_period_ns"] - period).abs() < 1e-8)
            & ((sta["input_delay_ns"] - input_delay).abs() < 1e-8)
            & ((sta["output_delay_ns"] - output_delay).abs() < 1e-8)
        ]

        if not actual.empty:
            actual_row = actual.iloc[0]
            slack = float(actual_row["setup_slack_ns"])
            actual_violation = int(actual_row["timing_violation"])
            actual_result = (
                "TIMING VIOLATION" if actual_violation else "TIMING PASS"
            )
            matches = prediction == actual_violation

            st.metric("OpenSTA Setup Slack", f"{slack:.2f} ns")
            st.write("**OpenSTA result:**", actual_result)

            if matches:
                st.success("AI prediction matches the recorded OpenSTA result.")
            else:
                st.warning("AI prediction differs from the recorded OpenSTA result.")
        else:
            slack = None
            actual_result = "No exact matching measurement"
            matches = None
            st.info("No exact matching OpenSTA scenario is recorded.")

        report = pd.DataFrame([{
            "Model": model_name,
            "Circuit": circuit,
            "Clock Period (ns)": period,
            "Input Delay (ns)": input_delay,
            "Output Delay (ns)": output_delay,
            "AI Prediction": (
                "TIMING VIOLATION" if prediction else "TIMING PASS"
            ),
            "Violation Probability (%)": round(
                violation_probability * 100, 2
            ),
            "OpenSTA Slack (ns)": slack,
            "OpenSTA Result": actual_result,
            "AI Matches OpenSTA": matches
        }])

        st.dataframe(report, hide_index=True, width="stretch")
        st.download_button(
            "Download Prediction and OpenSTA CSV",
            data=report.to_csv(index=False),
            file_name="chippredict_prediction_comparison.csv",
            mime="text/csv",
            width="stretch"
        )
    else:
        st.info("Choose the model and circuit, then click Predict and Compare.")

st.divider()
st.header("4. Dataset and Validation")
d1, d2, d3 = st.columns(3)
d1.metric("RTL Circuit Designs", features["circuit"].nunique())
d2.metric("Measured OpenSTA Scenarios", len(sta))
d3.metric("Training / Test Rows", f"{len(X_train)} / {len(X_test)}")

st.caption(
    "Important: the current random scenario split may place scenarios from "
    "the same circuit in both train and test sets. The benchmark is preliminary; "
    "use circuit-grouped validation and additional designs to estimate "
    "generalization to unseen circuits. AUC-ROC is calculated from model "
    "probabilities. Inference time is an average per sample over repeated "
    "predictions on the test batch and depends on the machine."
)
