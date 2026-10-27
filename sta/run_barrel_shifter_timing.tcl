read_liberty /home/sanja/.ciel/ciel/sky130/versions/0fe599b2afb6708d281543108caf8310912f54af/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib

read_verilog results/barrel_shifter_8bit_sky130.v
link_design barrel_shifter_8bit
read_sdc sta/barrel_shifter_8bit.sdc

report_checks -path_delay max -format full_clock_expanded
report_wns
report_tns
