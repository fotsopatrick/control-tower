import sys, json

def calculate_expected(input_val):
    ops = {"op_k7": {"a": 3, "b": 7}, "op_m2": {"a": 5, "b": 2}, "op_q9": {"a": 2, "b": 11}}
    procedure = ["op_q9", "op_k7", "op_m2"]
    val = input_val
    for op in procedure:
        val = val * ops[op]["a"] + ops[op]["b"]
    return val

if __name__ == "__main__":
    try:
        inp = int(sys.argv[1])
        print(calculate_expected(inp))
    except:
        sys.exit(1)
