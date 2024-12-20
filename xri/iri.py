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


from .uri import URI
from ._util import to_str


TO_PCT_ENCODED_PRINTABLE = str.maketrans(dict(zip(
    (chr(i) for i in range(256)),
    (chr(i) if 33 <= i <= 126 or i >= 160 else f"%{i:02X}" for i in range(256)),
)))


class IRI(URI):

    @classmethod
    def normalize(cls, value):
        str_value = to_str(value)
        return str_value.translate(TO_PCT_ENCODED_PRINTABLE)

    @classmethod
    def is_unreserved(cls, code):
        """ RFC 3987 § 2.2
        """
        return (super().is_unreserved(code) or
                0x00A0 <= code <= 0xD7FF or
                0xF900 <= code <= 0xFDCF or
                0xFDF0 <= code <= 0xFFEF or
                0x10000 <= code <= 0x1FFFD or
                0x20000 <= code <= 0x2FFFD or
                0x30000 <= code <= 0x3FFFD or
                0x40000 <= code <= 0x4FFFD or
                0x50000 <= code <= 0x5FFFD or
                0x60000 <= code <= 0x6FFFD or
                0x70000 <= code <= 0x7FFFD or
                0x80000 <= code <= 0x8FFFD or
                0x90000 <= code <= 0x9FFFD or
                0xA0000 <= code <= 0xAFFFD or
                0xB0000 <= code <= 0xBFFFD or
                0xC0000 <= code <= 0xCFFFD or
                0xD0000 <= code <= 0xDFFFD or
                0xE1000 <= code <= 0xEFFFD)
