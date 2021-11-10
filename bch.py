#!/usr/bin/env python3
from galois import BinaryGaloisField

class BchDecodingFailure(Exception):
    pass

class BCH:
    """t-errors correcting Primitive Narrow-sense BCH (2^m - 1, k)"""

    def __init__(self, m, k, t, g):
        self.n = 2**m - 1
        self.k = k
        self.t = t
        self.g = g
        self.gf = BinaryGaloisField(m)

    def binary_to_list(self, n):
        return list(reversed([1 if digit=='1' else 0 for digit in bin(n)[2:]]))

    def list_to_binary(self, l):
        return int(''.join(map(str, l)), 2)

    def syndrome(self, j, r):
        poly = self.binary_to_list(r)
        return self.gf.gf_poly_eval(poly, self.gf.gf_pow(2, j))

    def syndromes(self, r):
        s = [0] * (2 * self.t)

        for j in range(len(s)):
            s[j] = self.syndrome(j + 1, r)
        return s

    def decode(self, r):
        s = self.syndromes(r)
        print(s)
