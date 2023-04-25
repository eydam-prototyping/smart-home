API Documentation of the smart-home Project
*******************************************

There is a test server, build in flask, that provides a test interface. You can start it from the root directory with::

    flask --app ./test/apitest/ run

If you want to run it in debug mode, just add the debug flag::

    flask --app ./test/apitest/ run --debug

If you want to make it accessible from another PC from the local network, use::
    
    flask --app ./test/apitest/ run --debug --host <IP_OF_TEST_SERVER>

When the server is running, you can access a random state for the Air Conditioning System via::
    
    http://localhost:5000/apitest/ac/state


API for Air Conditioning System
===============================

All routes of the API for the AC are available on the test server via::

    http://localhost:5000/apitest/ac/<route>

The following routes are defined for the Air Conditioning System (a detailed description can be found in the project direcory in ``/api/air-conditioner.yml``):


GET /state
----------
Returns a json object with the state of the air conditioning system.

Responses
^^^^^^^^^
+-------+----------------------+--------------------------------------------------+
| Code  | Media Type           | Description                                      |
+=======+======================+==================================================+
| 200   | ``application/json`` | The current state of the air conditioning system |
+-------+----------------------+--------------------------------------------------+

An example response could look like this::

    {
      "powerState": "OFF", 
      "temperatureSet": 24, 
      "temperatureRoom": 20,  
      "mode": "COOL", 
      "vane": "SWING", 
      "dir": "|", 
      "fan": "QUIET", 
      "errorState": "OK"
    }

The property errorState is currently always "OK".

POST /state
-----------
Sets a new state.

Request body
^^^^^^^^^^^^
The new state as json object. Allowed keys are:

* powerState (string: ON, OFF)
* temperatureSet (decimal: 16 - 31)
* mode (string: HEAT, DRY, COOL, FAN)
* vane (string: AUTO, SWING, 1, 2, 3, 4, 5)
* dir (string: SWING, \<\<, \<, \|, \>,\>\>, \<\>)
* fan (string: AUTO, QUIET, 1, 2, 3, 4)

Responses
^^^^^^^^^
+------+----------------+-----------------------------------------------------+
| Code | Media Type     | Description                                         |
+======+================+=====================================================+
| 200  | ``plain/text`` | OK, if the state has been set, otherwise error code |
+------+----------------+-----------------------------------------------------+
| 400  | ``plain/text`` | Request body malformatted                           |
+------+----------------+-----------------------------------------------------+

GET /networkState
-----------------
Returns a json object with the network state


Responses
^^^^^^^^^
+------+----------------------+----------------------------------------------------------+
| Code | Media Type           | Description                                              |
+======+======================+==========================================================+
| 200  | ``application/json`` | The current network state of the air conditioning system |
+------+----------------------+----------------------------------------------------------+

An example response could look like this::

    {
      "ssid": "WiFi",
      "rssi": -85,
      "mac": "XX:XX:XX:XX:XX:XX",
      "hostname": "AC1",
      "ip": "192.168.178.231",
      "gateway": "192.168.178.1",
      "netmask": "255.255.255.0",
      "dns": "192.168.178.1"
    }

GET /reset
-----------------
Restarts the air conditioning controller.


Responses
^^^^^^^^^
No Response will be send.