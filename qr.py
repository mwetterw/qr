#!/usr/bin/env python3
from matplotlib import pyplot as plt
import numpy as np
from io import StringIO
from enum import Enum

import bch

QR = """111111100000001111111
100000100101001000001
101110100100101011101
101110100001101011101
101110100011101011101
100000101000001000001
111111101010101111111
000000000010000000000
100101101001110100001
010101011111011011011
001011100101001100111
110011010000101101001
010101100001000010000
000000001010011100100
111111100011111011110
100000101100000000011
101110100010100100010
101110101000001111111
101110100001011111001
100000100101100100000
111111101010000110010"""

class QrCode:
    """This class represents a QR Code"""

    POS_DETECT = 8

    # 8.4 Data Encodation (Table 2)
    class DataModeIndicator(Enum):
        ECI                 = 0b0111
        NUMERIC             = 0b0001
        ALPHANUMERIC        = 0b0010
        HEIGHTBITBYTE       = 0b0100
        KANJI               = 0b1000
        STRUCTURED_APPEND   = 0b0011
        FNC1_FIRST_POS      = 0b0101
        FNC1_SECOND_POS     = 0b1001
        TERMINATOR          = 0b0000

    # 8.9 Format Information (Table 25)
    class FormatErrorCorrectionLevel(Enum):
        EC_LEVEL_L = 0b01 # 7%
        EC_LEVEL_M = 0b00 # 15%
        EC_LEVEL_Q = 0b11 # 25%
        EC_LEVEL_H = 0b10 # 30%

    EC_LEVEL = ['M', 'L', 'H', 'Q']

    FORMAT_MASK_PATTERNS = [
            lambda i, j : (i + j) % 2 == 0,                         # 000
            lambda i, j : i % 2 == 0,                               # 001
            lambda i, j : j % 3 == 0,                               # 010
            lambda i, j : (i + j) % 3 == 0,                         # 011
            lambda i, j : ((i // 2) + (j // 3)) % 2 == 0,           # 100
            lambda i, j : (i * j) % 2 + (i * j) % 3 == 0,           # 101
            lambda i, j : ((i * j) % 2 + (i * j) % 3) % 2 == 0,     # 110
            lambda i, j : ((i * j) % 3 + (i + j) % 2) % 2 == 0,     # 111
    ]

    FORMAT_MASK_PATTERN = 0b101010000010010
    FORMAT_DATA_BIT_LEN = 5
    FORMAT_DATA_EC_BIT_LEN = 2
    FORMAT_DATA_MP_BIT_LEN = 3
    FORMAT_EC_BIT_LEN   = 10

    def __init__(self, qr_string):
        qr = self.qr_str_to_qr(qr_string)
        self.qr = qr
        print("Computing version...")
        self.get_version()
        print()
        print("Reading format...")
        self.read_format()
        # self.unmask()

    @staticmethod
    def qr_str_to_qr(qr_str):
        return [list(map(int, y)) for y in (x.strip() for x in qr_str.splitlines()) if y]

    @staticmethod
    def qr_to_qr_str(qr):
        return '\n'.join([''.join([str(module) for module in row]) for row in qr])

    def get_version(self):
        self.version = (len(self.qr) - 21) / 4 + 1
        print(f'Version: {self.version}')

    def raw_format_nw(self):
        format_raw_list = self.qr[self.POS_DETECT][0:6] \
                + self.qr[self.POS_DETECT][7:9] \
                + [self.qr[self.POS_DETECT - 1][self.POS_DETECT]] \
                + [row[self.POS_DETECT] for row in self.qr][5::-1]
        return int("".join(str(i) for i in format_raw_list), 2)

    def raw_format_swne(self):
        format_raw_list = [row[self.POS_DETECT] for row in self.qr][:-8:-1] \
                + self.qr[self.POS_DETECT][-self.POS_DETECT:]
        return int("".join(str(i) for i in format_raw_list), 2)

    def read_format(self):
        formats = [("NW", self.raw_format_nw()), ("SWNE", self.raw_format_swne())]
        for format_tuple in formats:
            location, format_raw = format_tuple
            print(f"- Processing {location} Format")
            print(f'Raw format: {format_raw:015b}')
            format_ = format_raw ^ self.FORMAT_MASK_PATTERN
            print(f'Unmasked format: {format_:015b}')

            syndromes = bch.syndromes(3, format_, 15)
            print(f"Format BCH syndromes: {syndromes}", end=" => ")
            if sum(syndromes):
                print("ERRORS detected in the format")
            else:
                print("Format is valid!")

            self.ec_level = (format_ >> (self.FORMAT_EC_BIT_LEN + self.FORMAT_DATA_MP_BIT_LEN)) & ((1 << self.FORMAT_DATA_EC_BIT_LEN) - 1)
            self.mask_pattern = (format_ >> self.FORMAT_EC_BIT_LEN) & ((1 << self.FORMAT_DATA_MP_BIT_LEN) - 1)
            print(f'\tEC Level = {self.EC_LEVEL[self.ec_level]} ({self.ec_level:02b})')
            print(f'\tMask Pattern = {self.mask_pattern:03b}')

    def unmask(self):
        unmasked_qr = []
        for i, row in enumerate(self.qr):
            unmasked_row = []
            for j, module in enumerate(row):
                unmasked_row.append(str(module ^ self.FORMAT_MASK_PATTERNS[self.mask_pattern](i, j)))
            unmasked_qr.append(unmasked_row)
        print(self.qr_to_qr_str(unmasked_qr))

def main():
    qr_code = QrCode(QR)

    # lol = np.genfromtxt(StringIO(QR), delimiter=1, autostrip=True, dtype=None).astype(bool)
    # plt.gray()
    # plt.imshow(np.invert(lol), interpolation='nearest')
    # plt.show()

if __name__ == '__main__':
    main()
