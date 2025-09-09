import json
import sys

def myfunc():
    const_num=0
    add_num=0
    prog=json.load(sys.stdin)
    #print(prog)

    for func in prog['functions']:
        #print(func['instrs'])

        for instr in func['instrs']:
            if instr['op'] == 'const':
                const_num+=1
            elif instr['op'] == 'add':
                add_num+=1
    print(const_num,add_num)




if __name__ == "__main__":
    try:
        myfunc()
    except BrokenPipeError:
        sys.stderr.close()
        sys.exit(0)
