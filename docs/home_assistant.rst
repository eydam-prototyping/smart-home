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
            resource: http://<IP>/state
            json_attributes:
            - powerState
            - temperatureSet
            - temperatureRoom
            - mode
            - fan
            - vane
            - dir
            - errorState

        - platform: template
            sensors:
            ac1_tempset:
                value_template: "{{ state_attr('sensor.ac1', 'temperatureSet') }}"
                device_class: temperature
                unit_of_measurement: "°C"
            ac1_temproom:
                value_template: "{{ state_attr('sensor.ac1', 'temperatureRoom') }}"
                device_class: temperature
                unit_of_measurement: "°C"
            ac1_mode:
                value_template: "{{ state_attr('sensor.ac1', 'mode') }}"
            ac1_power:
                value_template: "{{ state_attr('sensor.ac1', 'powerState') }}

    rest_command:
        ac1_state:
            url: http://<IP>/state
            method: POST
            payload: '{"powerState": "{{ states.input_boolean.ac1_power.state }}", "temperatureSet": {{ states.input_number.ac1_temperature.state }}, "mode": "{{ states.input_select.ac1_mode.state }}"}'
            content_type: 'application/json'