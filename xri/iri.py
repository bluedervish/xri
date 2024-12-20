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


class IRI(URI):

    EMPTY = ""

    SLASH = "/"
    COLON = ":"
    AT = "@"
    AMPERSAND = "&"
    HASH = "#"
    QUERY = "?"
    EQUALS = "="
    DOT = "."

    SLASH_SLASH = SLASH + SLASH
    DOT_DOT = DOT + DOT
    DOT_SLASH = DOT + SLASH
    DOT_DOT_SLASH = DOT + DOT + SLASH
    SLASH_DOT = SLASH + DOT
    SLASH_DOT_SLASH = SLASH + DOT + SLASH
    SLASH_DOT_DOT = SLASH + DOT + DOT
    SLASH_DOT_DOT_SLASH = SLASH + DOT + DOT + SLASH

    @classmethod
    def stringify(cls, value):
        return to_str(value)

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
