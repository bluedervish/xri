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


from ._util import to_bytes


GENERAL_DELIMITERS = b":/?#[]@"
SUB_DELIMITERS = b"!$&'()*+,;="
RESERVED = GENERAL_DELIMITERS + SUB_DELIMITERS          # RFC 3986 § 2.2

USERINFO_SAFE = SUB_DELIMITERS + b":"                   # RFC 3986 § 3.2.1
PATH_SAFE = SUB_DELIMITERS + b":@"  # TODO confirm colon rules (see 'segment-nz-nc' in RFC)
FRAGMENT_SAFE = SUB_DELIMITERS + b":/?@"


CHARS = [chr(i).encode("iso-8859-1") for i in range(256)]
PCT_ENCODED_CHARS = [f"%{i:02X}".encode("ascii") for i in range(256)]


class URI:

    EMPTY = b""

    SLASH = b"/"
    COLON = b":"
    AT = b"@"
    AMPERSAND = b"&"
    HASH = b"#"
    QUERY = b"?"
    EQUALS = b"="
    DOT = b"."

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
        return to_bytes(value)

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
            return b"".join(CHARS[ch] if ch in safe or cls.is_unreserved(ch) else PCT_ENCODED_CHARS[ch]
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
                        out.append(CHARS[char_code])
            return b"".join(out)
        elif isinstance(string, str):
            return cls.pct_decode(string.encode("utf-8")).decode("utf-8")
        elif string is None:
            return None
        else:
            raise TypeError(f"Unsupported input type {type(string)}")

    @classmethod
    def equal(cls, first, second, http_equals_https=False, ignore_trailing_slash=False) -> bool:
        # TODO: allow ignore order of query parameters
        # TODO: allow ignore fragment
        self = cls.parse(first)
        other = cls.parse(second)
        self_scheme = self["scheme"]
        other_scheme = other["scheme"]
        if http_equals_https:
            if self_scheme == cls.stringify("https"):
                self_scheme = cls.stringify("http")
            if other_scheme == cls.stringify("https"):
                other_scheme = cls.stringify("http")
        self_path = self["path"]
        other_path = other["path"]
        if ignore_trailing_slash:
            if self_path.endswith(cls.SLASH):
                self_path = self_path[:-1]
            if other_path.endswith(cls.SLASH):
                other_path = other_path[:-1]
        return (self_scheme == other_scheme and
                self["authority"] == other["authority"] and
                self_path == other_path and
                self["query"] == other["query"] and
                self["fragment"] == other["fragment"])

    @classmethod
    def parse(cls, string) -> dict:
        parts = cls._parse(cls.stringify(string))
        parts.update(cls.parse_authority(parts["authority"]))
        parts.update(cls.parse_path(parts["path"]))
        parts.update(cls.parse_query(parts["query"]))
        if parts["scheme"] is not None and parts["authority"] is not None:
            parts["origin"] = parts["scheme"] + cls.COLON + cls.SLASH_SLASH + parts["host"]
            if parts["port"]:
                parts["origin"] += cls.COLON + parts["port"]
        else:
            parts["origin"] = None
        return parts

    @classmethod
    def _parse(cls, string) -> dict:
        if string.startswith(cls.SLASH):
            # Parse as relative reference
            scheme, scheme_specific_part = None, string
        else:
            # Parse as absolute URI
            scheme, colon, scheme_specific_part = string.partition(cls.COLON)
            if not colon:
                scheme, scheme_specific_part = None, scheme
        auth_path_query, hash_sign, fragment = scheme_specific_part.partition(cls.HASH)
        if not hash_sign:
            fragment = None
        hierarchical_part, question_mark, query = auth_path_query.partition(cls.QUERY)
        if not question_mark:
            query = None
        if hierarchical_part.startswith(cls.SLASH_SLASH):
            hierarchical_part = hierarchical_part[2:]
            try:
                slash = hierarchical_part.index(cls.SLASH)
            except ValueError:
                authority = hierarchical_part
                path = cls.EMPTY
            else:
                authority = hierarchical_part[:slash]
                path = hierarchical_part[slash:]
        else:
            authority = None
            path = hierarchical_part
        return {
            "scheme": cls.pct_decode(scheme),
            "authority": authority,
            "path": path,
            "query": query,
            "fragment": cls.pct_decode(fragment),
        }

    @classmethod
    def parse_authority(cls, string):
        userinfo = host = port = None
        if string is not None:
            if cls.AT in string:
                userinfo, _, host_port = string.partition(cls.AT)
            else:
                userinfo = None
                host_port = string
            host, _, port = host_port.partition(cls.COLON)
        parts = {
            "userinfo": userinfo,
            "host": host,
            "port": port,
        }
        try:
            parts["port_number"] = int(port)
        except (ValueError, TypeError):
            parts["port_number"] = None
        return parts

    @classmethod
    def parse_path(cls, string):
        return {
            "path_segments": list(map(cls.pct_decode, string.split(cls.SLASH))),
        }

    @classmethod
    def parse_query(cls, string):
        if string is None:
            parameters = None
        else:
            parameters = []
            for item in string.split(cls.AMPERSAND):
                if cls.EQUALS in item:
                    key, _, value = item.partition(cls.EQUALS)
                    parameters.append((cls.pct_decode(key), cls.pct_decode(value)))
                else:
                    parameters.append((cls.pct_decode(item), None))
        return {"query_parameters": parameters}

    @classmethod
    def compose(cls, scheme=None, authority=None, path=None, query=None, fragment=None):
        """ Implementation of RFC3986, section 5.3
        """
        parts = []
        if scheme is not None:
            # Percent encoding is not required for the scheme, as only
            # ASCII characters A-Z, a-z, 0-9, '+', '-', and '.' are allowed.
            parts.append(cls.stringify(scheme))
            parts.append(cls.COLON)
        if authority is not None:
            # TODO: percent encoding
            parts.append(cls.SLASH_SLASH)
            parts.append(cls.stringify(authority))
        # TODO: full set of percent encoding rules for paths
        parts.append(cls.stringify(path or cls.EMPTY))
        if query is not None:
            # TODO: percent encoding
            parts.append(cls.QUERY)
            parts.append(cls.stringify(query))
        if fragment is not None:
            # Fragments may contain any unreserved characters, sub-delimiters,
            # or any of ":@/?". Everything else must be percent encoded.
            parts.append(cls.HASH)
            parts.append(cls.pct_encode(cls.stringify(fragment), safe=FRAGMENT_SAFE))
        return cls.EMPTY.join(parts)

    @classmethod
    def resolve(cls, base, ref, strict=True):
        """ Transform a reference relative to this URI to produce a full target
        URI.

        :param base:
        :param ref:
        :param strict:

        .. seealso::
            `RFC 3986 § 5.2.2`_

        .. _`RFC 3986 § 5.2.2`: http://tools.ietf.org/html/rfc3986#section-5.2.2
        """
        base = cls.parse(base)
        ref = cls.parse(ref)
        if not strict and ref["scheme"] == base["scheme"]:
            ref_scheme = None
        else:
            ref_scheme = ref["scheme"]
        if ref_scheme is not None:
            scheme = ref_scheme
            authority = ref["authority"]
            path = cls.remove_dot_segments(ref["path"])
            query = ref["query"]
        else:
            if ref["authority"] is not None:
                authority = ref["authority"]
                path = cls.remove_dot_segments(ref["path"])
                query = ref["query"]
            else:
                if not ref["path"]:
                    path = base["path"]
                    if ref["query"] is not None:
                        query = ref["query"]
                    else:
                        query = base["query"]
                else:
                    if ref["path"].startswith(cls.SLASH):
                        path = cls.remove_dot_segments(ref["path"])
                    else:
                        path = cls.merge_path(base["authority"], base["path"], ref["path"])
                        path = cls.remove_dot_segments(path)
                    query = ref["query"]
                authority = base["authority"]
            scheme = base["scheme"]
        fragment = ref["fragment"]
        return cls.compose(scheme, authority, path, query, fragment)

    @classmethod
    def merge_path(cls, authority, path, relative_path_ref):
        """ Implementation of RFC3986, section 5.2.3

        https://datatracker.ietf.org/doc/html/rfc3986#section-5.2.3

        :param authority:
        :param path:
        :param relative_path_ref:
        :return:
        """
        if authority is not None and not path:
            return cls.SLASH + cls.stringify(relative_path_ref)
        else:
            path_string = cls.stringify(path)
            ref_string = cls.stringify(relative_path_ref)
            try:
                last_slash = path_string.rindex(cls.SLASH)
            except ValueError:
                return ref_string
            else:
                return path_string[:(last_slash + 1)] + ref_string

    @classmethod
    def remove_dot_segments(cls, path):
        """ Implementation of RFC3986, section 5.2.4
        """
        new_path = cls.EMPTY
        while path:
            if path.startswith(cls.DOT_DOT_SLASH):
                path = path[3:]
            elif path.startswith(cls.DOT_SLASH):
                path = path[2:]
            elif path.startswith(cls.SLASH_DOT_SLASH):
                path = path[2:]
            elif path == cls.SLASH_DOT:
                path = cls.SLASH
            elif path.startswith(cls.SLASH_DOT_DOT_SLASH):
                path = path[3:]
                new_path = new_path.rpartition(cls.SLASH)[0]
            elif path == cls.SLASH_DOT_DOT:
                path = cls.SLASH
                new_path = new_path.rpartition(cls.SLASH)[0]
            elif path in (cls.DOT, cls.DOT_DOT):
                path = cls.EMPTY
            else:
                if path.startswith(cls.SLASH):
                    path = path[1:]
                    new_path += cls.SLASH
                seg, slash, path = path.partition(cls.SLASH)
                new_path += seg
                path = slash + path
        return new_path
