`timescale 1ns/1ps

module tb_array_multiplier_8bit;

reg  [7:0] a, b;
wire [15:0] product;
reg  [15:0] expected;
integer i, j;

array_multiplier_8bit dut (
    .a(a),
    .b(b),
    .product(product)
);

initial begin
    for (i = 0; i < 256; i = i + 1) begin
        for (j = 0; j < 256; j = j + 1) begin
            a = i;
            b = j;
            expected = i * j;
            #1;

            if (product !== expected) begin
                $display("FAIL: a=%0d b=%0d expected=%0d got=%0d",
                         a, b, expected, product);
                $finish;
            end
        end
    end

    $display("PASS: All 65536 multiplier test cases passed.");
    $finish;
end

endmodule
