from unittest import TestCase
from geo_converter import parse_various_formats, convert_all_coordinates, decimal_to_dms, coords_to_dms_format


class TestCoordinateConversion(TestCase):
    def test_decimal_to_dms(self):
        self.assertEqual(decimal_to_dms(49.123456), '49:07:24 N')
        self.assertEqual(decimal_to_dms(-75.123456, is_longitude=True), '075:07:24 W')
        self.assertEqual(decimal_to_dms(0), '00:00:00 N')
        # self.assertEqual(decimal_to_dms(180), '00:00:00 N') # test exceeding max_longitude and max_latitude

    def test_parse_various_formats(self):
        self.assertAlmostEquals(parse_various_formats('501347,71N0132453,65E'), (50.22991944444445, 13.414902777777778))
        self.assertAlmostEquals(parse_various_formats('N50°16\'36" E017°51\'56"'), (50.276666666666664, 17.865555555555556))
        self.assertAlmostEqual(parse_various_formats('490246,96N0164248,91E'), (49.04637777777778, 16.71358611111111))
        self.assertAlmostEqual(parse_various_formats('49 02 40,66 N 014 09 25,97 E'), (49.04462777777778, 14.15721388888889))

    def test_coords_to_dms_format(self):
        self.assertEquals(coords_to_dms_format(50.22991944444445, 13.414902777777778),('50:13:48 N 013:24:54 E'))


    def test_convert_all_coordinates(self):
        test_pairs = [
                ["""1. OP Benkov (49.7689256N, 17.0833339E)
                Horizontální rozsah: 6NM
                Vertikální rozsah: GND-FL95
                V čase: 17.8.2023 10:00-15:00 LT (8:00-13:00 UTC)
                2. Rybníček (49.7674703N, 17.1972742E)
                Horizontální rozsah: 6NM
                Vertikální rozsah: GND-FL95
                V čase: 17.8.2023 10:00-15:00 LT (8:00-13:00 UTC)""", #input1
                    ['49:46:08 N 017:05:00 E', '49:46:03 N 017:11:50 E'] #output1
                 ], # end of test_pair
                ["""Horizontální hranice: 0 PSN 494255,11N0163512,61E (1.6NM NE POHLEDY) - 1 PSN 492732,96N0164248,91E (0.6NM N NEMCICE) - 2 PSN 492530,09N0163303,64E (1.1NM N ZERNOVNIK) - 3 PSN 493044,56N0160640,45E (1.1NM E RADESINSKA SVRATKA) - 4 PSN 493335,75N0161318,88E (0.7NM SW PISECNE) - 5 PSN 493737,38N0162244,16E (1.2NM W SVOJANOV) - 6 PSN 494255,11N0163512,61E (1.6NM NE POHLEDY). Horizontální hranice prostoru shodná s LKTRA33.""",
                    ['49:42:55 N 016:35:13 E','49:27:33 N 016:42:49 E','49:25:30 N 016:33:04 E','49:30:45 N 016:06:40 E','49:33:36 N 016:13:19 E','49:37:37 N 016:22:44 E','49:42:55 N 016:35:13 E']
                 ], # end of test_pair
                ["""49 02 40,66 N 014 09 25,97 E -
                    49 02 40,62 N 014 18 55,71 E -
                    48 57 46,97 N 014 33 08,04 E -
                    48 57 44,42 N 014 49 35,66 E -
                    48 49 46,08 N 014 49 33,34 E -
                    48 49 46,99 N 014 33 31,15 E -
                    48 51 27,67 N 014 20 26,51 E -
                    48 55 46,37 N 014 11 35,05 E -
                    48 55 45,98 N 014 07 59,82 E -
                    49 01 56,84 N 014 07 58,47 E -
                    49 02 40,66 N 014 09 25,97 E""",
                    ['49:02:41 N 014:09:26 E', '49:02:41 N 014:18:56 E', '48:57:47 N 014:33:08 E', '48:57:44 N 014:49:36 E', '48:49:46 N 014:49:33 E', '48:49:47 N 014:33:31 E', '48:51:28 N 014:20:27 E', '48:55:46 N 014:11:35 E', '48:55:46 N 014:07:60 E', '49:01:57 N 014:07:58 E', '49:02:41 N 014:09:26 E']
                ], # end of test pair
                ["""ARP: 40° 48' 51" N, 15° 12' 06" E ARP: 41° 48' 51" N, 15° 12' 06" E ARP: 42° 48' 51" N, 15° 12' 06" E """,
                    ['40:48:51 N 015:12:06 E', '41:48:51 N 015:12:06 E', '42:48:51 N 015:12:06 E']
                ]# end of test_pair
        ]
        for pair in test_pairs:
            self.assertEquals(convert_all_coordinates(pair[0]), pair[1])


if __name__ == '__main__':
    unittest.main()