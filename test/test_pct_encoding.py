from unittest import TestCase

from xri import RESERVED_CHARS, UNRESERVED_CHARS, pct_encode, pct_decode


class PercentEncodingTest(TestCase):

    # Encoding rules:
    #   reserved (2.2) - encode unless marked safe:
    #     !#$&'()*+,/:;=?@[]
    #   unreserved (2.3) - never encode:
    #     ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~
    #   other ASCII - always encode:
    #     <00>..<1F> <SP> "%<>\^`{|} <DEL>
    #   other single byte (0x80-0xFF) - always encode, assumed to be part of extended char set
    #   other multi-byte (0x0100-0x10FFFF): convert to UTF-8, then encode

    cases = {
        "": "",
        "Laguna Beach": "Laguna%20Beach",
        "20% of $100 = $20": "20%25%20of%20%24100%20%3D%20%2420",
    }

    def test_reserved_chars(self):
        self.assertEqual(set(RESERVED_CHARS), set(b"!#$&'()*+,/:;=?@[]"))

    def test_unreserved_chars(self):
        self.assertEqual(set(UNRESERVED_CHARS),
                         set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"))

    def test_uri_cases(self):
        for string, expected in self.cases.items():
            string = string.encode("ascii")
            with self.subTest(string):
                self.assertEqual(pct_encode(string), expected.encode("ascii"))

    def test_iri_cases(self):
        for string, expected in self.cases.items():
            with self.subTest(string):
                self.assertEqual(pct_encode(string), expected)

    def test_bytes_returns_bytes(self):
        self.assertEqual(pct_encode(b"abc def"), b"abc%20def")

    def test_bytearray_returns_bytes(self):
        self.assertEqual(pct_encode(bytearray(b"abc def")), b"abc%20def")

    def test_str_returns_str(self):
        self.assertEqual(pct_encode("abc def"), "abc%20def")

    def test_none_returns_none(self):
        self.assertIsNone(pct_encode(None))

    def test_delimiters_are_encoded_by_default(self):
        self.assertEqual(pct_encode("https://example.com/a"), "https%3A%2F%2Fexample.com%2Fa")

    def test_delimiters_can_be_excluded_from_encoding(self):
        self.assertEqual(pct_encode("https://example.com/a", safe=":/"), "https://example.com/a")

    def test_unreserved_chars_cannot_be_encoded(self):
        with self.assertRaises(ValueError):
            _ = pct_encode("https://example.com/a", safe="a")

    def test_extended_chars_are_coerced_to_utf8(self):
        self.assertEqual(pct_encode("ä"), "%C3%A4")

    def test_other_chars_are_encoded(self):
        self.assertEqual(pct_encode(" %<>\\^`{|}\x7F"), "%20%25%3C%3E%5C%5E%60%7B%7C%7D%7F")

    def test_unknown_input_type_is_error(self):
        with self.assertRaises(TypeError):
            _ = pct_encode(object())

    def test_unknown_safe_input_type_is_error(self):
        with self.assertRaises(TypeError):
            _ = pct_encode("", safe=object())


class PercentDecodingTest(TestCase):

    cases = {
        "": "",
        "Laguna%20Beach": "Laguna Beach",
        "20%25%20of%20%24100%20%3D%20%2420": "20% of $100 = $20",
        "%4E": "N",
        "%4e": "N",
    }

    def test_uri_cases(self):
        for string, expected in self.cases.items():
            string = string.encode("ascii")
            with self.subTest(string):
                self.assertEqual(pct_decode(string), expected.encode("ascii"))

    def test_iri_cases(self):
        for string, expected in self.cases.items():
            with self.subTest(string):
                self.assertEqual(pct_decode(string), expected)

    def test_extended_char_upper_case_string(self):
        self.assertEqual(pct_decode("%C3%91"), "Ñ")

    def test_extended_char_lower_case_string(self):
        self.assertEqual(pct_decode("%c3%91"), "Ñ")

    def test_extended_char_upper_case_bytes(self):
        self.assertEqual(pct_decode(b"%C3%91"), b"\xC3\x91")

    def test_extended_char_lower_case_bytes(self):
        self.assertEqual(pct_decode(b"%c3%91"), b"\xC3\x91")

    def test_none_returns_none(self):
        self.assertIsNone(pct_decode(None))

    def test_unknown_input_type_is_error(self):
        with self.assertRaises(TypeError):
            _ = pct_decode(object())

    def test_incomplete_code_is_error_0(self):
        with self.assertRaises(ValueError):
            _ = pct_decode("%")

    def test_incomplete_code_is_error_1(self):
        with self.assertRaises(ValueError):
            _ = pct_decode("%4")

    def test_invalid_code_is_error(self):
        with self.assertRaises(ValueError):
            _ = pct_decode("%xx")
