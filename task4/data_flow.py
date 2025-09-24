import sys
import json
from collections import namedtuple

from form_blocks import form_blocks
import cfg

def get_pred_succ(blocks):
    cfg.add_terminators(blocks)
    pred, succ=cfg.edges(blocks)
    return pred, succ

def merge_cd(out_block):
    res=set()
    for output in out_block:
        res.update(output)
    return res

def transfer_cd(block,in_block):
    out=set()
    for instr in block:
        if 'dest' in instr:
            out.add(instr['dest'])
    for var in in_block:
        out.add(var)
    out=sorted(out)
    return out
    
def currently_defined(blocks):
    pred,succ=get_pred_succ(blocks)
    in_block={list(blocks.keys())[0]:set()}
    out_block={node: set() for node in blocks}
    worklist = list(blocks.keys())
    while worklist:
        block=worklist.pop(0)
        out_pre_block=[out_block[b] for b in pred[block]]
        in_block[block]=merge_cd(out_pre_block)
        out_block_current=transfer_cd(blocks[block],in_block[block])
        if out_block_current != out_block[block]:
            out_block[block]=out_block_current
            worklist.extend(succ[block])
    for block in blocks:
        print(block,"in:",set(in_block[block]))
        print(block,"out:",set(out_block[block]))   

def merge_cp(out_block):
    out={}
    for values in out_block:
        for name,value in values.items():
            if value =="?":
                out[name] = "?"
            else:
                if name in out:
                    out[name]="?"
                else:
                    out[name]=value
    return out
def transfer_cp(block,in_block):
    out=in_block
    for instr in block:
        if 'dest' in instr : 
            if instr['op'] == "const":
                out[instr['dest']]=instr['value']
            else:
                out[instr['dest']]="?"
    return out

def const_propagation(blocks):
    pred,succ=get_pred_succ(blocks)
    in_block={list(blocks.keys())[0]:{}}
    out_block={node: {} for node in blocks}
    worklist = list(blocks.keys())
    while worklist:
        block=worklist.pop(0)
        out_pre_block=[out_block[b] for b in pred[block]]
        in_block[block]=merge_cp(out_pre_block)
        out_block_current=transfer_cp(blocks[block],in_block[block])
        if out_block_current != out_block[block]:
            out_block[block]=out_block_current
            worklist.extend(succ[block])
    for block in blocks:
        print(block,"in:",in_block[block])
        print(block,"out:",out_block[block])
        


    

bril = json.load(sys.stdin)
for func in bril["functions"]:
    blocks = cfg.block_map(form_blocks(func["instrs"]))         
    const_propagation(blocks)


