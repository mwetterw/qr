from functools import reduce

# As this module is essentially dealing with pure mathematics, let's allow
# ourselves to use variables of one character length, like "x", "y", etc.
# The variable names shouldn't have a big importance (because of the mathematical abstraction)
# pylint: disable=invalid-name

class BinaryGaloisField:
    """Represent a Binary Galois Field

    This class implements Binary Galois Fields. Therefore, the characteristic
    of the field, always equals 2 (we only support GF(2^m), the Galois field
    extensions of GF(2)).
    It allows us to do computations in that algebraic structure.
    """

    # Primitive polynomials for GF(2^(idx+3))
    PRIMITIVE_POLY = [
            0b1011,
            0b10011,
            0b100101,
            0b1000011,
            0b10001001,
            0b100011101,
            0b1000010001,
            0b10000001001,
            0b100000000101,
            0b1000001010011
    ]

    M_MIN, M_MAX = (3, len(PRIMITIVE_POLY) + 2)

    LOG_TO_VECTOR_TABLES = [[]] * len(PRIMITIVE_POLY)
    VECTOR_TO_LOG_TABLES = [[]] * len(PRIMITIVE_POLY)

    def __init__(self, m):
        if m < self.M_MIN:
            raise ValueError(f"The exponent m must be greater or equal to {self.M_MIN}")
        if m > self.M_MAX:
            raise ValueError(f"Exponent m greater than {self.M_MAX} are not supported")

        self.m = m
        self.n = 2**m - 1

        # Only generate table if it doesn't already exist
        # And then always make the dynamic instance table point to the static
        # pre-computed one as syntactic sugar
        if not self.LOG_TO_VECTOR_TABLES[m - self.M_MIN]:
            self.LOG_TO_VECTOR_TABLES[m - self.M_MIN] = self.generate_log_to_vector()
        self.log_to_vector = self.LOG_TO_VECTOR_TABLES[m - self.M_MIN]

        if not self.VECTOR_TO_LOG_TABLES[m - self.M_MIN]:
            self.VECTOR_TO_LOG_TABLES[m - self.M_MIN] = self.generate_vector_to_log()
        self.vector_to_log = self.VECTOR_TO_LOG_TABLES[m - self.M_MIN]


    def generate_log_to_vector(self):
        m = self.m
        log_to_vector = [2**i for i in range(0, m)] + [-1] * (2**m - 1 - m)
        primitive_poly = self.PRIMITIVE_POLY[m-self.M_MIN]

        log_to_vector[m] = (1 << m) ^ primitive_poly

        for i in range(m+1, len(log_to_vector)):
            vector = log_to_vector[i-1] << 1

            # If m bit is set, we need to simplify that alpha^m into a combination of lower alphas
            if vector & (1 << m):
                # Replace alpha^m by its simplification
                vector ^= (1 << m)
                vector ^= log_to_vector[m]
            # Store the result in our table
            log_to_vector[i] = vector
        return log_to_vector

    def generate_vector_to_log(self):
        vector_to_log = [-1] * (2**self.m)
        for idx, value in enumerate(self.log_to_vector):
            vector_to_log[value] = idx

        return vector_to_log

    # Note that gf_add and gf_sub are both the same as a XOR (^ operator)

    @staticmethod
    def gf_sum(list_to_sum):
        """Implement the summation of GF(2^m) numbers"""

        return reduce(lambda x, y: x ^ y, list_to_sum, 0)

    def gf_mul(self, x, y):
        """Multiply 2 GF(2^m) number together

        To multiply 2 GF number, we can convert it to alpha notation and add their powers together.
        Finally, we convert it back to the vector notation
        """
        if not x or not y:
            return 0

        exponent = (self.vector_to_log[x] + self.vector_to_log[y]) % self.n
        return self.log_to_vector[exponent]

    def gf_div(self, x, y):
        """Divide 2 GF(2^m) number together

        To divide 2 GF numbers, we convert them to alpha notation and substract their powers.
        But we cannot have negative powers, and power need to be between [0, self.n[
        Then, we convert it back to the vector notation
        """
        if not y:
            raise ZeroDivisionError()
        if not x:
            return 0

        exponent = (self.vector_to_log[x] + self.n  - self.vector_to_log[y]) % self.n
        return self.log_to_vector[exponent]

    def gf_pow(self, x, power):
        """Compute the power of a GF(2^m) number

        To compute the power of a GF number, we convert it to alpha notation
        and multiply its power with the power of the function call.
        Again, the resulting power has to stay within [0, self.n].
        Then we convert it back to the vector notation.
        """

        if not x and power:
            return 0

        return self.log_to_vector[(self.vector_to_log[x] * power) % self.n]

    def gf_inv(self, x):
        """Compute the inverse of a GF(2^m) number

        To compute the inverse of a GF number, we convert it to alpha notation.
        Then, we subtract the cardinality of the Galois Field from that alpha
        power.
        Finally, we convert it back to the vector notation.
        This is equivalent to calling gf_div(1, x)
        """

        if not x:
            raise ZeroDivisionError()

        return self.log_to_vector[(self.n - self.vector_to_log[x]) % self.n]

    def gf_poly_scale(self, poly, x):
        """Multiply (in GF(2^m)) a polynomial with a constant"""

        res_poly = [0] * len(poly)

        for idx, coeff in enumerate(poly):
            res_poly[idx] = self.gf_mul(x, coeff)

        return res_poly

    @staticmethod
    def gf_poly_add(poly1, poly2):
        """Add 2 GF(2^m) polynomials"""

        res_poly = [0] * max(len(poly1), len(poly2))

        for idx, val in enumerate(poly1):
            res_poly[idx] = val

        for idx, val in enumerate(poly2):
            res_poly[idx] ^= val

        return res_poly

    def gf_poly_mul(self, poly1, poly2):
        """Multiply 2 GF(2^m) polynomials"""

        res_poly = [0] * (len(poly1) + len(poly2) - 1)

        for deg1, coeff1 in enumerate(poly1):
            for deg2, coeff2 in enumerate(poly2):
                res_poly[deg1 + deg2] ^= self.gf_mul(coeff1, coeff2)

        return res_poly

    def gf_poly_eval(self, poly, x):
        """Evaluate a polynomial at a particular value x"""

        res = poly[-1]
        for idx in range(len(poly) - 2, -1, -1):
            res = self.gf_mul(res, x) ^ poly[idx]

        return res
