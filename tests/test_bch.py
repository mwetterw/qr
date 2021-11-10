#!/usr/bin/env python3

import unittest

from ec.bch import BCH
from ec.bch import BchDecodingFailure

class TestSyndromes(unittest.TestCase):
    def test_syndrome_zero(self):
        # Example from a valid QR Code Format
        bin_bch = BCH(4, 5, 3, 0)
        self.assertEqual(bin_bch.syndrome(1, 0b001111010110010), 0)

    def test_syndrome_one_only_without_any_alpha(self):
        # Same QR Code Format as above, but with one error added in it
        bin_bch = BCH(4, 5, 3, 0)
        self.assertEqual(bin_bch.syndrome(1, 0b001111010110011), 1)

    def test_syndromes_gf16_book_example_6_16_p261(self):
        R = 0b100001010
        EXPECTED_SYNDROMES = [15, 10, 8, 8, 0, 12]

        bin_bch = BCH(4, 5, 3, 0)
        self.assertEqual(bin_bch.syndromes(R), EXPECTED_SYNDROMES)

    def test_syndromes_gf32_book_example_6_12_p253(self):
        C = 0b11101101110100010101111001
        R = 0b11101100110100010101101001
        G = 0b11101101001
        M = 5
        K = 21
        T = 2
        EXPECTED_SYNDROMES_C = [0, 0, 0, 0]
        EXPECTED_SYNDROMES_R = [19, 8, 1, 10]

        bin_bch = BCH(M, K, T, G)
        self.assertEqual(bin_bch.syndromes(C), EXPECTED_SYNDROMES_C)
        self.assertEqual(bin_bch.syndromes(R), EXPECTED_SYNDROMES_R)

    def test_syndromes_gf16_book_digital_communications_example_7_10_3_p465(self):
        # This example is interesting because the code word is zero
        C = 0b0
        R = 0b1001
        M = 4
        K = 7
        G = 0b111010001
        T = 2
        EXPECTED_SYNDROMES_C = [0, 0, 0, 0]
        EXPECTED_SYNDROMES_R = [9, 13, 11, 14]

        bin_bch = BCH(M, K, T, G)
        self.assertEqual(bin_bch.syndromes(C), EXPECTED_SYNDROMES_C)
        self.assertEqual(bin_bch.syndromes(R), EXPECTED_SYNDROMES_R)

class TestBerlekampMassey(unittest.TestCase):
    def test_berlekamp_massey_gf32_book_example_6_12_p253(self):
        C = 0b11101101110100010101111001
        R = 0b11101100110100010101101001
        G = 0b11101101001
        M = 5
        K = 21
        T = 2

        EXPECTED_SIGMA = [1, 19, 21]

        bin_bch = BCH(M, K, T, G)
        syndromes = bin_bch.syndromes(R)
        sigma = bin_bch.berlekamp_massey(syndromes)
        self.assertListEqual(sigma, EXPECTED_SIGMA)

class TestDecode(unittest.TestCase):
    QR_BCH = BCH(4, 5, 3, 0)

    QR_CODE_FORMATS = [
            0b111011111000100,
            0b111001011110011,
            0b111110110101010,
            0b111100010011101,
            0b110011000101111,
            0b110001100011000,
            0b110110001000001,
            0b110100101110110,
            0b101010000010010,
            0b101000100100101,
            0b101111001111100,
            0b101101101001011,
            0b100010111111001,
            0b100000011001110,
            0b100111110010111,
            0b100101010100000,
            0b011010101011111,
            0b011000001101000,
            0b011111100110001,
            0b011101000000110,
            0b010010010110100,
            0b010000110000011,
            0b010111011011010,
            0b010101111101101,
            0b001011010001001,
            0b001001110111110,
            0b001110011100111,
            0b001100111010000,
            0b000011101100010,
            0b000001001010101,
            0b000110100001100,
            0b000100000111011
    ]

    QR_CODE_FORMAT_MASK = 0b101010000010010

    def test_decode_qr_code_format_correct(self):
        for format_raw in self.QR_CODE_FORMATS:
            format_ = format_raw ^ self.QR_CODE_FORMAT_MASK
            self.assertEqual((False, format_), self.QR_BCH.decode(format_))

    def test_decode_qr_code_format_1_error(self):
        for format_raw in self.QR_CODE_FORMATS:
            format_ = format_raw ^ self.QR_CODE_FORMAT_MASK
            errors = [(1 << a) for a in range(0, 15)]
            formats_wrong = [(format_ ^ error) for error in errors]
            for format_wrong in formats_wrong:
                self.assertEqual((True, format_), self.QR_BCH.decode(format_wrong))

    def test_decode_qr_code_format_2_errors(self):
        for format_raw in self.QR_CODE_FORMATS:
            format_ = format_raw ^ self.QR_CODE_FORMAT_MASK
            errors = []
            for i in range(0, 14):
                for j in range(i+1, 15):
                    errors.append(1 << i | 1 << j)

            formats_wrong = [(format_ ^ error) for error in errors]
            for format_wrong in formats_wrong:
                self.assertEqual((True, format_), self.QR_BCH.decode(format_wrong))

    def test_decode_qr_code_format_3_errors(self):
        for format_raw in self.QR_CODE_FORMATS:
            format_ = format_raw ^ self.QR_CODE_FORMAT_MASK
            errors = [0b111, 0b1110, 0b100101000000, 0b10011, 0b101000100000, 0b11100000000000]
            formats_wrong = [(format_ ^ error) for error in errors]
            for format_wrong in formats_wrong:
                self.assertEqual((True, format_), self.QR_BCH.decode(format_wrong))

    def test_decode_qr_code_format_too_many_errors(self):
        for format_raw in self.QR_CODE_FORMATS:
            format_ = format_raw ^ self.QR_CODE_FORMAT_MASK
            format_wrong = format_ ^ 0b11110000000

            with self.assertRaises(BchDecodingFailure):
                error, corrected = self.QR_BCH.decode(format_wrong)
