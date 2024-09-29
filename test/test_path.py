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


class URIPathTest(TestCase):

    def test_null_path_is_empty(self):
        self.assertFalse(URI.Path())

    def test_empty_path_is_empty(self):
        self.assertFalse(URI.Path(""))

    def test_root_path_is_not_empty(self):
        self.assertTrue(URI.Path("/"))

    def test_non_empty_relative_path_is_not_empty(self):
        self.assertTrue(URI.Path("a"))

    def test_non_empty_absolute_path_is_not_empty(self):
        self.assertTrue(URI.Path("/a"))

    def test_null_path_is_not_absolute(self):
        self.assertFalse(URI.Path().is_absolute())

    def test_empty_path_is_not_absolute(self):
        self.assertFalse(URI.Path("").is_absolute())

    def test_root_path_is_absolute(self):
        self.assertTrue(URI.Path("/").is_absolute())

    def test_non_empty_relative_path_is_not_absolute(self):
        self.assertFalse(URI.Path("a").is_absolute())

    def test_non_empty_absolute_path_is_absolute(self):
        self.assertTrue(URI.Path("/a").is_absolute())


class IRIPathTest(TestCase):

    def test_null_path_is_empty(self):
        self.assertFalse(IRI.Path())

    def test_empty_path_is_empty(self):
        self.assertFalse(IRI.Path(""))

    def test_root_path_is_not_empty(self):
        self.assertTrue(IRI.Path("/"))

    def test_non_empty_relative_path_is_not_empty(self):
        self.assertTrue(IRI.Path("a"))

    def test_non_empty_absolute_path_is_not_empty(self):
        self.assertTrue(IRI.Path("/a"))

    def test_null_path_is_not_absolute(self):
        self.assertFalse(IRI.Path().is_absolute())

    def test_empty_path_is_not_absolute(self):
        self.assertFalse(IRI.Path("").is_absolute())

    def test_root_path_is_absolute(self):
        self.assertTrue(IRI.Path("/").is_absolute())

    def test_non_empty_relative_path_is_not_absolute(self):
        self.assertFalse(IRI.Path("a").is_absolute())

    def test_non_empty_absolute_path_is_absolute(self):
        self.assertTrue(IRI.Path("/a").is_absolute())
