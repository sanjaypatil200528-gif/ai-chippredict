read_liberty /home/sanja/.ciel/ciel/sky130/versions/0fe599b2afb6708d281543108caf8310912f54af/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib

read_verilog results/comparator_8bit_sky130.v
link_design comparator_8bit
read_sdc sta/comparator_8bit.sdc

puts "\n===== COMPARATOR TIMING CHECKS ====="
report_checks -path_delay max -format full -group_count 10

puts "\n===== WORST NEGATIVE SLACK ====="
report_wns

puts "\n===== TOTAL NEGATIVE SLACK ====="
report_tns
