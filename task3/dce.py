import json
import sys

def myfunc():
    #read json file
    prog=json.load(sys.stdin)

    #find reassign, assume one function in one block
    for func in prog['functions']:
        last_def={}
        instrs=func['instrs']
        for instr in instrs:
            #check for use
            if 'args' in instr:
                for arg in instr['args']:
                    if arg in last_def:
                        last_def.pop(instr['args'])
            #check for defination
            if 'dest'in instr and instr['dest'] in last_def:
                instrs.remove(last_def[instr['dest']])
            last_def[instr['dest']]=instr
        print(instrs)

    #find redundancy
    for func in prog['functions']:
        instrs=func['instrs']
        need_next=1
        while(need_next==1):
            used=[]
            need_next=0
            for instr in instrs:
                if 'args' in instr:
                    used+=instr['args']
        
        #find dead code 
            for instr in instrs:
                if 'dest' in instr and instr['dest'] not in used:
                    instrs.remove(instr)
                    need_next=1
        print(instrs)
        

if __name__ == "__main__":
    try:
        myfunc()
    except BrokenPipeError:
        sys.stderr.close()
        sys.exit(0)