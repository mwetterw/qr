from ec.galois import BinaryGaloisField

GF8 = BinaryGaloisField(3)
GF16 = BinaryGaloisField(4)
GF256 = BinaryGaloisField(8)

class TestBinaryGaloisFieldTables:
    def test_tables_gf8(self):
        GF8_LOG_TO_VECTOR=[1,2,4,3,6,7,5]
        GF8_VECTOR_TO_LOG=[-1,0,1,3,2,6,4,5]

        assert GF8.log_to_vector == GF8_LOG_TO_VECTOR
        assert GF8.vector_to_log == GF8_VECTOR_TO_LOG

    def test_tables_gf16(self):
        GF16_LOG_TO_VECTOR=[1,2,4,8,3,6,12,11,5,10,7,14,15,13,9]
        GF16_VECTOR_TO_LOG=[-1,0,1,4,2,8,5,10,3,14,9,7,6,13,11,12]

        assert GF16.log_to_vector == GF16_LOG_TO_VECTOR
        assert GF16.vector_to_log == GF16_VECTOR_TO_LOG


class TestBinaryGaloisFieldMult:
    def test_gf_mult_gf16(self):
        assert GF16.gf_mul(0, 0) == 0
        assert GF16.gf_mul(8, 0) == 0
        assert GF16.gf_mul(0, 8) == 0

        assert GF16.gf_mul(1, 1) == 1
        assert GF16.gf_mul(2, 2) == 4
        assert GF16.gf_mul(2, 3) == 6
        assert GF16.gf_mul(8, 1) == 8

        assert GF16.gf_mul(8, 2) == 3
        assert GF16.gf_mul(3, 7) == 9
        assert GF16.gf_mul(13, 14) == 10

    def test_gf_mult_gf256(self):
        assert GF256.gf_mul(137, 42) == 195


class TestBinaryGaloisFieldDiv:
    def test_gf_div_gf16(self):
        assert GF16.gf_div(0, 15) == 0
        assert GF16.gf_div(1, 1) == 1
        assert GF16.gf_div(2, 4) == 9
        assert GF16.gf_div(11, 4) == 6
        assert GF16.gf_div(9, 13) == 2
        assert GF16.gf_div(14, 14) == 1
        assert GF16.gf_div(12, 13) == 5

    def test_gf_div_gf256(self):
        assert GF256.gf_div(0, 127) == 0
        assert GF256.gf_div(1, 1) == 1
        assert GF256.gf_div(16, 4) == 4
        assert GF256.gf_div(195, 42) == 137
        assert GF256.gf_div(137, 195) == 31


class TestBinaryGaloisFieldPow:
    def test_pow_gf8(self):
        assert GF8.gf_pow(0, 0) == 1
        assert GF8.gf_pow(0, 2) == 0
        assert GF8.gf_pow(0, 510) == 0
        assert GF8.gf_pow(1, 0) == 1
        assert GF8.gf_pow(2, 0) == 1
        assert GF8.gf_pow(7, 0) == 1
        assert GF8.gf_pow(7, 1) == 7
        assert GF8.gf_pow(5, 2) == 7
        assert GF8.gf_pow(7, 25) == 5

class TestBinaryGaloisFieldInv:
    def test_gf_inv_gf8(self):
        assert GF8.gf_inv(1) == 1
        assert GF8.gf_inv(6) == 3

    def test_gf_inv_gf256(self):
        assert GF256.gf_inv(195) == 53

class TestBinaryGaloisFieldPoly:
    def test_gf_poly_scale(self):
        assert GF256.gf_poly_scale([1, 1, 0, 5, 0, 0, 8, 4], 6) == [6, 6, 0, 30, 0, 0, 48, 24]
        assert GF256.gf_poly_scale([200, 142, 13, 0, 28, 245, 4, 74], 23) == [94, 133, 243, 0, 137, 26, 92, 63]

    def test_gf_poly_add(self):
        POLY1 = [4, 2, 0, 0, 0, 7, 0, 7]
        POLY2 = [2, 0, 0, 1, 0, 0, 0, 1, 1]
        EXPECTED = [6, 2, 0, 1, 0, 7, 0, 6, 1]

        assert GF256.gf_poly_add(POLY1, POLY2) == EXPECTED

    def test_gf_poly_eval(self):
        assert GF256.gf_poly_eval([7, 5, 2, 3], 5) == 203
