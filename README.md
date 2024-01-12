## Introduction

Hello, I am Minsun Kim, studying Cryptography and playing CTFs as name `soon_haari` with `CyKor` and `Super Guesser`.

I read the following papers with great interest. 
- [Forging tropical signatures](https://eprint.iacr.org/2023/1748)
- [More forging (and patching) of tropical signatures](https://eprint.iacr.org/2023/1837)

I understood multiple attacks exist for the Tropical Signature, and only the attack from `4.6 Re-hashing an honest signature` survived after patching.

I would like to propose another attack which survives every constraints from the latest verification, and yet very simple.

I downloaded the files from https://yx7.cc/files/tropical-attack.tar.gz, and added `tropical-attack/forge3.py`  which is an implementation of my attack.

Let me give you a brief explanation of my attack.

## Exploiting the fact that the result of division is not unique

`Tropical polynomial division` was explained in [More forging (and patching) of tropical signatures](https://eprint.iacr.org/2023/1837). It is pretty obvious that result of division is not unique after some tests.

$$(R \otimes S) / S \neq R$$

However, the following properties always hold.

1. $(R / S) \otimes S = R$.
2. $R \otimes S$ is always divisible by $S$, however the result is more likely not $R$.

And the division algorithm was used to check if both $S_1$ and $S_2$ are multiple of $H$. And also used during the succeeding attack.

I thought this fact was very interesting, and try to use it generating random signature that can pass the verification.

<br>

$M$ is given, and it is hard to factorize since first and last coefficient is 0, which is the smallest.

And the challenge is to generate $m, S_1, S_2, N$ which satisfies the following tests.

- $H = \textnormal{hash}(m)$
- $S_1 \otimes S_2 = M \otimes N \otimes H \otimes H$
- And some more including both $S_1, S_2$ should be divisable by $H$

I first generated random $N$ of size `(2 * d, 2 * r)`, and $m, H$ which are random message and hash of it.

And defined $S_1, S_2 = H \otimes M, H \otimes N$. This signature fails because $S_1$ is mono-multiple of $H \otimes N$, and same for $S_2$.

I will define $T = S_1 \otimes S_2 = M \otimes N \otimes H \otimes H$.

When I put value of $T / S_2$ info $S_1$, the multiplication will succeed, however the verification will fail because $S_1$ is not divisible to $H$. 

Then what will happen if $S_1 = (T / (S_2 \otimes H)) \otimes H$?

$S_1$ is divisible by $H$, but does the multiplication succeed?

$$S_1 \otimes S_2 = (T / (S_2 \otimes H)) \otimes H \otimes S_2 = T / (S_2 \otimes H) \otimes (S_2 \otimes H) = T$$

We can see that the multiplication also succeeds, and the generated $S_1$ passes all the tests on it, just $S_2$ fail.

$S_2$ can also be regenerated through the same method.

$$S_2 = (T / (S_1 \otimes H)) \otimes H$$

The regeneration of $S_1, S_2$ should be calculated sequentially, not simultaneously.

After that, the signature of $(m, S_1, S_2, N)$ successfully verfies.

This attack always succeeds for any kind of $M$, and any $m$ is allowed to use.

## Conclusion

I think the property 1 and 2 during division is very interesting. I hope to study deep about it and maybe use it in a CTF someday, 

Thanks for Reading!!