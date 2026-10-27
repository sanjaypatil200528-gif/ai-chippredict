`timescale 1ns/1ps

module tb_cla_adder_8bit;

reg [7:0] a, b;
reg cin;
wire [7:0] sum;
wire cout;

integer i, j, k;
reg [8:0] expected;

cla_adder_8bit dut (
    .a(a), .b(b), .cin(cin),
    .sum(sum), .cout(cout)
);

initial begin
    for (i = 0; i < 256; i = i + 1)
        for (j = 0; j < 256; j = j + 1)
            for (k = 0; k < 2; k = k + 1) begin
                a = i;
                b = j;
                cin = k;
                expected = i + j + k;
                #1;

                if ({cout, sum} !== expected) begin
                    $display("FAIL: a=%h b=%h cin=%b got=%h expected=%h",
                             a, b, cin, {cout, sum}, expected);
                    $fatal(1);
                end
            end

    $display("PASS: All 131072 CLA test cases passed.");
    $finish;
end

endmodule
