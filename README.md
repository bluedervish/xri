# XRI

XRI is a small Python library for efficient and RFC-correct representation of URIs and IRIs.
It is currently work-in-progress and, as such, is not recommended for production environments.

The generic syntax for URIs is defined in [RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986/).
This is extended in the IRI specification, [RFC 3987](https://datatracker.ietf.org/doc/html/rfc3987/), to support extended characters outside of the ASCII range. 
The `URI` and `IRI` types defined in this library implement those definitions and store their constituent parts as `bytes` or `str` values respectively.


## Creating a URI or IRI

To get started, simply pass a string value into the `URI` or `IRI` constructor.
These can both accept either `bytes` or `str` values, and will encode or decode UTF-8 values as required.

```python-repl
>>> from xri import URI
>>> uri = URI("http://alice@example.com/a/b/c?q=x#z")
>>> uri
<URI scheme=b'http' authority=URI.Authority(b'example.com', userinfo=b'alice') \
     path=URI.Path(b'/a/b/c') query=b'q=x' fragment=b'z'>
>>> uri.scheme = "https"
>>> print(uri)
https://alice@example.com/a/b/c?q=x#z
```


## Component parts

Each `URI` or `IRI` object is fully mutable, allowing any component parts to be get, set, or deleted.
The following component parts are available:

- `URI`/`IRI` object
  - `.scheme` (None or string)
  - `.authority` (None or `Authority` object)
    - `.userinfo` (None or string) 
    - `.host` (string)
    - `.port` (None, string or int)
  - `.path` (`Path` object - can be used as an iterable of segment strings)
  - `.query` (None or `Query` object)
  - `.fragment` (None or string)

(The type "string" here refers to `bytes` or `bytearray` for `URI` objects, and `str` for `IRI` objects.)


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
>>> urlparse("https://example.com/ä").path
'/ä'
>>> urlparse("https://example.com/ä".encode("utf-8")).path
UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 20: ordinal not in range(128)
```

Conversely, `xri` handles these scenarios correctly according to the RFCs.
```python
>>> URI("https://example.com/ä").path
URI.Path(b'/%C3%A4')
>>> URI("https://example.com/ä".encode("utf-8")).path
URI.Path(b'/%C3%A4')
>>> IRI("https://example.com/ä").path
IRI.Path('/ä')
>>> IRI("https://example.com/ä".encode("utf-8")).path
IRI.Path('/ä')
```

### Optional components may be empty
Optional URI components, such as _query_ and _fragment_ are allowed to be present but empty, [according to RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986/#section-3.4).
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
>>> str(URI("https://example.com/a"))
'https://example.com/a'
>>> str(URI("https://example.com/a?"))
'https://example.com/a?'
```