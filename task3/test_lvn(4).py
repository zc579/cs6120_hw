import json
import sys
from collections import namedtuple

from form_blocks import form_blocks
from util import flatten

Value = namedtuple("Value", ["op", "args"])

class Numbering(dict):

    def __init__(self, init={}):
        super(Numbering, self).__init__(init)
        self._next_fresh = 0

    def add(self, key):
        n = self._next_fresh
        self[key] = n
        self._next_fresh = n + 1
        return n

def if_overwritten(instrs):
    size=len(instrs)
    exist=set()
    res=[0]*size
    index=size-1
    for instr in instrs[::-1]:
        if 'dest' in instr and instr['dest'] not in exist:
            exist.add(instr['dest'])
            res[index]=1
        index-=1
    return res

def if_external(instrs):
    res=set()
    dests=set()
    for instr in instrs:
        if 'args' in instr :
            res.update(set(instr['args'])-dests)
        if 'dest' in instr:
            dests.add(instr['dest'])
    return res

def lvn(block):
    var2num=Numbering()
    num2var={}
    value2num={}
    res=if_overwritten(block)

    for var in if_external(block):
        num=var2num.add(var)
        num2var[num]=[var]

    index=0
    for instr in block:
        args=instr.get('args',[])
        nums_arg=tuple(var2num[var] for var in args)
        val=None

        if 'args' in instr:
            instr['args']=[num2var[num1][0] for num1 in nums_arg]
        if 'dest' in instr:
            for rhs in num2var.values():
                if instr["dest"] in rhs:
                    rhs.remove(instr["dest"])

        if "dest" in instr and "args" in instr and instr["op"] != "call":
            if instr['op'] == 'id' and len(nums_arg) == 1:
                var2num[instr['dest']] = nums_arg[0]
                num2var[nums_arg[0]].append(instr['dest'])
                continue
            
            if instr['op'] in ['add', 'mul']:
                val = Value(instr['op'], tuple(sorted(nums_arg)))
            else:
                val = Value(instr['op'], tuple(nums_arg))
            
            num = value2num.get(val)
            if num is not None:
                var2num[instr['dest']] = num
                instr['op'] = 'id'
                instr['args'] = [num2var[num][0]]
                num2var[num].append(instr['dest'])
                continue

        if 'dest' in instr:
            update_num=var2num.add(instr['dest'])

            res_temp=res[index]
            if not res_temp:
                var = "temp{}".format(update_num)
            else:
                var = instr['dest']
            num2var[update_num]=[var]
            instr['dest']=var

            if val is not None:
                value2num[val]=update_num

        index+=1
def start(bril):
    for func in bril["functions"]:
        blocks = list(form_blocks(func["instrs"]))
        for block in blocks:
            lvn(block)
        func["instrs"] = flatten(blocks)

if __name__ == "__main__":
    bril = json.load(sys.stdin)
    start(bril)
    json.dump(bril, sys.stdout, indent=2, sort_keys=True)



