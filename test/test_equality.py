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


class TypeEquivalenceTestCase(TestCase):

    def test_equal_bytes_and_bytes(self):
        first = b"https://example.com/a"
        second = b"https://example.com/a"
        self.assertTrue(URI.equal(first, second))
        self.assertTrue(IRI.equal(first, second))

    def test_equal_str_and_str(self):
        first = "https://example.com/a"
        second = "https://example.com/a"
        self.assertTrue(URI.equal(first, second))
        self.assertTrue(IRI.equal(first, second))

    def test_equal_bytes_and_str(self):
        first = b"https://example.com/a"
        second = "https://example.com/a"
        self.assertTrue(URI.equal(first, second))
        self.assertTrue(URI.equal(second, first))
        self.assertTrue(IRI.equal(first, second))
        self.assertTrue(IRI.equal(second, first))

    def test_almost_equal_bytes_and_bytes(self):
        first = b"https://example.com/a"
        second = b"http://example.com/a/"
        self.assertTrue(URI.equal(first, second, http_equals_https=True, ignore_trailing_slash=True))
        self.assertTrue(URI.equal(second, first, http_equals_https=True, ignore_trailing_slash=True))
        self.assertTrue(IRI.equal(first, second, http_equals_https=True, ignore_trailing_slash=True))
        self.assertTrue(IRI.equal(second, first, http_equals_https=True, ignore_trailing_slash=True))

    def test_almost_equal_str_and_str(self):
        first = "https://example.com/a"
        second = "http://example.com/a/"
        self.assertTrue(URI.equal(first, second, http_equals_https=True, ignore_trailing_slash=True))
        self.assertTrue(URI.equal(second, first, http_equals_https=True, ignore_trailing_slash=True))
        self.assertTrue(IRI.equal(first, second, http_equals_https=True, ignore_trailing_slash=True))
        self.assertTrue(IRI.equal(second, first, http_equals_https=True, ignore_trailing_slash=True))

    def test_almost_equal_bytes_and_str(self):
        first = b"https://example.com/a"
        second = "http://example.com/a/"
        self.assertTrue(URI.equal(first, second, http_equals_https=True, ignore_trailing_slash=True))
        self.assertTrue(URI.equal(second, first, http_equals_https=True, ignore_trailing_slash=True))
        self.assertTrue(IRI.equal(first, second, http_equals_https=True, ignore_trailing_slash=True))
        self.assertTrue(IRI.equal(second, first, http_equals_https=True, ignore_trailing_slash=True))

    def test_almost_equal_str_and_bytes(self):
        first = "https://example.com/a"
        second = b"http://example.com/a/"
        self.assertTrue(URI.equal(first, second, http_equals_https=True, ignore_trailing_slash=True))
        self.assertTrue(URI.equal(second, first, http_equals_https=True, ignore_trailing_slash=True))
        self.assertTrue(IRI.equal(first, second, http_equals_https=True, ignore_trailing_slash=True))
        self.assertTrue(IRI.equal(second, first, http_equals_https=True, ignore_trailing_slash=True))


class InequalityTest(TestCase):

    def test_unequal_bytes_and_bytes(self):
        first = b"https://example.com/a"
        second = b"https://example.com/b"
        self.assertFalse(URI.equal(first, second))
        self.assertFalse(IRI.equal(first, second))

    def test_unequal_str_and_str(self):
        first = "https://example.com/a"
        second = "https://example.com/b"
        self.assertFalse(URI.equal(first, second))
        self.assertFalse(IRI.equal(first, second))

    def test_unequal_bytes_and_str(self):
        first = b"https://example.com/a"
        second = "https://example.com/b"
        self.assertFalse(URI.equal(first, second))
        self.assertFalse(IRI.equal(first, second))

    def test_unequal_str_and_bytes(self):
        first = "https://example.com/a"
        second = b"https://example.com/b"
        self.assertFalse(URI.equal(first, second))
        self.assertFalse(IRI.equal(first, second))
