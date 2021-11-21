from enum import IntEnum
from qr import consts

from ec.bch import BchDecodingFailure

class QrCodeDecoder:
    """QR Code Decoder"""


    def __init__(self, qr):
        self.version = 0
        self.ec_level, self.mask_pattern = (None, None)
        self.fp_mask = None
        self.blocks = None

        self.size, self.matrix = self._load(qr)

    @staticmethod
    def _load(qr_code):
        if isinstance(qr_code, str):
            load_from_file = True
            with open(qr_code, 'r', encoding="ascii") as file:
                rows = file.readlines()
        else:
            load_from_file = False
            rows = qr_code

        height = len(rows)
        matrix = [[0] * height for _ in range(height)]

        for row_idx, row in enumerate(rows):
            if load_from_file:
                row = row.strip()

            if len(row) != height:
                raise ValueError("QR Matrix needs to be a square")

            for col_idx, module in enumerate(row):
                module_int = int(module)
                if module_int not in [0, 1]:
                    raise ValueError("QR module values should be 0 or 1")
                matrix[row_idx][col_idx] = module_int

        return height, matrix

    def decode(self):
        self.version = self._get_version()

        alignment_patterns = self._compute_alignment_patterns()
        self.fp_mask = self._compute_function_patterns_mask(alignment_patterns)

        self.ec_level, self.mask_pattern = self._decode_format()
        self._unmask()
        self.blocks = self._deinterlace_blocks()
        return self._split_data_blocks_into_segments()

    def _get_version(self):
        version = (self.size - 21) / 4 + 1

        if not version.is_integer():
            raise ValueError("Invalid QR code matrix size")

        return int(version)

    def _compute_alignment_patterns(self):
        ap_db = consts.ALIGNMENT_PATTERNS[self.version]
        my_ap = [None] * (len(ap_db) ** 2 - 3)
        i = 0
        for coord1 in ap_db:
            for coord2 in ap_db:
                # No alignment pattern at (6, 6) because of NW position detection pattern
                if coord1 == ap_db[0] and coord2 == ap_db[0]:
                    continue

                # No alignment pattern at (6, z) and (z, 6) (z = ap_db[-1])
                # Because of NE and SW position detection patterns
                if {coord1, coord2} == {ap_db[0], ap_db[-1]}:
                    continue

                my_ap[i] = (coord1, coord2)
                i = i+1
        return my_ap

    def _compute_function_patterns_mask(self, alignment_patterns):
        fp_mask = [[0] * self.size for _ in range(self.size)]

        # Finder Patterns (Position Detection Patterns + Spacers)
        # Formats
        # The Dark Module
        for i in range(consts.FINDER_PATTERN_SIZE + 1):
            for j in range(consts.FINDER_PATTERN_SIZE):
                j_mirror = -consts.FINDER_PATTERN_SIZE + j

                fp_mask[i][j] = 1
                fp_mask[i][j_mirror] = 1
                fp_mask[j_mirror][i] = 1

            fp_mask[i][consts.FINDER_PATTERN_SIZE] = 1

        # Timing Patterns
        for i in range(consts.FINDER_PATTERN_SIZE, self.size - consts.FINDER_PATTERN_SIZE):
            fp_mask[consts.TIMING_PATTERN_ROW_COL][i] = 1
            fp_mask[i][consts.TIMING_PATTERN_ROW_COL] = 1

        if self.version < consts.ALIGNMENT_PATTERN_VERSION_START:
            return fp_mask

        # Alignment Patterns
        for ap_center_row, ap_center_col in alignment_patterns:
            for i in range(ap_center_row - 2, ap_center_row + 3, 1):
                for j in range(ap_center_col - 2, ap_center_col + 3, 1):
                    fp_mask[i][j] = 1

        if self.version < consts.VERSION_BLOCK_VERSION_START:
            return fp_mask

        # Versions
        for i in range(consts.VERSION_DIM[0]):
            for j in range(consts.VERSION_DIM[1]):
                j_mirror = -consts.FINDER_PATTERN_SIZE - consts.VERSION_DIM[1] + j
                fp_mask[j_mirror][i] = 1
                fp_mask[i][j_mirror] = 1

        return fp_mask

    def _unfold_formats(self):
        nw_format = 0
        swne_format = 0

        # Read horizontal part of NW format and vertical part of SWNE format
        for i in range(consts.FINDER_PATTERN_SIZE):
            # Skip Vertical Timing Pattern for NW format
            if i != consts.TIMING_PATTERN_ROW_COL:
                nw_format = (nw_format << 1) | self.matrix[consts.FINDER_PATTERN_SIZE][i]
            # Skip The Dark Module for SWNE format
            if i != consts.FINDER_PATTERN_SIZE - 1:
                swne_format = (swne_format << 1) | self.matrix[-1 - i][consts.FINDER_PATTERN_SIZE]

        # Read vertical part of NW format and horizontal part of SWNE format
        for i in range(consts.FINDER_PATTERN_SIZE, -1, -1):
            # Skip Horizontal Timing Pattern for NW format
            if i != consts.TIMING_PATTERN_ROW_COL:
                nw_format = (nw_format << 1) | self.matrix[i][consts.FINDER_PATTERN_SIZE]
            # Skip out of bounds module for SWNE format
            if i > 0:
                swne_format = (swne_format << 1) | self.matrix[consts.FINDER_PATTERN_SIZE][-i]

        return [nw_format, swne_format]

    def _decode_format(self):
        formats = self._unfold_formats()
        valid_formats = []

        for format_raw in formats:
            format_ = format_raw ^ consts.FORMAT_MASK_PATTERN

            try:
                _, format_ = consts.BCH_FORMAT.decode(format_)
            except BchDecodingFailure:
                continue

            ec_level = (format_ >> (consts.FORMAT_EC_BIT_LEN + consts.FORMAT_DATA_MP_BIT_LEN)) & ((1 << consts.FORMAT_DATA_EC_BIT_LEN) - 1)
            mask_pattern = (format_ >> consts.FORMAT_EC_BIT_LEN) & ((1 << consts.FORMAT_DATA_MP_BIT_LEN) - 1)
            valid_formats.append((format_, ec_level, mask_pattern))

        if not valid_formats:
            raise ValueError("Both formats have non-recoverable errors")

        if len(valid_formats) == 2 and valid_formats[0][0] != valid_formats[1][0]:
            raise ValueError("Formats disagree")

        # Authoritative format is first correct one found (NW, or SWNE if NW was unrecoverable)
        _, ec_level, mask_pattern = valid_formats[0]
        return ec_level, mask_pattern

    def _unmask(self):
        for row in range(self.size):
            for col in range(self.size):
                if not self.fp_mask[row][col]:
                    self.matrix[row][col] ^= consts.FORMAT_MASK_PATTERNS[self.mask_pattern](row, col)


    def _unfold_modules_stream(self):
        go_up = True
        bit = 7
        byte = 0

        # Outer loop: for each "column couple"
        for column_right in range(self.size - 1, 0, -2):
            # Skip Vertical Timing Pattern
            if column_right <= consts.TIMING_PATTERN_ROW_COL:
                column_right = column_right - 1

            # Configure middle loop range depending on whether we are going up or down
            row_start = self.size - 1 if go_up else 0
            row_end = -1 if go_up else self.size
            row_dir = -1 if go_up else 1

            # Middle loop: Row up up up, or row down down down
            for row in range(row_start, row_end, row_dir):

                # Inner loop: Column right left
                for i in range(2):
                    col = column_right - i

                    # Skip Function Patterns
                    if self.fp_mask[row][col]:
                        continue

                    byte |= (self.matrix[row][col] << bit)
                    bit -= 1
                    if bit == -1:
                        yield byte
                        byte = 0
                        bit = 7

            # We've reached symbol bounds, let's reverse the middle loop direction
            go_up = not go_up

    def _deinterlace_blocks(self):
        ec_config = consts.EC_BLOCKS[self.version][self.ec_level]

        word_generator = self._unfold_modules_stream()

        # Allocate data and error bytearrays for each block
        blocks = []
        _, (max_nb_words, max_nb_data_words, _) = ec_config[-1] # Last blocks have max word number
        max_words_per_block = [max_nb_data_words, max_nb_words - max_nb_data_words]
        for nb_blocks, (nb_words, nb_data_words, _) in ec_config:
            nb_error_words = nb_words - nb_data_words
            for _ in range(nb_blocks):
                blocks.append([bytearray(nb_data_words), bytearray(nb_error_words)])

        # Fill each byte of each data and error bytearray of each block
        # Do this in a de-interlacing manner so that following bytes:
        # B0D0 B1D0 B2D0 B0D1 B1D1 B2D1 B0E0 B1E0 B2E0 B0E1 B1E1 B2E1
        # get stored with following layout:
        # B0D0 B0D1 B0E0 B0E1 B1D0 B1D1 B1E0 B1E1 B2D0 B2D1 B2E0 B2D1

        # All data words first, then all error words
        for is_error_word in range(2):
            # For each word
            for word_idx in range(max_words_per_block[is_error_word]):
                block_idx = 0
                # For each block group
                for nb_blocks, (nb_words, nb_data_words, _) in ec_config:
                    nb_words = [nb_data_words, nb_words - nb_data_words]

                    # When some blocks are shorter than others, we need to skip
                    # non-existing words for those blocks
                    if word_idx == nb_words[is_error_word]:
                        block_idx += nb_blocks
                        continue

                    # For each block of that block group, get the next byte in the QR code matrix
                    for _ in range(nb_blocks):
                        blocks[block_idx][is_error_word][word_idx] = next(word_generator)
                        block_idx += 1

        return blocks

    def _split_data_blocks_into_segments(self):
        bitstream = ""
        for block in self.blocks:
            for byte in block[0]:
                bitstream += format(byte, '08b')

        data = ""
        end = 0
        while True:
            start = end
            end = start + consts.DATA_MODE_INDICATOR_BIT_LEN

            if end > len(bitstream):
                print("Bitstream exhaustion (terminator implied)")
                break

            mode = int(bitstream[start:end], 2)

            if mode == consts.DataModeIndicator.TERMINATOR:
                print("Terminator")
                break

            print("Segment")
            print(f"    Mode: {consts.DATA_MODE_INDICATOR[mode]}")

            # Determine the number of characters encoded
            start = end
            end = start + consts.char_count_bit_len(self.version, mode)
            char_count = int(bitstream[start:end], 2)
            print(f"    Char count: {char_count}")

            if mode == consts.DataModeIndicator.EIGHTBITBYTE:
                # FIXME: Add protection for crazy char_count
                seg_data = bytearray(char_count)
                for char_idx in range(char_count):
                    start = end
                    end = start + 8
                    seg_data[char_idx] = int(bitstream[start:end], 2)
                print(f"    {seg_data}")
                data += str(seg_data.decode())
            elif mode == consts.DataModeIndicator.ALPHANUMERIC:
                seg_data = ""
                # FIXME: Add protection for crazy char_count
                # TODO: Handle odd number of chars
                for char_idx in range(0, char_count, 2):
                    start = end
                    end = start + 11
                    double_char = int(bitstream[start:end], 2)
                    char1 = double_char // 45
                    char2 = double_char % 45
                    seg_data += consts.BASE45[char1]
                    seg_data += consts.BASE45[char2]
                print(f"    {seg_data}")
                data += seg_data
            else:
                raise ValueError("This segment mode is not supported")
        print()
        print(data)
        return data
