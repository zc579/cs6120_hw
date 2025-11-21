#!/usr/bin/env python3
import json
import copy
import argparse

SUPPORTED_OPS = {
    "const", "add", "sub", "mul", "div",
    "eq", "lt", "gt", "le", "ge",
    "and", "or", "not",
    "print",
    "jmp", "br", "call", "ret"
}

def eval_op(op, vals):
    if op == "add": return vals[0] + vals[1]
    if op == "sub": return vals[0] - vals[1]
    if op == "mul": return vals[0] * vals[1]
    if op == "div": return vals[0] // vals[1]
    if op == "eq":  return vals[0] == vals[1]
    if op == "lt":  return vals[0] <  vals[1]
    if op == "gt":  return vals[0] >  vals[1]
    if op == "le":  return vals[0] <= vals[1]
    if op == "ge":  return vals[0] >= vals[1]
    if op == "and": return vals[0] and vals[1]
    if op == "or":  return vals[0] or vals[1]
    if op == "not": return not vals[0]
    raise RuntimeError(f"Unsupported op: {op}")

def run_function(fn, func_table, args_vals):
    instrs = fn["instrs"]
    labels = {ins["label"]: i for i, ins in enumerate(instrs) if "label" in ins}

    env = {}
    params = fn.get("args", [])
    if len(params) != len(args_vals):
        raise RuntimeError(f"{fn['name']} expects {len(params)} args, got {len(args_vals)}")

    for p, v in zip(params, args_vals):
        env[p["name"]] = v

    trace = []
    dyn_count = 0
    pc = 0

    while pc < len(instrs):
        ins = instrs[pc]

        if "label" in ins:
            pc += 1
            continue

        op = ins["op"]

        if op not in SUPPORTED_OPS:
            raise RuntimeError(f"Unsupported op in trace: {op}")

        dyn_count += 1   # count dynamic instruction

        # record into trace (excluding control-flow instructions)
        if op not in ("jmp", "br", "call"):
            trace.append(copy.deepcopy(ins))

        # === execution ===
        if op == "const":
            env[ins["dest"]] = ins["value"]
            pc += 1

        elif op in ("add","sub","mul","div",
                    "eq","lt","gt","le","ge",
                    "and","or","not"):
            vals = [env[a] for a in ins.get("args",[])]
            env[ins["dest"]] = eval_op(op, vals)
            pc += 1

        elif op == "print":
            vals = [env[a] for a in ins.get("args",[])]
            print(*vals)
            pc += 1

        elif op == "jmp":
            tgt = ins["labels"][0]
            pc = labels[tgt]

        elif op == "br":
            cond = env[ins["args"][0]]
            tgt = ins["labels"][0] if cond else ins["labels"][1]
            pc = labels[tgt]

        elif op == "call":
            callee = func_table[ins["funcs"][0]]
            call_args = [env[a] for a in ins.get("args",[])]
            ret_val, sub_trace, sub_count = run_function(callee, func_table, call_args)
            trace.extend(sub_trace)
            dyn_count += sub_count
            if "dest" in ins:
                env[ins["dest"]] = ret_val
            pc += 1

        elif op == "ret":
            args = ins.get("args", [])
            ret_val = env[args[0]] if args else None
            return ret_val, trace, dyn_count

    return None, trace, dyn_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prog")
    parser.add_argument("--arg", action="append", default=[])
    args = parser.parse_args()

    with open(args.prog) as f:
        prog = json.load(f)

    func_table = {fn["name"]: fn for fn in prog["functions"]}

    # parse CLI args
    arg_dict = {}
    for a in args.arg:
        name, val = a.split("=")
        arg_dict[name] = int(val)

    main_fn = func_table["main"]
    main_params = main_fn.get("args", [])

    main_args = []
    for p in main_params:
        name = p["name"]
        main_args.append(arg_dict.get(name, 0))

    # === run program + trace ===
    ret, trace, dyn_count = run_function(main_fn, func_table, main_args)

    # === output count ===
    print(f"total_dyn_inst: {dyn_count}")

    # === make executable trace ===
    main_args_decl = main_fn.get("args", [])
    
    trace.append({"op": "ret"})
    out = {
        "functions": [
            {
                "name": "main",
                "args": main_args_decl,
                "instrs": trace
            }
        ]
    }

    with open("Trace.json","w") as f:
        json.dump(out, f, indent=2)

    print("Trace generated.")


if __name__ == "__main__":
    main()
