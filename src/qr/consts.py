from enum import IntEnum
from ec import bch

# 8.5 Error correction, Table 13-22 page 35-44
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

    # Version 8
    [   [(2, (60, 38, 11)), (2, (61, 39, 11))],     # M
        [(2, (121, 97, 12))],                       # L
        [(4, (40, 14, 13)), (2, (41, 15, 13))],     # H
        [(4, (40, 18, 11)), (2, (41, 19, 11))]],    # Q

    # Version 9
    [   [(3, (58, 36, 11)), (2, (59, 37, 11))],     # M
        [(2, (146, 116, 15))],                      # L
        [(4, (36, 12, 12)), (4, (37, 13, 12))],     # H
        [(4, (36, 16, 10)), (4, (37, 17, 10))]],    # Q

    # Version 10
    [   [(4, (69, 43, 13)), (1, (70, 44, 13))],     # M
        [(2, (86, 68, 9)), (2, (87, 69, 9))],       # L
        [(6, (43, 15, 14)), (2, (44, 16, 14))],     # H
        [(6, (43, 19, 12)), (2, (44, 20, 12))]],    # Q

    # Version 11
    [   [(1, (80, 50, 15)), (4, (81, 51, 15))],     # M
        [(4, (101, 81, 10))],                       # L
        [(3, (36, 12, 12)), (8, (37, 13, 12))],     # H
        [(4, (50, 22, 14)), (4, (51, 23, 14))]],    # Q

    # Version 12
    [   [(6, (58, 36, 11)), (2, (59, 37, 11))],     # M
        [(2, (116, 92, 12)), (2, (117, 93, 12))],   # L
        [(7, (42, 14, 14)), (4, (43, 15, 14))],     # H
        [(4, (46, 20, 13)), (6, (47, 21, 13))]],    # Q

    # Version 13
    [   [(8, (59, 37, 11)), (1, (60, 38, 11))],     # M
        [(4, (133, 107, 13))],                      # L
        [(12, (33, 11, 11)), (4, (34, 12, 11))],    # H
        [(8, (44, 20, 12)), (4, (45, 21, 12))]],    # Q

    # Version 14
    [   [(4, (64, 40, 12)), (5, (65, 41, 12))],     # M
        [(3, (145, 115, 15)), (1, (146, 116, 15))], # L
        [(11, (36, 12, 12)), (5, (37, 13, 12))],    # H
        [(11, (36, 16, 10)), (5, (37, 17, 10))]],   # Q

    # Version 15
    [   [(5, (65, 41, 12)), (5, (66, 42, 12))],     # M
        [(5, (109, 87, 11)), (1, (110, 88, 11))],   # L
        [(11, (36, 12, 12)), (7, (37, 13, 12))],    # H
        [(5, (54, 24, 15)), (7, (55, 25, 15))]],    # Q

    # Version 16
    [   [(7, (73, 45, 14)), (3, (74, 46, 14))],     # M
        [(5, (122, 98, 12)), (1, (123, 99, 12))],   # L
        [(3, (45, 15, 15)), (13, (46, 16, 15))],    # H
        [(15, (43, 19, 12)), (2, (44, 20, 12))]],   # Q

    # Version 17
    [   [(10, (74, 46, 14)), (1, (75, 47, 14))],    # M
        [(1, (135, 107, 14)), (5, (136, 108, 14))], # L
        [(2, (42, 14, 14)), (17, (43, 15, 14))],    # H
        [(1, (50, 22, 14)), (15, (51, 23, 14))]],   # Q

    # Version 18
    [   [(9, (69, 43, 13)), (4, (70, 44, 13))],     # M
        [(5, (150, 120, 15)), (1, (151, 121, 15))], # L
        [(2, (42, 14, 14)), (19, (43, 15, 14))],    # H
        [(17, (50, 22, 14)), (1, (51, 23, 14))]],   # Q

    # Version 19
    [   [(3, (70, 44, 13)), (11, (71, 45, 13))],    # M
        [(3, (141, 113, 14)), (4, (142, 114, 14))], # L
        [(9, (39, 13, 13)), (16, (40, 14, 13))],    # H
        [(17, (47, 21, 13)), (4, (48, 22, 13))]],   # Q

    # Version 20
    [   [(3, (67, 41, 13)), (13, (68, 42, 13))],    # M
        [(3, (135, 107, 14)), (5, (136, 108, 14))], # L
        [(15, (43, 15, 14)), (10, (44, 16, 14))],   # H
        [(15, (54, 24, 15)), (5, (55, 25, 15))]],   # Q

    # Version 21
    [   [(17, (68, 42, 13))],                       # M
        [(4, (144, 116, 14)), (4, (145, 117, 14))], # L
        [(19, (46, 16, 15)), (6, (47, 17, 15))],    # H
        [(17, (50, 22, 14)), (6, (51, 23, 14))]],   # Q

    # Version 22
    [   [(17, (74, 46, 14))],                       # M
        [(2, (139, 111, 14)), (7, (140, 112, 14))], # L
        [(34, (37, 13, 12))],                       # H
        [(7, (54, 24, 15)), (16, (55, 25, 15))]],   # Q

    # Version 23
    [   [(4, (75, 47, 14)), (14, (76, 48, 14))],    # M
        [(4, (151, 121, 15)), (5, (152, 122, 15))], # L
        [(16, (45, 15, 15)), (14, (46, 16, 15))],   # H
        [(11, (54, 24, 15)), (14, (55, 25, 15))]],  # Q

    # Version 24
    [   [(6, (73, 45, 14)), (14, (74, 46, 14))],    # M
        [(6, (147, 117, 15)), (4, (148, 118, 15))], # L
        [(30, (46, 16, 15)), (2, (47, 17, 15))],    # H
        [(11, (54, 24, 15)), (16, (55, 25, 15))]],  # Q

    # Version 25
    [   [(8, (75, 47, 14)), (13, (76, 48, 14))],    # M
        [(8, (132, 106, 13)), (4, (133, 107, 13))], # L
        [(22, (45, 15, 15)), (13, (46, 16, 15))],   # H
        [(7, (54, 24, 15)), (22, (55, 25, 15))]],   # Q

    # Version 26
    [   [(19, (74, 46, 14)), (4, (75, 47, 14))],        # M
        [(10, (142, 114, 14)), (2, (143, 115, 14))],    # L
        [(33, (46, 16, 15)), (4, (47, 17, 15))],        # H
        [(28, (50, 22, 14)), (6, (51, 23, 14))]],       # Q

    # Version 27
    [   [(22, (73, 45, 14)), (3, (74, 46, 14))],        # M
        [(8, (152, 122, 15)), (4, (153, 123, 15))],     # L
        [(12, (45, 15, 15)), (28, (46, 16, 15))],       # H
        [(8, (53, 23, 15)), (26, (54, 24, 15))]],       # Q

    # Version 28
    [   [(3, (73, 45, 14)), (23, (74, 46, 14))],        # M
        [(3, (147, 117, 15)), (10, (148, 118, 15))],    # L
        [(11, (45, 15, 15)), (31, (46, 16, 15))],       # H
        [(4, (54, 24, 15)), (31, (55, 25, 15))]],       # Q

    # Version 29
    [   [(21, (73, 45, 14)), (7, (74, 46, 14))],        # M
        [(7, (146, 116, 15)), (7, (147, 117, 15))],     # L
        [(19, (45, 15, 15)), (26, (46, 16, 15))],       # H
        [(1, (53, 23, 15)), (37, (54, 24, 15))]],       # Q

    # Version 30
    [   [(19, (75, 47, 14)), (10, (76, 48, 14))],       # M
        [(5, (145, 115, 15)), (10, (146, 116, 15))],    # L
        [(23, (45, 15, 15)), (25, (46, 16, 15))],       # H
        [(15, (54, 24, 15)), (25, (55, 25, 15))]],      # Q

    # Version 31
    [   [(2, (74, 46, 14)), (29, (75, 47, 14))],        # M
        [(13, (145, 115, 15)), (3, (146, 116, 15))],    # L
        [(23, (45, 15, 15)), (28, (46, 16, 15))],       # H
        [(42, (54, 24, 15)), (1, (55, 25, 15))]],       # Q

    # Version 32
    [   [(10, (74, 46, 14)), (23, (75, 47, 14))],       # M
        [(17, (145, 115, 15))],                         # L
        [(19, (45, 15, 15)), (35, (46, 16, 15))],       # H
        [(10, (54, 24, 15)), (35, (55, 25, 15))]],      # Q

    # Version 33
    [   [(14, (74, 46, 14)), (21, (75, 47, 14))],       # M
        [(17, (145, 115, 15)), (1, (146, 116, 15))],    # L
        [(11, (45, 15, 15)), (46, (46, 16, 15))],       # H
        [(29, (54, 24, 15)), (19, (55, 25, 15))]],      # Q

    # Version 34
    [   [(14, (74, 46, 14)), (23, (75, 47, 14))],       # M
        [(13, (145, 115, 15)), (6, (146, 116, 15))],    # L
        [(59, (46, 16, 15)), (1, (47, 17, 15))],        # H
        [(44, (54, 24, 15)), (7, (55, 25, 15))]],       # Q

    # Version 35
    [   [(12, (75, 47, 14)), (26, (76, 48, 14))],       # M
        [(12, (151, 121, 15)), (7, (152, 122, 15))],    # L
        [(22, (45, 15, 15)), (41, (46, 16, 15))],       # H
        [(39, (54, 24, 15)), (14, (55, 25, 15))]],      # Q

    # Version 36
    [   [(6, (75, 47, 14)), (34, (76, 48, 14))],        # M
        [(6, (151, 121, 15)), (14, (152, 122, 15))],    # L
        [(2, (45, 15, 15)), (64, (46, 16, 15))],        # H
        [(46, (54, 24, 15)), (10, (55, 25, 15))]],      # Q

    # Version 37
    [   [(29, (74, 46, 14)), (14, (75, 47, 14))],       # M
        [(17, (152, 122, 15)), (4, (153, 123, 15))],    # L
        [(24, (45, 15, 15)), (46, (46, 16, 15))],       # H
        [(49, (54, 24, 14)), (10, (55, 25, 15))]],      # Q

    # Version 38
    [   [(13, (74, 46, 14)), (32, (75, 47, 14))],       # M
        [(4, (152, 122, 15)), (18, (153, 123, 15))],    # L
        [(42, (45, 15, 15)), (32, (46, 16, 15))],       # H
        [(48, (54, 24, 15)), (14, (55, 25, 15))]],      # Q

    # Version 39
    [   [(40, (75, 47, 14)), (7, (76, 48, 14))],        # M
        [(20, (147, 117, 15)), (4, (148, 118, 15))],    # L
        [(10, (45, 15, 15)), (67, (46, 16, 15))],       # H
        [(43, (54, 24, 15)), (22, (55, 25, 15))]],      # Q

    # Version 40
    [   [(18, (75, 47, 14)), (31, (76, 48, 14))],       # M
        [(19, (148, 118, 15)), (6, (149, 119, 15))],    # L
        [(20, (45, 15, 15)), (61, (46, 16, 15))],       # H
        [(34, (54, 24, 15)), (34, (55, 25, 15))]],      # Q
]

# Table E.1 page 82
ALIGNMENT_PATTERNS = [
    None, # Version 0 doesn't exist
    [],   # Version 1 has no Alignment Patterns
    [6, 18], # Version 2
    [6, 22], # Version 3
    [6, 26], # Version 4
    [6, 30], # Version 5
    [6, 34], # Version 6
    [6, 22, 38], # Version 7
    [6, 24, 42], # Version 8
    [6, 26, 46], # Version 9
    [6, 28, 50], # Version 10
    [6, 30, 54], # Version 11
    [6, 32, 58], # Version 12
    [6, 34, 62], # Version 13
    [6, 26, 46, 66], # Version 14
    [6, 26, 48, 70], # Version 15
    [6, 26, 50, 74], # Version 16
    [6, 30, 54, 78], # Version 17
    [6, 30, 56, 82], # Version 18
    [6, 30, 58, 86], # Version 19
    [6, 34, 62, 90], # Version 20
    [6, 28, 50, 72, 94], # Version 21
    [6, 26, 50, 74, 98], # Version 22
    [6, 30, 54, 78, 102], # Version 23
    [6, 28, 54, 80, 106], # Version 24
    [6, 32, 58, 84, 110], # Version 25
    [6, 30, 58, 86, 114], # Version 26
    [6, 34, 62, 90, 118], # Version 27
    [6, 26, 50, 74, 98, 122], # Version 28
    [6, 30, 54, 78, 102, 126], # Version 29
    [6, 26, 52, 78, 104, 130], # Version 30
    [6, 30, 56, 82, 108, 134], # Version 31
    [6, 34, 60, 86, 112, 138], # Version 32
    [6, 30, 58, 86, 114, 142], # Version 33
    [6, 34, 62, 90, 118, 146], # Version 34
    [6, 30, 54, 78, 102, 126, 150], # Version 35
    [6, 24, 50, 76, 102, 128, 154], # Version 36
    [6, 28, 54, 80, 106, 132, 158], # Version 37
    [6, 32, 58, 84, 110, 136, 162], # Version 38
    [6, 26, 54, 82, 110, 138, 166], # Version 39
    [6, 30, 58, 86, 114, 142, 170], # Version 40
]


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

CHAR_COUNT_BIT_LEN = [
    [27, {'numeric': 14, 'alphanumeric': 13, 'eightbitbyte': 16, 'kanji': 12}],
    [10, {'numeric': 12, 'alphanumeric': 11, 'eightbitbyte': 16, 'kanji': 10}],
    [1,  {'numeric': 10, 'alphanumeric': 9, 'eightbitbyte': 8, 'kanji': 8}]
]

def char_count_bit_len(version, mode):
    mode_txt = DATA_MODE_INDICATOR[mode]
    for [version_min, dict_] in CHAR_COUNT_BIT_LEN:
        if version >= version_min:
            return dict_[mode_txt]

FINDER_PATTERN_SIZE = 8
TIMING_PATTERN_ROW_COL = 6
VERSION_DIM = (6, 3)

ALIGNMENT_PATTERN_VERSION_START = 2
VERSION_BLOCK_VERSION_START = 7

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
FORMAT_DATA_EC_BIT_LEN = 2
FORMAT_DATA_MP_BIT_LEN = 3
FORMAT_DATA_MP_MASK = (1 << FORMAT_DATA_MP_BIT_LEN) - 1
FORMAT_EC_BIT_LEN   = 10

BCH_FORMAT = bch.BCH(4, 5, 3, 0)

ALPHANUM_CHARSET = [str(i) for i in range(10)] \
        + [chr(ord('A') + i) for i in range(26)] \
        + [' ', '$', '%', '*', '+', '-', '.', '/', ':']
ALPHANUM_CHARSET_LEN = len(ALPHANUM_CHARSET)
ALPHANUM_SINGLE_MAX = ALPHANUM_CHARSET_LEN - 1
ALPHANUM_DOUBLE_MAX = ALPHANUM_SINGLE_MAX * ALPHANUM_CHARSET_LEN + ALPHANUM_SINGLE_MAX
ALPHANUM_SINGLE_BIT_LEN = 6
ALPHANUM_DOUBLE_BIT_LEN = 11

NUM_SINGLE_MAX = 9
NUM_DOUBLE_MAX = 99
NUM_TRIPLE_MAX = 999
NUM_SINGLE_BIT_LEN = 4
NUM_DOUBLE_BIT_LEN = 7
NUM_TRIPLE_BIT_LEN = 10

EIGHTBIT_BIT_LEN = 8

class Eci:
    # Those ECIs are in the category:
    # Encodable -> Interpretative -> Character Set ECIs (0-899)

    DESIGNATOR_WORD_LEN = 8

    CHARSET_RANGE = (0, 900)

    DEFAULT_CHARSET = 3

    CHARSETS = {
        3: 'iso-8859-1',    # Western Europe
        4: 'iso-8859-2',    # Central & Eastern Europe
        5: 'iso-8859-3',    # South Europe
        6: 'iso-8859-4',    # North Europe
        7: 'iso-8859-5',    # Cyrillic
        8: 'iso-8859-6',    # Arabic
        9: 'iso-8859-7',    # Greek
        10: 'iso-8859-8',   # Hebrew
        11: 'iso-8859-9',   # Turkish
        12: 'iso-8859-10',  # Nordic
        13: 'iso-8859-11',  # Thai
        15: 'iso-8859-13',  # Baltic
        16: 'iso-8859-14',  # Celtic
        17: 'iso-8859-15',  # Western Europe (with € sign)
        18: 'iso-8859-16',  # South-Eastern Europe
        20: 'shift-jis',    # Japanese
        21: 'windows-1250', # Central & Eastern Europe
        22: 'windows-1251', # Cyrillic
        23: 'windows-1252', # Western Europe (with € sign)
        24: 'windows-1256', # Arabic
        25: 'utf-16-be',    # UTF-16 Unicode (Big Endian)
        26: 'utf-8',        # UTF-8 Unicode
        27: 'ascii',        # ISO-646:1991 7bit Charset
        28: 'big5',         # Traditional Chinese (Taiwan)
        29: 'gb18030',      # Unified Chinese (China)
        30: 'euc-kr',       # Korean (KSX1001:1998)
    }
