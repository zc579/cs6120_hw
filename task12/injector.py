import json
import argparse

def find_main(prog):
    for f in prog["functions"]:
        if f["name"] == "main":
            return f
    return None

def load_trace_instrs(trace_prog):
    f = find_main(trace_prog)
    return f["instrs"]

def fresh_label(used, base):
    s = base
    i = 0
    while s in used:
        i+=1
        s=f"{base}_{i}"
    used.add(s)
    return s

def inject_trace(orig, trace):
    main = find_main(orig)
    orig_instrs = main["instrs"]

    used_labels = {i["label"] for i in orig_instrs if "label" in i}
    used_labels.add("__trace_fail")
    fast_label = fresh_label(used_labels,"__fast")

    new = []
    new.append({"label": fast_label})
    new.append({"op":"speculate"})
    new.append({"op":"guard","args":[True],"labels":["__trace_fail"]})

    for ins in trace[:-1]:
        new.append(ins)

    new.append({"op":"commit"})
    new.append(trace[-1])

    new.append({"label":"__trace_fail"})
    new.extend(orig_instrs)

    main["instrs"] = new
    return orig

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("orig")
    ap.add_argument("trace")
    ap.add_argument("-o","--out",default="gpf_opt.json")
    args = ap.parse_args()

    with open(args.orig) as f:
        orig=json.load(f)
    with open(args.trace) as f:
        trace=json.load(f)

    trace_instrs = load_trace_instrs(trace)
    new_prog = inject_trace(orig, trace_instrs)

    with open(args.out,"w") as f:
        json.dump(new_prog,f,indent=2)

    print("optimized program written to",args.out)

if __name__=="__main__":
    main()
