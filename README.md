# XRI

XRI is a small Python library for efficient and RFC-correct representation of URIs and IRIs.
It is currently work-in-progress and, as such, is not recommended for production environments.

The generic syntax for URIs is defined in [RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986/).
This is extended in the IRI specification, [RFC 3987](https://datatracker.ietf.org/doc/html/rfc3987/), to support extended characters outside of the ASCII range. 
The `URI` and `IRI` types defined in this library implement those definitions and store their constituent parts as `bytes` or `str` values respectively.


## Parsing a URI or IRI

To parse, simply pass a string value into the `URI.parse` or `IRI.parse` method.
These can both accept either `bytes` or `str` values, and will encode or decode UTF-8 values as required.

```python
>>> from xri import URI
>>> URI.parse("http://alice@example.com/ä/b/c?q=x#z")
{'scheme': 'http',
 'authority': 'alice@example.com',
 'path': '/%C3%A4/b/c',
 'query': 'q=x',
 'fragment': 'z',
 'userinfo': 'alice',
 'host': 'example.com',
 'port': '',
 'port_number': None,
 'path_segments': ['', 'ä', 'b', 'c'],
 'query_parameters': [('q', 'x')],
 'origin': 'http://example.com'}
```


## Percent encoding and decoding

Each of the `URI` and `IRI` classes has class methods called `pct_encode` and `pct_decode`.
These operate slightly differently, depending on the base class, as a slightly different set of characters are kept "safe" during encoding.

```python
>>> URI.pct_encode("abc/def")
'abc%2Fdef'
>>> URI.pct_encode("abc/def", safe="/")
'abc/def'
>>> URI.pct_encode("20% of $125 is $25")
'20%25%20of%20%24125%20is%20%2425'
>>> URI.pct_encode("20% of £125 is £25")                        # '£' is encoded with UTF-8
'20%25%20of%20%C2%A3125%20is%20%C2%A325'
>>> from xri import IRI
>>> IRI.pct_encode("20% of £125 is £25")                        # '£' is safe within an IRI
'20%25%20of%20£125%20is%20£25'
>>> URI.pct_decode('20%25%20of%20%C2%A3125%20is%20%C2%A325')    # str in, str out (using UTF-8)
'20% of £125 is £25'
>>> URI.pct_decode(b'20%25%20of%20%C2%A3125%20is%20%C2%A325')   # bytes in, bytes out (no UTF-8)
b'20% of \xc2\xa3125 is \xc2\xa325'
```

Safe characters (passed in via the `safe` argument) can only be drawn from the set below.
Other characters passed to this argument will give a `ValueError`.
```
! # $ & ' ( ) * + , / : ; = ? @ [ ]
```


## Advantages over built-in `urllib.parse` module

### Correct handling of character encodings

RFC 3986 specifies that extended characters (beyond the ASCII range) are not supported directly within URIs.
When used, these should always be encoded with UTF-8 before percent encoding.
IRIs (defined in RFC 3987) do however allow such characters. 

`urllib.parse` does not enforce this behaviour according to the RFCs, and does not support UTF-8 encoded bytes as input values.
```python
>>> from urllib.parse import urlparse
>>> urlparse("https://example.com/ä").path
'/ä'
>>> urlparse("https://example.com/ä".encode("utf-8")).path
UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 20: ordinal not in range(128)
```

Conversely, `xri` handles these scenarios correctly according to the RFCs.
```python
>>> URI.parse("https://example.com/ä b")["path"]
'/%C3%A4%20b'
>>> IRI.parse("https://example.com/ä b")["path"]
'/ä%20b'
```

### Optional components may be empty
Optional URI components, such as _query_ and _fragment_, are allowed to be present but empty, [according to RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986/#section-3.4).
As such, there is a semantic difference between an empty component and a missing component.
When composed, this will be denoted by the absence or presence of a marker character (`'?'` in the case of the query component).

The `urlparse` function does not distinguish between empty and missing components;
both are treated as "missing".
```python
>>> urlparse("https://example.com/a").geturl()
'https://example.com/a'
>>> urlparse("https://example.com/a?").geturl()
'https://example.com/a'
```

`xri`, on the other hand, correctly distinguishes between these cases:
```python
>>> uri = URI.parse("https://example.com/a")
>>> URI.compose(uri["scheme"], uri["authority"], uri["path"], uri["query"], uri["fragment"])
'https://example.com/a'
>>> uri = URI.parse("https://example.com/a?")
>>> URI.compose(uri["scheme"], uri["authority"], uri["path"], uri["query"], uri["fragment"])
'https://example.com/a?'
```
