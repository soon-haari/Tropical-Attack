#!/usr/bin/env python3
import sys, io

################################################################

stdout, sys.stdout = sys.stdout, io.StringIO()
from tropicalDS import d, r, M, m, P, pol_times_pol2, one_v_poly, hashing_to_P
s, sys.stdout = sys.stdout.getvalue(), stdout
assert s == 'True\n'

################################################################

import z3

blen = (5+5*r).bit_length()

def find_factor(S, deg=1):
    cs1 = z3.BitVecs([f'x1_{i}' for i in range(len(S)-deg)], blen)
    cs2 = z3.BitVecs([f'x2_{i}' for i in range(deg+1)], blen)

    z3min = lambda u,v: z3.If(u <= v, u, v)
    z3add = lambda u,v: u + v
    def z3mul(poly1, poly2):
        res = [None] * (len(poly1)+len(poly2)-1)
        for i1,c1 in enumerate(poly1):
            for i2,c2 in enumerate(poly2):
                i3 = i1 + i2
                c3 = z3add(c1, c2)
                if res[i3] is None:
                    res[i3] = c3
                else:
                    res[i3] = z3min(res[i3], c3)
                res[i3] = z3.simplify(res[i3])
        assert None not in res
        return res

    solver = z3.Solver()

    k = len(S)//d
    for v in cs1:
        solver.add(v >= 0)
        solver.add(v <= (k-1)*r)
    for v in cs2:
        solver.add(v >= 0)
        solver.add(v <= r)

    for idx,coeff in enumerate(z3mul(cs1,cs2)):
        assert S[idx][1] == idx
        solver.add(coeff == S[idx][0])

    chk = solver.check()
    if chk != z3.sat:
        return None
    sol = solver.model()

    myR = [[sol[c].as_long(),i] for i,c in enumerate(cs1)]
    myD = [[sol[c].as_long(),i] for i,c in enumerate(cs2)]
    assert pol_times_pol2(myR, myD) == S

    return myR, myD


for counter in range(100):
    if counter:
        m = f'Hello world #{counter}'
        P = hashing_to_P(m, d)
    PM = pol_times_pol2(P, M)
    if (sol1 := find_factor(PM,1)) is not None:
        break
    if (sol1 := find_factor(PM,2)) is not None:
        break
    if (sol1 := find_factor(PM,3)) is not None:
        break
    if (sol1 := find_factor(PM,4)) is not None:
        break
    if (sol1 := find_factor(PM,5)) is not None:
        break
else:
    assert False

R1,D1 = sol1

D2 = one_v_poly(len(D1)-1, r>>1)
U2 = one_v_poly(d-len(D1)+1, r>>1)
U = pol_times_pol2(U2, D2)
V = one_v_poly(d, r)
N = pol_times_pol2(U, V)
N2 = pol_times_pol2(U2, V)
R2 = pol_times_pol2(P, N2)
assert pol_times_pol2(R2, D2) == pol_times_pol2(P, N)

S1 = pol_times_pol2(R1, D2)
S2 = pol_times_pol2(R2, D1)

lhs = pol_times_pol2(S1, S2)
rhs = pol_times_pol2(pol_times_pol2(P,P), pol_times_pol2(M,N))
assert lhs == rhs

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

