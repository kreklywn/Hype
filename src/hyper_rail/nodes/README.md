# Nodes

Driven by the roscore to communicate between all parts of the ROS structure
Files here should be left without file extensions as it looks cleaner, and they require a shebang line at the beginning (#!/usr/bin/env python3)

### CS467 Fall Updates
- The eGreenhouse_Driver.py code provides the ability to constantly poll the different sensors to gather the CO2, temperature, humdity and luminosity readings. The only additional work that the team added involving the sensor data was creating the main program node that subscribes to the topic that sensor node publishes too. Therefore, the system has the ability to obtain the greenhouse sensor data at a high level and send that data to any other entities that are subcribed to the program node i.e. the user interface.
