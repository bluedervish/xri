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

from xri import URI
from .fixtures import resolver_base, normal_resolver_fixtures, abnormal_resolver_fixtures


class URIResolveTestCase(TestCase):
    """
    See: https://datatracker.ietf.org/doc/html/rfc3986#section-5.4
    """

    def test_uri_normal_examples(self):
        for string, parts in normal_resolver_fixtures.items():
            with self.subTest(string):
                resolved = URI.resolve(resolver_base, string)
                self.assertEqual(URI.compose(*parts), resolved)

    def test_uri_abnormal_examples(self):
        for string, parts in abnormal_resolver_fixtures.items():
            with self.subTest(string):
                resolved = URI.resolve(resolver_base, string)
                self.assertEqual(URI.compose(*parts), resolved)

    def test_uri_strict_true(self):
        resolved = URI.resolve(resolver_base, "http:g", strict=True)
        self.assertEqual("http:g", resolved)

    def test_uri_strict_false(self):
        resolved = URI.resolve(resolver_base, "http:g", strict=False)
        self.assertEqual("http://a/b/c/g", resolved)

    def test_base_uri_with_authority_and_no_path(self):
        resolved = URI.resolve("http://a", "b")
        self.assertEqual("http://a/b", resolved)

    def test_empty_base_uri(self):
        resolved = URI.resolve("", "a")
        self.assertEqual("a", resolved)
