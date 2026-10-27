import csv
import re
import subprocess
from pathlib import Path

LIB = (
    "/home/sanja/.ciel/ciel/sky130/versions/"
    "0fe599b2afb6708d281543108caf8310912f54af/"
    "sky130A/libs.ref/sky130_fd_sc_hd/"
    "lib/sky130_fd_sc_hd__tt_025C_1v80.lib"
)

NETLIST = Path("results/array_multiplier_8bit_sky130.v")
OUT_DIR = Path("results/timing_sweep")
CSV_OUT = OUT_DIR / "multiplier_timing_sweep.csv"

# Test increasingly tight clock periods, in nanoseconds.
PERIODS = [10.0, 8.0, 6.0, 5.0, 4.0, 3.0, 2.5, 2.0, 1.5, 1.0]

OUT_DIR.mkdir(parents=True, exist_ok=True)

if not NETLIST.exists():
    raise SystemExit(f"Missing synthesized netlist: {NETLIST}")
if not Path(LIB).exists():
    raise SystemExit(f"Missing Liberty file: {LIB}")

rows = []

for period in PERIODS:
    sdc = OUT_DIR / f"multiplier_{period:g}ns.sdc"
    tcl = OUT_DIR / f"multiplier_{period:g}ns.tcl"
    log = OUT_DIR / f"multiplier_{period:g}ns.log"

    sdc.write_text(
        f"create_clock -name virtual_clk -period {period}\n"
        "set_input_delay 1.0 -clock virtual_clk "
        "[get_ports {a[*] b[*]}]\n"
        "set_output_delay 1.0 -clock virtual_clk "
        "[get_ports {product[*]}]\n"
    )

    tcl.write_text(
        f"read_liberty {LIB}\n"
        f"read_verilog {NETLIST}\n"
        "link_design array_multiplier_8bit\n"
        f"read_sdc {sdc}\n"
        "report_checks -path_delay max -format full_clock_expanded\n"
        "report_wns\n"
        "report_tns\n"
        "exit\n"
    )

    result = subprocess.run(
        ["sta", "-exit", str(tcl)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + "\n" + result.stderr
    log.write_text(output)

    if result.returncode != 0 or "slack" not in output.lower():
        print(f"STA failed at {period:g} ns. Inspect {log}")
        print(output[-1500:])
        continue

    # Extract the slack from the first reported critical path.
    matches = re.findall(
        r"([-+]?\d+(?:\.\d+)?)\s+slack\s+\((?:MET|VIOLATED)\)",
        output,
        flags=re.IGNORECASE,
    )
    if not matches:
        print(f"Could not parse path slack at {period:g} ns.")
        print(f"Inspect {log}")
        continue

    slack = float(matches[0])
    violation = int(slack < 0)

    rows.append({
        "circuit": "array_multiplier_8bit",
        "clock_period_ns": period,
        "input_delay_ns": 1.0,
        "output_delay_ns": 1.0,
        "setup_slack_ns": slack,
        "timing_violation": violation,
    })

    print(
        f"Period={period:>4g} ns | "
        f"Slack={slack:>8.3f} ns | "
        f"Violation={violation}"
    )

if rows:
    with CSV_OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved {len(rows)} measurements to {CSV_OUT}")
    print("Label definition: setup slack < 0 ns means violation.")
else:
    raise SystemExit("No measurements collected; inspect the STA logs.")
