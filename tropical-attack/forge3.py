#!/usr/bin/env python3
import sys, io

################################################################

stdout, sys.stdout = sys.stdout, io.StringIO()
from tropicalDS import d, r, M, m, P, pol_times_pol2, one_v_poly, hashing_to_P
s, sys.stdout = sys.stdout.getvalue(), stdout
assert s == 'True\n'

################################################################

def poly_div_pol2(R, S):
    Rn = len(R) - 1
    Sn = len(S) - 1

    q = []

    for i in range(Rn - Sn + 1):
        try:
            v = max(
                (R[i + j][0] - S[j][0]) for j in range(Sn + 1)
            )
        except:
            return None

        q.append([v, i])

    if pol_times_pol2(q, S) == R:
        return q

    return None

m = "soon_haari" * 20 # Any message can be used for a valid signature in this attack
P = hashing_to_P(m, d)
N = one_v_poly(2 * d, 2 * r)

target = pol_times_pol2(pol_times_pol2(M, P), pol_times_pol2(N, P))

S1, S2 = pol_times_pol2(M, P), pol_times_pol2(N, P)

S1 = pol_times_pol2(poly_div_pol2(target, pol_times_pol2(P, S2)), P)
S2 = pol_times_pol2(poly_div_pol2(target, pol_times_pol2(P, S1)), P)

################################################################

import tropicalDS as tDS
tDS.m = m
tDS.P = P
tDS.sig_vec = [S1, S2, N]

print('public key:')
print('   ', [c for c,_ in M])
print('message:')
print('   ', repr(m))
print('signature:')
print('   ', [c for c,_ in S1])
print('   ', [c for c,_ in S2])
print('   ', [c for c,_ in N])
print()

# check forgery
stdout, sys.stdout = sys.stdout, io.StringIO()
tDS.verification_all3()
s, sys.stdout = sys.stdout.getvalue(), stdout
if s != 'True\n':
    print(f'!! {s.strip()}')
    exit(1)

print('ok')

