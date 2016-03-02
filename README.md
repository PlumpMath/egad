#  Extensible Graphite API Daemon

EGAD is a python/bottle application whose purpose is to act as a proxy
in front of a graphite server and allow modification and extension of
the API provided by it. It does this with a plugin system that allows
easy extensibility. For each API call to graphite if a plugin claims
the request it is then allowed to respond how it sees fit. The current
use-case is to fix-up certain types of queries to work the way a naive
user would expect them to before passing them off to graphite and
relaying the results back to the requester. If no plugin claims a
request then it is transparently proxied to graphite and the results
returned without any changes to the content.

EGAD allows developers to extend the functionality of their metrics
querying engine that rely upon graphite in a way that doesn't involve
modifying the graphite source or breaking compatibility with any existing
graphite tools.

