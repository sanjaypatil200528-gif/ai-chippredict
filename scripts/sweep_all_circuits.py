import csv
import re
import subprocess
from pathlib import Path

LIB = Path(
    "/home/sanja/.ciel/ciel/sky130/versions/"
    "0fe599b2afb6708d281543108caf8310912f54af/"
    "sky130A/libs.ref/sky130_fd_sc_hd/"
    "lib/sky130_fd_sc_hd__tt_025C_1v80.lib"
)

OUT_DIR = Path("results/timing_sweep")
OUT_CSV = OUT_DIR / "all_circuits_timing_sweep.csv"

PERIODS = [10.0, 8.0, 6.0, 5.0, 4.0, 3.0, 2.5, 2.0, 1.5, 1.0]

# Netlist filename, top-level module, input ports, output ports.
CIRCUITS = [
    (
        "results/array_multiplier_8bit_sky130.v",
        "array_multiplier_8bit",
        ["a", "b"],
        ["product"],
    ),
    (
        "results/barrel_shifter_8bit_sky130.v",
        "barrel_shifter_8bit",
        ["data_in", "shift_amt", "dir"],
        ["data_out"],
    ),
    (
        "results/cla_adder_8bit_sky130.v",
        "cla_adder_8bit",
        ["a", "b", "cin"],
        ["sum", "cout"],
    ),
    (
        "results/comparator_8bit_sky130.v",
        "comparator_8bit",
        ["a", "b"],
        ["less", "equal", "greater"],
    ),
    (
        "results/mux_8bit_sky130.v",
        "mux_8bit",
        ["a", "b", "sel"],
        ["y"],
    ),
    (
        "results/ripple_carry_adder_sky130.v",
        "ripple_carry_adder",
        ["a", "b", "cin"],
        ["sum", "cout"],
    ),
]

OUT_DIR.mkdir(parents=True, exist_ok=True)

if not LIB.exists():
    raise SystemExit(f"Liberty file not found: {LIB}")

if subprocess.run(
    ["sta", "-version"], capture_output=True, text=True
).returncode != 0:
    raise SystemExit("OpenSTA command 'sta' is unavailable.")

for netlist, module, _, _ in CIRCUITS:
    if not Path(netlist).exists():
        raise SystemExit(f"Missing netlist: {netlist}")

rows = []

for netlist, module, inputs, outputs in CIRCUITS:
    for period in PERIODS:
        tag = f"{module}_{period:g}ns"
        sdc = OUT_DIR / f"{tag}.sdc"
        tcl = OUT_DIR / f"{tag}.tcl"
        log = OUT_DIR / f"{tag}.log"

        scalar_ports = {"cin", "sel", "dir", "less", "equal", "greater"}

        def port_pattern(port):
            return port if port in scalar_ports else f"{port}[*]"

        input_ports = " ".join(port_pattern(p) for p in inputs)
        output_ports = " ".join(port_pattern(p) for p in outputs)

        sdc.write_text(
            f"create_clock -name virtual_clk -period {period}\n"
            f"set_input_delay 1.0 -clock virtual_clk "
            f"[get_ports {{{input_ports}}}]\n"
            f"set_output_delay 1.0 -clock virtual_clk "
            f"[get_ports {{{output_ports}}}]\n"
        )

        tcl.write_text(
            f"read_liberty {LIB}\n"
            f"read_verilog {netlist}\n"
            f"link_design {module}\n"
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

        matches = re.findall(
            r"([-+]?\d+(?:\.\d+)?)\s+slack\s+\((?:MET|VIOLATED)\)",
            output,
            flags=re.IGNORECASE,
        )

        if result.returncode != 0 or not matches:
            print(f"FAILED: {module}, period={period:g} ns; inspect {log}")
            continue

        slack = float(matches[0])
        violation = int(slack < 0)

        rows.append({
            "circuit": module,
            "clock_period_ns": period,
            "input_delay_ns": 1.0,
            "output_delay_ns": 1.0,
            "setup_slack_ns": slack,
            "timing_violation": violation,
        })

        print(
            f"{module:24} period={period:>4g} ns "
            f"slack={slack:>8.3f} ns violation={violation}"
        )

if not rows:
    raise SystemExit(
        "No valid measurements collected. Inspect the generated .log files."
    )

with OUT_CSV.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"\nSaved {len(rows)} measured cases to {OUT_CSV}")
print(f"Failed cases: {len(CIRCUITS) * len(PERIODS) - len(rows)}")
print("Violation label: setup slack < 0 ns.")
