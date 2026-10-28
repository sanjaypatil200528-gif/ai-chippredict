🚀 AI ChipPredict

🧠 AI-Based Early Prediction of PPA and Timing Violations in RTL-to-GDS Flow

<p align="center">
  <img src="https://img.shields.io/badge/Domain-VLSI%20%7C%20EDA-blueviolet?style=for-the-badge" alt="VLSI EDA"/>
  <img src="https://img.shields.io/badge/AI-Machine%20Learning-blue?style=for-the-badge" alt="Machine Learning"/>
  <img src="https://img.shields.io/badge/Language-Python%20%7C%20MATLAB-orange?style=for-the-badge" alt="Python and MATLAB"/>
  <img src="https://img.shields.io/badge/Tools-Yosys%20%7C%20OpenSTA-success?style=for-the-badge" alt="Yosys and OpenSTA"/>
</p><p align="center">
  <b>Predict early. Analyze intelligently. Validate scientifically.</b>
</p>---

🌟 1. What Is AI ChipPredict?

AI ChipPredict is an open-source research project exploring how Artificial Intelligence and Machine Learning can help predict critical-path delay, timing violations, and selected Power, Performance, and Area (PPA) metrics during the early stages of digital chip design.

Traditional chip implementation can reveal timing problems late in the design flow. AI ChipPredict investigates whether design features and historical EDA measurements can help identify potential problems earlier.

🎯 Our mission: Build a reproducible, data-driven framework that connects RTL design, electronic design automation (EDA), mathematical modeling, and machine learning.

«⚠️ Predictions are estimates. Final timing and physical-design verification must use appropriate EDA analysis.»

🎨 2. Project at a Glance

Feature| Description
🧩 RTL input| Digital circuits described using Verilog
⚙️ Synthesis| Yosys
⏱️ Timing analysis| OpenSTA
🤖 AI models| Regression and classification
📊 Scientific validation| Error metrics and held-out tests
🧮 Mathematical analysis| Timing slack and prediction errors
📈 Dashboard| Streamlit
🧪 Research environment| MATLAB or Python

🔄 3. Complete Project Workflow

flowchart TD
    A(["🚀 START"]) --> B["🧩 Select RTL Circuit"]
    B --> C["🔍 Validate RTL and Constraints"]
    C --> D["⚙️ Synthesize with Yosys"]
    D --> E["📦 Extract Netlist Features"]
    E --> F["⏱️ Run OpenSTA"]
    F --> G[("🗃️ Measured Dataset")]
    G --> H["🧹 Clean and Prepare Data"]
    H --> I["✂️ Split Training and Test Data"]
    I --> J["🤖 Train ML Models"]
    J --> K["🔮 Predict Delay and Violation Risk"]
    K --> L["📏 Compare Against STA Results"]
    L --> M["📊 Calculate Error and Classification Metrics"]
    M --> N{"✅ Meets Evaluation Criteria?"}
    N -- "No" --> O["🔧 Improve Features or Model"]
    O --> J
    N -- "Yes" --> P["📈 Visualize Results"]
    P --> Q["📄 Generate CSV Report"]
    Q --> R(["🏁 END"])

    classDef input fill:#dbeafe,stroke:#2563eb,color:#111827,stroke-width:2px
    classDef eda fill:#d1fae5,stroke:#059669,color:#111827,stroke-width:2px
    classDef ai fill:#ede9fe,stroke:#7c3aed,color:#111827,stroke-width:2px
    classDef result fill:#fef3c7,stroke:#d97706,color:#111827,stroke-width:2px
    classDef decision fill:#fee2e2,stroke:#dc2626,color:#111827,stroke-width:2px

    class A,B,C input
    class D,E,F,G eda
    class H,I,J,K,O ai
    class L,M,P,Q,R result
    class N decision

🧭 How to understand the flow

- 🔵 Input: Choose a circuit and validate its constraints.
- 🟢 EDA: Synthesize the circuit and measure its timing.
- 🟣 AI: Learn patterns from measured design data and make predictions.
- 🟡 Validation: Compare predicted values with measured results.
- 🔴 Decision: Improve the model if its performance is insufficient.

The loop is important: the model must be evaluated and improved using evidence, not simply assumed to work.

🧮 4. Mathematical Foundation

⏱️ A. Timing Slack

A simplified setup-timing relationship is:

[
S=T_{\mathrm{required}}-T_{\mathrm{arrival}}
]

Slack condition| Meaning
(S>0)| Positive slack
(S=0)| Timing requirement is met exactly
(S<0)| Timing violation

Actual slack depends on the clock definitions, timing constraints, cell delays, interconnect, and analysis settings.

🤖 B. Machine-Learning Prediction

Represent a circuit using extracted features:

[
X=[x_1,x_2,\ldots,x_n]
]

The trained model predicts the target:

[
\hat{y}=f_{\theta}(X)
]

For example, the target (y) may be critical-path delay. The prediction error is:

[
e=y-\hat{y}
]

🚨 C. Timing-Violation Classification

[
z=
\begin{cases}
1,&S<0\
0,&S\geq0
\end{cases}
]

The classifier estimates the probability of a timing violation using the available design features.

📏 D. Regression Metrics

Mean Absolute Error (MAE)

[
MAE=\frac{1}{N}\sum_{i=1}^{N}|y_i-\hat{y}_i|
]

Root Mean Squared Error (RMSE)

[
RMSE=\sqrt{\frac{1}{N}\sum_{i=1}^{N}(y_i-\hat{y}_i)^2}
]

Use these metrics on held-out data and report the units of the target.

🛠️ 5. Technology Stack

Technology| Role
💻 Verilog / SystemVerilog| Hardware description
⚙️ Yosys| Logic synthesis
⏱️ OpenSTA| Static timing analysis
🐍 Python| Data preparation and model integration
📐 MATLAB| Mathematical modeling and ML experiments
📊 Streamlit| Interactive dashboard
🌿 Git / GitHub| Version control and collaboration

🧩 6. Benchmark Circuits

The initial benchmark plan includes:

Circuit| Research purpose
"adder_8bit"| Arithmetic logic
"cla_adder"| Carry-lookahead logic
"array_multiplier"| Multiplication paths
"barrel_shifter"| Shift and selection logic
"comparator_8bit"| Comparison logic
"mux_8bit"| Multiplexer paths

🎯 Dataset target: 1,000 netlist samples.

This is a target for dataset development, not a claim that 1,000 real measurements have already been collected.

🤖 7. Machine-Learning Models

flowchart LR
    A["📚 Measured Dataset"] --> B["🌲 Random Forest"]
    A --> C["🚀 Gradient Boosting"]
    A --> D["🧠 Neural Network"]
    A --> E["🕸️ Graph Neural Network"]
    B --> F["📊 Compare Results"]
    C --> F
    D --> F
    E --> F
    F --> G["🏆 Select Using Held-Out Evaluation"]

    classDef data fill:#dbeafe,stroke:#2563eb,color:#111827
    classDef model fill:#ede9fe,stroke:#7c3aed,color:#111827
    classDef output fill:#d1fae5,stroke:#059669,color:#111827

    class A data
    class B,C,D,E model
    class F,G output

Models should be compared using the same evaluation protocol. A graph neural network is an advanced extension requiring a meaningful circuit graph; it should not be assumed to outperform simpler models.

📊 8. Scientific Evaluation

Metric| What it measures
MAE| Average absolute prediction error
RMSE| Prediction error with greater penalty for large errors
(R^2)| Explained variation for regression
Precision| Fraction of predicted violations that are real violations
Recall| Fraction of actual violations detected
F1 score| Balance between precision and recall
ROC-AUC| Ability to rank positive and negative cases

🔬 Validation strategy

1. Generate measured timing results using a consistent EDA flow.
2. Keep training and testing data separate.
3. Test on entire circuit designs excluded from training.
4. Compare the ML model against simple baselines.
5. Report uncertainty and limitations.
6. Reproduce the experiment with documented settings.

Scientific goal: Establish measured predictive performance under defined conditions. Do not claim perfect prediction or real-world improvement before the experiments demonstrate it.

📈 9. Dashboard Vision

The dashboard can present:

- 🧩 Circuit inputs and timing constraints.
- ⏱️ Predicted delay and measured delay.
- 🚨 Timing-violation probability and classification.
- 📊 Evaluation metrics and charts.
- 🔍 Circuit and critical-path information where available.
- 📄 CSV reports for analysis.

The interface must clearly distinguish measured results, model predictions, and illustrative demonstration values.

📁 10. Project Structure

ai-chippredict/
├── app/
│   └── dashboard.py
├── dataset/
│   ├── rtl_features.csv
│   ├── measured_results.csv
│   └── timing_ml_dataset.csv
├── models/
├── rtl/
├── tb/
├── synthesis/
├── sta/
├── scripts/
├── tests/
├── requirements.txt
├── README.md
└── .gitignore

This is the proposed structure; retain your actual files and adapt the layout as the project evolves.

🚀 11. Getting Started

Step 1 — Clone the repository

git clone https://github.com/sanjaypatil200528-gif/ai-chippredict.git
cd ai-chippredict

Step 2 — Create a Python environment

python3 -m venv .venv
source .venv/bin/activate

Step 3 — Install dependencies

python -m pip install -r requirements.txt

Installation requires network access or an appropriately prepared offline package cache. MATLAB and external EDA tools may require separate installation.

Step 4 — Run the dashboard

If the project dependencies are installed and the dashboard entry point exists:

streamlit run app/dashboard.py

Open the local URL displayed in your terminal.

Note: A working dashboard does not automatically establish that the complete synthesis, STA, and machine-learning pipeline is implemented. Verify each stage separately.

🔭 12. Future Enhancements

- 🕸️ Circuit-graph extraction and graph neural networks.
- 📉 More robust delay prediction.
- 🚨 Timing-violation risk calibration.
- 📐 MATLAB-based statistical validation.
- ⚡ More comprehensive area and power estimation.
- 🔬 Generalization testing across circuit designs.
- 🎞️ Animated workflow visualization.
- 📦 Reproducible benchmark and experiment automation.

⚠️ 13. Limitations

- Early design features may not capture post-route parasitics.
- Accuracy depends on the quality and diversity of measured data.
- Different technology libraries and constraints may change results.
- Power estimation requires suitable technology and switching-activity information.
- Predictions do not replace signoff STA or physical verification.
- Synthetic data alone cannot establish real EDA prediction accuracy.

🏁 14. Final Goal

AI ChipPredict aims to connect hardware design, mathematical analysis, machine learning, and measured EDA results in a reproducible research workflow.

The success of the project will be demonstrated through experiments, held-out validation, fair model comparisons, and transparent reporting—not through unverified accuracy claims.

---

<p align="center">
  <b>🚀 AI ChipPredict — Making Early Chip-Timing Prediction Research Measurable</b>
</p><p align="center">
  <sub>Open-source research • VLSI • EDA • Machine Learning • Scientific Validation</sub>
</p>
