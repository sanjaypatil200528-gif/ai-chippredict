import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

MODEL_PATH = Path("models/timing_violation_rf.joblib")
FEATURES_PATH = Path("dataset/rtl_features.csv")
STA_PATH = Path("results/timing_sweep/all_circuits_timing_sweep.csv")

st.set_page_config(
    page_title="AI ChipPredict",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ AI ChipPredict")
st.subheader("AI-Based Timing Violation Prediction in RTL-to-GDS Flow")
st.caption("Random Forest prediction with OpenSTA timing comparison")

if not all(p.exists() for p in [MODEL_PATH, FEATURES_PATH, STA_PATH]):
    st.error("A required model or dataset file is missing.")
    st.stop()

saved = joblib.load(MODEL_PATH)
model = saved["model"]
feature_cols = saved["feature_cols"]
features = pd.read_csv(FEATURES_PATH)
sta = pd.read_csv(STA_PATH)

left, right = st.columns(2)

with left:
    st.subheader("Circuit Configuration")
    circuit = st.selectbox("Select RTL circuit", features["circuit"].tolist())
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
    predict = st.button("Predict and Compare", type="primary", width="stretch")

with right:
    st.subheader("Prediction Results")

    if predict:
        row = features.loc[features["circuit"] == circuit].iloc[[0]].copy()
        row["clock_period_ns"] = period
        row["input_delay_ns"] = input_delay
        row["output_delay_ns"] = output_delay

        X = row[feature_cols]
        prediction = int(model.predict(X)[0])
        probabilities = model.predict_proba(X)[0]
        violation_probability = probabilities[list(model.classes_).index(1)]

        st.metric("AI Violation Probability", f"{violation_probability:.1%}")

        if prediction:
            st.error("AI Prediction: TIMING VIOLATION")
        else:
            st.success("AI Prediction: TIMING PASS")

        # Match exact timing constraints in the measured OpenSTA dataset.
        actual = sta[
            (sta["circuit"] == circuit)
            & (sta["clock_period_ns"].sub(period).abs() < 1e-8)
            & (sta["input_delay_ns"].sub(input_delay).abs() < 1e-8)
            & (sta["output_delay_ns"].sub(output_delay).abs() < 1e-8)
        ]

        if not actual.empty:
            actual_row = actual.iloc[0]
            actual_violation = int(actual_row["timing_violation"])
            slack = float(actual_row["setup_slack_ns"])

            st.metric("OpenSTA Setup Slack", f"{slack:.2f} ns")

            if actual_violation:
                st.error("OpenSTA Result: TIMING VIOLATION")
            else:
                st.success("OpenSTA Result: TIMING PASS")

            if prediction == actual_violation:
                st.success("AI and OpenSTA results MATCH")
            else:
                st.warning("AI and OpenSTA results DO NOT MATCH")

            report = pd.DataFrame([{
                "Circuit": circuit,
                "Clock Period (ns)": period,
                "Input Delay (ns)": input_delay,
                "Output Delay (ns)": output_delay,
                "AI Prediction": "TIMING VIOLATION" if prediction else "TIMING PASS",
                "AI Violation Probability (%)": round(violation_probability * 100, 2),
                "OpenSTA Setup Slack (ns)": slack,
                "OpenSTA Result": "TIMING VIOLATION" if actual_violation else "TIMING PASS",
                "AI Matches OpenSTA": prediction == actual_violation
            }])
        else:
            st.info(
                "No exact OpenSTA measurement exists for these constraints. "
                "The AI prediction is shown, but actual timing cannot be compared."
            )
            report = pd.DataFrame([{
                "Circuit": circuit,
                "Clock Period (ns)": period,
                "Input Delay (ns)": input_delay,
                "Output Delay (ns)": output_delay,
                "AI Prediction": "TIMING VIOLATION" if prediction else "TIMING PASS",
                "AI Violation Probability (%)": round(violation_probability * 100, 2),
                "OpenSTA Setup Slack (ns)": None,
                "OpenSTA Result": "No matching measurement",
                "AI Matches OpenSTA": None
            }])

        st.dataframe(report, hide_index=True, width="stretch")
        st.download_button(
            "Download Comparison CSV",
            data=report.to_csv(index=False),
            file_name="chippredict_sta_comparison.csv",
            mime="text/csv",
            width="stretch"
        )
    else:
        st.info("Choose a circuit and constraints, then click Predict and Compare.")

st.divider()
st.subheader("Project Overview")

a, b, c = st.columns(3)
a.metric("Available Circuits", len(features))
b.metric("Prediction Model", "Random Forest")
c.metric("OpenSTA Scenarios", len(sta))

st.caption(
    "OpenSTA comparison is available only for constraints present in the measured dataset. "
    "Results depend on the current synthesized netlists and timing assumptions."
)
