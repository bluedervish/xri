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


from collections import namedtuple


VERSION = "0.0.0"


_CHARS = [chr(i).encode("iso-8859-1") for i in range(256)]
_PCT_ENCODED_CHARS = [f"%{i:02X}".encode("ascii") for i in range(256)]

RESERVED_CHARS = b"!#$&'()*+,/:;=?@[]"                  # RFC 3986 § 2.2
UNRESERVED_CHARS = (b"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    b"abcdefghijklmnopqrstuvwxyz"
                    b"0123456789-._~")                  # RFC 3986 § 2.3


def pct_encode(string, safe=b""):
    r""" Percent encode a string of data, optionally keeping certain
    characters unencoded.

    This function implements the percent encoding mechanism described in
    section 2 of RFC 3986. For the corresponding decode function, see
    `pct_decode`.

    The default input and output types are bytes (or bytearrays). Strings can
    also be passed, but will be internally encoded using UTF-8 (as described in
    RFC 3987). If an alternate encoding is required, this should be applied
    before calling the function. If a string is passed as input, a string will
    also be returned as output.

    Safe characters can be passed into the function to prevent these from being
    encoded. These must be drawn from the set of reserved characters defined in
    section 2.2 of RFC 3986. Passing other characters will result in a
    ValueError. Unlike the standard library function `quote`, no characters are
    denoted as safe by default. For a compatible drop-in function, see the
    `xri.compat` module.

    As described by RFC 3986, the set of "unreserved" characters are always safe
    and will never be encoded. These are:

        A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
        a b c d e f g h i j k l m n o p q r s t u v w x y z
        0 1 2 3 4 5 6 7 8 9 - . _ ~

    The "reserved" characters are used as delimiters in many URI schemes, and will
    not be encoded unless explicitly marked as safe. These are:

        ! # $ & ' ( ) * + , / : ; = ? @ [ ]

    Other characters within the ASCII range will always be encoded:

        «00»..«1F» «SP» " % < > \ ^ ` { | } «DEL»

    Extended single byte characters («80»..«FF») fall outside of the ASCII range
    and are therefore always encoded as they do not have a default representation.
    In many cases, these will constitute part of a multi-byte UTF-8 sequence.

    :param string:
        The str, bytes or bytearray value to be encoded. If this is a Unicode
        string, then UTF-8 encoding is applied before processing.
    :param safe:
        Characters which should not be encoded. These can be selected from the
        reserved set of characters as defined in RFC3986§2.2 and passed as
        either strings or bytes. Any characters from the reserved set that are
        not denoted here as "safe" will be encoded. Any characters added to
        the safe list which are not in the RFC reserved set will trigger a
        ValueError.
    :return:
        The return value will either be a string or a bytes instance depending
        on the input value supplied.

    """
    if isinstance(string, (bytes, bytearray)):
        if isinstance(safe, str):
            safe = safe.encode("utf-8")
        if not isinstance(safe, (bytes, bytearray)):
            raise TypeError(f"Unsupported type for safe characters {type(safe)}")
        bad_safe_chars = bytes(ch for ch in safe if ch not in RESERVED_CHARS)
        if bad_safe_chars:
            raise ValueError(f"Safe characters must be in the set \"!#$&'()*+,/:;=?@[]\" "
                             f"(found {bad_safe_chars!r})")
        safe += UNRESERVED_CHARS
        return b"".join(_CHARS[ch] if ch in safe else _PCT_ENCODED_CHARS[ch]
                        for ch in string)
    elif isinstance(string, str):
        return pct_encode(string.encode("utf-8"), safe=safe).decode("utf-8")
    elif string is None:
        return None
    else:
        raise TypeError(f"Unsupported input type {type(string)}")


def pct_decode(string):
    """ Percent decode a string of data.

    TODO: docs

    """
    if isinstance(string, (bytes, bytearray)):
        out = []
        p = 0
        size = len(string)
        while p < size:
            q = string.find(b"%", p)
            if q == -1:
                out.append(string[p:])
                p = size + 1
            else:
                out.append(string[p:q])
                p = q + 3
                char_hex = string[(q + 1):p]
                if len(char_hex) < 2:
                    raise ValueError(f"Illegal percent-encoded octet '%{char_hex}' at index {q} "
                                     f"(premature end of string)")
                try:
                    char_code = int(char_hex, 16)
                except ValueError:
                    raise ValueError(f"Illegal percent-encoded octet '%{char_hex}' at index {q}")
                else:
                    out.append(_CHARS[char_code])
        return b"".join(out)
    elif isinstance(string, str):
        return pct_decode(string.encode("utf-8")).decode("utf-8")
    elif string is None:
        return None
    else:
        raise TypeError(f"Unsupported input type {type(string)}")


URI = namedtuple("URI", ["scheme", "authority", "path", "query", "fragment"])
IRI = namedtuple("IRI", ["scheme", "authority", "path", "query", "fragment"])


_URI_SYMBOLS = type("URISymbols", (), {
    "EMPTY": b"",
    "SLASH": b"/",
    "DOT_SLASH": b"./",
    "DOT_DOT_SLASH": b"../",
    "SLASH_DOT_SLASH": b"/./",
    "SLASH_DOT_DOT_SLASH": b"/../",
    "SLASH_DOT_DOT": b"/..",
    "SLASH_DOT": b"/.",
    "DOT": b".",
    "DOT_DOT": b"..",
    "COLON": b":",
    "QUERY": b"?",
    "HASH": b"#",
    "SLASH_SLASH": b"//",
})()

_IRI_SYMBOLS = type("IRISymbols", (), {
    "EMPTY": "",
    "SLASH": "/",
    "DOT_SLASH": "./",
    "DOT_DOT_SLASH": "../",
    "SLASH_DOT_SLASH": "/./",
    "SLASH_DOT_DOT_SLASH": "/../",
    "SLASH_DOT_DOT": "/..",
    "SLASH_DOT": "/.",
    "DOT": ".",
    "DOT_DOT": "..",
    "COLON": ":",
    "QUERY": "?",
    "HASH": "#",
    "SLASH_SLASH": "//",
})()


def _parse(string, symbols):
    # TODO: strict
    #   scheme to lower case, check pattern: (a-z)(a-z|0-9|+|.|-)*
    scheme, colon, scheme_specific_part = string.partition(symbols.COLON)
    if not colon:
        scheme, scheme_specific_part = None, scheme
    auth_path_query, hash_sign, fragment = scheme_specific_part.partition(symbols.HASH)
    if not hash_sign:
        fragment = None
    hierarchical_part, question_mark, query = auth_path_query.partition(symbols.QUERY)
    if not question_mark:
        query = None
    if hierarchical_part.startswith(symbols.SLASH_SLASH):
        hierarchical_part = hierarchical_part[2:]
        try:
            slash = hierarchical_part.index(symbols.SLASH)
        except ValueError:
            authority = hierarchical_part
            path = symbols.EMPTY
        else:
            authority = hierarchical_part[:slash]
            path = hierarchical_part[slash:]
    else:
        authority = None
        path = hierarchical_part
    return scheme, authority, path, query, fragment


def xri(value):
    """ Create a URI or IRI based on a given `value`.

    If the value is already a URI value, an IRI value, or None, this is
    returned directly without change. If the value is a `str` object then
    an IRI is generated by parsing that string; similarly, a `bytes` or
    `bytearray` object is parsed to create a URI.

    :param value:
    :return: URI or IRI value
    :raise TypeError: if the supplied value is not of a supported type
    """
    if isinstance(value, (URI, IRI)):
        return value
    elif isinstance(value, str):
        return IRI(*_parse(value, _IRI_SYMBOLS))
    elif isinstance(value, (bytes, bytearray)):
        return URI(*_parse(value, _URI_SYMBOLS))
    elif value is None:
        return None
    else:
        raise TypeError("Resource identifier must be of a string type")


def validate_scheme(string):
    raise NotImplementedError  # TODO


def _resolve(base, ref, strict, symbols):
    """ Transform a reference relative to this URI to produce a full target
    URI.

    :param base:
    :param ref:
    :param strict:
    :param symbols:

    .. seealso::
        `RFC 3986 § 5.2.2`_

    .. _`RFC 3986 § 5.2.2`: http://tools.ietf.org/html/rfc3986#section-5.2.2
    """
    if not strict and ref.scheme == base.scheme:
        ref_scheme = None
    else:
        ref_scheme = ref.scheme
    if ref_scheme is not None:
        scheme = ref_scheme
        authority = ref.authority
        path = _remove_dot_segments(ref.path, symbols)
        query = ref.query
    else:
        if ref.authority is not None:
            authority = ref.authority
            path = _remove_dot_segments(ref.path, symbols)
            query = ref.query
        else:
            if not ref.path:
                path = base.path
                if ref.query is not None:
                    query = ref.query
                else:
                    query = base.query
            else:
                if ref.path.startswith(symbols.SLASH):
                    path = _remove_dot_segments(ref.path, symbols)
                else:
                    path = _merge_path(base.authority, base.path, ref.path, symbols)
                    path = _remove_dot_segments(path, symbols)
                query = ref.query
            authority = base.authority
        scheme = base.scheme
    fragment = ref.fragment
    return scheme, authority, path, query, fragment


URI.resolve = lambda base, ref, strict=True: URI(*_resolve(base, xri(ref), strict, _URI_SYMBOLS))
IRI.resolve = lambda base, ref, strict=True: IRI(*_resolve(base, xri(ref), strict, _IRI_SYMBOLS))


def _merge_path(authority, path, relative_path_ref, symbols):
    """ Implementation of RFC3986, section 5.2.3

    https://datatracker.ietf.org/doc/html/rfc3986#section-5.2.3

    :param authority:
    :param path:
    :param relative_path_ref:
    :return:
    """
    if authority is not None and not path:
        return symbols.SLASH + relative_path_ref
    else:
        try:
            last_slash = path.rindex(symbols.SLASH)
        except ValueError:
            return relative_path_ref
        else:
            return path[:(last_slash + 1)] + relative_path_ref


def _remove_dot_segments(path, symbols):
    """ Implementation of RFC3986, section 5.2.4
    """
    new_path = symbols.EMPTY
    while path:
        if path.startswith(symbols.DOT_DOT_SLASH):
            path = path[3:]
        elif path.startswith(symbols.DOT_SLASH):
            path = path[2:]
        elif path.startswith(symbols.SLASH_DOT_SLASH):
            path = path[2:]
        elif path == symbols.SLASH_DOT:
            path = symbols.SLASH
        elif path.startswith(symbols.SLASH_DOT_DOT_SLASH):
            path = path[3:]
            new_path = new_path.rpartition(symbols.SLASH)[0]
        elif path == symbols.SLASH_DOT_DOT:
            path = symbols.SLASH
            new_path = new_path.rpartition(symbols.SLASH)[0]
        elif path in (symbols.DOT, symbols.DOT_DOT):
            path = symbols.EMPTY
        else:
            if path.startswith(symbols.SLASH):
                path = path[1:]
                new_path += symbols.SLASH
            seg, slash, path = path.partition(symbols.SLASH)
            new_path += seg
            path = slash + path
    return new_path


def _compose(uri, symbols):
    """ Implementation of RFC3986, section 5.3

    :return:
    """
    parts = []
    if uri.scheme is not None:
        parts.append(uri.scheme)
        parts.append(symbols.COLON)
    if uri.authority is not None:
        parts.append(symbols.SLASH_SLASH)
        parts.append(uri.authority)
    parts.append(uri.path)
    if uri.query is not None:
        parts.append(symbols.QUERY)
        parts.append(uri.query)
    if uri.fragment is not None:
        parts.append(symbols.HASH)
        parts.append(uri.fragment)
    return parts


URI.__bytes__ = lambda self: b"".join(_compose(self, _URI_SYMBOLS))
URI.__str__ = lambda self: b"".join(_compose(self, _URI_SYMBOLS)).decode("ascii")
URI.__repr__ = lambda self: f'<{b"".join(_compose(self, _URI_SYMBOLS)).decode("ascii")}>'
IRI.__bytes__ = lambda self: "".join(_compose(self, _IRI_SYMBOLS)).encode("utf-8")
IRI.__str__ = lambda self: "".join(_compose(self, _IRI_SYMBOLS))
IRI.__repr__ = lambda self: f'«{"".join(_compose(self, _IRI_SYMBOLS))}»'
