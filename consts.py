from enum import IntEnum
from ec import bch

EC_BLOCKS = [
    None, # Version 0 doesn't exist

    # Version 1
    [   [(1, (26, 16, 4))],     # M
        [(1, (26, 19, 2))],     # L
        [(1, (26, 9, 8))],      # H
        [(1, (26, 13, 6))]],    # Q

    # Version 2
    [   [(1, (44, 28, 8))],     # M
        [(1, (44, 34, 4))],     # L
        [(1, (44, 16, 14))],    # H
        [(1, (44, 22, 11))]],   # Q

    # Version 3
    [   [(1, (70, 44, 13))],    # M
        [(1, (70, 55, 7))],     # L
        [(2, (35, 13, 11))],    # H
        [(2, (35, 17, 9))]],    # Q

    # Version 4
    [   [(2, (50, 32, 9))],     # M
        [(1, (100, 80, 10))],   # L
        [(4, (25, 9, 8))],      # H
        [(2, (50, 24, 13))]],   # Q

    # Version 5
    [   [(2, (67, 43, 12))],                        # M
        [(1, (134, 108, 13))],                      # L
        [(2, (33, 11, 11)), (2, (34, 12, 11))],     # H
        [(2, (33, 15, 9)), (2, (34,16,9))]],        # Q

    # Version 6
    [   [(4, (43, 27, 8))],                         # M
        [(2, (86, 68, 9))],                         # L
        [(4, (43, 15, 14))],                        # H
        [(4, (43, 19, 12))]],                       # Q

    # Version 7
    [   [(4, (49, 31, 9))],                         # M
        [(2, (98, 78, 10))],                        # L
        [(4, (39, 13, 13)), (1, (40, 14, 13))],     # H
        [(2, (32, 14, 9)), (4, (33, 15, 9))]],      # Q
]

ALIGNMENT_PATTERNS = [
    None, # Version 0 doesn't exist
    None, # Version 1 has no Alignment Patterns
    [6, 18],
    [6, 22],
    [6, 26],
    [6, 30],
    [6, 34],
    [6, 22, 38],
]

def alignment_pattern(version):
    my_ap = ALIGNMENT_PATTERNS[version]
    for coord1 in my_ap:
        for coord2 in my_ap:
            # No alignment pattern at (6, 6) because of NW position detection pattern
            if coord1 == my_ap[0] and coord2 == my_ap[0]:
                continue

            # No alignment pattern at (6, z) and (z, 6) (z = my_ap[-1])
            # Because of NE and SW position detection patterns
            if {coord1, coord2} == {my_ap[0], my_ap[-1]}:
                continue

            yield (coord1, coord2)


# 8.4 Data Encodation (Table 2)
class DataModeIndicator(IntEnum):
    ECI                 = 0b0111
    NUMERIC             = 0b0001
    ALPHANUMERIC        = 0b0010
    EIGHTBITBYTE        = 0b0100
    KANJI               = 0b1000
    STRUCTURED_APPEND   = 0b0011
    FNC1_FIRST_POS      = 0b0101
    FNC1_SECOND_POS     = 0b1001
    TERMINATOR          = 0b0000

DATA_MODE_INDICATOR_BIT_LEN = 4
DATA_MODE_INDICATOR = ['terminator', 'numeric', 'alphanumeric', 'structured', 'eightbitbyte', 'fnc1_first', '', 'eci', 'kanji', 'fnc1_second']


POS_DETECT = 8

# 8.9 Format Information (Table 25)
class FormatErrorCorrectionLevel(IntEnum):
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

BCH_FORMAT = bch.BCH(4, 5, 3, 0)
