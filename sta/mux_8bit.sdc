create_clock -name virtual_clk -period 10.0
set_input_delay 1.0 -clock virtual_clk [get_ports {a[*] b[*] sel}]
set_output_delay 1.0 -clock virtual_clk [get_ports {y[*]}]
