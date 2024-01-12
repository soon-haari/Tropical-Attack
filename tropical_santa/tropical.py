from hashlib import sha512
import os


def randint(a, b):
    blen = int(b - a).bit_length()
    bytelen = (blen + 7) // 8

    v = int.from_bytes(os.urandom(bytelen), "little")
    return (v % (b - a + 1)) + a


class Elem:
    def __init__(self, v: int | None):
        self.v = v

    def is_inf(self):
        return self.v is None

    def is_zero(self):
        return self.v == 0

    def copy(self):
        return Elem(self.v)

    def __str__(self):
        if self.v is not None:
            return str(self.v)
        else:
            return "Inf"

    __repr__ = __str__

    def __add__(self, other):
        if self.is_inf():
            return other.copy()
        elif other.is_inf():
            return self.copy()
        else:
            return Elem(min(self.v, other.v))

    __radd__ = __add__

    def __mul__(self, other):
        if self.is_inf() or other.is_inf():
            return Elem.Inf
        else:
            return Elem(self.v + other.v)

    __rmul__ = __mul__

    def __eq__(self, other):
        if type(other) == int:
            return self.v == other
        return self.v == other.v

    def __truediv__(self, other):
        if other.is_inf():
            raise ZeroDivisionError
        elif self.is_inf():
            return Elem.Inf
        else:
            return Elem(self.v - other.v)

    def in_range(self, a, b):
        return not self.is_inf() and a <= self.v <= b

    @classmethod
    @property
    def Inf(cls):
        return cls(None)


class Polynomial:
    def __init__(self, coefs: list[Elem]):
        assert all(type(v) == Elem for v in coefs)
        self.coefs = coefs
        self.n = len(coefs) - 1

    @classmethod
    def random(cls, r: int, d: int, trailing_zero=False):
        coefs = [Elem(randint(0, r)) for _ in range(d + 1)]
        if trailing_zero:
            coefs[0].v = 0
            coefs[-1].v = 0
        return cls(coefs)

    @classmethod
    def hash_message(cls, m: bytes, r: int, d: int):
        hsh = sha512(m).digest()

        total_bits = r.bit_length() * (d + 1)
        required_mults = (total_bits + 127) // 128
        hash_int = int.from_bytes(hsh * required_mults, "little")

        coefs = []
        for _ in range(d + 1):
            coefs.append(Elem(hash_int % (r + 1)))
            hash_int //= r + 1

        return cls(coefs)

    def __getitem__(self, idx: int):
        if idx > self.n:
            return Elem.Inf
        return self.coefs[idx]

    def __str__(self):
        return "Polynomial(" + " ".join(map(str, self.coefs)) + ")"

    __repr__ = __str__

    def __add__(self, other):
        if type(other) is Elem:
            coefs = self.coefs[:]
            coefs[0] = coefs[0] + other
            return Polynomial(coefs)

        coefs = [self[i] + other[i] for i in range(max(self.n, other.n) + 1)]
        return Polynomial(coefs)

    __radd__ = __add__

    def __mul__(self, other):
        if type(other) is Elem:
            coefs = [other * v for v in self.coefs]
            return Polynomial(coefs)

        coefs = [Elem.Inf for _ in range(self.n + other.n + 1)]

        for i in range(self.n + 1):
            for j in range(other.n + 1):
                coefs[i + j] += self[i] * other[j]

        return Polynomial(coefs)

    __rmul__ = __mul__

    def __eq__(self, other):
        return self.n == other.n and all(
            x == y for x, y in zip(self.coefs, other.coefs)
        )

    def __truediv__(self, other):
        q_coefs = []
        for i in range(self.n - other.n + 1):
            try:
                v = max(
                    (self.coefs[i + j] / other.coefs[j]).v for j in range(other.n + 1)
                )
            except TypeError:
                v = None
            q_coefs.append(Elem(v))

        q = Polynomial(q_coefs)

        if self == other * q:
            return q
        return None

    def check_constant_multiple(self, other) -> bool:
        if self.n != other.n:
            return False

        mult = None
        for i in range(self.n + 1):
            try:
                if mult is None:
                    mult = other.coefs[i] / self.coefs[i]
                elif mult != other.coefs[i] / self.coefs[i]:
                    return False
            except ZeroDivisionError:
                return False

        return True


class PublicKey:
    def __init__(self, r, d, M):
        self.r, self.d, self.M = r, d, M

    @classmethod
    def from_private_key(cls, privkey):
        return cls(privkey.r, privkey.d, privkey.M)

    def __str__(self):
        return f"PublicKey(r={self.r}, d={self.d}, M={self.M})"

    def verify(self, m: bytes, signature: tuple[Polynomial]) -> bool:
        H_ = Polynomial.hash_message(m, self.r, self.d)
        H, A, B, N = signature

        if H != H_:
            return False

        if A.n != 3 * self.d or not all(c.in_range(0, 3 * self.r) for c in A.coefs):
            return False

        if B.n != 3 * self.d or not all(c.in_range(0, 3 * self.r) for c in B.coefs):
            return False

        if N.n != 2 * self.d or not all(c.in_range(0, 2 * self.r) for c in N.coefs):
            return False

        if A * B != H * H * self.M * N:
            return False

        HM, HN = H * self.M, H * N
        if HM.check_constant_multiple(A) or HM.check_constant_multiple(B):
            return False
        if HN.check_constant_multiple(A) or HN.check_constant_multiple(B):
            return False

        if (A / H) is None or (B / H) is None:
            return False
        if (A / self.M) is not None or (B / self.M) is not None:
            return False
        if (A / N) is not None or (B / N) is not None:
            return False

        return True


class PrivateKey:
    def __init__(self, r=127, d=150):
        self.r, self.d = r, d
        self.X, self.Y = [
            Polynomial.random(self.r, self.d, trailing_zero=True) for _ in range(2)
        ]
        self.M = self.X * self.Y
        self.pubkey = PublicKey(self.r, self.d, self.M)

    @classmethod
    def gen_key_pair(cls, r=127, d=150):
        privkey = cls(r, d)
        return privkey, privkey.pubkey

    def sign(self, m: bytes) -> tuple[Polynomial]:
        H = Polynomial.hash_message(m, self.r, self.d)
        U, V = [Polynomial.random(self.r, self.d) for _ in range(2)]

        A = H * self.X * U
        B = H * self.Y * V
        N = U * V

        return (H, A, B, N)

    def verify(self, m: bytes, signature: tuple[Polynomial]) -> bool:
        return self.pubkey.verify(m, signature)
