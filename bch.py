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

    def berlekamp_massey(self, syndromes):
        """Implements the Berlekamp-Massey algorithm

        This algo is used to compute sigma(x), the error locator polynomial.
        The inverse-roots of this polynomial give us the location of the errors.
        """

        sigma = [1] # Current error locator polynomial called sigma(x)
        sigma_old = sigma # Previous sigma

        lfsr_len = 0 # Current length of the LFSR
        discrep_old = 1 # Previous discrepency
        l = 1 # Amount of shift in update (syndnum - m)

        for syndnum in range(1, len(syndromes) + 1):
            # Compute discrepency
            sum_ = 0
            [sum_ := sum_ ^ self.gf.gf_mul(sigma[i], syndromes[syndnum - i - 1]) for i in range(1, lfsr_len + 1)]
            discrep = syndromes[syndnum - 1] ^ sum_

            # No change in polynomial
            if not discrep:
                l = l + 1
                continue

            # Change in polynomial

            sigma_backup = sigma
            coeff = self.gf.gf_mul(discrep, self.gf.gf_inv(discrep_old))
            coeff_x_l = [0] * l + [coeff] # Create a polynomial of degree l equaling to coeff*X^l
            sigma = self.gf.gf_poly_add(sigma, self.gf.gf_poly_mul(coeff_x_l, sigma_old))

            # No-length change in update
            if 2 * lfsr_len >= syndnum:
                l = l + 1
                continue

            # Update with length change
            lfsr_len = syndnum - lfsr_len
            sigma_old = sigma_backup
            discrep_old = discrep
            l = 1
        return sigma

    def decode(self, r):
        s = self.syndromes(r)
        print(s)
