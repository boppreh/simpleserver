simpleserver
============

One liner HTTP server.


    serve('It works!', port=8080)

    $ curl localhost:8080
    It works!
  
  
    serve({'a': {'b': {'c': 'This is /a/b/c'}}}, port=8080)

    $ curl localhost:8080/a/b/c
    This is /a/b/c
