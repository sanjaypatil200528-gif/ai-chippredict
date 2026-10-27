#!/usr/bin/env python3
import argparse
import csv
import re
import sys
from pathlib import Path

FIELDS = [
    "circuit", "cell_count", "cell_area",
    "path_startpoint", "path_endpoint",
    "data_arrival_ns", "input_delay_ns",
    "estimated_cell_path_delay_ns", "required_time_ns",
    "slack_ns", "timing_violation", "wns_ns", "tns_ns"
]


def find_number(pattern, text, description):
    match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
    if not match:
        raise ValueError(f"Could not find {description} in OpenSTA log.")
    return float(match.group(1))


def main():
    parser = argparse.ArgumentParser(
        description="Extract timing metrics from an OpenSTA report."
    )
    parser.add_argument("--log", default="results/opensta_timing.log")
    parser.add_argument("--csv", default="dataset/measured_results.csv")
    parser.add_argument("--circuit", default="ripple_carry_adder")
    parser.add_argument("--cell-count", type=int, default=38)
    parser.add_argument("--cell-area", type=float, default=238.9792)
    parser.add_argument("--input-delay", type=float, default=1.0)
    args = parser.parse_args()

    log_path = Path(args.log)
    csv_path = Path(args.csv)

    if not log_path.is_file():
        sys.exit(f"ERROR: Log file not found: {log_path}")

    text = log_path.read_text(encoding="utf-8", errors="replace")

    # OpenSTA prints timing paths in order; extract the first reported path.
    blocks = re.split(r"(?=^Startpoint:)", text, flags=re.MULTILINE)
    path_block = next(
        (block for block in blocks if block.startswith("Startpoint:")),
        None
    )
    if path_block is None:
        sys.exit("ERROR: No timing path found. Check the OpenSTA log.")

    start_match = re.search(r"^Startpoint:\s*(\S+)", path_block, re.MULTILINE)
    end_match = re.search(r"^Endpoint:\s*(\S+)", path_block, re.MULTILINE)
    if not start_match or not end_match:
        sys.exit("ERROR: Could not extract path startpoint/endpoint.")

    try:
        arrival = find_number(
            r"^\s*([-+]?\d+(?:\.\d+)?)\s+data arrival time\b",
            path_block, "data arrival time"
        )
        slack = find_number(
            r"^\s*([-+]?\d+(?:\.\d+)?)\s+slack\s+\((?:MET|VIOLATED)\)",
            path_block, "path slack"
        )
        wns = find_number(r"^\s*wns\s+([-+]?\d+(?:\.\d+)?)\s*$",
                          text, "WNS")
        tns = find_number(r"^\s*tns\s+([-+]?\d+(?:\.\d+)?)\s*$",
                          text, "TNS")
    except ValueError as error:
        sys.exit(f"ERROR: {error}")

    required_match = re.search(
        r"^\s*([-+]?\d+(?:\.\d+)?)\s+data required time\b",
        path_block, re.MULTILINE
    )
    required = float(required_match.group(1)) if required_match else arrival + slack

    row = {
        "circuit": args.circuit,
        "cell_count": args.cell_count,
        "cell_area": f"{args.cell_area:.4f}",
        "path_startpoint": start_match.group(1),
        "path_endpoint": end_match.group(1),
        "data_arrival_ns": f"{arrival:.2f}",
        "input_delay_ns": f"{args.input_delay:.2f}",
        "estimated_cell_path_delay_ns": f"{arrival - args.input_delay:.2f}",
        "required_time_ns": f"{required:.2f}",
        "slack_ns": f"{slack:.2f}",
        "timing_violation": int(slack < 0),
        "wns_ns": f"{wns:.2f}",
        "tns_ns": f"{tns:.2f}",
    }

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    existing = []

    if csv_path.exists():
        with csv_path.open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames and "circuit" in reader.fieldnames:
                existing = [
                    {field: old.get(field, "") for field in FIELDS}
                    for old in reader
                    if old.get("circuit") != args.circuit
                ]

    existing.append(row)

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(existing)

    print("PASS: Timing metrics extracted successfully.")
    print(f"Circuit:       {row['circuit']}")
    print(f"Critical path: {row['path_startpoint']} -> {row['path_endpoint']}")
    print(f"Arrival:       {row['data_arrival_ns']} ns")
    print(f"Path slack:    {row['slack_ns']} ns")
    print(f"WNS / TNS:     {row['wns_ns']} / {row['tns_ns']} ns")
    print(f"Violation:     {row['timing_violation']}")
    print(f"CSV updated:   {csv_path}")


if __name__ == "__main__":
    main()
