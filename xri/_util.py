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


def to_bytes(value) -> bytes:
    """ Coerce value to bytes, assuming UTF-8 encoding if appropriate.

    >>> to_bytes(None)
    b''
    >>> to_bytes("café")
    b'caf\xC3\xA9'
    >>> to_bytes(b"abc")
    b'abc'
    >>> to_bytes(123)
    b'123'
    >>> to_bytes(12.3)
    b'12.3'

    """
    if not value:
        return b""
    elif isinstance(value, (bytes, bytearray)):
        return bytes(value)
    elif isinstance(value, int):
        return str(value).encode("utf-8")
    else:
        try:
            return value.encode("utf-8")
        except (AttributeError, UnicodeEncodeError):
            try:
                return bytes(value)
            except TypeError:
                return str(value).encode("utf-8")


def to_str(value) -> str:
    """ Coerce value to a string, assuming UTF-8 encoding if appropriate.

    >>> to_str(None)
    ''
    >>> to_str("café")
    'café'
    >>> to_str(b"abc")
    'abc'
    >>> to_str(123)
    '123'
    >>> to_str(12.3)
    '12.3'

    """
    if not value:
        return ""
    elif isinstance(value, str):
        return value
    else:
        try:
            return value.decode("utf-8")
        except (AttributeError, UnicodeDecodeError):
            return str(value)
