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
<URI scheme=b'http' authority=b'alice@example.com' path=URI.Path(b'/a/b/c') query=b'q=x' fragment=b'z'>
>>> uri.scheme = "https"
>>> print(uri)
https://alice@example.com/a/b/c?q=x#z
```
