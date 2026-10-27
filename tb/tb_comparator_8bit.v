`timescale 1ns/1ps

module tb_comparator_8bit;

reg  [7:0] a, b;
wire less, equal, greater;

integer i, j;
integer errors = 0;

comparator_8bit dut (
    .a(a),
    .b(b),
    .less(less),
    .equal(equal),
    .greater(greater)
);

initial begin
    for (i = 0; i < 256; i = i + 1) begin
        for (j = 0; j < 256; j = j + 1) begin
            a = i;
            b = j;
            #1;

            if ((less !== (a < b)) ||
                (equal !== (a == b)) ||
                (greater !== (a > b))) begin
                errors = errors + 1;
                if (errors <= 10)
                    $display("FAIL: a=%0d b=%0d", a, b);
            end
        end
    end

    if (errors == 0)
        $display("PASS: All 65536 comparator test cases passed.");
    else
        $display("FAIL: %0d errors detected.", errors);

    $finish;
end

endmodule
