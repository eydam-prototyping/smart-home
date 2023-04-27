:mod:`http_server` - A minimal http server running on MicroPython
*****************************************************************

Example::
    
    srv = http_server.HttpServer(port=8080)

    state = "Running"

    @srv.route("/state", methods=("GET", "POST"))
    def _state(request: http_server.HttpRequest):
        global state
        if request.method == "GET":
            return http_server.HttpResponse(request, state)
        if request.method == "POST":
            state = request.body
            return http_server.HttpResponse(request, state)

    loop = uasyncio.get_event_loop()
    loop.create_task(srv.run())
    loop.run_forever()

.. module:: http_server
   :synopsis: a minimal http server running on MicroPython

Class: :class:`HttpServer`
==========================

.. class:: HttpServer([port: int=80, address: str='0.0.0.0'])
    
    Initializes the http server.

    * port (int, optional): The port, on which the server listens. Defaults to 80.
    * address (str, optional): The IP address of the server. Defaults to '0.0.0.0'.

Methods
-------

.. method:: HttpServer.route(route: str, [methods: tuple=("GET", )])

    Route decorator, adds a route to the server.

    * route (str): The route.
    * methods (tuple, optional): The HTTP methods for the route ("GET", "POST", "PUT", ...). Defaults to ("GET",)

Example::

    @srv.route("/state", methods=("GET", "POST"))
    def _state(request: http_server.HttpRequest):
        global state
        if request.method == "GET":
            return http_server.HttpResponse(request, state)
        if request.method == "POST":
            state = request.body
            return http_server.HttpResponse(request, state)


.. method:: HttpServer.async_route(route: str, [methods: tuple=("GET", )])

    Async route decorator, like route decorator, but for async methods.

    * route (str): The route.
    * methods (tuple, optional): The HTTP methods for the route (GET, POST, PUT, ...). Defaults to ("GET",)

Example::

    @srv.async_route("/state")
    async def _state(request: http_server.HttpRequest):
        global state
        await asyncio.sleep(1)
        return http_server.HttpResponse(request, state)


.. method:: HttpServer.run()

    Start the server.

    This is a coroutine.


Class: :class:`HttpRequest`
===========================

.. class:: HttpRequest(method: str, url: str, version: str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter)

    Initialize a http request. You shouldn't have to do it by yourself.

    * method (str): The HTTP method (GET, POST, DELETE, ...)
    * url (str): The requested URL
    * version (str): The HTTP version
    * reader (asyncio.StreamReader): an async stream reader
    * writer (asyncio.StreamWriter): an async stream writer


Class: :class:`HttpResponse`
============================

.. class:: HttpResponse(request: HttpRequest, data: any, code: int=200, headers=None, default_headers: bool=True)

    Initialize a http response. This is the return value of a route handler.

    * request (HttpRequest): the request, on which this is the response
    * data (any): the data (body), that is returned inside this response.
    * code (int, optional): the http status code. Defaults to 200.
    * headers (dict, optional): if you want to pass additional headers. Defaults to None.
    * default_headers (bool, optional): if you want to send default headers (Content-Type, Content-Length, ...). Defaults to True.

    data can be:

    * ``string`` headers will be added: ``{Content-Type: text/html, Content-Length: <length>}``
    * ``list`` headers will be added: ``{Content-Type: application/json, Content-Length: <length>}``
    * ``dict`` headers will be added: ``{Content-Type: application/json, Content-Length: <length>}``
    * ``tuple`` if you want to send a file:
  
      * ``("file", <type>, <path>)`` headers will be added: ``{Content-Type: <type>, Content-Length: <length>}``

Class: :class:`HttpError(HttpResponse)`
=======================================

.. class:: HttpError(request: HttpRequest, code: int, message: str=None)

    Initialize a http error
    
    * request (HttpRequest): the request, on which this is the response.
    * code (int): the http status code.
    * message (str, optional): if you don't want to send the default message. Defaults to None.