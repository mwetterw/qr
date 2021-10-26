#!/usr/bin/env python3
import unittest

from galois import BinaryGaloisField

GF8 = BinaryGaloisField(3)
GF16 = BinaryGaloisField(4)
GF256 = BinaryGaloisField(8)

class TestBinaryGaloisFieldTables(unittest.TestCase):
    def test_tables_gf8(self):
        GF8_LOG_TO_VECTOR=[1,2,4,3,6,7,5]
        GF8_VECTOR_TO_LOG=[-1,0,1,3,2,6,4,5]

        self.assertEqual(GF8.log_to_vector, GF8_LOG_TO_VECTOR)
        self.assertEqual(GF8.vector_to_log, GF8_VECTOR_TO_LOG)

    def test_tables_gf16(self):
        GF16_LOG_TO_VECTOR=[1,2,4,8,3,6,12,11,5,10,7,14,15,13,9]
        GF16_VECTOR_TO_LOG=[-1,0,1,4,2,8,5,10,3,14,9,7,6,13,11,12]

        self.assertEqual(GF16.log_to_vector, GF16_LOG_TO_VECTOR)
        self.assertEqual(GF16.vector_to_log, GF16_VECTOR_TO_LOG)

class TestBinaryGaloisFieldMult(unittest.TestCase):
    def test_mult_gf16(self):
        self.assertEqual(GF16.gf_mul(0, 0), 0)
        self.assertEqual(GF16.gf_mul(8, 0), 0)
        self.assertEqual(GF16.gf_mul(0, 8), 0)

        self.assertEqual(GF16.gf_mul(1, 1), 1)
        self.assertEqual(GF16.gf_mul(2, 2), 4)
        self.assertEqual(GF16.gf_mul(2, 3), 6)
        self.assertEqual(GF16.gf_mul(8, 1), 8)

        self.assertEqual(GF16.gf_mul(8, 2), 3)
        self.assertEqual(GF16.gf_mul(3, 7), 9)
        self.assertEqual(GF16.gf_mul(13, 14), 10)

    def test_mult_gf256(self):
        self.assertEqual(GF256.gf_mul(137, 42), 195)

class TestBinaryGaloisFieldDiv(unittest.TestCase):
    def test_div_gf16(self):
        self.assertEqual(GF16.gf_div(0, 15), 0)
        self.assertEqual(GF16.gf_div(1, 1), 1)
        self.assertEqual(GF16.gf_div(2, 4), 9)
        self.assertEqual(GF16.gf_div(11, 4), 6)
        self.assertEqual(GF16.gf_div(9, 13), 2)
        self.assertEqual(GF16.gf_div(14, 14), 1)
        self.assertEqual(GF16.gf_div(12, 13), 5)

    def test_div_gf256(self):
        self.assertEqual(GF256.gf_div(0, 127), 0)
        self.assertEqual(GF256.gf_div(1, 1), 1)
        self.assertEqual(GF256.gf_div(16, 4), 4)
        self.assertEqual(GF256.gf_div(195, 42), 137)
        self.assertEqual(GF256.gf_div(137, 195), 31)

class TestBinaryGaloisFieldPow(unittest.TestCase):
    def test_pow_gf8(self):
        self.assertEqual(GF8.gf_pow(0, 0), 1)
        self.assertEqual(GF8.gf_pow(0, 2), 0)
        self.assertEqual(GF8.gf_pow(0, 510), 0)
        self.assertEqual(GF8.gf_pow(1, 0), 1)
        self.assertEqual(GF8.gf_pow(2, 0), 1)
        self.assertEqual(GF8.gf_pow(7, 0), 1)
        self.assertEqual(GF8.gf_pow(7, 1), 7)
        self.assertEqual(GF8.gf_pow(5, 2), 7)
        self.assertEqual(GF8.gf_pow(7, 25), 5)

class TestBinaryGaloisFieldInv(unittest.TestCase):
    def test_inv_gf8(self):
        self.assertEqual(GF8.gf_inv(1), 1)
        self.assertEqual(GF8.gf_inv(6), 3)

    def test_inv_gf256(self):
        self.assertEqual(GF256.gf_inv(195), 53)

class TestBinaryGaloisFieldPoly(unittest.TestCase):
    def test_poly_scale(self):
        self.assertListEqual(GF256.gf_poly_scale([1, 1, 0, 5, 0, 0, 8, 4], 6), [6, 6, 0, 30, 0, 0, 48, 24])
        self.assertListEqual(GF256.gf_poly_scale([200, 142, 13, 0, 28, 245, 4, 74], 23), [94, 133, 243, 0, 137, 26, 92, 63])

    def test_poly_add(self):
        POLY1 = [4, 2, 0, 0, 0, 7, 0, 7]
        POLY2 = [2, 0, 0, 1, 0, 0, 0, 1, 1]
        EXPECTED = [6, 2, 0, 1, 0, 7, 0, 6, 1]

        self.assertListEqual(GF256.gf_poly_add(POLY1, POLY2), EXPECTED)
