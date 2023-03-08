Integration into Home Assistant
*******************************

If you want to integrate the devices into Home Assistant, you have to edit the `configuration.yaml`-File.

`Documentation of RESTful Sensor <https://www.home-assistant.io/integrations/sensor.rest>`_


Integration of Air Conditioning System
======================================

Example Code::

    sensor:
    - platform: rest
        name: ac1
        resource: http://192.168.10.21:5000/apitest/ac/state
        json_attributes:
        - powerState
        - temperatureSet
        - temperatureMeas
        - mode
        - errorState
    - platform: template
        sensors:
        ac_temperature:
            value_template: "{{ state_attr('sensor.ac1', 'temperatureMeas')}}"
            device_class: temperature
            unit_of_measurement: "°C"