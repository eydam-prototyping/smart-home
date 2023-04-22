import http_server
import ujson
import umachine

_sta_if = None
_ac_state = None
_adp = None

def setup(sta_if, ac_state, adp):
    global _sta_if
    global _ac_state
    global _adp
    _sta_if = sta_if
    _ac_state = ac_state
    _adp = adp

def reset(request: http_server.HttpRequest):
    umachine.reset()

def networkState(request: http_server.HttpRequest):
    global _sta_if
    ifconfig = _sta_if.ifconfig()
    data = {
        "ip": ifconfig[0],
        "netmask": ifconfig[1],
        "gateway": ifconfig[2],
        "dns": ifconfig[3],
        "ssid": _sta_if.config("essid"),
        "mac": ":".join(["{:02X}".format(x) for x in _sta_if.config("mac")]),
        "hostname": _sta_if.config("dhcp_hostname"),
        "rssi": _sta_if.status("rssi")
    }
    return http_server.HttpResponse(request, data)

def networkConfig(request: http_server.HttpRequest):
    with open("wifi_credentials.json", "w") as f:
        ujson.dump(request.body, f)
    return http_server.HttpResponse(request, "OK")

async def state(request: http_server.HttpRequest):
    if request.method == "GET":
        global _ac_state
        if _ac_state is None:
            _ac_state = {}
        data = {
            "powerState": _ac_state.get("POWER", (None,None))[1],
            "temperatureSet": _ac_state.get("TEMP", (None,None))[1],
            "temperatureRoom": _ac_state.get("ROOMTEMP", (None,None))[1],
            "mode": _ac_state.get("MODE", (None,None))[1],
            "fan": _ac_state.get("FAN", (None,None))[1],
            "vane": _ac_state.get("VANE", (None,None))[1],
            "dir": _ac_state.get("DIR", (None,None))[1],
            "errorState": _ac_state.get("ERROR", "OK"),
        }
        return http_server.HttpResponse(request, data)
    elif request.method == "POST":
        valid_keys = ["powerState", "temperatureSet", "mode", "fan", "vane", "dir"]
        
        for key in request.body:
            if key not in valid_keys:
                return http_server.HttpError(request, 400, f"Key {key} is not allowed. Allowd keys are {valid_keys}")
        
        new_state = {}
        if "powerState" in request.body:
            if request.body["powerState"] in [0, "0", "off", "Off", "OFF"]:
                new_state["POWER"] = 0
            elif request.body["powerState"] in [1, "1", "on", "On", "ON"]:
                new_state["POWER"] = 1
            else:
                return http_server.HttpError(request, 400, "could not parse powerState")
            
        if "temperatureSet" in request.body:
            try:
                # round to x.0 or x.5
                t = float(request.body["temperatureSet"])
                t = round(2*t)/2
                new_state["TEMP"] = max(min(t,31.5),16)
            except:
                return http_server.HttpError(request, 400, "could not parse temperatureSet")
            
        if "mode" in request.body:
            if request.body["mode"] in [1, "1", "heat", "Heat", "HEAT"]:
                new_state["MODE"] = 1
            elif request.body["mode"] in [2, "2", "dry", "Dry", "DRY"]:
                new_state["MODE"] = 2
            elif request.body["mode"] in [3, "3", "cool", "Cool", "COOL"]:
                new_state["MODE"] = 3
            elif request.body["mode"] in [7, "7", "fan", "Fan", "FAN"]:
                new_state["MODE"] = 7
            elif request.body["mode"] in [8, "8", "auto", "Auto", "AUTO"]:
                new_state["MODE"] = 8
            else:
                return http_server.HttpError(request, 400, "could not parse mode")
            
        if "fan" in request.body:
            if request.body["fan"] in [0, "0", "auto", "Auto", "AUTO"]:
                new_state["FAN"] = 0
            elif request.body["fan"] in ["quiet", "Quiet", "QUIET"]:
                new_state["FAN"] = 1
            elif request.body["fan"] in [1, "1"]:
                new_state["FAN"] = 2
            elif request.body["fan"] in [2, "2"]:
                new_state["FAN"] = 3
            elif request.body["fan"] in [3, "3"]:
                new_state["FAN"] = 5
            elif request.body["fan"] in [4, "4"]:
                new_state["FAN"] = 6
            else:
                return http_server.HttpError(request, 400, "could not parse fan")
            
        if "vane" in request.body:
            if request.body["vane"] in [0, "0", "auto", "Auto", "AUTO"]:
                new_state["VANE"] = 0
            elif request.body["vane"] in [7, "7", "swing", "Swing", "SWING"]:
                new_state["VANE"] = 7
            else:
                try:
                    v = int(request.body["vane"])
                    if v in range(1,6): # check, if i in [1,5]; i=6 is not defined 
                        new_state["VANE"] = v
                except:
                    return http_server.HttpError(request, 400, "could not parse vane")
            
        if "dir" in request.body:
            if request.body["dir"] in [0, "0", "na", "Na", "NA"]:
                new_state["DIR"] = 0
            elif request.body["dir"] in [1, "1", "<<"]:
                new_state["DIR"] = 1
            elif request.body["dir"] in [2, "2", "<"]:
                new_state["DIR"] = 2
            elif request.body["dir"] in [3, "3", "|"]:
                new_state["DIR"] = 3
            elif request.body["dir"] in [4, "4", ">"]:
                new_state["DIR"] = 4
            elif request.body["dir"] in [5, "5", ">>"]:
                new_state["DIR"] = 5
            elif request.body["dir"] in [8, "8", "<>"]:
                new_state["DIR"] = 8
            elif request.body["dir"] in [12, "12", "swing", "Swing", "SWING"]:
                new_state["DIR"] = 12
            else:
                return http_server.HttpError(request, 400, "could not parse dir")

        try:
            await _adp.ac_set_state(new_state)
        except:
            return http_server.HttpError(request, 500, "could not set new state")

        return http_server.HttpResponse(request, "OK")
    

def raw_state(request: http_server.HttpRequest):
        global _ac_state
        if _ac_state is None:
            _ac_state = {}
        data = {
            "powerState": _ac_state.get("POWER", (None,None))[1],
            "temperatureSet": _ac_state.get("TEMP", (None,None))[1],
            "temperatureRoom": _ac_state.get("ROOMTEMP", (None,None))[1],
            "mode": _ac_state.get("MODE", (None,None))[1],
            "fan": _ac_state.get("FAN", (None,None))[1],
            "vane": _ac_state.get("VANE", (None,None))[1],
            "dir": _ac_state.get("DIR", (None,None))[1],
            "raw1": _ac_state.get("RAW1", (None,None)),
            "raw2": _ac_state.get("RAW2", (None,None)),
            "errorState": _ac_state.get("ERROR", "OK"),
        }
        return http_server.HttpResponse(request, data)