import json 
import sys
from collections import OrderedDict

TERMINATOR='jmp', 'br','ret'


def form_blocks(body):
    current_block=[]
    for instr in body:
        if 'op'in instr:
            current_block.append(instr)
            if instr['op'] in TERMINATOR: 
                yield current_block
                current_block=[]
        else :
            yield current_block
            current_block=[instr]

    yield current_block

def block_map(blocks):
    out =OrderedDict()
    for block in blocks:
        if "label" in block[0]:
            name=block[0]['label']
            block=block[1:]
        else:
            name='b{}'.format(len(out))
        out[name]=block

    return out

def get_cfg(name2block):
    #given name to block map,produce mapping to successor
    out = {}
    blocks_list = list(name2block.items())  # Convert to list for indexing
    
    for i, (name, block) in enumerate(blocks_list):
            
        last = block[-1]  # Get the last instruction
        if last['op'] in ('jmp','br') :
            succ = last['labels']
        elif last['op']=='ret':
            succ=[]
        else:
            if i ==len(name2block)-1:
                succ=[]
            else:
                succ=[list(name2block.keys())[i+1]]
        out[name]=succ
    return out


def mycfg():
        prog = json.load(sys.stdin)  
        for func in prog['functions']:
            name2block = block_map(form_blocks(func['instrs']))
            cfg=get_cfg(name2block)
            print(cfg)



if __name__ == '__main__':

    try:
        mycfg()
    except BrokenPipeError:
        # Explicitly close stdout to avoid the error message
        try:
            sys.stdout.close()
        except:
            pass
        sys.exit(0)
