import network
import ujson
import umachine
import utime
import uasyncio
import http_server
import ac_adap
import uos
import routes

WIFI_CONNECT_TIMEOUT = 20

sta_if = None
wifi_credentials = None

print("loading wifi credentials... ", end="")
with open("wifi_credentials.json", "r") as f:
    wifi_credentials = ujson.load(f)
print("done")

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

utime.sleep_us(100)
if "hostname" in wifi_credentials:
    print("trying to set dhcp hostname... ", end="")
    try:
        sta_if.config(dhcp_hostname=wifi_credentials["hostname"])
        print("done")
    except:
        print("could not set dhcp hostname")

print("Connecting to Wifi " + wifi_credentials["ssid"] + "... ", end="")
# check, if wifi is connected after soft reset
if not sta_if.isconnected():
    sta_if.connect(wifi_credentials["ssid"], wifi_credentials["password"])

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

srv = http_server.HttpServer()
ac_state = {}

adp = ac_adap.AcAdapter()

routes.setup(sta_if, ac_state, adp)

srv.async_routes["/state"] = (("GET", "POST", "OPTIONS"), routes.state)
srv.routes["/rawState"] = (("GET", ), routes.raw_state)
srv.routes["/reset"] = (("GET",), routes.reset)
srv.routes["/networkState"] = (("GET",), routes.networkState)

async def read_ac_state():
    global ac_state
    while True:
        try:
            if adp.connected:
                await uasyncio.sleep(5)
                packet = await adp.ac_get_state1()
                ac_state.update(packet.data)
                ac_state["RAW1"] = str(packet)
                packet = await adp.ac_get_state2()
                ac_state.update(packet.data)
                ac_state["RAW2"] = str(packet)
            else:
                await adp.ac_connect()
        except:
            adp.connected = False
            adp.ac_connect()
            print("ac error")


async def check_wifi_state():
    # while wifi is connected, do noting
    while sta_if.isconnected():
        await uasyncio.sleep(10)
    
    # check, if wifi_credentials.json exists
    wifi_credentials_exists = True
    try:
        uos.stat("wifi_credentials.json")
    except:
        wifi_credentials_exists = False

    # if wifi_credentials.json exists, 
    #   reboot every 5 min and try to reconnect 
    #   (maybe wifi is just temporarily not available)
    # else
    #   no need to check wifi state any longer
    if wifi_credentials_exists:
        await uasyncio.sleep(300)
        umachine.reset()
    else:
        return


loop = uasyncio.get_event_loop()
loop.create_task(srv.run())
loop.create_task(read_ac_state())
loop.create_task(check_wifi_state())
try:
    loop.run_forever()
    # Sometimes, an "IndexError: empty heap" occures.
    # I have no idea, why
except:
    umachine.soft_reset()