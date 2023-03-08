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


POST /state
-----------
Sets a new state.

Request body
^^^^^^^^^^^^
The new state as json object. Allowed keys are:

* powerState (string: on, off)
* temperatureSet (decimal: 16 - 28.5)
* mode (string: heating, drying, cooling, fan)

Responses
^^^^^^^^^
+-------+----------------------+--------------------------------------------------+
| Code  | Media Type           | Description                                      |
+=======+======================+==================================================+
| 200   | ``application/json`` | The current state of the air conditioning system |
+-------+----------------------+--------------------------------------------------+
| 400   | ``plain/text``       | Request body malformatted                        |
+-------+----------------------+--------------------------------------------------+