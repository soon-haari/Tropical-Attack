from pwn import *
from tropical import *
from tqdm import trange
import string
import hashlib
import time

io = process(["python3", "task.py"])
# io = remote("host3.dreamhack.games", 15025)

def polyrecv():
	io.recvuntil(b"Polynomial(")
	res = list(map(int, io.recvuntil(b")")[:-1].decode().split()))
	res = list(map(Elem, res))

	return Polynomial(res)

def PoW():
	CHARSET = string.ascii_letters + string.digits

	io.recvuntil(b"+ ")
	sfx = io.recvuntil(b" ")[:-1]
	assert len(sfx) == 16
	io.recvuntil(b"= ")
	hsh = bytes.fromhex(io.recvline().decode())

	for pfx_int in trange(62**4):
		pfx = ""
		for _ in range(4):
			pfx += CHARSET[pfx_int % 62]
			pfx_int //= 62

		pfx = pfx.encode()

		if hashlib.sha256(pfx + sfx).digest() == hsh:
			break

	io.sendlineafter(b"> ", pfx)


PoW()

for _ in trange(10):
	M, H, A, B, N = [polyrecv() for i in range(5)]

	io.recvuntil(b"message ")
	msg = bytes.fromhex(io.recvuntil(b".\n")[:-2].decode())

	r, d = 127, 150

	mymsg = b"soon_haari"

	myH = Polynomial.hash_message(mymsg, r, d)
	myN = Polynomial.random(2 * r, 2 * d)
	myA = myH * myN
	myB = myH * M

	target = myA * myB

	myA = (target / (myB * myH)) * myH
	myB = (target / (myA * myH)) * myH
	
	assert PublicKey(r, d, M).verify(mymsg, [myH, myA, myB, myN])

	io.sendline(bytes.hex(mymsg).encode())
	io.sendline(str(myH)[11:-1].encode())
	io.sendline(str(myA)[11:-1].encode())
	io.sendline(str(myB)[11:-1].encode())
	io.sendline(str(myN)[11:-1].encode())

	io.recvuntil(b"verifying...\n")


io.interactive()