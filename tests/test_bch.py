#!/usr/bin/env python3

import unittest

from bch import BinaryBCH

class TestSyndromes(unittest.TestCase):
    def test_syndrome_zero(self):
        # Example from a valid QR Code Format
        bin_bch = BinaryBCH(4, 5, 3, 0)
        self.assertEqual(bin_bch.syndrome(1, 0b001111010110010), 0)

    def test_syndrome_one_only_without_any_alpha(self):
        # Same QR Code Format as above, but with one error added in it
        bin_bch = BinaryBCH(4, 5, 3, 0)
        self.assertEqual(bin_bch.syndrome(1, 0b001111010110011), 1)

    def test_syndromes_gf16_book_example_6_16_p261(self):
        R = 0b100001010
        EXPECTED_SYNDROMES = [1 << 12, 1 << 9, 1 << 3, 1 << 3, 0, 1 << 6]

        bin_bch = BinaryBCH(4, 5, 3, 0)
        self.assertEqual(bin_bch.syndromes(R), EXPECTED_SYNDROMES)

    def test_syndromes_gf32_book_example_6_12_p253(self):
        C = 0b11101101110100010101111001
        R = 0b11101100110100010101101001
        G = 0b11101101001
        M = 5
        K = 21
        T = 2
        EXPECTED_SYNDROMES_C = [0, 0, 0, 0]
        EXPECTED_SYNDROMES_R = [1 << 17, 1 << 3, 1, 1 << 6]

        bin_bch = BinaryBCH(M, K, T, G)
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
        EXPECTED_SYNDROMES_R = [1 << 14, 1 << 13, 1 << 7, 1 << 11]

        bin_bch = BinaryBCH(M, K, T, G)
        self.assertEqual(bin_bch.syndromes(C), EXPECTED_SYNDROMES_C)
        self.assertEqual(bin_bch.syndromes(R), EXPECTED_SYNDROMES_R)
