# XRI

XRI is a small Python library for efficient and RFC-correct representation of URIs and IRIs.

The generic syntax for URIs is defined in RFC 3986;
this is extended in RFC 3987 to support extended characters outside of the ASCII range. 
The `URI` and `IRI` types defined in this library are `namedtuple` objects which store their string components as `bytes` and `str` respectively.

To create an URI or IRI, simply pass a `bytes` or `str` object into the `xri` function:
```python
>>> from xri import xri
>>> uri = xri(b"http://example.com/a/b/c?q=x#z")
>>> uri
<http://example.com/a/b/c?q=x#z>
>>> iri = xri("http://example.com/ä/b/c?q=x#z")
>>> iri
«http://example.com/ä/b/c?q=x#z»
```
