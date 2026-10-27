`timescale 1ns/1ps

module tb_barrel_shifter_8bit;

reg  [7:0] data_in;
reg  [2:0] shift_amt;
reg        dir;
wire [7:0] data_out;

integer d, s, x;
reg [7:0] expected;

barrel_shifter_8bit dut (
    .data_in(data_in),
    .shift_amt(shift_amt),
    .dir(dir),
    .data_out(data_out)
);

initial begin
    for (d = 0; d < 2; d = d + 1) begin
        dir = d;

        for (s = 0; s < 8; s = s + 1) begin
            shift_amt = s;

            for (x = 0; x < 256; x = x + 1) begin
                data_in = x;
                #1;

                if (dir == 0)
                    expected = (data_in << shift_amt) & 8'hFF;
                else
                    expected = data_in >> shift_amt;

                if (data_out !== expected) begin
                    $display(
                        "FAIL: dir=%0d shift=%0d input=%h output=%h expected=%h",
                        dir, shift_amt, data_in, data_out, expected
                    );
                    $fatal(1);
                end
            end
        end
    end

    $display("PASS: All 4096 test cases passed.");
    $finish;
end

endmodule
