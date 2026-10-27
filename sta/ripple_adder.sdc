
# Virtual clock for combinational input-to-output timing
create_clock -name virtual_clk -period 10.0

# Input arrival-time constraints
set_input_delay -clock virtual_clk 1.0 [get_ports {a[*] b[*] cin}]

# Output required-time constraints
set_output_delay -clock virtual_clk 1.0 [get_ports {sum[*] cout}]
