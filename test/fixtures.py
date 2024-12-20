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


component_fixtures = {

    # Examples taken from https://datatracker.ietf.org/doc/html/rfc3986#section-1.1.2
    "ftp://ftp.is.co.za/rfc/rfc1808.txt": ("ftp", "ftp.is.co.za", "/rfc/rfc1808.txt", None, None),
    "http://www.ietf.org/rfc/rfc2396.txt": ("http", "www.ietf.org", "/rfc/rfc2396.txt", None, None),
    "ldap://[2001:db8::7]/c=GB?objectClass?one": ("ldap", "[2001:db8::7]", "/c=GB", "objectClass?one", None),
    "mailto:John.Doe@example.com": ("mailto", None, "John.Doe@example.com", None, None),
    "news:comp.infosystems.www.servers.unix": ("news", None, "comp.infosystems.www.servers.unix", None, None),
    "tel:+1-816-555-1212": ("tel", None, "+1-816-555-1212", None, None),
    "telnet://192.0.2.16:80/": ("telnet", "192.0.2.16:80", "/", None, None),
    "urn:oasis:names:specification:docbook:dtd:xml:4.1.2":
        ("urn", None, "oasis:names:specification:docbook:dtd:xml:4.1.2", None, None),

    # Examples taken from https://datatracker.ietf.org/doc/html/rfc3986#section-3
    "foo://example.com:8042/over/there?name=ferret#nose":
        ("foo", "example.com:8042", "/over/there", "name=ferret", "nose"),
    "urn:example:animal:ferret:nose": ("urn", None, "example:animal:ferret:nose", None, None),

    # Examples taken from https://datatracker.ietf.org/doc/html/rfc3986#section-3.3
    "mailto:fred@example.com": ("mailto", None, "fred@example.com", None, None),
    "foo://info.example.com?fred": ("foo", "info.example.com", "", "fred", None),

    # Examples taken from https://datatracker.ietf.org/doc/html/rfc3986#section-5.4
    "http://a/b/c/d;p?q": ("http", "a", "/b/c/d;p", "q", None),

    # Examples taken from https://datatracker.ietf.org/doc/html/rfc3986#section-7.6
    "ftp://cnn.example.com&story=breaking_news@10.0.0.1/top_story.htm":
        ("ftp", "cnn.example.com&story=breaking_news@10.0.0.1", "/top_story.htm", None, None),

    # Additional examples
    "": (None, None, "", None, None),
    "filename.ext": (None, None, "filename.ext", None, None),
    "file:filename.ext": ("file", None, "filename.ext", None, None),
    "file:///path/to/filename.ext": ("file", "", "/path/to/filename.ext", None, None),
    "http://example.com": ("http", "example.com", "", None, None),
    "http://example.com/": ("http", "example.com", "/", None, None),
    "http://example.com/#bookmark": ("http", "example.com", "/", None, "bookmark"),
    "http://example.com/abc?def=ghi&jkl=mno": ("http", "example.com", "/abc", "def=ghi&jkl=mno", None),
    "http://example.com/abc?def=ghi&jkl=mno%23pqr": ("http", "example.com", "/abc", "def=ghi&jkl=mno%23pqr", None),
    "http://example.com/abc?def=ghi&jkl=mno%26pqr": ("http", "example.com", "/abc", "def=ghi&jkl=mno%26pqr", None),
    "http://example.com/abc?def=ghi&jkl=mno#pqr": ("http", "example.com", "/abc", "def=ghi&jkl=mno", "pqr"),
    "https://example.com/abc%20def": ("https", "example.com", "/abc%20def", None, None),
    "/abc/def": (None, None, "/abc/def", None, None),
    "//abc/def": (None, "abc", "/def", None, None),
    "//abc:123/def": (None, "abc:123", "/def", None, None),
    "///abc/def": (None, "", "/abc/def", None, None),
    "http://user:password@host": ("http", "user:password@host", "", None, None),
    "http://user:p@ssword@host": ("http", "user:p@ssword@host", "", None, None),
    "http://user:p%40ssword@host": ("http", "user:p%40ssword@host", "", None, None),
    "http://user:p%41ssword@host": ("http", "user:p%41ssword@host", "", None, None),
}

resolver_base = "http://a/b/c/d;p?q"

# Taken from https://datatracker.ietf.org/doc/html/rfc3986#section-5.4.1
normal_resolver_fixtures = {
    "g:h": ("g", None, "h", None, None),
    "g": ("http", "a", "/b/c/g", None, None),
    "./g": ("http", "a", "/b/c/g", None, None),
    "g/": ("http", "a", "/b/c/g/", None, None),
    "/g": ("http", "a", "/g", None, None),
    "//g": ("http", "g", "", None, None),
    "?y": ("http", "a", "/b/c/d;p", "y", None),
    "g?y": ("http", "a", "/b/c/g", "y", None),
    "#s": ("http", "a", "/b/c/d;p", "q", "s"),
    "g#s": ("http", "a", "/b/c/g", None, "s"),
    "g?y#s": ("http", "a", "/b/c/g", "y", "s"),
    ";x": ("http", "a", "/b/c/;x", None, None),
    "": ("http", "a", "/b/c/d;p", "q", None),
    ".": ("http", "a", "/b/c/", None, None),
    "./": ("http", "a", "/b/c/", None, None),
    "..": ("http", "a", "/b/", None, None),
    "../": ("http", "a", "/b/", None, None),
    "../g": ("http", "a", "/b/g", None, None),
    "../..": ("http", "a", "/", None, None),
    "../../": ("http", "a", "/", None, None),
    "../../g": ("http", "a", "/g", None, None),
}

# Taken from https://datatracker.ietf.org/doc/html/rfc3986#section-5.4.2
abnormal_resolver_fixtures = {
    "../../../g": ("http", "a", "/g", None, None),
    "../../../../g": ("http", "a", "/g", None, None),
    "/./g": ("http", "a", "/g", None, None),
    "/../g": ("http", "a", "/g", None, None),
    "g.": ("http", "a", "/b/c/g.", None, None),
    ".g": ("http", "a", "/b/c/.g", None, None),
    "g..": ("http", "a", "/b/c/g..", None, None),
    "..g": ("http", "a", "/b/c/..g", None, None),
    "./../g": ("http", "a", "/b/g", None, None),
    "./g/.": ("http", "a", "/b/c/g/", None, None),
    "g/./h": ("http", "a", "/b/c/g/h", None, None),
    "g/../h": ("http", "a", "/b/c/h", None, None),
    "g;x=1/./y": ("http", "a", "/b/c/g;x=1/y", None, None),
    "g;x=1/../y": ("http", "a", "/b/c/y", None, None),
    "g?y/./x": ("http", "a", "/b/c/g", "y/./x", None),
    "g?y/../x": ("http", "a", "/b/c/g", "y/../x", None),
    "g#s/./x": ("http", "a", "/b/c/g", None, "s/./x"),
    "g#s/../x": ("http", "a", "/b/c/g", None, "s/../x"),
}
