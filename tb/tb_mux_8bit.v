module tb_mux_8bit;

reg  [7:0] a, b;
reg        sel;
wire [7:0] y;

integer i, j, k;
integer count;

mux_8bit dut (
    .a(a),
    .b(b),
    .sel(sel),
    .y(y)
);

initial begin
    count = 0;

    for (i = 0; i < 256; i = i + 1) begin
        for (j = 0; j < 256; j = j + 1) begin
            for (k = 0; k < 2; k = k + 1) begin
                a = i;
                b = j;
                sel = k;

                #1;

                if (y !== (sel ? b : a)) begin
                    $display(
                        "FAIL: a=%h b=%h sel=%b y=%h",
                        a, b, sel, y
                    );
                    $finish;
                end

                count = count + 1;
            end
        end
    end

    $display("PASS: All %0d test cases passed.", count);
    $finish;
end

endmodule
