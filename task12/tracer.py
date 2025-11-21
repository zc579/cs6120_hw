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
    if op == "eq": return vals[0] == vals[1]
    if op == "lt": return vals[0] < vals[1]
    if op == "gt": return vals[0] > vals[1]
    if op == "le": return vals[0] <= vals[1]
    if op == "ge": return vals[0] >= vals[1]
    if op == "and": return vals[0] and vals[1]
    if op == "or": return vals[0] or vals[1]
    if op == "not": return not vals[0]
    raise RuntimeError(op)

def run_function(fn, func_table, args_vals):
    instrs = fn["instrs"]
    labels = {ins.get("label"): i for i, ins in enumerate(instrs) if "label" in ins}
    params = fn.get("args", [])
    env = {}
    for p, v in zip(params, args_vals):
        env[p["name"]] = v

    trace = []
    dyn = 0
    pc = 0

    while pc < len(instrs):
        ins = instrs[pc]
        if "label" in ins:
            pc += 1
            continue
        op = ins["op"]
        dyn += 1
        if op not in ("jmp","br","call"):
            trace.append(copy.deepcopy(ins))
        if op == "const":
            env[ins["dest"]] = ins["value"]
            pc += 1
        elif op in ("add","sub","mul","div","eq","lt","gt","le","ge","and","or","not"):
            vals = [env[a] for a in ins.get("args",[])]
            env[ins["dest"]] = eval_op(op, vals)
            pc += 1
        elif op == "print":
            vals = [env[a] for a in ins.get("args",[])]
            print(*vals)
            pc += 1
        elif op == "jmp":
            pc = labels[ins["labels"][0]]
        elif op == "br":
            cond = env[ins["args"][0]]
            tgt = ins["labels"][0] if cond else ins["labels"][1]
            pc = labels[tgt]
        elif op == "call":
            callee = func_table[ins["funcs"][0]]
            arg_names = ins.get("args",[])
            arg_vals = [env[a] for a in arg_names]
            ret_val, sub_trace, sub_dyn = run_function(callee, func_table, arg_vals)
            dyn += sub_dyn
            param_list = callee.get("args",[])
            init_list = []
            for p,v in zip(param_list,arg_vals):
                init_list.append({
                    "dest": p["name"],
                    "op":"const",
                    "type": p["type"],
                    "value": v
                })
            clean_sub = [t for t in sub_trace if t.get("op")!="ret"]
            trace.extend(init_list)
            trace.extend(clean_sub)
            if "dest" in ins:
                env[ins["dest"]] = ret_val
                trace.append({
                    "dest": ins["dest"],
                    "op":"const",
                    "type": ins["type"],
                    "value": ret_val
                })
            pc += 1
        elif op == "ret":
            args = ins.get("args",[])
            rv = env[args[0]] if args else None
            return rv, trace, dyn

    return None, trace, dyn

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prog")
    ap.add_argument("--arg", action="append", default=[])
    args = ap.parse_args()
    with open(args.prog) as f:
        prog = json.load(f)
    func_table = {fn["name"]:fn for fn in prog["functions"]}

    arg_dict = {}
    for a in args.arg:
        n,v = a.split("=")
        arg_dict[n]=int(v)

    main_fn = func_table["main"]
    params = main_fn.get("args",[])
    main_args = []
    for p in params:
        main_args.append(arg_dict.get(p["name"],0))

    ret, trace, dyn = run_function(main_fn, func_table, main_args)
    print(f"total_dyn_inst: {dyn}")

    if trace[-1]["op"]=="ret":
        if "args" not in trace[-1] or trace[-1]["args"]==[]:
            for ins in reversed(trace[:-1]):
                if "dest" in ins:
                    trace[-1]["args"]=[ins["dest"]]
                    break

    init_list = []
    for p,v in zip(params, main_args):
        init_list.append({
            "dest": p["name"],
            "op":"const",
            "type": p["type"],
            "value": v
        })

    out = {
        "functions":[
            {
                "name":"main",
                "args":[],
                "instrs": init_list + trace
            }
        ]
    }

    with open("Trace.json","w") as f:
        json.dump(out,f,indent=2)
    print("Trace generated.")

if __name__=="__main__":
    main()
