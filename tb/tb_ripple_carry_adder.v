`timescale 1ns/1ps

module tb_ripple_carry_adder;

    reg  [7:0] a;
    reg  [7:0] b;
    reg        cin;

    wire [7:0] sum;
    wire       cout;

    integer i;
    integer j;
    integer k;
    integer errors;
    reg [8:0] expected;

    ripple_carry_adder dut (
        .a(a),
        .b(b),
        .cin(cin),
        .sum(sum),
        .cout(cout)
    );

    initial begin
        errors = 0;

        // Exhaustively test all input combinations:
        // 256 values of A × 256 values of B × 2 carry inputs.
        for (i = 0; i < 256; i = i + 1) begin
            for (j = 0; j < 256; j = j + 1) begin
                for (k = 0; k < 2; k = k + 1) begin
                    a = i;
                    b = j;
                    cin = k;

                    expected = i + j + k;

                    #1;

                    if ({cout, sum} !== expected) begin
                        errors = errors + 1;

                        if (errors <= 10) begin
                            $display(
                                "FAIL: A=%0d B=%0d Cin=%0d Got=%0d Expected=%0d",
                                a, b, cin, {cout, sum}, expected
                            );
                        end
                    end
                end
            end
        end

        if (errors == 0)
            $display("PASS: All 131072 test cases passed.");
        else
            $display("FAIL: %0d test cases failed.", errors);

        $finish;
    end

endmodule
