# Misc - Calculator
>Author: Wong Chee Hong

Calculator is a pretty straight-forward challenge. Upon entering the challenge, we are greeted with the following:

```
$ nc challs.nusgreyhats.org 15521

           __________
         .'----------`.
         | .--------. |
         | |########| |       __________
         | |########| |      /__________\
.--------| `--------' |------|    --=-- |-------------. 
|        `----,-.-----'      |o ======  |             | 
|       ______|_|_______     |__________|             | 
|      /  %%%%%%%%%%%%  \                             | 
|     /  %%%%%%%%%%%%%%  \                            | 
|     ^^^^^^^^^^^^^^^^^^^^                            | 
+-----------------------------------------------------+ 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 

How fast are you on calculating basic math expression?
Answer 100 math questions in 30 seconds to the flag

Operations include:
1. add x y -> returns x + y
2. mul x y -> returns x * y
3. sub x y -> returns x - y
4. neg x -> returns -x
5. inc x -> returns x + 1

Example1: mul add 1 2 sub 5 1
Ans1: (1 + 2) * (5 - 1) = 12

Example2: add mul sub 3 2 inc 5 3
Ans2: (3 - 2) * (5 + 1) + 3 = 9

Send START when you are ready!
```

The challenger will be required to answer 100 math questions correctly with the 5 specified operations `add`, `mul`, `sub`, `neg` and `inc` within 30 seconds, and they are given in prefix notation.

Obviously, this is impossible to do manually, and the challenge tests us on being able to communicate with the socket exposed on port `15521` programatically, as well as being able to perform prefix evaluation. 

A stack data structure can be used to perform prefix evaluation, and socket programming can be used to communicate with the challenge server. Alternatively, libraries such as `pwntools` also offer some abstractions for socket programming, which offers slightly more convenience.

Code for this challenge is shown below:

```python
from pwn import *

binary_commands = ["add", "mul", "sub"]
mono_commands = ["neg", "inc"]

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush() 


def prefix_eval(lines):
    args = lines.split()
    args.reverse()
    # print(args)
    stack = []

    for i in args:
        if (i not in mono_commands and i not in binary_commands):
            stack.append( int(i) )
        elif (i in binary_commands):
            arg1 = stack.pop()
            arg2 = stack.pop()
            result = eval_binary_func(i, arg1, arg2)
            stack.append(result)
        elif (i in mono_commands):
            arg = stack.pop()
            result = eval_mono_func(i, arg)
            stack.append(result)

    return stack.pop()

def eval_mono_func(operation, operand):
    if (operation == "neg"):
        return -1 * operand
    elif (operation == "inc"):
        return operand + 1
    else:
        raise "UNKNOWN OPERATION: {0}".format(operation)

def eval_binary_func(operation, operand1, operand2):
    if (operation == "add"):
        return operand1 + operand2
    elif (operation == "sub"):
        return operand1 - operand2
    elif (operation == "mul"):
        return operand1 * operand2
    else:
        raise "UNKNOWN OPERATION: {0}".format(operation)

def main(): 
    url = "challs.nusgreyhats.org"
    port = 15521

    conn = remote(url, port)

    msg_buffer = ''

    while (True):
        line = conn.recvline().decode()
        msg_buffer += line
        if 'START' in line:
            break

    print(msg_buffer)
    msg_buffer = ''
    conn.send(b'START\n')
    start(conn)

def start(conn):
    for i in range(100):
        qn = conn.recvline().decode()
        answer = prefix_eval(qn)
        conn.send(bytes(str(answer), "utf-8") + b'\n')
        outcome = conn.recvline().decode()  #skip the blank line
        
        #simple progress bar, optional
        if i == 99:
            progress(i + 1, 100, "Done!     ")
            print("\n")
        else :
            progress(i + 1, 100, "hacking")

    #receive remaining messages and print them
    line = conn.recvline().decode()
    line += conn.recvline().decode()
    print(line)

if __name__ == "__main__":
    main()
```