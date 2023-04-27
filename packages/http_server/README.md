Minimal HTTP-Server running von MicroPython
===========================================

Example usage:

```python
import network
import ujson
import utime
import uasyncio
import http_server

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect("<SSID>", "<PASS>")

WIFI_CONNECT_TIMEOUT = 20
i = 0
while not (sta_if.isconnected() or (i>WIFI_CONNECT_TIMEOUT)):
    print(". ", end="")
    utime.sleep(1)
    i += 1

if sta_if.isconnected():
    print("connected!")
    print("My IP is: " + sta_if.ifconfig()[0])
else:
    print("could not connect to wifi (timeout)")

srv = http_server.HttpServer(port=8080)

state = "Running"

@srv.route("/state", methods=("GET", "POST"))
async def state(request: http_server.HttpRequest):
    if request.method == "GET":
        return HttpResponse(request, state)
    if request.method == "POST":
        state = request.body
        return HttpResponse(request, state)

loop = uasyncio.get_event_loop()
loop.create_task(srv.run())
loop.run_forever()
```

You can access the http server with `curl` or a web browser:

```powershell
tobias@Tobias-DellXPS:~$ curl http://192.168.10.45:8080/state
Running
tobias@Tobias-DellXPS:~$ curl http://192.168.10.45:8080/state -X POST -d Stopped -H "Content-Type: text/html"
Stopped
```

The output would be:

```
My IP is: 192.168.10.45
Request: GET /state -> 200 Running
Request: POST /state -> 200 Stopped
```

For more details see: https://eydam-prototyping-smart-home.readthedocs.io/en/latest/packages_http_server.html