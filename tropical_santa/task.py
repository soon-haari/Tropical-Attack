#!/usr/bin/env python3

from tropical import *
import hashlib
import itertools
import os
import random
import signal
import string


def handler(_signum, _frame):
    print("Time out!")
    exit(1)


def PoW():
    random.seed(os.urandom(10))
    CHARSET = string.ascii_letters + string.digits
    to_digest = "".join(random.sample(CHARSET, 20))
    result = hashlib.sha256(to_digest.encode()).hexdigest()

    print(f"SHA-256( XXXX + {to_digest[4:]} ) = {result}")
    user_input = input("What is the answer? > ").strip()

    return user_input == to_digest[:4]


def main():
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(60)
    if not PoW():
        print("PoW failed.")
        exit(1)

    print("Welcome!")

    for stage in range(10):
        signal.alarm(5)

        print(f"=== [STAGE {stage + 1}] ===")
        privkey, pubkey = PrivateKey.gen_key_pair()
        msg = os.urandom(16)
        signature = privkey.sign(msg)

        print(f"Here is a public key: {pubkey},")
        print(f"and this is the signature: {signature}")
        print(f"for a message {msg.hex()}.")

        user_msg = bytes.fromhex(input("Give me your message > ").strip())
        if user_msg == msg:
            print(">:(")
            exit(1)

        print("Give me your signature: ")
        sig1 = Polynomial([Elem(int(v)) for v in input("1 > ").strip().split()])
        sig2 = Polynomial([Elem(int(v)) for v in input("2 > ").strip().split()])
        sig3 = Polynomial([Elem(int(v)) for v in input("3 > ").strip().split()])
        sig4 = Polynomial([Elem(int(v)) for v in input("4 > ").strip().split()])
        user_sig = (sig1, sig2, sig3, sig4)

        print("Now verifying...")
        if not pubkey.verify(user_msg, user_sig):
            print(":(")
            exit(1)

    with open("./flag", "r") as f:
        print("Congratz.")
        print(f"Flag is: {f.read()}")


if __name__ == "__main__":
    main()
