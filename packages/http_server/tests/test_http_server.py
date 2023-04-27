import unittest
from http_server import HttpServer, HttpRequest, HttpResponse
import httpx
import asyncio
import json
from ddt import ddt, data, unpack
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class TestHttpServer(unittest.TestCase):
    def setUp(self) -> None:
        self.srv = HttpServer()
        return super().setUp()


    def test_add_route1(self):
        self.assertEqual(len(self.srv.routes), 0)

        @self.srv.route("/test_route")
        def test_route1(request: HttpRequest):
            return "TEST"

        # Route should be added
        self.assertEqual(len(self.srv.routes), 1)
        # Route should be used for GET-Requests (default)
        self.assertEqual(self.srv.routes["/test_route"][0], ("GET", ))
        # Function should be callable
        self.assertEqual(self.srv.routes["/test_route"][1](None), "TEST")


    def test_add_route2(self):
        self.assertEqual(len(self.srv.routes), 0)

        @self.srv.route("/test_route", methods=("GET", "POST"))
        def test_route2(request: HttpRequest):
            return "TEST"

        self.assertEqual(len(self.srv.routes), 1)
        # Route should be used for GET- and POST-Requests
        self.assertEqual(self.srv.routes["/test_route"][0], ("GET", "POST"))
        self.assertEqual(self.srv.routes["/test_route"][1](None), "TEST")

@ddt
class TestAscyncHttpServer(unittest.IsolatedAsyncioTestCase):
    

    async def asyncSetUp(self):
        self.srv = HttpServer(port=8081)
        self.task = asyncio.create_task(self.srv.run())
        return await super().asyncSetUp()

    async def asyncTearDown(self):
        self.srv.stop()
        self.task.cancel()
        asyncio.ensure_future(self.task)
        return await super().asyncTearDown()
    
    @data(
            ('TEST',                                                {'content-type': 'text/html', 'content-length': '4', 'access-control-allow-origin': '*'}),
            ({"key1": "value1", "key2": {"key2.1": "value2.1"}},    {'content-type': 'application/json', 'content-length': '50', 'access-control-allow-origin': '*'}),
            (["a", "b", "c"],                                       {'content-type': 'application/json', 'content-length': '15', 'access-control-allow-origin': '*'}),
            (("file", "text/html", "./tests/test.html"),            {'content-type': 'text/html', 'content-length': '51', 'access-control-allow-origin': '*'}),
        )
    @unpack
    async def test_add_route_get_text(self, test_content, expected_headers):
        @self.srv.route("/test_route")
        def test_route(request: HttpRequest):
            return HttpResponse(request, test_content)
        
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8081/test_route")
        
        self.assertEqual(response.status_code, 200)
        if type(test_content) is str:
            self.assertEqual(response.content.decode("utf-8"), test_content)
        if type(test_content) is dict:
            self.assertEqual(response.content.decode("utf-8"), json.dumps(test_content))
        for key in expected_headers:
            self.assertTrue(key in response.headers)
            self.assertTrue(response.headers[key] == expected_headers[key])
       

if __name__ == '__main__':
    unittest.main()