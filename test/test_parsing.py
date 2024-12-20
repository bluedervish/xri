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

from xri import URI, IRI
from xri._util import to_bytes, to_str
from .fixtures import component_fixtures


class URIParseTestCase(TestCase):

    def test_parsing_uri_from_str(self):
        for string, parts in component_fixtures.items():
            parts = tuple(None if part is None else part.encode("ascii") for part in parts)
            with self.subTest(string):
                parsed = URI.parse(to_str(string))
                self.assertEqual(parts[0], parsed["scheme"])
                self.assertEqual(parts[1], parsed["authority"])
                self.assertEqual(parts[2], parsed["path"])
                self.assertEqual(parts[3], parsed["query"])
                self.assertEqual(parts[4], parsed["fragment"])

    def test_parsing_uri_from_bytes(self):
        for string, parts in component_fixtures.items():
            parts = tuple(None if part is None else part.encode("ascii") for part in parts)
            with self.subTest(string):
                parsed = URI.parse(to_bytes(string))
                self.assertEqual(parts[0], parsed["scheme"])
                self.assertEqual(parts[1], parsed["authority"])
                self.assertEqual(parts[2], parsed["path"])
                self.assertEqual(parts[3], parsed["query"])
                self.assertEqual(parts[4], parsed["fragment"])

    def test_parsing_uri_from_bytearray(self):
        for string, parts in component_fixtures.items():
            parts = tuple(None if part is None else part.encode("ascii") for part in parts)
            with self.subTest(string):
                parsed = URI.parse(bytearray(to_bytes(string)))
                self.assertEqual(parts[0], parsed["scheme"])
                self.assertEqual(parts[1], parsed["authority"])
                self.assertEqual(parts[2], parsed["path"])
                self.assertEqual(parts[3], parsed["query"])
                self.assertEqual(parts[4], parsed["fragment"])


class IRIParseTestCase(TestCase):

    def test_parsing_iri_from_str(self):
        for string, parts in component_fixtures.items():
            with self.subTest(string):
                parsed = IRI.parse(to_str(string))
                self.assertEqual(parts[0], parsed["scheme"])
                self.assertEqual(parts[1], parsed["authority"])
                self.assertEqual(parts[2], parsed["path"])
                self.assertEqual(parts[3], parsed["query"])
                self.assertEqual(parts[4], parsed["fragment"])

    def test_parsing_iri_from_bytes(self):
        for string, parts in component_fixtures.items():
            with self.subTest(string):
                parsed = IRI.parse(to_bytes(string))
                self.assertEqual(parts[0], parsed["scheme"])
                self.assertEqual(parts[1], parsed["authority"])
                self.assertEqual(parts[2], parsed["path"])
                self.assertEqual(parts[3], parsed["query"])
                self.assertEqual(parts[4], parsed["fragment"])

    def test_parsing_iri_from_bytearray(self):
        for string, parts in component_fixtures.items():
            with self.subTest(string):
                parsed = IRI.parse(bytearray(to_bytes(string)))
                self.assertEqual(parts[0], parsed["scheme"])
                self.assertEqual(parts[1], parsed["authority"])
                self.assertEqual(parts[2], parsed["path"])
                self.assertEqual(parts[3], parsed["query"])
                self.assertEqual(parts[4], parsed["fragment"])
