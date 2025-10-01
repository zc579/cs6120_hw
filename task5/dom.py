import json
import sys
from cfg import block_map, successors, add_terminators, add_entry
from form_blocks import form_blocks


def dom(bril, mode="dom"):
    for fn in bril["functions"]:
        blocks = block_map(form_blocks(fn["instrs"]))
        add_entry(blocks)
        add_terminators(blocks)
        next_map = {blk: successors(instrs[-1]) for blk, instrs in blocks.items()}

        pred_map = {k: [] for k in next_map}
        for parent, children in next_map.items():
            for child in children:
                pred_map[child].append(parent)

        visited = set()
        post_order = []

        def dfs(node):
            if node in visited:
                return
            visited.add(node)
            for nxt in next_map[node]:
                dfs(nxt)
            post_order.append(node)

        dfs(list(blocks.keys())[0])
        rev_post = list(reversed(post_order))

        doms = {n: set(rev_post) for n in next_map}

        while True:
            changed = False
            for node in rev_post:
                if pred_map[node]:
                    new_dom = set(doms[pred_map[node][0]])
                    for p in pred_map[node][1:]:
                        new_dom &= doms[p]
                else:
                    new_dom = set()
                new_dom.add(node)
                if new_dom != doms[node]:
                    doms[node] = new_dom
                    changed = True
            if not changed:
                break

        if mode == "front":

            inv_dom = {k: [] for k in doms}
            for blk, dominated_set in doms.items():
                for d in dominated_set:
                    inv_dom[d].append(blk)

            frontier = {}
            for blk in doms:
                succs_of_dom = set()
                for d in inv_dom[blk]:
                    succs_of_dom.update(next_map[d])
                frontier[blk] = [
                    b for b in succs_of_dom if b not in inv_dom[blk] or b == blk
                ]
            result = frontier

        elif mode == "tree":
            inv_dom = {k: [] for k in doms}
            for blk, dominated_set in doms.items():
                for d in dominated_set:
                    inv_dom[d].append(blk)

            strict = {k: {x for x in v if x != k} for k, v in inv_dom.items()}
            two_step = {k: set().union(*(strict[x] for x in v)) for k, v in strict.items()}
            tree = {k: {x for x in v if x not in two_step[k]} for k, v in strict.items()}
            result = tree

        else:
            result = doms

        print(json.dumps({k: sorted(list(v)) for k, v in result.items()},
                         indent=2, sort_keys=True))


if __name__ == "__main__":
    dom(json.load(sys.stdin), "dom" if len(sys.argv) < 2 else sys.argv[1])
