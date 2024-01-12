#!/usr/bin/env python3
import sys, io

################################################################

stdout, sys.stdout = sys.stdout, io.StringIO()
from tropicalDS import d, r, M, P, pol_times_pol2, one_v_poly
s, sys.stdout = sys.stdout.getvalue(), stdout
assert s == 'True\n'

################################################################

import copy, itertools
PM = pol_times_pol2(P, M)

while True:
    U = one_v_poly(d, r)
    V = one_v_poly(d, r)
    N = pol_times_pol2(U, V)
    PN = pol_times_pol2(P, N)

    rhs = pol_times_pol2(PM, PN)

    for s,i in itertools.product((+1,-1), range(len(PM))):
        S1 = copy.deepcopy(PM)
        S1[i][0] += s
        if pol_times_pol2(S1, PN) == rhs:
            break
    else:
        continue

    for s,i in itertools.product((+1,-1), range(len(PN))):
        S2 = copy.deepcopy(PN)
        S2[i][0] += s
        if pol_times_pol2(S1, S2) == rhs:
            break
    else:
        continue

    break
else:
    assert False

################################################################

import tropicalDS as tDS
tDS.sig_vec = [S1, S2, N]

print('public key:')
print('   ', [c for c,_ in M])
print('message:')
print('   ', repr(tDS.m))
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

