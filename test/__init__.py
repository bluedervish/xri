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


class XRITestCase(TestCase):

    def assert_components(self, xri, scheme, authority, path, query, fragment):
        self.assertEqual(xri.scheme, scheme)
        self.assertEqual(xri.authority, authority)
        self.assertEqual(xri.path, path)
        self.assertEqual(xri.query, query)
        self.assertEqual(xri.fragment, fragment)
