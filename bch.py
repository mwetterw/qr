#!/usr/bin/env python3
import math

from galois import BinaryGaloisField

class BinaryBCH:
    def __init__(self, m, k, t, g):
        self.n = 2**m - 1
        self.k = k
        self.t = t
        self.g = g
        self.gf = BinaryGaloisField(m)

    def syndrome(self, j, r):
        s = 0
        if r:
            for pos in range (0, int(math.log(r, 2)) + 1):
                if not (r >> pos) & 1:
                    continue

                alpha = self.gf.log_to_vector[(pos * j) % self.n]
                s ^= alpha
        alphas = self.gf.vector_to_log[s] if s else 0

        poly_constant = 1 if s == 1 else 0
        poly_alpha = (1 << alphas) if alphas else 0
        return poly_alpha | poly_constant

    def syndromes(self, r):
        s = [0 for j in range(2*self.t)]
        for j in range(len(s)):
            s[j] = self.syndrome(j + 1, r)
        return s

    def decode(self, r):
        s = self.syndromes(r)
        print(s)
