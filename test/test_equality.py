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


from test import XRITestCase
from xri import XRI


class EqualityTest(XRITestCase):

    def test_uri_equality(self):
        first = XRI(b"https://example.com/a")
        second = XRI(b"https://example.com/a")
        self.assertEqual(first, second)

    def test_iri_equality(self):
        first = XRI("https://example.com/a")
        second = XRI("https://example.com/a")
        self.assertEqual(first, second)

    def test_uri_to_iri_equality(self):
        first = XRI(b"https://example.com/a")
        second = XRI("https://example.com/a")
        self.assertEqual(first, second)

    def test_iri_to_uri_equality(self):
        first = XRI("https://example.com/a")
        second = XRI(b"https://example.com/a")
        self.assertEqual(first, second)


class InequalityTest(XRITestCase):

    def test_uri_inequality(self):
        first = XRI(b"https://example.com/a")
        second = XRI(b"https://example.com/b")
        self.assertNotEqual(first, second)

    def test_iri_inequality(self):
        first = XRI("https://example.com/a")
        second = XRI("https://example.com/b")
        self.assertNotEqual(first, second)

    def test_uri_to_iri_inequality(self):
        first = XRI(b"https://example.com/a")
        second = XRI("https://example.com/b")
        self.assertNotEqual(first, second)

    def test_iri_to_uri_inequality(self):
        first = XRI("https://example.com/a")
        second = XRI(b"https://example.com/b")
        self.assertNotEqual(first, second)


class HashingTest(XRITestCase):

    def test_uri_hash_equality(self):
        first = XRI(b"https://example.com/a")
        second = XRI(b"https://example.com/a")
        self.assertEqual(hash(first), hash(second))

    def test_iri_hash_equality(self):
        first = XRI("https://example.com/a")
        second = XRI("https://example.com/a")
        self.assertEqual(hash(first), hash(second))

    def test_uri_to_iri_hash_equality(self):
        first = XRI(b"https://example.com/a")
        second = XRI("https://example.com/a")
        self.assertEqual(hash(first), hash(second))

    def test_iri_to_uri_hash_equality(self):
        first = XRI("https://example.com/a")
        second = XRI(b"https://example.com/a")
        self.assertEqual(hash(first), hash(second))

    def test_uri_to_string_hash_equality(self):
        first = XRI(b"https://example.com/a")
        second = "https://example.com/a"
        self.assertEqual(hash(first), hash(second))

    def test_iri_to_string_hash_equality(self):
        first = XRI("https://example.com/a")
        second = "https://example.com/a"
        self.assertEqual(hash(first), hash(second))


class FuzzyEqualityTest(XRITestCase):

    def test_uri_equality(self):
        first = XRI(b"https://example.com/a")
        second = XRI(b"http://example.com/a/")
        self.assertTrue(first.equals(second, http_equals_https=True, ignore_trailing_slash=True))

    def test_iri_equality(self):
        first = XRI("https://example.com/a")
        second = XRI("http://example.com/a/")
        self.assertTrue(first.equals(second, http_equals_https=True, ignore_trailing_slash=True))

    def test_uri_to_iri_equality(self):
        first = XRI(b"https://example.com/a")
        second = XRI("http://example.com/a/")
        self.assertTrue(first.equals(second, http_equals_https=True, ignore_trailing_slash=True))

    def test_iri_to_uri_equality(self):
        first = XRI("https://example.com/a")
        second = XRI(b"http://example.com/a/")
        self.assertTrue(first.equals(second, http_equals_https=True, ignore_trailing_slash=True))
