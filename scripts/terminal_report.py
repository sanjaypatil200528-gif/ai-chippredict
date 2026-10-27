
import csv
import os
import statistics

ROOT = os.getcwd()
DATASET = os.path.join(ROOT, "dataset")
RESULTS = os.path.join(ROOT, "results")

GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def read_csv(path):
    if not os.path.isfile(path):
        return []
    with open(path, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def number(row, *keys):
    for key in keys:
        try:
            value = row.get(key)
            if value not in (None, ""):
                return float(value)
        except (ValueError, TypeError):
            pass
    return None


def stats(values):
    values = [v for v in values if v is not None]
    if not values:
        return None
    return min(values), max(values), statistics.mean(values)


def print_table(headers, rows):
    if not rows:
        print("  No data available yet.")
        return

    widths = [
        max(len(str(header)), *(len(str(row[i])) for row in rows))
        for i, header in enumerate(headers)
    ]

    border = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    print(border)
    print("| " + " | ".join(
        str(h).ljust(w) for h, w in zip(headers, widths)
    ) + " |")
    print(border)

    for row in rows:
        print("| " + " | ".join(
            str(value).ljust(width)
            for value, width in zip(row, widths)
        ) + " |")
    print(border)


def main():
    measured_path = os.path.join(DATASET, "measured_results.csv")
    sweep_path = os.path.join(
        RESULTS, "timing_sweep", "multiplier_timing_sweep.csv"
    )
    model_path = os.path.join(RESULTS, "algorithm_comparison.csv")

    measured = read_csv(measured_path)
    sweep = read_csv(sweep_path)
    models = read_csv(model_path)

    print(CYAN + "=" * 76)
    print(" AI CHIP PREDICT: AI-BASED TIMING VIOLATION PREDICTION")
    print(" RTL-to-GDS Flow | Timing Analysis and Model Evaluation")
    print("=" * 76 + RESET)

    stages = [
        ("Input RTL Design", "Verilog benchmark circuits"),
        ("Functional Simulation", "Icarus Verilog"),
        ("Logic Synthesis", "Yosys"),
        ("Static Timing Analysis", "OpenSTA"),
        ("Feature Extraction", "Measured timing and RTL features"),
        ("Dataset Generation", "Measured results and clock-period sweeps"),
        ("Model Evaluation", "Only when trained model results are available"),
    ]

    print("\n" + GREEN + "[PROJECT PIPELINE]" + RESET)
    for i, (stage, detail) in enumerate(stages, 1):
        print(f" [STEP {i}] {stage:<27}: {detail}")

    print("\n" + GREEN + "[DATASET SUMMARY]" + RESET)
    print(f" Measured timing rows : {len(measured)}")
    print(f" Clock sweep rows     : {len(sweep)}")
    print(f" Model result rows    : {len(models)}")

    if measured:
        circuits = sorted({
            row.get("circuit", "unknown") for row in measured
        })
        print(f" Unique circuits      : {len(circuits)}")
        print(" Circuit names        : " + ", ".join(circuits))

        print("\n" + GREEN + "[MEASURED FEATURE STATISTICS]" + RESET)
        feature_specs = [
            ("Mapped cell count", ("cell_count",), "cells"),
            ("Mapped cell area", ("cell_area",), "area units"),
            ("Data arrival time", ("data_arrival_ns",), "ns"),
            ("Setup slack", ("slack_ns",), "ns"),
        ]

        rows = []
        for label, keys, unit in feature_specs:
            result = stats([number(row, *keys) for row in measured])
            if result:
                low, high, mean = result
                rows.append([
                    label,
                    f"{low:.3f}",
                    f"{high:.3f}",
                    f"{mean:.3f}",
                    unit,
                ])

        print_table(
            ["Feature", "Min", "Max", "Mean", "Unit"],
            rows
        )

        print("\n" + GREEN + "[MEASURED CIRCUIT TIMING]" + RESET)
        rows = []
        for row in measured:
            slack = number(row, "slack_ns")
            label = (
                f"{RED}VIOLATION{RESET}"
                if slack is not None and slack < 0
                else f"{GREEN}PASS{RESET}"
            )
            rows.append([
                row.get("circuit", "unknown"),
                f"{number(row, 'data_arrival_ns'):.3f}"
                if number(row, "data_arrival_ns") is not None else "N/A",
                f"{slack:.3f}" if slack is not None else "N/A",
                label,
            ])
        print_table(
            ["Circuit", "Arrival (ns)", "Slack (ns)", "Measured Status"],
            rows
        )
    else:
        print(YELLOW + "\nMeasured dataset not found or empty." + RESET)
        print("Expected: dataset/measured_results.csv")

    if sweep:
        print("\n" + GREEN + "[CLOCK-PERIOD SWEEP]" + RESET)
        rows = []
        for row in sweep:
            period = number(row, "clock_period_ns", "period_ns", "period")
            slack = number(row, "slack_ns", "setup_slack_ns", "slack")
            violation = row.get("timing_violation", "")
            if violation == "":
                violation = (
                    "1" if slack is not None and slack < 0 else "0"
                )
            status = (
                f"{RED}VIOLATION{RESET}"
                if str(violation) == "1"
                else f"{GREEN}PASS{RESET}"
            )
            rows.append([
                f"{period:.2f}" if period is not None else "N/A",
                f"{slack:.3f}" if slack is not None else "N/A",
                status,
            ])
        print_table(["Clock Period (ns)", "Slack (ns)", "STA Label"], rows)

    print("\n" + GREEN + "[AI ALGORITHM COMPARISON]" + RESET)
    if models:
        headers = list(models[0].keys())
        rows = []
        for model in models:
            rows.append([model.get(h, "") for h in headers])
        print_table(headers, rows)
    else:
        print(YELLOW + "No trained-model comparison CSV found." + RESET)
        print("Expected: results/algorithm_comparison.csv")
        print("Train and evaluate the models before reporting accuracy.")

    prediction_path = os.path.join(RESULTS, "prediction_result.txt")
    print("\n" + GREEN + "[NEW CIRCUIT PREDICTION]" + RESET)
    if os.path.isfile(prediction_path):
        with open(prediction_path, encoding="utf-8") as file:
            print(file.read().strip())
    else:
        print("No saved prediction found.")
        print("Run the prediction script to create results/prediction_result.txt.")

    print("\n" + CYAN + "=" * 76)
    print(" REPORT COMPLETE — values are read from the available project files.")
    print("=" * 76 + RESET)


if __name__ == "__main__":
    main()
