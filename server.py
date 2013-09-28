from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class _HttpHandler(BaseHTTPRequestHandler):
    """
    Extracts the response from the class attribute "_HttpHandler.dictionary".,
    according to the path requested. GET /a/b/c is evaluated as
    _HttpHandler.dictionary['a']['b']['c']. Functions are replaced by their
    returned values.
    """
    def do_GET(self):
        if self.path.startswith('/'):
            self.path = self.path[1:]

        value = _HttpHandler.dictionary
        if self.path:
            for part in self.path.split('/'):
                # Use parts as list indexes.
                if isinstance(value, list):
                    part = int(part)

                value = value[part]

                # Replace function values by their returns.
                if hasattr(value, '__call__'):
                    value = value()

        self.wfile.write(str(value))

def serve(dictionary, port=80, stop_condition=lambda: False):
    """
    Starts an HTTP server in a new thread that returns the values from the
    given dictionary. GET /a/b/c is evaluated as dictionary['a']['b']['c']. If
    an intermediary value is a function, it'll be invoked and the return value
    used.

    Blocks until `stop_condition` returns True.
    """
    server_address = ('', port)
    _HttpHandler.dictionary = dictionary
    httpd = HTTPServer(server_address, _HttpHandler)
    while not stop_condition():
        httpd.handle_request()
