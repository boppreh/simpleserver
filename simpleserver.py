try:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from urlparse import urlparse, parse_qs
except:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import parse_qs, urlparse
from posixpath import basename

class _HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        o = urlparse(self.path)

        result, _ = _navigate_value(_HttpHandler.data[0], o.path)
        result = _conditional_invocation(result, o.query)

        self.wfile.write(str(result))

    def do_POST(self):
        o = urlparse(self.path)
        result, parent = _navigate_value(_HttpHandler.post_data[0], o.path)

        # Append body to lists.
        if hasattr(result, 'append'):
            result.append(self.rfile.read())
        # Invoke functions.
        elif hasattr(result, '__cal__'):
            result = _conditional_invocation(result, o.query)
        # Replace strings in a dictionary.
        elif isinstance(result, str) and hasattr(parent, '__setitem__'):
            result = self.rfile.read()
            parent[basename(o.path)] = result

        self.wfile.write(bytes(str(result), 'utf-8'))


def _conditional_invocation(result, query):
    """
    Try to invoke `result` with the arguments in the query string `query`,
    returning the result or result unchanged if not possible.
    """
    query_dict = parse_qs(query)
    if hasattr(result, '__call__') and len(query_dict):
        # parse_qs returns the values as lists (because you can declare the
        # same value many times), so we have to extract only a single
        # instance for each parameter name.
        arguments = {name: value[0] for name, value in query_dict.items()}
        return result(**arguments)
    else:
        return result

def _navigate_value(value, http_path):
    """
    Takes an initial value and a http path of the form "/some/path" and returns
    (value['some'], value['some']['path']), converting list accesses to integer
    indexes (value[2] or value['2'] depending on the type of `value`) and
    replacing function values with their returns (value['some']()['path']).
    """
    parent = None

    if hasattr(value, '__call__'):
        value = value()

    for part in filter(bool, http_path.split('/')):
        parent = value

        # Use parts as list indexes.
        if isinstance(value, list):
            part = int(part)
        # Replace function values by their returns.
        elif hasattr(value, '__call__'):
            value = value()

        value = value[part]

    if hasattr(value, '__call__'):
        value = value()


    return (value, parent)

def blocking_serve(data, post_data=None, port=80, stop_condition=lambda: False):
    """
    Starts an HTTP server in a new thread that returns the values from the
    given data. GET /a/b/c is evaluated as data['a']['b']['c']. If
    an intermediary value is a function, it'll be invoked and the return value
    used.

    Blocks until `stop_condition` returns True.
    """
    server_address = ('', port)
    # Wrap in a list so if `data` is a function it doesn't become bound to the
    # class.
    _HttpHandler.data = [data]
    _HttpHandler.post_data = [post_data]
    httpd = HTTPServer(server_address, _HttpHandler)
    while not stop_condition():
        httpd.handle_request()

def serve(data, post_data=None, port=80, stop_condition=lambda: False):
    """
    Starts an HTTP server in a new thread that returns the values from the
    given data. GET /a/b/c is evaluated as data['a']['b']['c']. If
    an intermediary value is a function, it'll be invoked and the return value
    used. Query params can be used in the URL to specify the function
    arguments.

    Continues running in the background until `stop_condition` returns True.
    """
    args = (data, post_data, port, stop_condition)
    from threading import Thread
    Thread(target=blocking_serve, args=args).start()

if __name__ == '__main__':
    serve({}, post_data={'a': 'b'}, port=8080)
