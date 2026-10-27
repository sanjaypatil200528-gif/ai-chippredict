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


# CHIPPREDICT_PRO_THEME
st.markdown("""
<style>
/* Main application canvas */
.stApp {
    background:
        radial-gradient(ellipse at 8% 0%, rgba(14,165,233,.12), transparent 35%),
        radial-gradient(ellipse at 95% 15%, rgba(99,102,241,.10), transparent 32%),
        #0b1120;
    color: #e5edf8;
}
[data-testid="stHeader"] {
    background: rgba(11,17,32,.86);
}
[data-testid="stMainBlockContainer"] {
    max-width: 1500px;
    padding-top: 2.1rem;
    padding-bottom: 3rem;
}

/* Typography */
h1 {
    color: #f4f8ff !important;
    font-weight: 800 !important;
    letter-spacing: -1.2px;
}
h2, h3 {
    color: #dceafe !important;
    font-weight: 700 !important;
    letter-spacing: -.35px;
}
p, label, .stMarkdown, [data-testid="stCaptionContainer"] {
    color: #aabbd2;
}
hr {
    border-color: #26364d !important;
    margin: 1.8rem 0 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101b30, #0b1120);
    border-right: 1px solid #23344d;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #15233a, #111b2d);
    border: 1px solid #2b405e;
    border-radius: 15px;
    padding: 18px 20px;
    box-shadow: 0 8px 24px rgba(0,0,0,.15);
}
[data-testid="stMetricLabel"] {
    color: #9db2ce !important;
    font-size: .83rem !important;
}
[data-testid="stMetricValue"] {
    color: #f1f7ff !important;
    font-weight: 750 !important;
}
[data-testid="stMetricDelta"] {
    color: #42d9c8 !important;
}

/* Input controls */
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div {
    background: #111c30 !important;
    border: 1px solid #344966 !important;
    border-radius: 10px !important;
    color: #eff6ff !important;
}
[data-baseweb="select"] * {
    color: #eff6ff !important;
}
input {
    color: #eff6ff !important;
}
[data-testid="stNumberInput"] button {
    color: #c4d8f5 !important;
    background: #1b2a42 !important;
    border-color: #344966 !important;
}
[data-testid="stWidgetLabel"] p {
    color: #c6d5e9 !important;
    font-weight: 600;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button {
    border: 1px solid #3689f5;
    border-radius: 10px;
    min-height: 43px;
    font-weight: 700;
    color: white;
    background: linear-gradient(105deg, #2563eb, #0891b2);
    box-shadow: 0 5px 18px rgba(37,99,235,.18);
    transition: all .18s ease;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: #67e8f9;
    color: white;
    filter: brightness(1.12);
    transform: translateY(-1px);
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #9fb4cf !important;
    font-weight: 650 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #67e8f9 !important;
}
[data-baseweb="tab-highlight"] {
    background-color: #22d3ee !important;
}

/* Data tables */
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    border: 1px solid #293e5b;
    border-radius: 12px;
    overflow: hidden;
}
[data-testid="stDataFrame"] * {
    border-color: #293e5b !important;
}

/* Charts and progress */
[data-testid="stVegaLiteChart"],
[data-testid="stArrowVegaLiteChart"],
[data-testid="stPlotlyChart"] {
    background: #101b2d;
    border: 1px solid #293e5b;
    border-radius: 14px;
    padding: 10px;
}
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #2563eb, #22d3ee);
}

/* Status messages */
[data-testid="stAlert"] {
    border-radius: 12px;
    border: 1px solid #344966;
}

/* Section separators and footers */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #293e5b !important;
    border-radius: 14px;
}
small {
    color: #8da5c4 !important;
}

/* Keep layout usable on small screens */
@media (max-width: 768px) {
    [data-testid="stMainBlockContainer"] {
        padding: 1rem .8rem 2rem;
    }
    h1 {
        font-size: 1.8rem !important;
    }
    [data-testid="stMetric"] {
        padding: 12px;
    }
}
</style>
""", unsafe_allow_html=True)


# CHIPPREDICT_PREMIUM_TITLE
st.markdown("""
<style>
.chippredict-hero {
    padding: 30px 24px;
    margin: 8px 0 28px 0;
    border-radius: 20px;
    background: linear-gradient(125deg, #101b32 0%, #163a63 55%, #075985 100%);
    border: 1px solid #2e648b;
    box-shadow: 0 12px 35px rgba(0, 0, 0, .22);
}
.chippredict-kicker {
    color: #67e8f9;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.chippredict-title {
    color: #ffffff;
    font-size: clamp(30px, 5vw, 48px);
    line-height: 1.15;
    font-weight: 850;
    margin: 0;
}
.chippredict-title span {
    color: #67e8f9;
}
.chippredict-subtitle {
    color: #dbeafe;
    font-size: 16px;
    margin-top: 14px;
    line-height: 1.7;
}
.chippredict-tags {
    margin-top: 18px;
    color: #bae6fd;
    font-size: 12px;
    letter-spacing: .5px;
}
</style>
<div class="chippredict-hero">
  <div class="chippredict-kicker">AI-powered semiconductor analytics</div>
  <h1 class="chippredict-title">⚡ AI <span>ChipPredict</span></h1>
  <div class="chippredict-subtitle">
    Predict timing violations early in the RTL-to-GDS design flow.
    Analyze circuit features, estimate timing risk, and compare predictions with OpenSTA.
  </div>
  <div class="chippredict-tags">
    RTL ANALYSIS &nbsp; • &nbsp; MACHINE LEARNING &nbsp; • &nbsp; OPENSTA
  </div>
</div>
""", unsafe_allow_html=True)

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


# CHIPPREDICT_DATA_AT_BOTTOM
import pandas as pd
from pathlib import Path as _ChipPath

st.divider()
st.header("📊 Project Dataset")
st.caption(
    "Explore the timing scenarios used by AI ChipPredict. "
    "This table shows the available dataset, not newly measured results."
)

_chip_data_path = _ChipPath("dataset/timing_ml_dataset.csv")

if _chip_data_path.exists():
    _chip_df = pd.read_csv(_chip_data_path)

    _m1, _m2, _m3 = st.columns(3)
    _m1.metric("Total scenarios", len(_chip_df))
    _m2.metric("Circuit designs", (
        _chip_df["circuit"].nunique()
        if "circuit" in _chip_df.columns else "N/A"
    ))
    _m3.metric("Dataset columns", len(_chip_df.columns))

    _chip_search = st.text_input(
        "🔎 Filter dataset by circuit name",
        key="chippredict_dataset_filter",
        placeholder="Example: mux or adder"
    )

    _chip_view = _chip_df
    if _chip_search and "circuit" in _chip_df.columns:
        _chip_view = _chip_df[
            _chip_df["circuit"].astype(str).str.contains(
                _chip_search, case=False, na=False
            )
        ]

    st.dataframe(_chip_view, hide_index=True, width="stretch")

    st.download_button(
        "⬇️ Download dataset as CSV",
        data=_chip_df.to_csv(index=False).encode("utf-8"),
        file_name="chippredict_timing_dataset.csv",
        mime="text/csv",
        key="chippredict_dataset_download"
    )
else:
    st.warning(
        "Dataset not found at dataset/timing_ml_dataset.csv. "
        "Run the dashboard from the ~/ai_chippredict project directory."
    )
