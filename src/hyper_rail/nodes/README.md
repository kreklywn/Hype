# Nodes

Driven by the roscore to communicate between all parts of the ROS structure
Files here should be left without file extensions as it looks cleaner, and they require a shebang line at the beginning (#!/usr/bin/env python3)

### CS467 Fall Updates
- The eGreenhouse_Driver.py code provides the ability to constantly poll the different sensors at a rate of 9hz or every ~110ms to gather the CO2, temperature, humdity and luminosity readings. The only additional work that the team added involving the sensor data was creating the main program node that subscribes to the topic that sensor node publishes too. Therefore, the system has the ability to obtain the greenhouse sensor data at a high level and send that data to any other entities that are subcribed to the program node i.e. the user interface.

## Dependencies
- GreenhouseSensorReadings.msg - Defines the message type that is published to the topic
- serial_comms.eGreenhouse_Driver - Defines the poll_data() module to obtain the current sensor readings
- communication.constants - Contains GREENHOUSE_SENSOR_SERIAL, which is an array that contains the sensor device port and baud rate

To run the Greenhouse Sensor Parser node, run the following commands in separate terminals:
* `roscore`
* `rosrun hyper_rail GreenhouseSensorParser`

## Notes
- The polling occurs in the greenhouse driver located at the following path: HyperRail/src/hyper_rail/src/serial_comms/eGreenhouse_Driver.py
- The greenhouse driver reads 223 bytes of data from the sensor port and serializes one json object. From there, we can access each attribute, i.e. CO2, temperature etc.
