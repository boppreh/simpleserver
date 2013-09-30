from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urlparse import urlparse, parse_qs

class _HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        o = urlparse(self.path)
        result, _ = navigate_value(_HttpHandler.data[0], o.path)

        query_string = parse_qs(o.query)
        if hasattr(result, '__call__') and len(query_string):
            # parse_qs returns the values as lists (because you can declare the
            # same value many times), so we have to extract only a single
            # instance for each parameter name.
            arguments = {name: value[0] for name, value in query_string.items()}
            print arguments
            result = result(**arguments)

        self.wfile.write(str(result))

def navigate_value(value, http_path):
    """
    Takes an initial value and a http path of the form "/some/path" and returns
    (value['some'], value['some']['path']), converting list accesses to integer
    indexes (value[2] or value['2'] depending on the type of `value`) and
    replacing function values with their returns (value['some']()['path']).
    """
    parent = None
    for part in filter(bool, http_path.split('/')):
        parent = value

        # Use parts as list indexes.
        if isinstance(value, list):
            part = int(part)
        # Replace function values by their returns.
        elif hasattr(value, '__call__'):
            value = value()

        value = value[part]

    return (value, parent)

def blocking_serve(data, port=80, stop_condition=lambda: False):
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
    httpd = HTTPServer(server_address, _HttpHandler)
    while not stop_condition():
        httpd.handle_request()

def serve(data, port=80, stop_condition=lambda: False):
    """
    Starts an HTTP server in a new thread that returns the values from the
    given data. GET /a/b/c is evaluated as data['a']['b']['c']. If
    an intermediary value is a function, it'll be invoked and the return value
    used.

    Continues running in the background until `stop_condition` returns True.
    """
    from threading import Thread
    Thread(target=blocking_serve, args=(data, port, stop_condition)).start()

if __name__ == '__main__':
    serve(lambda x, y: int(x) + int(y), port=8080)
