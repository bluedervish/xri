from unittest import TestCase

from xri import pct_encode


class PercentEncodingTest(TestCase):

    cases = {
        "": "",
        "Laguna Beach": "Laguna%20Beach",
        "20% of $100 = $20": "20%25%20of%20%24100%20%3D%20%2420",
    }

    def test_uri_cases(self):
        for string, expected in self.cases.items():
            string = string.encode("ascii")
            with self.subTest(string):
                self.assertEqual(pct_encode(string), expected.encode("ascii"))

    def test_iri_cases(self):
        for string, expected in self.cases.items():
            with self.subTest(string):
                self.assertEqual(pct_encode(string), expected)

    # TODO: implement tests based on:
    #   reserved (2.2) - encode unless marked safe:
    #     !#$&'()*+,/:;=?@[]
    #   unreserved (2.3) - never encode:
    #     ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~
    #   other ASCII - always encode:
    #     <00>..<1F> <SP> "%<>\^`{|} <DEL>
    #   other single byte (0x80-0xFF) - always encode, assumed to be part of extended char set
    #   other multi-byte (0x0100-0x10FFFF): convert to UTF-8, then encode
