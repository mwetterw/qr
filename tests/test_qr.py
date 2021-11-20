import pytest
from os.path import exists
from os import makedirs

import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H

from qr.decoder import QrCodeDecoder

EC_STR = ['L', 'M', 'Q', 'H']
EC_DICT = {val: idx for idx, val in enumerate(EC_STR)}
EC_QR = [ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H]

CAPACITY = [
        17, 14, 11, 7,
        32, 26, 20, 14,
        53, 42, 32, 24,
        78, 62, 46, 34,
        106, 84, 60, 44,
        134, 106, 74, 58,
        154, 122, 86, 64,
        192, 152, 108, 84,
        230, 180, 130, 98,
        271, 213, 151, 119,
        321, 251, 177, 137,
        367, 287, 203, 155,
        425, 331, 241, 177,
        458, 362, 258, 194,
        520, 412, 292, 220,
        586, 450, 322, 250,
        644, 504, 364, 280,
        718, 560, 394, 310,
        792, 624, 442, 338,
        858, 666, 482, 382,
        929, 711, 509, 403,
        1003, 779, 565, 439,
        1091, 857, 611, 461,
        1171, 911, 661, 511,
        1273, 997, 715, 535,
        1367, 1059, 751, 593,
        1465, 1125, 805, 625,
        1528, 1190, 868, 658,
        1628, 1264, 908, 698,
        1732, 1370, 982, 742,
        1840, 1452, 1030, 790,
        1952, 1538, 1112, 842,
        2068, 1628, 1168, 898,
        2188, 1722, 1228, 958,
        2303, 1809, 1283, 983,
        2431, 1911, 1351, 1051,
        2563, 1989, 1423, 1093,
        2699, 2099, 1499, 1139,
        2809, 2213, 1579, 1219,
        2953, 2331, 1663, 1273,
]

LOREM = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed elementum volutpat porta. Sed nulla nibh, dapibus et egestas et, sodales nec felis. Aliquam erat volutpat. In in eleifend enim. Nunc aliquam ipsum eget libero sagittis, sed vestibulum justo ultricies. Praesent ornare nisl ut est facilisis, nec malesuada quam venenatis. Quisque sed aliquam erat. Etiam semper magna a dui consectetur, vel pretium ante fermentum. Vestibulum quis consectetur turpis, a viverra risus. Mauris sodales metus ac arcu fermentum, eu rhoncus sapien cursus. Nullam ac nunc sed elit sodales sollicitudin nec id libero.

Etiam posuere, ipsum vel laoreet varius, purus enim sagittis velit, sit amet ultricies est ante ac diam. Sed commodo neque vel luctus laoreet. Aliquam erat volutpat. Ut ullamcorper, magna feugiat vehicula congue, nunc elit fringilla massa, quis lobortis purus leo at quam. Curabitur ornare pulvinar lacus in imperdiet. Mauris fermentum nunc vel libero feugiat, et suscipit quam aliquet. Nunc aliquet est condimentum, convallis ligula id, volutpat diam. Vestibulum sodales enim sit amet tincidunt suscipit. In dapibus, ligula a vehicula rhoncus, lorem tellus dictum dui, sit amet lacinia sem nunc et odio. Duis non tortor quam. Duis et mauris nec tellus blandit accumsan. Ut euismod vitae nisi vel molestie.

Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Duis vel tincidunt sem. Pellentesque eu lacus vel ligula venenatis dignissim. Curabitur non suscipit massa. Donec blandit nisi et cursus imperdiet. Phasellus lacinia tincidunt feugiat. Cras a est quam. Donec ut mattis tortor. Aenean vitae tellus libero. Morbi nec sagittis nibh. Fusce sed sagittis nunc. Nulla eget vestibulum neque. Etiam enim nunc, egestas at cursus sit amet, commodo quis nulla. Vestibulum quis condimentum justo, id eleifend nulla. Donec ut aliquet sapien, quis lobortis quam.

Suspendisse gravida, metus eget dapibus placerat, dui quam interdum tortor, eu facilisis massa est ac augue. In egestas velit metus, nec pharetra elit tristique sit amet. Morbi eros nisi, accumsan eu cursus eu, malesuada at erat. Curabitur convallis eu turpis non sollicitudin. Vivamus non erat hendrerit, fringilla enim ac, molestie ligula. Nam malesuada vulputate eros, vitae sollicitudin metus. Maecenas at lobortis purus, pharetra viverra nulla. Nulla sed finibus metus, nec dictum est. Praesent ornare mauris at magna pulvinar dapibus.

Ut in arcu viverra, placerat mauris eget, dictum purus. Nunc eleifend tempor turpis ac imperdiet. Nam placerat tempus dolor sit amet mollis. Ut eget massa elit. Donec id gravida arcu. Sed a arcu sit amet purus lacinia suscipit. Aliquam imperdiet nunc quis finibus consequat. Nullam et euismod nibh. Donec scelerisque massa nec dolor gravida, ac suscipit sem aliquet. Vivamus convallis est a sapien fringilla tristique sed."""


class TestDecode:
    @pytest.fixture(scope="class", autouse=True)
    def create_qr_cache_dir(self):
        makedirs("tests/qr_cache", exist_ok=True)

    @pytest.mark.parametrize("ec_str", EC_STR)
    @pytest.mark.parametrize("version", [v for v in range(1, 41)])
    def test_decode_all_versions_with_8bit_max_size(self, version, ec_str):
        ec = EC_DICT[ec_str]
        capacity_idx = 4 * (version - 1) + ec
        data = LOREM[:CAPACITY[capacity_idx]]

        filename = f"tests/qr_cache/{version}{ec_str}.qr"

        # If QR Code doesn't exist, generate it with a reference lib and cache
        # to disk to speed-up subsequent pytest runs
        if not exists(filename):
            mask_pattern = (ec + version) % 8 # Prevent helper lib from choosing the best mask for each QR Code
            qr = qrcode.QRCode(version=version, error_correction=EC_QR[ec], mask_pattern=mask_pattern)
            qr.add_data(data)
            qr.make(fit=False)
            # Make sure the helper lib generated a QR code with the characteristics we want
            assert qr.version == version
            assert qr.error_correction == EC_QR[ec]

            # Cache generated QR Code to disk
            with open(filename, "w") as f:
                for row in qr.modules:
                    f.write(''.join(str(int(module)) for module in row))
                    f.write('\n')

        # Load reference QR Code from disk and check if we can retrieve the correct data
        my_qr = QrCodeDecoder(filename)
        assert my_qr.decode() == data
