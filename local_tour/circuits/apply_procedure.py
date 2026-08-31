import json
import sys

def apply_op(val, op_data):
    return val * op_data["a"] + op_data["b"]

def run():
    ops = {"op_k7": {"a": 3, "b": 7}, "op_m2": {"a": 5, "b": 2}, "op_q9": {"a": 2, "b": 11}}
    val = 17
    procedure = ["op_q9", "op_k7", "op_m2"]
    for op in procedure:
        val = apply_op(val, ops[op])
    print(val)

if __name__ == "__main__":
    run()
