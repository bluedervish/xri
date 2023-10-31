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
