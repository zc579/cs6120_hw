import json
import sys
from collections import defaultdict
from cfg import block_map, successors, add_terminators, add_entry, reassemble
from form_blocks import form_blocks
from dom import get_dom, dom_fronts, dom_tree


def ssa(bril_program):

    def_blocks_map = {}
    get_insert_map = {}
    variable_types = {}
    set_instructions = {}
    get_destinations = {}
    init_values = {}
    rename_counter = defaultdict(int)
    stack_versions = defaultdict(list)

    for func in bril_program["functions"]:
        # (1) Build CFG and basic block info
        basic_blocks = block_map(form_blocks(func["instrs"]))
        add_entry(basic_blocks)
        add_terminators(basic_blocks)

        successors_map = {blk_name: successors(blk[-1]) for blk_name, blk in basic_blocks.items()}
        dominators = get_dom(successors_map, list(basic_blocks.keys())[0])
        dom_frontiers = dom_fronts(dominators, successors_map)
        domtree = dom_tree(dominators)

        # (2) Record where each variable is defined
        var_def_blocks = defaultdict(set)
        for blk_name, blk in basic_blocks.items():
            for instr in blk:
                if "dest" in instr:
                    var_def_blocks[instr["dest"]].add(blk_name)
        def_blocks_map = dict(var_def_blocks)

        # (3) Collect variable types
        var_types = {arg["name"]: arg["type"] for arg in func.get("args", [])}
        for instr in func["instrs"]:
            if "dest" in instr:
                var_types[instr["dest"]] = instr["type"]
        variable_types = var_types

        # (4) Determine where to insert get (phi) instructions
        get_insert_map = {b: set() for b in basic_blocks}
        for var, def_blocks in def_blocks_map.items():
            worklist = list(def_blocks)
            for def_block in worklist:
                for frontier_block in dom_frontiers[def_block]:
                    if var not in get_insert_map[frontier_block]:
                        get_insert_map[frontier_block].add(var)
                        if frontier_block not in worklist:
                            worklist.append(frontier_block)

        # (5) Initialize SSA rename bookkeeping
        func_args = {a["name"] for a in func.get("args", [])}
        stack_versions = defaultdict(list, {v: [v] for v in func_args})
        get_destinations = {b: {p: "" for p in get_insert_map[b]} for b in basic_blocks}
        set_instructions = {b: [] for b in basic_blocks}
        init_values = {}
        rename_counter = defaultdict(int)

        # (6) SSA rename process using explicit stack management
        visited_blocks = set()
        entry_block = list(basic_blocks.keys())[0]
        traversal_stack = [entry_block]

        # iterative DFS replacing recursive _rename
        while traversal_stack:
            current_block = traversal_stack.pop()
            if current_block in visited_blocks:
                continue
            visited_blocks.add(current_block)

            # Save old version stack to restore later
            saved_stack = {k: list(v) for k, v in stack_versions.items()}

            # --- Assign names for GET (phi) destinations ---
            for phi_var in get_insert_map[current_block]:
                new_name = f"{phi_var}.{rename_counter[phi_var]}"
                rename_counter[phi_var] += 1
                stack_versions[phi_var].insert(0, new_name)
                get_destinations[current_block][phi_var] = new_name

            # --- Rename variables inside block instructions ---
            for instr in basic_blocks[current_block]:
                # Rename argument references
                if "args" in instr:
                    renamed_args = []
                    for arg in instr["args"]:
                        if stack_versions[arg]:
                            renamed_args.append(stack_versions[arg][0])
                        else:
                            init_name = f"{arg}.init"
                            init_values[arg] = init_name
                            renamed_args.append(init_name)
                    instr["args"] = renamed_args

                # Rename destination variables
                if "dest" in instr:
                    dest_var = instr["dest"]
                    new_dest = f"{dest_var}.{rename_counter[dest_var]}"
                    rename_counter[dest_var] += 1
                    stack_versions[dest_var].insert(0, new_dest)
                    instr["dest"] = new_dest

            # --- Generate SET instructions for successors ---
            for succ_blk in successors_map[current_block]:
                for phi_var in get_insert_map[succ_blk]:
                    if stack_versions[phi_var]:
                        top_var = stack_versions[phi_var][0]
                    else:
                        init_name = f"{phi_var}.init"
                        init_values[phi_var] = init_name
                        top_var = init_name
                    set_instructions[current_block].append((succ_blk, phi_var, top_var))

            # --- Add dominated children to traversal stack ---
            for child_block in sorted(domtree[current_block]):
                traversal_stack.append(child_block)

            # --- Restore version stack after finishing this block ---
            stack_versions.clear()
            stack_versions.update(saved_stack)

        # (7) Insert SETs and GETs into actual code
        for blk_name, instrs in basic_blocks.items():
            # Add SETs before terminator
            for succ_blk, old_var, val in sorted(set_instructions[blk_name]):
                set_instr = {"op": "set", "args": [get_destinations[succ_blk][old_var], val]}
                instrs.insert(-1, set_instr)
            # Add GETs at top of block
            for old_var, new_var in sorted(get_destinations[blk_name].items()):
                get_instr = {"op": "get", "dest": new_var, "type": variable_types[old_var]}
                instrs.insert(0, get_instr)

        # (8) Insert undef initializations
        entry_instrs = next(iter(basic_blocks.values()))
        for old_var, init_var in sorted(init_values.items()):
            undef_instr = {"op": "undef", "type": variable_types[old_var], "dest": init_var}
            entry_instrs.insert(0, undef_instr)

        # (9) Reassemble final SSA instruction sequence
        func["instrs"] = reassemble(basic_blocks)

    return bril_program


if __name__ == "__main__":
    program = json.load(sys.stdin)
    ssa_program = ssa(program)
    print(json.dumps(ssa_program, indent=2, sort_keys=True))
