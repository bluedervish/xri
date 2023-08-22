==========================================
``xri`` -- Parse and compose URIs and IRIs
==========================================

.. module:: xri


URIs and IRIs
=============

.. autofunction:: xri

.. autoclass:: URI
    :members:

.. autoclass:: IRI
    :members:

Normalisation and Comparison
----------------------------

.. describe:: bytes(uri)

.. describe:: str(uri)

.. describe:: bytes(iri)

.. describe:: str(iri)

Scheme
------
TODO

Authority
---------
TODO

Path
----
TODO

Query
------
TODO

Fragment
--------
TODO


Reference Resolution
====================
TODO


Characters and Percent Encoding
===============================

.. autodata:: RESERVED_CHARS

.. autodata:: UNRESERVED_CHARS

.. autofunction:: pct_encode

.. autofunction:: pct_decode
