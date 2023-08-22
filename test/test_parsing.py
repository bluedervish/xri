#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

# Copyright 2023, Nigel Small
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from unittest import TestCase

from xri import XRI


class ParsingTest(TestCase):

    cases = {

        # Examples taken from https://datatracker.ietf.org/doc/html/rfc3986#section-1.1.2
        "ftp://ftp.is.co.za/rfc/rfc1808.txt": ("ftp", "ftp.is.co.za", "/rfc/rfc1808.txt", None, None),
        "http://www.ietf.org/rfc/rfc2396.txt": ("http", "www.ietf.org", "/rfc/rfc2396.txt", None, None),
        "ldap://[2001:db8::7]/c=GB?objectClass?one": ("ldap", "[2001:db8::7]", "/c=GB", "objectClass?one", None),
        "mailto:John.Doe@example.com": ("mailto", None, "John.Doe@example.com", None, None),
        "news:comp.infosystems.www.servers.unix": ("news", None, "comp.infosystems.www.servers.unix", None, None),
        "tel:+1-816-555-1212": ("tel", None, "+1-816-555-1212", None, None),
        "telnet://192.0.2.16:80/": ("telnet", "192.0.2.16:80", "/", None, None),
        "urn:oasis:names:specification:docbook:dtd:xml:4.1.2":
            ("urn", None, "oasis:names:specification:docbook:dtd:xml:4.1.2", None, None),

        # Examples taken from https://datatracker.ietf.org/doc/html/rfc3986#section-3
        "foo://example.com:8042/over/there?name=ferret#nose":
            ("foo", "example.com:8042", "/over/there", "name=ferret", "nose"),
        "urn:example:animal:ferret:nose": ("urn", None, "example:animal:ferret:nose", None, None),

        # Examples taken from https://datatracker.ietf.org/doc/html/rfc3986#section-3.3
        "mailto:fred@example.com": ("mailto", None, "fred@example.com", None, None),
        "foo://info.example.com?fred": ("foo", "info.example.com", "", "fred", None),

        # Examples taken from https://datatracker.ietf.org/doc/html/rfc3986#section-5.4
        "http://a/b/c/d;p?q": ("http", "a", "/b/c/d;p", "q", None),

        # Examples taken from https://datatracker.ietf.org/doc/html/rfc3986#section-7.6
        "ftp://cnn.example.com&story=breaking_news@10.0.0.1/top_story.htm":
            ("ftp", "cnn.example.com&story=breaking_news@10.0.0.1", "/top_story.htm", None, None),

        # Additional examples
        "": (None, None, "", None, None),
        "filename.ext": (None, None, "filename.ext", None, None),
        "file:filename.ext": ("file", None, "filename.ext", None, None),
        "file:///path/to/filename.ext": ("file", "", "/path/to/filename.ext", None, None),
        "http://example.com": ("http", "example.com", "", None, None),
        "http://example.com/": ("http", "example.com", "/", None, None),
        "http://example.com/#bookmark": ("http", "example.com", "/", None, "bookmark"),
        "http://example.com/abc?def=ghi&jkl=mno": ("http", "example.com", "/abc", "def=ghi&jkl=mno", None),
        "http://example.com/abc?def=ghi&jkl=mno#pqr": ("http", "example.com", "/abc", "def=ghi&jkl=mno", "pqr"),
        "https://example.com/abc%20def": ("https", "example.com", "/abc def", None, None),
    }

    def test_uri_cases(self):
        for string, parts in self.cases.items():
            string = string.encode("ascii")
            parts = tuple(None if part is None else part.encode("ascii") for part in parts)
            with self.subTest(string):
                self.assertEqual(XRI(string), parts)

    def test_iri_cases(self):
        for string, parts in self.cases.items():
            with self.subTest(string):
                self.assertEqual(XRI(string), parts)


class XRICastingTest(TestCase):

    def test_str_to_iri(self):
        iri = XRI("https://example.com/a")
        self.assertIsInstance(iri, XRI)
        self.assertIsInstance(iri.path, str)

    def test_bytes_to_uri(self):
        uri = XRI(b"https://example.com/a")
        self.assertIsInstance(uri, XRI)
        self.assertIsInstance(uri.path, bytes)

    def test_bytearray_to_uri(self):
        uri = XRI(bytearray(b"https://example.com/a"))
        self.assertIsInstance(uri, XRI)
        self.assertIsInstance(uri.path, bytes)

    def test_none_to_none(self):
        none = XRI(None)
        self.assertIsNone(none)

    def test_iri_to_iri(self):
        iri0 = XRI("https://example.com/a")
        self.assertIsInstance(iri0, XRI)
        iri = XRI(iri0)
        self.assertIsInstance(iri, XRI)
        self.assertIsInstance(iri.path, str)

    def test_uri_to_uri(self):
        uri0 = XRI(b"https://example.com/a")
        self.assertIsInstance(uri0, XRI)
        uri = XRI(uri0)
        self.assertIsInstance(uri, XRI)
        self.assertIsInstance(uri.path, bytes)

    def test_unknown_type(self):
        with self.assertRaises(TypeError):
            _ = XRI(object())
