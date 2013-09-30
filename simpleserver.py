from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class _HttpHandler(BaseHTTPRequestHandler):
    """
    Extracts the response from the class attribute "_HttpHandler.data".,
    according to the path requested. GET /a/b/c is evaluated as
    _HttpHandler.data['a']['b']['c']. Functions are replaced by their
    returned values.
    """
    def do_GET(self):
        if self.path.startswith('/'):
            self.path = self.path[1:]

        value = _HttpHandler.data
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

def blocking_serve(data, port=80, stop_condition=lambda: False):
    """
    Starts an HTTP server in a new thread that returns the values from the
    given data. GET /a/b/c is evaluated as data['a']['b']['c']. If
    an intermediary value is a function, it'll be invoked and the return value
    used.

    Blocks until `stop_condition` returns True.
    """
    server_address = ('', port)
    _HttpHandler.data = data
    httpd = HTTPServer(server_address, _HttpHandler)
    while not stop_condition():
        httpd.handle_request()

def serve(data, port=80, stop_condition=lambda: False):
    from threading import Thread
    Thread(target=blocking_serve, args=(data, port, stop_condition)).start()

if __name__ == '__main__':
    serve('It works!', port=8080)
