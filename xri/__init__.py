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


from abc import ABC
from typing import Optional, List


VERSION = "0.7.3"


ALPHA_UPPER = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPHA_LOWER = b"abcdefghijklmnopqrstuvwxyz"
DIGIT = b"0123456789"

GENERAL_DELIMITERS = b":/?#[]@"
SUB_DELIMITERS = b"!$&'()*+,;="
RESERVED = GENERAL_DELIMITERS + SUB_DELIMITERS          # RFC 3986 § 2.2

USERINFO_SAFE = SUB_DELIMITERS + b":"                   # RFC 3986 § 3.2.1
PATH_SAFE = SUB_DELIMITERS + b":@"  # TODO confirm colon rules (see 'segment-nz-nc' in RFC)
FRAGMENT_SAFE = SUB_DELIMITERS + b":/?@"


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


def _to_bytes(value) -> bytes:
    """ Coerce value to bytes, assuming UTF-8 encoding if appropriate.

    >>> _to_bytes(None)
    b''
    >>> _to_bytes("café")
    b'caf\xC3\xA9'
    >>> _to_bytes(b"abc")
    b'abc'
    >>> _to_bytes(123)
    b'123'
    >>> _to_bytes(12.3)
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


def _to_str(value) -> str:
    """ Coerce value to a string, assuming UTF-8 encoding if appropriate.

    >>> _to_str(None)
    ''
    >>> _to_str("café")
    'café'
    >>> _to_str(b"abc")
    'abc'
    >>> _to_str(123)
    '123'
    >>> _to_str(12.3)
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


class XRI:

    class Authority(ABC):

        _host = ""
        _port = None
        _userinfo = None

        @classmethod
        def _parse_userinfo(cls, string: bytes) -> bytes:
            """ Validate and normalise user information.

            .. seealso::
                `RFC 3986 § 3.2.1`_

            .. _`RFC 3986 § 3.2.1`: http://tools.ietf.org/html/rfc3986#section-3.2.1
            """
            return string  # TODO

        @classmethod
        def _parse_host(cls, string: bytes) -> bytes:
            """ Validate and normalise a host value.

            .. seealso::
                `RFC 3986 § 3.2.2`_

            .. _`RFC 3986 § 3.2.2`: http://tools.ietf.org/html/rfc3986#section-3.2.2
            """
            return string  # TODO

        @classmethod
        def parse(cls, string):
            """ Parse and decode a string value into an Authority object.

            >>> XRI.Authority.parse(b'example.com')
            URI.Authority(b'example.com')
            >>> XRI.Authority.parse('example.com')
            IRI.Authority('example.com')

            """
            if isinstance(string, (bytes, bytearray)):
                return URI.Authority.parse(string)
            elif isinstance(string, str):
                return IRI.Authority.parse(string)
            else:  # pragma: no cover
                raise TypeError("Authority value must be a string")

        def __new__(cls, host, port=None, userinfo=None):
            """ Create a new Authority object directly.

            >>> XRI.Authority(b'example.com', port=8080, userinfo=b'alice')
            URI.Authority(b'example.com', port=8080, userinfo=b'alice')
            >>> XRI.Authority('example.com', port=8080, userinfo='alice')
            IRI.Authority('example.com', port=8080, userinfo='alice')

            """
            if isinstance(host, (bytes, bytearray)):
                return URI.Authority(host, port=port, userinfo=userinfo)
            elif isinstance(host, str):
                return IRI.Authority(host, port=port, userinfo=userinfo)
            else:  # pragma: no cover
                raise TypeError("Host value must be a string")

        def __repr__(self):
            parts = [repr(self._host)]
            if self._port is not None:
                parts.append(f"port={self._port!r}")
            if self._userinfo is not None:
                parts.append(f"userinfo={self._userinfo!r}")
            return f"{self.__class__.__qualname__}({', '.join(parts)})"

    class Path(ABC):

        @classmethod
        def parse(cls, string):
            """ Parse and decode a string value into a Path object.
            """
            if isinstance(string, (bytes, bytearray)):
                return URI.Path.parse(string)
            elif isinstance(string, str):
                return IRI.Path.parse(string)
            else:
                raise TypeError("Path value must be a string")

        def startswith(self, value) -> bool:
            """ Return true if the path starts with the given value, which
            can either be a string or an iterable of string segments.
            """
            raise NotImplementedError

        def partition(self, separator):
            raise NotImplementedError

        def rpartition(self, separator):
            raise NotImplementedError

        def compose(self):
            raise NotImplementedError

        def is_absolute(self) -> bool:
            return len(self._segments) >= 2 and not self._segments[0]

        def __new__(cls, segments=()):
            if isinstance(segments, (bytes, bytearray, str)):
                return cls.parse(segments)
            else:
                obj = super().__new__(cls)
                obj._segments = list(segments)
                return obj

        def __repr__(self):
            return f"{self.__class__.__qualname__}([{', '.join(map(repr, self._segments))}])"

        def __bool__(self):
            n_segments = len(self._segments)
            if n_segments == 0:
                return False
            elif n_segments == 1 and not self._segments[0]:
                return False
            else:
                return True

        def __add__(self, other):
            cls = self.__class__
            obj = cls(self)
            obj._segments += iter(cls(other))
            return obj

        def __len__(self):
            return len(self._segments)

        def __iter__(self):
            return iter(self._segments)

        @property
        def segments(self):
            return self._segments

        def insert(self, index, value):
            raise NotImplementedError

    class Query(ABC):
        pass  # TODO

    _scheme = None
    _authority = None
    _path = Path()
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
        if value is None or isinstance(value, cls):
            return value

        if isinstance(value, str):
            cls = IRI
            symbols = _STRING_SYMBOLS
        elif isinstance(value, (bytes, bytearray)):
            cls = URI
            symbols = _BYTE_SYMBOLS
        else:
            # If the value is not of a type we explicitly recognise, stringify
            # it, encode it with UTF-8 and treat it as a URI. This approach is
            # taken because __str__ implementations are more common than
            # __bytes__ implementations for objects in general, and URIs are
            # more widely used and understood than IRIs.
            cls = URI
            value = str(value).encode("utf-8")
            symbols = _BYTE_SYMBOLS

        scheme, authority, path, query, fragment = cls._parse(value, symbols)

        obj = super().__new__(cls)
        # TODO: strict mode (maybe)
        obj.scheme = scheme
        obj.authority = authority
        obj.path = path
        obj.query = query
        obj.fragment = fragment
        return obj

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

    def __iter__(self):
        yield "scheme", self.scheme
        yield "authority", self.authority
        yield "path", self.path
        yield "query", self.query
        yield "fragment", self.fragment

    @classmethod
    def _parse(cls, string: bytes, symbols) -> \
            (Optional[bytes], Optional[bytes], bytes, Optional[bytes], Optional[bytes]):
        """ Parse the input string into a 5-tuple.
        """
        if string.startswith(symbols.SLASH):
            # Parse as relative reference
            scheme, scheme_specific_part = None, string
        else:
            # Parse as absolute URI
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
        return cls.pct_decode(scheme), authority, path, query, cls.pct_decode(fragment)

    @classmethod
    def _parse_scheme(cls, string: bytes) -> bytes:
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
    def _parse_query(cls, string: bytes) -> bytes:
        # TODO
        return bytes(string)

    @classmethod
    def _parse_fragment(cls, string: bytes) -> bytes:
        # TODO
        return bytes(string)

    def _compose(self, symbols) -> List:
        """ Implementation of RFC3986, section 5.3

        :return:
        """
        parts = []
        if self.scheme is not None:
            # Percent encoding is not required for the scheme, as only
            # ASCII characters A-Z, a-z, 0-9, '+', '-', and '.' are allowed.
            parts.append(self.scheme)
            parts.append(symbols.COLON)
        if self.authority is not None:
            # TODO: percent encoding
            parts.append(symbols.SLASH_SLASH)
            parts.append(self.authority.compose())
        # TODO: full set of percent encoding rules for paths
        parts.append(self.path.compose())
        if self.query is not None:
            # TODO: percent encoding
            parts.append(symbols.QUERY)
            parts.append(self.query)
        if self.fragment is not None:
            # Fragments may contain any unreserved characters, sub-delimiters,
            # or any of ":@/?". Everything else must be percent encoded.
            parts.append(symbols.HASH)
            parts.append(self.pct_encode(self.fragment, safe=FRAGMENT_SAFE))
        return parts

    def compose(self):
        raise NotImplementedError

    def resolve(self, ref, strict=True):
        raise NotImplementedError


class URI(XRI):

    class Authority(XRI.Authority):

        @classmethod
        def parse(cls, string):
            if isinstance(string, str):
                string = string.encode("utf-8")
            elif not isinstance(string, (bytes, bytearray)):
                raise TypeError("Authority value must be a string")

            if b"@" in string:
                userinfo, _, host_port = string.partition(b"@")
            else:
                userinfo = None
                host_port = string

            host, _, port = host_port.partition(b":")
            return cls(host, port=(port or None), userinfo=URI.pct_decode(userinfo))

        def compose(self):
            return bytes(self)

        def __new__(cls, host, port=None, userinfo=None):
            obj = object.__new__(cls)
            obj.host = host
            obj.port = port
            obj.userinfo = userinfo
            return obj

        def __iter__(self):
            yield "userinfo", self.userinfo
            yield "host", self.host
            yield "port", self.port

        def __eq__(self, other):
            if isinstance(other, (bytes, bytearray, str)):
                other = self.parse(other)
            try:
                return (self.userinfo, self.host, self.port) == (other.userinfo, other.host, other.port)
            except AttributeError:
                return False

        def __hash__(self):
            return hash((self.userinfo, self.host, self.port))

        def __bytes__(self):
            parts = [self._host]
            if self._port is not None:
                parts.append(b":")
                parts.append(self._port)
            if self._userinfo is not None:
                parts.insert(0, b"@")
                parts.insert(0, URI.pct_encode(self._userinfo, safe=USERINFO_SAFE))
            return b"".join(map(_to_bytes, parts))

        def __str__(self):
            parts = [self._host]
            if self._port is not None:
                parts.append(":")
                parts.append(self._port)
            if self._userinfo is not None:
                parts.insert(0, "@")
                parts.insert(0, URI.pct_encode(self._userinfo, safe=USERINFO_SAFE))
            return "".join(map(_to_str, parts))

        @property
        def host(self):
            return self._host

        @host.setter
        def host(self, value):
            if value is None:
                raise ValueError("Host cannot be None")
            elif isinstance(value, (bytes, bytearray)):
                self._host = self._parse_host(value)
            elif isinstance(value, str):
                self._host = self._parse_host(value.encode("utf-8"))
            else:
                raise TypeError("Host must be of a string type")

        @property
        def port(self):
            try:
                return int(self._port)
            except (TypeError, ValueError):
                return self._port

        @port.setter
        def port(self, value):
            if value is None:
                self._port = None
            elif isinstance(value, (bytes, bytearray, int)):
                self._port = value
            elif isinstance(value, str):
                self._port = value.encode("utf-8")
            else:
                raise TypeError("Port must be of a string or integer type")

        @property
        def userinfo(self):
            return self._userinfo

        @userinfo.setter
        def userinfo(self, value):
            if value is None:
                self._userinfo = None
            elif isinstance(value, (bytes, bytearray)):
                self._userinfo = self._parse_userinfo(value)
            elif isinstance(value, str):
                self._userinfo = self._parse_userinfo(value.encode("utf-8"))
            else:
                raise TypeError("User information must be of a string type")

    class Path(XRI.Path):

        @classmethod
        def parse(cls, string):
            if isinstance(string, (bytes, bytearray)):
                return cls(map(URI.pct_decode, string.split(b"/")))
            elif isinstance(string, str):
                return cls(map(URI.pct_decode, string.encode("utf-8").split(b"/")))
            else:
                raise TypeError("Path value must be a string")

        def startswith(self, value) -> bool:
            if isinstance(value, (bytes, bytearray, str)):
                return self.compose().startswith(URI.Path(value).compose())
            else:
                self_segments = self._segments
                if len(self_segments) >= len(value):
                    for i, segment in enumerate(value):
                        if _to_bytes(segment) != self_segments[i]:
                            return False
                    else:
                        return True
                else:
                    return False

        def partition(self, separator) -> (bytes, bytes, bytes):
            return bytes(self).partition(separator)

        def rpartition(self, separator) -> (bytes, bytes, bytes):
            return bytes(self).rpartition(separator)

        def compose(self):
            return bytes(self)

        def __eq__(self, other):
            if isinstance(other, (bytes, bytearray, str)):
                other = self.parse(other)
            return list(self) == list(other)

        def __bytes__(self):
            return b"/".join(URI.pct_encode(_to_bytes(segment), safe=PATH_SAFE) for segment in self._segments)

        def __str__(self):
            return "/".join(URI.pct_encode(_to_str(segment), safe=PATH_SAFE) for segment in self._segments)

        def __repr__(self):
            return f"{self.__class__.__qualname__}({bytes(self)!r})"

        def insert(self, index, value):
            if isinstance(value, str):
                self._segments.insert(index, value.encode("utf-8"))
            else:
                self._segments.insert(index, bytes(value))

    class Query(XRI.Query):
        pass  # TODO

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

    def __new__(cls, value):
        if value is None or isinstance(value, cls):
            return value
        elif isinstance(value, (bytes, bytearray)):
            return super().__new__(cls, value)
        elif isinstance(value, str):
            return super().__new__(cls, value.encode("utf-8"))
        else:
            return super().__new__(cls, bytes(value))

    def __bytes__(self):
        return b"".join(self._compose(_BYTE_SYMBOLS))

    def __str__(self):
        # The "ascii" codec should never trigger a UnicodeDecodeError here,
        # as the _compose function is responsible for percent-encoding all
        # characters outside of the ASCII range. Therefore, only ASCII-
        # compatible characters should exist within the _compose output.
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
            self._scheme = self._parse_scheme(value)
        elif isinstance(value, str):
            self._scheme = self._parse_scheme(value.encode("utf-8"))
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
            self._authority = URI.Authority.parse(value)
        elif isinstance(value, str):
            self._authority = URI.Authority.parse(value.encode("utf-8"))
        else:
            self._authority = URI.Authority.parse(bytes(value))

    @authority.deleter
    def authority(self):
        self._authority = None

    @property
    def path(self):
        # TODO: pct_encode
        return self._path

    @path.setter
    def path(self, value):
        if value is None:
            raise ValueError("Path cannot be None (but could be an empty string)")
        elif isinstance(value, (bytes, bytearray, str)):
            self._path = self.Path.parse(value)
        else:
            try:
                self._path = self.Path(map(_to_bytes, iter(value)))
            except TypeError:
                raise TypeError("Path must be a string or an iterable of string segments")

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
        elif isinstance(value, (bytes, bytearray)):
            self._query = self._parse_query(value)
        elif isinstance(value, str):
            self._query = self._parse_query(value.encode("utf-8"))
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
        elif isinstance(value, (bytes, bytearray)):
            self._fragment = self._parse_fragment(value)
        elif isinstance(value, str):
            self._fragment = self._parse_fragment(value.encode("utf-8"))
        else:
            raise TypeError("Fragment must be of a string type")

    @fragment.deleter
    def fragment(self):
        self._fragment = None

    def compose(self):
        return bytes(self)

    def resolve(self, ref, strict=True):
        scheme, authority, path, query, fragment = _resolve(self, XRI(ref), strict, _BYTE_SYMBOLS)
        obj = super().__new__(self.__class__, b"")
        obj.scheme = scheme
        obj.authority = authority
        obj.path = path
        obj.query = query
        obj.fragment = fragment
        return obj


class IRI(XRI):

    class Authority(XRI.Authority):

        @classmethod
        def parse(cls, string):
            if isinstance(string, (bytes, bytearray)):
                string = string.decode("utf-8")
            elif not isinstance(string, str):
                raise TypeError("Authority value must be a string")

            if "@" in string:
                userinfo, _, host_port = string.partition("@")
            else:
                userinfo = None
                host_port = string

            host, _, port = host_port.partition(":")
            return cls(host, port=(port or None), userinfo=IRI.pct_decode(userinfo))

        def compose(self):
            return str(self)

        def __new__(cls, host, port=None, userinfo=None):
            obj = object.__new__(cls)
            obj.host = host
            obj.port = port
            obj.userinfo = userinfo
            return obj

        def __iter__(self):
            yield "userinfo", self.userinfo
            yield "host", self.host
            yield "port", self.port

        def __eq__(self, other):
            if isinstance(other, (bytes, bytearray, str)):
                other = self.parse(other)
            try:
                return (self.userinfo, self.host, self.port) == (other.userinfo, other.host, other.port)
            except AttributeError:
                return False

        def __hash__(self):
            return hash((self.userinfo, self.host, self.port))

        def __bytes__(self):
            parts = [self._host]
            if self._port is not None:
                parts.append(b":")
                parts.append(self._port)
            if self._userinfo is not None:
                parts.insert(0, b"@")
                parts.insert(0, IRI.pct_encode(self._userinfo, safe=USERINFO_SAFE))
            return b"".join(map(_to_bytes, parts))

        def __str__(self):
            parts = [self._host]
            if self._port is not None:
                parts.append(":")
                parts.append(self._port)
            if self._userinfo is not None:
                parts.insert(0, "@")
                parts.insert(0, IRI.pct_encode(self._userinfo, safe=USERINFO_SAFE))
            return "".join(map(_to_str, parts))

        @property
        def host(self):
            return self._host

        @host.setter
        def host(self, value):
            if value is None:
                raise ValueError("Host cannot be None")
            elif isinstance(value, (bytes, bytearray)):
                self._host = self._parse_host(value).decode("utf-8")
            elif isinstance(value, str):
                self._host = self._parse_host(value.encode("utf-8")).decode("utf-8")
            else:
                raise TypeError("Host must be of a string type")

        @property
        def port(self):
            try:
                return int(self._port)
            except (TypeError, ValueError):
                return self._port

        @port.setter
        def port(self, value):
            if value is None:
                self._port = None
            elif isinstance(value, (str, int)):
                self._port = value
            elif isinstance(value, (bytes, bytearray)):
                self._port = value.decode("utf-8")
            else:
                raise TypeError("Port must be of a string or integer type")

        @property
        def userinfo(self):
            return self._userinfo

        @userinfo.setter
        def userinfo(self, value):
            if value is None:
                self._userinfo = None
            elif isinstance(value, (bytes, bytearray)):
                self._userinfo = self._parse_userinfo(value).decode("utf-8")
            elif isinstance(value, str):
                self._userinfo = self._parse_userinfo(value.encode("utf-8")).decode("utf-8")
            else:
                raise TypeError("User information must be of a string type")

    class Path(XRI.Path):

        @classmethod
        def parse(cls, string):
            if isinstance(string, (bytes, bytearray)):
                return cls(IRI.pct_decode(segment.decode("utf-8")) for segment in string.split(b"/"))
            elif isinstance(string, str):
                return cls(map(IRI.pct_decode, string.split("/")))
            else:
                raise TypeError("Path value must be a string")

        def startswith(self, value) -> bool:
            if isinstance(value, (str, bytes, bytearray)):
                return self.compose().startswith(IRI.Path(value).compose())
            else:
                self_segments = self._segments
                if len(self_segments) >= len(value):
                    for i, segment in enumerate(value):
                        if _to_str(segment) != self_segments[i]:
                            return False
                    else:
                        return True
                else:
                    return False

        def partition(self, separator) -> (str, str, str):
            return str(self).partition(separator)

        def rpartition(self, separator) -> (str, str, str):
            return str(self).rpartition(separator)

        def compose(self):
            return str(self)

        def __eq__(self, other):
            if isinstance(other, (bytes, bytearray, str)):
                other = self.parse(other)
            return list(self) == list(other)

        def __bytes__(self):
            return b"/".join(IRI.pct_encode(_to_bytes(segment), safe=PATH_SAFE) for segment in self._segments)

        def __str__(self):
            return "/".join(IRI.pct_encode(_to_str(segment), safe=PATH_SAFE) for segment in self._segments)

        def __repr__(self):
            return f"{self.__class__.__qualname__}({str(self)!r})"

        def insert(self, index, value):
            if isinstance(value, (bytes, bytearray)):
                self._segments.insert(index, value.decode("utf-8"))
            else:
                self._segments.insert(index, str(value))

    class Query(XRI.Query):
        pass  # TODO

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

    def __new__(cls, value):
        if value is None or isinstance(value, cls):
            return value
        elif isinstance(value, str):
            return super().__new__(cls, value)
        elif isinstance(value, (bytes, bytearray)):
            return super().__new__(cls, value.decode("utf-8"))
        else:
            return super().__new__(cls, str(value))

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
            self._scheme = self._parse_scheme(value).decode("utf-8")
        elif isinstance(value, str):
            self._scheme = self._parse_scheme(value.encode("utf-8")).decode("utf-8")
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
            self._authority = IRI.Authority.parse(value)
        elif isinstance(value, str):
            self._authority = IRI.Authority.parse(value.encode("utf-8"))
        else:
            self._authority = IRI.Authority.parse(str(value))

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
        elif isinstance(value, (bytes, bytearray, str)):
            self._path = self.Path.parse(value)
        else:
            try:
                self._path = self.Path(map(_to_str, iter(value)))
            except TypeError:
                raise TypeError("Path must be a string or an iterable of string segments")

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
        elif isinstance(value, (bytes, bytearray)):
            self._query = self._parse_query(value).decode("utf-8")
        elif isinstance(value, str):
            self._query = self._parse_query(value.encode("utf-8")).decode("utf-8")
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
        elif isinstance(value, (bytes, bytearray)):
            self._fragment = self._parse_fragment(value).decode("utf-8")
        elif isinstance(value, str):
            self._fragment = self._parse_fragment(value.encode("utf-8")).decode("utf-8")
        else:
            raise TypeError("Fragment must be of a string type")

    @fragment.deleter
    def fragment(self):
        self._fragment = None

    def compose(self):
        return str(self)

    def resolve(self, ref, strict=True):
        scheme, authority, path, query, fragment = _resolve(self, XRI(ref), strict, _STRING_SYMBOLS)
        obj = super().__new__(self.__class__, "")
        obj.scheme = scheme
        obj.authority = authority
        obj.path = path
        obj.query = query
        obj.fragment = fragment
        return obj


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
        path_string = path.compose()
        ref_string = relative_path_ref.compose()
        try:
            last_slash = path_string.rindex(symbols.SLASH)
        except ValueError:
            return ref_string
        else:
            return path_string[:(last_slash + 1)] + ref_string


def _remove_dot_segments(path, symbols):
    """ Implementation of RFC3986, section 5.2.4
    """
    if isinstance(path, XRI.Path):
        path = path.compose()
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
