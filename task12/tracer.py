#!/usr/bin/env python3
import json
import copy
import argparse

# 支持的操作集合（call + 比较）
ALLOWED_OPS = {
    "const", "add", "sub", "mul", "div",
    "and", "or", "not",
    "eq", "lt", "gt", "le", "ge",
    "print",
    "jmp", "br", "ret", "call"
}

def eval_op(op, vals):
    if op == "add": return vals[0] + vals[1]
    if op == "sub": return vals[0] - vals[1]
    if op == "mul": return vals[0] * vals[1]
    if op == "div": return vals[0] // vals[1]
    if op == "and": return vals[0] and vals[1]
    if op == "or":  return vals[0] or vals[1]
    if op == "not": return not vals[0]

    # --- 新增比较支持 ---
    if op == "eq": return vals[0] == vals[1]
    if op == "lt": return vals[0] <  vals[1]
    if op == "gt": return vals[0] >  vals[1]
    if op == "le": return vals[0] <= vals[1]
    if op == "ge": return vals[0] >= vals[1]

    raise RuntimeError(f"Unsupported op in eval_op: {op}")

def run_function(fn_name, arg_vals, func_table):
    """
    执行函数 fn_name，并返回：
      (ret_val, trace_instrs)

    - 为这个函数建立一个新的 env（局部作用域）
    - 遇到 call 时递归调用 run_function（inline trace）
    """

    fn = func_table[fn_name]
    instrs = fn["instrs"]

    # label -> pc 映射
    labels = {
        ins["label"]: i
        for i, ins in enumerate(instrs)
        if "label" in ins
    }

    # 局部 env（函数栈帧）
    env = {}
    params = fn.get("args", [])
    if len(params) != len(arg_vals):
        raise RuntimeError(f"{fn_name} expects {len(params)} args, got {len(arg_vals)}")
    for p, v in zip(params, arg_vals):
        env[p["name"]] = v

    pc = 0
    trace = []

    def record(ins):
        if "label" not in ins:
            trace.append(copy.deepcopy(ins))

    while pc < len(instrs):
        ins = instrs[pc]
        if "label" in ins:
            pc += 1
            continue

        op = ins["op"]

        if op not in ALLOWED_OPS:
            raise RuntimeError(f"Unsupported op {op} in tracing")

        # 默认记录
        record(ins)

        # ===== 普通操作 =====
        if op == "const":
            env[ins["dest"]] = ins["value"]
            pc += 1
            continue

        if op in ("add","sub","mul","div",
                  "and","or","not",
                  "eq","lt","gt","le","ge"):
            dest = ins["dest"]
            args = ins.get("args", [])
            vals = [env[a] for a in args]
            env[dest] = eval_op(op, vals)
            pc += 1
            continue

        # ===== IO =====
        if op == "print":
            vals = [env[a] for a in ins.get("args",[])]
            print(*vals)
            pc += 1
            continue

        # ===== 跳转 =====
        if op == "jmp":
            tgt = ins["labels"][0]
            pc = labels[tgt]
            continue

        if op == "br":
            cond_name = ins["args"][0]
            cond_val  = env[cond_name]

            tgt = ins["labels"][0] if cond_val else ins["labels"][1]

            # 修改刚记录的 br → guard
            trace[-1] = {
                "op": "guard",
                "args": [cond_name],
                "labels": [".trace_fail"]
            }

            pc = labels[tgt]
            continue

        # ===== call inline =====
        if op == "call":
            callee = ins["funcs"][0]
            arg_names = ins.get("args", [])
            call_vals = [env[a] for a in arg_names]

            ret_val, callee_trace = run_function(callee, call_vals, func_table)

            # 替换掉刚才 record 的 call 指令
            trace.pop()
            trace.extend(callee_trace)

            # 写回返回值
            if "dest" in ins and ins["dest"] is not None:
                env[ins["dest"]] = ret_val

            pc += 1
            continue

        # ===== ret =====
        if op == "ret":
            # 删除刚记录的 ret
            trace.pop()
            args = ins.get("args", [])
            ret_val = env[args[0]] if args else None
            return ret_val, trace

        raise RuntimeError(f"Unexpected op {op}")

    return None, trace


def main():
    p = argparse.ArgumentParser()
    p.add_argument("prog")
    args = p.parse_args()

    with open(args.prog) as f:
        prog = json.load(f)

    # 构建函数表
    func_table = { fn["name"]: fn for fn in prog["functions"] }

    main_args = [3,6]

    # 调用 main
    _, trace_instrs = run_function("main", main_args, func_table)

    out = {
        "functions": [
            { "name": "trace_main", "instrs": trace_instrs }
        ]
    }

    with open("Trace.json", "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
