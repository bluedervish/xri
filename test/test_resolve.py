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


from unittest import TestCase, skip

from xri import XRI


@skip
class ResolutionTest(TestCase):
    """
    See: https://datatracker.ietf.org/doc/html/rfc3986#section-5.4
    """

    base = "http://a/b/c/d;p?q"

    # Taken from https://datatracker.ietf.org/doc/html/rfc3986#section-5.4.1
    normal_examples = {
        "g:h": ("g", None, "h", None, None),
        "g": ("http", "a", "/b/c/g", None, None),
        "./g": ("http", "a", "/b/c/g", None, None),
        "g/": ("http", "a", "/b/c/g/", None, None),
        "/g": ("http", "a", "/g", None, None),
        "//g": ("http", "g", "", None, None),
        "?y": ("http", "a", "/b/c/d;p", "y", None),
        "g?y": ("http", "a", "/b/c/g", "y", None),
        "#s": ("http", "a", "/b/c/d;p", "q", "s"),
        "g#s": ("http", "a", "/b/c/g", None, "s"),
        "g?y#s": ("http", "a", "/b/c/g", "y", "s"),
        ";x": ("http", "a", "/b/c/;x", None, None),
        "": ("http", "a", "/b/c/d;p", "q", None),
        ".": ("http", "a", "/b/c/", None, None),
        "./": ("http", "a", "/b/c/", None, None),
        "..": ("http", "a", "/b/", None, None),
        "../": ("http", "a", "/b/", None, None),
        "../g": ("http", "a", "/b/g", None, None),
        "../..": ("http", "a", "/", None, None),
        "../../": ("http", "a", "/", None, None),
        "../../g": ("http", "a", "/g", None, None),
    }

    # Taken from https://datatracker.ietf.org/doc/html/rfc3986#section-5.4.2
    abnormal_examples = {
        "../../../g": ("http", "a", "/g", None, None),
        "../../../../g": ("http", "a", "/g", None, None),
        "/./g": ("http", "a", "/g", None, None),
        "/../g": ("http", "a", "/g", None, None),
        "g.": ("http", "a", "/b/c/g.", None, None),
        ".g": ("http", "a", "/b/c/.g", None, None),
        "g..": ("http", "a", "/b/c/g..", None, None),
        "..g": ("http", "a", "/b/c/..g", None, None),
        "./../g": ("http", "a", "/b/g", None, None),
        "./g/.": ("http", "a", "/b/c/g/", None, None),
        "g/./h": ("http", "a", "/b/c/g/h", None, None),
        "g/../h": ("http", "a", "/b/c/h", None, None),
        "g;x=1/./y": ("http", "a", "/b/c/g;x=1/y", None, None),
        "g;x=1/../y": ("http", "a", "/b/c/y", None, None),
        "g?y/./x": ("http", "a", "/b/c/g", "y/./x", None),
        "g?y/../x": ("http", "a", "/b/c/g", "y/../x", None),
        "g#s/./x": ("http", "a", "/b/c/g", None, "s/./x"),
        "g#s/../x": ("http", "a", "/b/c/g", None, "s/../x"),
    }

    def test_uri_normal_examples(self):
        base = XRI(self.base.encode("ascii"))
        for string, parts in self.normal_examples.items():
            string = string.encode("ascii")
            parts = tuple(None if part is None else part.encode("ascii") for part in parts)
            with self.subTest(string):
                self.assertEqual(base.resolve(string), parts)

    def test_iri_normal_examples(self):
        base = XRI(self.base)
        for string, parts in self.normal_examples.items():
            with self.subTest(string):
                self.assertEqual(base.resolve(string), parts)

    def test_uri_abnormal_examples(self):
        base = XRI(self.base.encode("ascii"))
        for string, parts in self.abnormal_examples.items():
            string = string.encode("ascii")
            parts = tuple(None if part is None else part.encode("ascii") for part in parts)
            with self.subTest(string):
                self.assertEqual(base.resolve(string), parts)

    def test_iri_abnormal_examples(self):
        base = XRI(self.base)
        for string, parts in self.abnormal_examples.items():
            with self.subTest(string):
                self.assertEqual(base.resolve(string), parts)

    def test_uri_strict_true(self):
        base = XRI(self.base.encode("ascii"))
        self.assertEqual(base.resolve(b"http:g", strict=True), (b"http", None, b"g", None, None))

    def test_uri_strict_false(self):
        base = XRI(self.base.encode("ascii"))
        self.assertEqual(base.resolve(b"http:g", strict=False), (b"http", b"a", b"/b/c/g", None, None))

    def test_iri_strict_true(self):
        base = XRI(self.base)
        self.assertEqual(base.resolve("http:g", strict=True), ("http", None, "g", None, None))

    def test_iri_strict_false(self):
        base = XRI(self.base)
        self.assertEqual(base.resolve("http:g", strict=False), ("http", "a", "/b/c/g", None, None))
