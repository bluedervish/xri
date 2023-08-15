# XRI

XRI is a small Python library for efficient and RFC-correct representation of URIs and IRIs.

The generic syntax for URIs is defined in RFC 3986;
this is extended in RFC 3987 to support extended characters outside of the ASCII range. 
The `URI` and `IRI` types defined in this library implement those definitions.
Each is a `namedtuple` object which stores its string components as `bytes` or `str` values respectively.


## Creating a URI/IRI

The simplest way to get started is to use the `xri` function.
This can accept a `bytes` or `str` object, and will generate the a URI or IRI value respectively.

```python-repl
>>> from xri import xri
>>> xri(b"http://example.com/a/b/c?q=x#z")
<http://example.com/a/b/c?q=x#z>
>>> xri("http://example.com/ä/b/c?q=x#z")
«http://example.com/ä/b/c?q=x#z»
```
