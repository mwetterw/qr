from os.path import exists
from os import makedirs
from io import StringIO

import pytest

from qrcode import QRCode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H

from qr.decoder import QrCodeDecoder

class TestDecodeNumericSegment:
    @pytest.mark.parametrize(("expected", "bitstring"),
        [   ("145", "0010010001"),
            ("47122", "01110101110010110"),
            ("3412", "01010101010010"),
            ("0123456789", "0000001100010101100110101001101001"),
            ("", ""),
            ("7", "0111"),
            ("47", "0101111"),
            ("47", "01011110100001110"),
            ("000", "0000000000"),
            ("007", "0000000111"),
            ("00", "0000000"),
            ("07", "0000111"),
            ("0", "0000"),
        ],
        ids = ["simple_3", "simple_rest_2", "simple_rest_1", "complete_charset", "zero_digit_empty",
            "one_digit", "two_digit", "bitstream_underflow", "zeroes_3", "leading_zeroes_3",
            "zeroes_rest_2", "leading_zeroes_rest_2", "zeroes_rest_1"])
    def test_numeric_valid(self, expected, bitstring, char_count=None):
        if char_count is None:
            char_count = len(expected)
        bitstream = StringIO(bitstring)
        try:
            assert QrCodeDecoder._decode_numeric_segment(bitstream, char_count) == expected
        finally:
            bitstream.close()

    @pytest.mark.parametrize(("expected", "bitstring", "char_count"),
        [   ("145",  "001001001", None),
            ("47122", "011101111", None),
            ("3412", "0101010101010", None),
            ("145", "0010010001", 4),
            ("47122", "0111010111", 6),
            ("3412", "01010101010010", 5),
            ("145", "0010010001", 1031),
            ("47122", "0111010111", 1031),
            ("3412", "01010101010010", 1031),
            ("999", "1111101000", None),
            ("99", "1100100", None),
            ("9", "1010", None)],
        ids = ["bitstream_3", "bitstream_rest_2", "bitstream_rest_1", "bitstream_overflow_3",
            "bitstream_overflow_rest_2", "bitstream_overflow_rest_1", "bitstream_overflow_crazy_3",
            "bitstream_overflow_crazy_rest_2", "bitstream_overflow_crazy_rest_1",
            "charset_overflow_triple", "charset_overflow_double", "charset_overflow_single"])
    def test_numeric_invalid(self, expected, bitstring, char_count):
        with pytest.raises(ValueError):
            self.test_numeric_valid(expected, bitstring, char_count)

class TestDecodeAlphaNumericSegment:
    @pytest.mark.parametrize(("expected", "bitstring"),
        [   ("BCD+78", "001111110110100111000100101000011"),
            ("AC-42", "0011100111011100111001000010"),
            ("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:", "000000000010000101110100010111001" \
                "00100010101001011100010011100110101000101001010100001010101110000101100111101" \
                "01110011001011111101011000101000110010101101101000010011010110010110111000001" \
                "1100001110111001111001110110101011110011000111110001101101100"),
            ("", ""),
            ("/", "101011"),
            ("O1", "1000011100100111000110")],
        ids = ["simple_even", "simple_odd", "complete_charset", "zero_char_empty", "one_char",
            "bitstream_underflow"])
    def test_alphanumeric_valid(self, expected, bitstring, char_count=None):
        if char_count is None:
            char_count = len(expected)
        bitstream = StringIO(bitstring)
        try:
            assert QrCodeDecoder._decode_alphanumeric_segment(bitstream, char_count) == expected
        finally:
            bitstream.close()

    @pytest.mark.parametrize(("expected", "bitstring", "char_count"),
        [   ("O1",  "1000011101", None),
            ("O14", "1000011100100100", None),
            ("A1", "00111000011", 3),
            ("O14", "10000111001000100", 4),
            ("A1", "00111000011", 1031),
            ("O14", "10000111001000100", 1031),
            ("F4", "11111101001", None),
            ("F4N", "01010100111101101", None)],
        ids = ["bitstream_even", "bitstream_odd", "bitstream_overflow_even",
            "bitstream_overflow_odd", "bitstream_overflow_crazy_even",
            "bitstream_overflow_crazy_odd", "charset_overflow_double", "charset_overflow_single"])
    def test_alphanumeric_invalid(self, expected, bitstring, char_count):
        with pytest.raises(ValueError):
            self.test_alphanumeric_valid(expected, bitstring, char_count)


class TestDecode:
    EC_STR = ['L', 'M', 'Q', 'H']
    EC_DICT = {val: idx for idx, val in enumerate(EC_STR)}
    EC_QR = [ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H]


    @pytest.fixture(scope="class", autouse=True)
    def create_qr_cache_dir(self):
        makedirs("tests/qr_cache", exist_ok=True)

    @pytest.fixture(scope="class")
    def lorem(self):
        with open('tests/lorem.txt', 'r', encoding='utf-8') as file:
            lorem = file.read()
        return lorem

    @pytest.fixture(scope="class")
    def eightbit_capa(self):
        return [
            17, 14, 11, 7, 32, 26, 20, 14, 53, 42, 32, 24, 78, 62, 46, 34, 106, 84, 60, 44,
            134, 106, 74, 58, 154, 122, 86, 64, 192, 152, 108, 84, 230, 180, 130, 98,
            271, 213, 151, 119, 321, 251, 177, 137, 367, 287, 203, 155, 425, 331, 241, 177,
            458, 362, 258, 194, 520, 412, 292, 220, 586, 450, 322, 250, 644, 504, 364, 280,
            718, 560, 394, 310, 792, 624, 442, 338, 858, 666, 482, 382, 929, 711, 509, 403,
            1003, 779, 565, 439, 1091, 857, 611, 461, 1171, 911, 661, 511, 1273, 997, 715, 535,
            1367, 1059, 751, 593, 1465, 1125, 805, 625, 1528, 1190, 868, 658, 1628, 1264, 908, 698,
            1732, 1370, 982, 742, 1840, 1452, 1030, 790, 1952, 1538, 1112, 842,
            2068, 1628, 1168, 898, 2188, 1722, 1228, 958, 2303, 1809, 1283, 983,
            2431, 1911, 1351, 1051, 2563, 1989, 1423, 1093, 2699, 2099, 1499, 1139,
            2809, 2213, 1579, 1219, 2953, 2331, 1663, 1273
        ]

    @pytest.mark.parametrize("ec_str", EC_STR)
    @pytest.mark.parametrize("version", list(range(1, 41)))
    def test_decode_all_versions_with_8bit_max_size(self, lorem, eightbit_capa, version, ec_str):
        ecl = self.EC_DICT[ec_str]
        capacity_idx = 4 * (version - 1) + ecl
        data = lorem[:eightbit_capa[capacity_idx]]

        filename = f"tests/qr_cache/{version}{ec_str}.qr"

        # If QR Code doesn't exist, generate it with a reference lib and cache
        # to disk to speed-up subsequent pytest runs
        if not exists(filename):
            # Prevent helper lib from choosing the best mask for each QR Code
            mask = (ecl + version) % 8
            qr_code = QRCode(version=version, error_correction=self.EC_QR[ecl], mask_pattern=mask)
            qr_code.add_data(data)
            qr_code.make(fit=False)
            # Make sure the helper lib generated a QR code with the characteristics we want
            assert qr_code.version == version
            assert qr_code.error_correction == self.EC_QR[ecl]

            # Cache generated QR Code to disk
            with open(filename, "w", encoding="ascii") as file:
                for row in qr_code.modules:
                    file.write(''.join(str(int(module)) for module in row))
                    file.write('\n')

        # Load reference QR Code from disk and check if we can retrieve the correct data
        my_qr = QrCodeDecoder(filename)
        assert my_qr.decode() == data
