from enum import IntEnum
from qr import consts

from ec.bch import BchDecodingFailure

class QrCodeDecoder:
    """QR Code Decoder"""


    def __init__(self, qr):
        self.load(qr)
        print("Computing version...")
        self.get_version()
        self.compute_alignment_patterns()
        self.compute_function_patterns_mask()
        print()
        print("Reading format...")
        self.decode_format()
        print("Unmasking...")
        self.unmask()
        print()
        print("Extracting blocks...")
        self.deinterlace_blocks()
        print("Splitting data blocks into data segments...")
        self.split_data_blocks_into_segments()

    def load(self, qr):
        if isinstance(qr, str):
            load_from_file = True
            with open(qr, 'r') as f:
                rows = f.readlines()
        else:
            load_from_file = False
            rows = qr

        height = len(rows)

        qr = [None] * height

        for row_idx, row in enumerate(rows):
            if load_from_file:
                row = row.strip()

            if len(row) != height:
                raise ValueError("QR Matrix needs to be a square")

            qr[row_idx] = [None] * height

            for col_idx, module in enumerate(row):
                module_int = int(module)
                if module_int not in [0, 1]:
                    raise ValueError("QR module values should be 0 or 1")
                qr[row_idx][col_idx] = module_int

        self.qr = qr

    def get_version(self):
        version = (len(self.qr) - 21) / 4 + 1

        if not version.is_integer():
            raise ValueError("Invalid QR code matrix size")

        self.version = int(version)
        print(f'Version: {self.version}')

    def compute_alignment_patterns(self):
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
        self.alignment_patterns = my_ap

    def compute_function_patterns_mask(self):
        self.fp_mask = [[0] * len(self.qr) for _ in range(len(self.qr))]

        # Finder Patterns (Position Detection Patterns + Spacers)
        # Formats
        # The Dark Module
        for i in range(9):
            for j in range(8):
                j_mirror = len(self.qr) - 8 + j

                self.fp_mask[i][j] = 1
                self.fp_mask[i][j_mirror] = 1
                self.fp_mask[j_mirror][i] = 1

            self.fp_mask[i][8] = 1

        # Timing Patterns
        for i in range(8, len(self.qr) - 8):
            self.fp_mask[6][i] = 1
            self.fp_mask[i][6] = 1

        if self.version < 2:
            return

        # Alignment Patterns
        for ap_center_row, ap_center_col in self.alignment_patterns:
            for i in range(ap_center_row - 2, ap_center_row + 3, 1):
                for j in range(ap_center_col - 2, ap_center_col + 3, 1):
                    self.fp_mask[i][j] = 1

        if self.version < 7:
            return

        # Versions
        for i in range(6):
            for j in range(3):
                j_mirror = len(self.qr) - 11 + j

                self.fp_mask[j_mirror][i] = 1
                self.fp_mask[i][j_mirror] = 1


    def unfold_formats(self):
        nw = 0
        swne = 0

        # Read horizontal part of NW format and vertical part of SWNE format
        for i in range(8):
            # Skip Vertical Timing Pattern for NW format
            if i != 6:
                nw = (nw << 1) | self.qr[8][i]
            # Skip The Dark Module for SWNE format
            if i != 7:
                swne = (swne << 1) | self.qr[len(self.qr) - 1 - i][8]

        # Read vertical part of NW format and horizontal part of SWNE format
        for i in range(9):
            # Skip Horizontal Timing Pattern for NW format
            if 8 - i != 6:
                nw = (nw << 1) | self.qr[8 - i][8]
            # Skip out of bounds module for SWNE format
            if i <= 7:
                swne = (swne << 1) | self.qr[8][len(self.qr) - 8 + i]

        return nw, swne

    def decode_format(self):
        nw, swne = self.unfold_formats()
        formats = [("NW", nw), ("SWNE", swne)]
        valid_formats = []

        for location, format_raw in formats:
            print(f"- Processing {location} format")
            print(f"    Raw:      {format_raw:015b}")
            format_ = format_raw ^ consts.FORMAT_MASK_PATTERN
            print(f"    Unmasked: {format_:015b}")

            try:
                err, format_ = consts.BCH_FORMAT.decode(format_)
            except(BchDecodingFailure):
                print(f'    Format has non-recoverable errors')
                continue

            if err:
                print(f'    Format had errors -> Corrected to {format_:015b}')


            ec_level = (format_ >> (consts.FORMAT_EC_BIT_LEN + consts.FORMAT_DATA_MP_BIT_LEN)) & ((1 << consts.FORMAT_DATA_EC_BIT_LEN) - 1)
            mask_pattern = (format_ >> consts.FORMAT_EC_BIT_LEN) & ((1 << consts.FORMAT_DATA_MP_BIT_LEN) - 1)
            valid_formats.append((location, format_, ec_level, mask_pattern))
            print(f'    EC Level = {consts.EC_LEVEL[ec_level]} ({ec_level:02b})')
            print(f'    Mask Pattern = {mask_pattern:03b}')


        if not valid_formats:
            raise ValueError("Both formats have non-recoverable errors")

        if len(valid_formats) == 2 and valid_formats[0][1] != valid_formats[1][1]:
            raise ValueError("Formats disagree")

        location, format_, ec_level, mask_pattern = valid_formats[0]
        self.ec_level = ec_level
        self.mask_pattern = mask_pattern
        print(f'Choosing {location} as the authoritative format')
        print(f'EC Level = {consts.EC_LEVEL[self.ec_level]} ({self.ec_level:02b})')
        print(f'Mask Pattern = {self.mask_pattern:03b}')
        print()

    def unmask(self):
        for row in range(self.size):
            for col in range(self.size):
                if not self.fp_mask[row][col]:
                    self.qr[row][col] ^= consts.FORMAT_MASK_PATTERNS[self.mask_pattern](row, col)


    def unfold_modules_stream(self):
        up = True
        bit = 7
        byte = 0

        print("- Unfolding modules stream into bytes")
        print("    ", end="")

        # Outer loop: for each "column couple"
        for column_right in range(len(self.qr) - 1, 0, -2):
            # Skip Vertical Timing Pattern
            if column_right <= 6:
                column_right = column_right - 1

            # Configure middle loop range depending on whether we are going up or down
            row_start = len(self.qr) - 1 if up else 0
            row_end = -1 if up else len(self.qr)
            row_dir = -1 if up else 1

            # Middle loop: Row up up up, or row down down down
            for row in range(row_start, row_end, row_dir):

                # Inner loop: Column right left
                for i in range(2):
                    col = column_right - i

                    # Skip Function Patterns
                    if self.fp_mask[row][col]:
                        continue

                    byte |= (self.qr[row][col] << bit)
                    bit -= 1
                    if bit == -1:
                        yield byte
                        print(f"{byte:02x}", end=" ")
                        byte = 0
                        bit = 7

            # We've reached symbol bounds, let's reverse the middle loop direction
            up = not up

    def deinterlace_blocks(self):
        ec_config = consts.EC_BLOCKS[self.version][self.ec_level]
        print(f"This QR code version uses following blocks configuration: {ec_config}")

        word_generator = self.unfold_modules_stream()

        blocks = []
        max_words_per_block = [0, 0]
        for nb, (n, k, _) in ec_config:
            max_words_per_block[0] = max(max_words_per_block[0], k)
            max_words_per_block[1] = max(max_words_per_block[1], n - k)
            for _ in range(nb):
                blocks.append([bytearray(k), bytearray(n - k)])

        for is_error_word in range(2):
            for word_idx in range(max_words_per_block[is_error_word]):
                block_idx = 0
                for nb, (n, k, _) in ec_config:
                    nb_words = [k, n - k]

                    # When some blocks are shorter than others, we need to skip
                    # non-existing words for those blocks
                    if word_idx == nb_words[is_error_word]:
                        block_idx += nb
                        continue

                    for _ in range(nb):
                        blocks[block_idx][is_error_word][word_idx] = next(word_generator)
                        block_idx += 1

        print()
        print("- Deinterlacing blocks")
        print(f"    {blocks}")
        self.blocks = blocks
        print()

    def split_data_blocks_into_segments(self):
        print("- Generating data bitstream")
        bitstream = ""
        for block in self.blocks:
            for byte in block[0]:
                bitstream += format(byte, '08b')

        print(f"    {bitstream}")

        print("- Splitting bitstream to segments")
        data = ""
        end = 0
        while True:
            start = end
            end = start + consts.DATA_MODE_INDICATOR_BIT_LEN

            if end > len(bitstream):
                print("    Bitstream exhaustion (terminator implied)")
                break

            mode = int(bitstream[start:end], 2)

            if mode == consts.DataModeIndicator.TERMINATOR:
                print("    Terminator")
                break

            print("    Segment")
            print(f"        Mode: {consts.DATA_MODE_INDICATOR[mode]}")

            # Determine the number of characters encoded
            start = end
            end = start + consts.char_count_bit_len(self.version, mode)
            char_count = int(bitstream[start:end], 2)
            print(f"        Char count: {char_count}")

            if mode == consts.DataModeIndicator.EIGHTBITBYTE:
                # FIXME: Add protection for crazy char_count
                seg_data = bytearray(char_count)
                for char_idx in range(char_count):
                    start = end
                    end = start + 8
                    seg_data[char_idx] = int(bitstream[start:end], 2)
                print(f"        {seg_data}")
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
                print(f"        {seg_data}")
                data += seg_data
            else:
                raise ValueError("This segment mode is not supported")
        self.data = data
        print()
        print(data)
