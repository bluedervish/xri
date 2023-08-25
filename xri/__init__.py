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


from typing import Optional, List


VERSION = "1.0.0a1"


ALPHA_UPPER = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPHA_LOWER = b"abcdefghijklmnopqrstuvwxyz"
DIGIT = b"0123456789"

GENERAL_DELIMITERS = b":/?#[]@"
SUB_DELIMITERS = b"!$&'()*+,;="
RESERVED = GENERAL_DELIMITERS + SUB_DELIMITERS                # RFC 3986 § 2.2


_CHARS = [chr(i).encode("iso-8859-1") for i in range(256)]
_PCT_ENCODED_CHARS = [f"%{i:02X}".encode("ascii") for i in range(256)]


_SYMBOLS = {
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
    "AT": "@",
}
_BYTE_SYMBOLS = type("ByteSymbols", (), {key: value.encode("ascii") for key, value in _SYMBOLS.items()})()
_STRING_SYMBOLS = type("StringSymbols", (), _SYMBOLS)()


class XRI:

    _scheme = None
    _authority = None
    _path = b""
    _query = None
    _fragment = None

    @classmethod
    def is_unreserved(cls, code):
        raise NotImplementedError

    @classmethod
    def is_private(cls, code):
        raise NotImplementedError

    @classmethod
    def pct_encode(cls, string, safe=None):
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

        RFC 3987 extends the set of unreserved characters to also include extended
        characters outside of the ASCII range.

        The "reserved" characters are used as delimiters in many URI schemes, and will
        not be encoded unless explicitly marked as safe. These are:

            ! # $ & ' ( ) * + , / : ; = ? @ [ ]

        Other characters within the ASCII range will always be encoded:

            «00»..«1F» «SP» " % < > \ ^ ` { | } «DEL»

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
            if not safe:
                safe = b""
            elif not isinstance(safe, (bytes, bytearray)):
                raise TypeError(f"Unsupported type for safe characters {type(safe)}")
            bad_safe_chars = bytes(ch for ch in safe if ch not in RESERVED)
            if bad_safe_chars:
                raise ValueError(f"Safe characters must be in the set \"!#$&'()*+,/:;=?@[]\" "
                                 f"(found {bad_safe_chars!r})")
            return b"".join(_CHARS[ch] if ch in safe or cls.is_unreserved(ch) else _PCT_ENCODED_CHARS[ch]
                            for ch in string)
        elif isinstance(string, str):
            return cls.pct_encode(string.encode("utf-8"), safe=safe).decode("utf-8")
        elif string is None:
            return None
        else:
            raise TypeError(f"Unsupported input type {type(string)}")

    @classmethod
    def pct_decode(cls, string):
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
            return cls.pct_decode(string.encode("utf-8")).decode("utf-8")
        elif string is None:
            return None
        else:
            raise TypeError(f"Unsupported input type {type(string)}")

    def __new__(cls, value):
        if value is None:
            return None
        elif isinstance(value, cls):
            return value
        else:
            if isinstance(value, str):
                cls = IRI
            elif isinstance(value, (bytes, bytearray)):
                cls = URI
            return super().__new__(cls)

    def __init__(self, string):
        if isinstance(string, str):
            symbols = _STRING_SYMBOLS
        elif isinstance(string, (bytes, bytearray)):
            symbols = _BYTE_SYMBOLS
        else:
            raise TypeError(f"XRI value must be of a string type ({type(string)} found)")

        scheme, authority, path, query, fragment = self._parse(string, symbols)

        # TODO: strict mode (maybe)
        self.scheme = scheme
        self.authority = authority
        self.path = path
        self.query = query
        self.fragment = fragment

    def __repr__(self):
        parts = []
        if self.scheme is not None:
            parts.append(f"scheme={self.scheme!r}")
        if self.authority is not None:
            parts.append(f"authority={self.authority!r}")
        parts.append(f"path={self.path!r}")
        if self.query is not None:
            parts.append(f"query={self.query!r}")
        if self.fragment is not None:
            parts.append(f"fragment={self.fragment!r}")
        return f"<{self.__class__.__name__} {' '.join(parts)}>"

    @classmethod
    def _parse(cls, string: bytes, symbols) -> \
            (Optional[bytes], Optional[bytes], bytes, Optional[bytes], Optional[bytes]):
        """ Parse the input string into a 5-tuple.

        Percent decoding is carried out here, as opposed to when setting the individual
        properties. Only when combined as a full URI/IRI is percent encoding useful and
        therefore relevant. If we set xri.path = "abc%20def" for example, we literally
        mean "abc%20def" and not "abc def".
        """
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
        return tuple(map(cls.pct_decode, (scheme, authority, path, query, fragment)))

    @classmethod
    def _scheme_to_bytes(cls, string: bytes) -> bytes:
        """ Validate and normalise a scheme name.

        Schemes can only consist of ASCII characters, even for IRIs.
        Specifically, the subset of allowed characters is:

            A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
            a b c d e f g h i j k l m n o p q r s t u v w x y z
            0 1 2 3 4 5 6 7 8 9 + - .

        Furthermore, only letters are permitted at the start, and
        schemes cannot be empty.

        TODO: work with registered schemes at IANA?

        .. seealso::
            `RFC 3986 § 3.1`_

        .. _`RFC 3986 § 3.1`: http://tools.ietf.org/html/rfc3986#section-3.1
        """
        byte_string = bytearray(string)
        for i, b in enumerate(byte_string):
            if 0x41 <= b <= 0x5A:                                               # Upper case alpha
                byte_string[i] += 0x20                                          # (coerce to lower case)
            elif 0x61 <= b <= 0x7A:                                             # Lower case alpha
                pass                                                            # (do nothing)
            elif i == 0:
                raise ValueError(f"Invalid character {chr(b)!r} at position {i} in scheme {string!r} "
                                 f"(scheme must start with an ASCII letter A..Z or a..z)")
            elif 0x30 <= b <= 0x39 or b == 0x2B or b == 0x2D or b == 0x2E:      # Digit, '+', '-', or '.'
                pass                                                            # (do nothing)
            else:
                raise ValueError(f"Invalid character {chr(b)!r} at position {i} in scheme {string!r}")
        return bytes(byte_string)

    @classmethod
    def _authority_to_bytes(cls, string: bytes) -> bytes:
        # TODO
        return bytes(string)

    @classmethod
    def _path_to_bytes(cls, string: bytes) -> bytes:
        # Note: percent decoding is not carried out here, as it is only relevant
        # when considering the URI/IRI as a whole.
        # TODO
        return bytes(string)

    @classmethod
    def _query_to_bytes(cls, string: bytes) -> bytes:
        # TODO
        return bytes(string)

    @classmethod
    def _fragment_to_bytes(cls, string: bytes) -> bytes:
        # TODO
        return bytes(string)

    def _compose(self, symbols) -> List[bytes]:
        """ Implementation of RFC3986, section 5.3

        :return:
        """
        # TODO: percent encoding
        parts = []
        if self.scheme is not None:
            parts.append(self.scheme)
            parts.append(symbols.COLON)
        if self.authority is not None:
            parts.append(symbols.SLASH_SLASH)
            parts.append(self.authority)
        parts.append(self.path)
        if self.query is not None:
            parts.append(symbols.QUERY)
            parts.append(self.query)
        if self.fragment is not None:
            parts.append(symbols.HASH)
            parts.append(self.fragment)
        return parts

    def resolve(self, ref, strict=True):
        raise NotImplementedError


class URI(XRI):

    @classmethod
    def is_unreserved(cls, code):
        """ RFC 3986 § 2.3
        """
        return (0x41 <= code <= 0x5A or     # ABCDEFGHIJKLMNOPQRSTUVWXYZ
                0x61 <= code <= 0x7A or     # abcdefghijklmnopqrstuvwxyz
                0x30 <= code <= 0x39 or     # 0123456789
                code == 0x2D or             # -  HYPHEN-MINUS
                code == 0x2E or             # .  FULL STOP
                code == 0x5F or             # _  LOW LINE
                code == 0x7E)               # ~  TILDE

    @classmethod
    def is_private(cls, code):
        return False

    def __bytes__(self):
        return b"".join(self._compose(_BYTE_SYMBOLS))

    def __str__(self):
        return b"".join(self._compose(_BYTE_SYMBOLS)).decode("ascii")

    @property
    def scheme(self):
        return self._scheme

    @scheme.setter
    def scheme(self, value):
        """ Validate and normalise a scheme name.

        .. seealso::
            `RFC 3986 § 3.1`_

        .. _`RFC 3986 § 3.1`: http://tools.ietf.org/html/rfc3986#section-3.1
        """
        if value is None:
            self._scheme = None
        elif len(value) == 0:
            raise ValueError("Scheme cannot be an empty string (but could be None)")
        elif isinstance(value, (bytes, bytearray)):
            self._scheme = self._scheme_to_bytes(value)
        elif isinstance(value, str):
            self._scheme = self._scheme_to_bytes(value.encode("utf-8"))
        else:
            raise TypeError("Scheme must be of a string type")

    @scheme.deleter
    def scheme(self):
        self._scheme = None

    @property
    def authority(self):
        return self._authority

    @authority.setter
    def authority(self, value):
        # TODO (authority can be empty)
        if value is None:
            self._authority = None
        elif isinstance(value, (bytes, bytearray)):
            self._authority = self._authority_to_bytes(value)
        elif isinstance(value, str):
            self._authority = self._authority_to_bytes(value.encode("utf-8"))
        else:
            raise TypeError("Authority must be of a string type")

    @authority.deleter
    def authority(self):
        self._authority = None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        # TODO
        if value is None:
            raise ValueError("Path cannot be None (but could be an empty string)")
        elif isinstance(value, (bytes, bytearray)):
            self._path = self._path_to_bytes(value)
        elif isinstance(value, str):
            self._path = self._path_to_bytes(value.encode("utf-8"))
        else:
            raise TypeError("Path must be of a string type")

    @path.deleter
    def path(self):
        raise TypeError(f"All {self.__class__.__name__} objects must have a path")

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        # TODO
        if value is None:
            self._query = None
        elif len(value) == 0:
            raise ValueError("Query cannot be an empty string (but could be None)")
        elif isinstance(value, (bytes, bytearray)):
            self._query = self._query_to_bytes(value)
        elif isinstance(value, str):
            self._query = self._query_to_bytes(value.encode("utf-8"))
        else:
            raise TypeError("Query must be of a string type")

    @query.deleter
    def query(self):
        self._query = None

    @property
    def fragment(self):
        return self._fragment

    @fragment.setter
    def fragment(self, value):
        # TODO
        if value is None:
            self._fragment = None
        elif len(value) == 0:
            raise ValueError("Fragment cannot be an empty string (but could be None)")
        elif isinstance(value, (bytes, bytearray)):
            self._fragment = self._fragment_to_bytes(value)
        elif isinstance(value, str):
            self._fragment = self._fragment_to_bytes(value.encode("utf-8"))
        else:
            raise TypeError("Fragment must be of a string type")

    @fragment.deleter
    def fragment(self):
        self._fragment = None

    def resolve(self, ref, strict=True):
        raise NotImplementedError


class IRI(XRI):

    @classmethod
    def is_unreserved(cls, code):
        """ RFC 3987 § 2.2
        """
        return (URI.is_unreserved(code) or
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

    @classmethod
    def is_private(cls, code):
        return (0xE000 <= code <= 0xF8FF or
                0xF0000 <= code <= 0xFFFFD or
                0x100000 <= code <= 0x10FFFD)

    def __bytes__(self):
        return "".join(self._compose(_STRING_SYMBOLS)).encode("utf-8")

    def __str__(self):
        return "".join(self._compose(_STRING_SYMBOLS))

    @property
    def scheme(self):
        return self._scheme

    @scheme.setter
    def scheme(self, value):
        """ Validate and normalise a scheme name.

        .. seealso::
            `RFC 3986 § 3.1`_

        .. _`RFC 3986 § 3.1`: http://tools.ietf.org/html/rfc3986#section-3.1
        """
        if value is None:
            self._scheme = None
        elif len(value) == 0:
            raise ValueError("Scheme cannot be an empty string (but could be None)")
        elif isinstance(value, (bytes, bytearray)):
            self._scheme = self._scheme_to_bytes(value).decode("utf-8")
        elif isinstance(value, str):
            self._scheme = self._scheme_to_bytes(value.encode("utf-8")).decode("utf-8")
        else:
            raise TypeError("Scheme must be of a string type")

    @scheme.deleter
    def scheme(self):
        self._scheme = None

    @property
    def authority(self):
        return self._authority

    @authority.setter
    def authority(self, value):
        # TODO (authority can be empty)
        if value is None:
            self._authority = None
        elif isinstance(value, (bytes, bytearray)):
            self._authority = self._authority_to_bytes(value).decode("utf-8")
        elif isinstance(value, str):
            self._authority = self._authority_to_bytes(value.encode("utf-8")).decode("utf-8")
        else:
            raise TypeError("Authority must be of a string type")

    @authority.deleter
    def authority(self):
        self._authority = None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if value is None:
            raise ValueError("Path cannot be None (but could be an empty string)")
        elif isinstance(value, (bytes, bytearray)):
            self._path = self._path_to_bytes(value).decode("utf-8")
        elif isinstance(value, str):
            self._path = self._path_to_bytes(value.encode("utf-8")).decode("utf-8")
        else:
            raise TypeError("Path must be of a string type")

    @path.deleter
    def path(self):
        raise TypeError(f"All {self.__class__.__name__} objects must have a path")

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        # TODO
        if value is None:
            self._query = None
        elif len(value) == 0:
            raise ValueError("Query cannot be an empty string (but could be None)")
        elif isinstance(value, (bytes, bytearray)):
            self._query = self._query_to_bytes(value).decode("utf-8")
        elif isinstance(value, str):
            self._query = self._query_to_bytes(value.encode("utf-8")).decode("utf-8")
        else:
            raise TypeError("Query must be of a string type")

    @query.deleter
    def query(self):
        self._query = None

    @property
    def fragment(self):
        return self._fragment

    @fragment.setter
    def fragment(self, value):
        # TODO
        if value is None:
            self._fragment = None
        elif len(value) == 0:
            raise ValueError("Fragment cannot be an empty string (but could be None)")
        elif isinstance(value, (bytes, bytearray)):
            self._fragment = self._fragment_to_bytes(value).decode("utf-8")
        elif isinstance(value, str):
            self._fragment = self._fragment_to_bytes(value.encode("utf-8")).decode("utf-8")
        else:
            raise TypeError("Fragment must be of a string type")

    @fragment.deleter
    def fragment(self):
        self._fragment = None

    def resolve(self, ref, strict=True):
        raise NotImplementedError


def _resolve(base: XRI, ref: XRI, strict: bool, symbols):
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


def _resolve_xri(base, ref, strict=True):
    if isinstance(base.path, (bytes, bytearray)):
        return XRI(*_resolve(base, XRI(ref), strict, _BYTE_SYMBOLS))
    elif isinstance(base.path, str):
        return XRI(*_resolve(base, XRI(ref), strict, _STRING_SYMBOLS))
    else:
        return NotImplemented


XRI.resolve = _resolve_xri


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
