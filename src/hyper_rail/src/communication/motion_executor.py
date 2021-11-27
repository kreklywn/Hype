#!/usr/bin/env python3

# This class handles data passing through the Motion node

import rospy
import time
import math

from queue import Queue
from communication.constants import GCODE_SCALE

from hyper_rail.msg import MachinePosition                                                  # Message format for current position polling
from hyper_rail.msg import ProgramStatus

from hyper_rail.srv import PathService, PathServiceRequest
from hyper_rail.srv import MotionService, MotionServiceRequest, MotionServiceResponse       # For incoming waypoints
from hyper_rail.srv import ManualService, ManualServiceRequest, ManualServiceResponse      # For individual Gcodes received from UI

class MotionWatcher:
    def __init__(self, publisher):
        self.location = None
        self.motion_status = "idle" 
        self.response_status = ""
        self.single_codes = Queue()
        self.w = ""
        self.publisher = publisher
        self.publish_rate = rospy.Rate(10)

    def watch_for_single_codes(self):
        while True:
            if not self.single_codes.empty():
                cur = self.single_codes.get()
                print(cur)
                self.motion_status = f"Executing {cur}"
                code = cur.split(" ")
                print("manual code:",code)
                if code[0] == "G00" or code[0] == "G01":
                    self.calculate_intermediates(code)
                # Parse Code
                # Calc intermediate waypoints
                # Publish
                # Return Response
                self.motion_status = 'idle'


    def update_position(self, Position: MachinePosition):
        self.location = Position.machinePosition
        # status = Position.status
    
    def update_program_status(self, Status: ProgramStatus):
        self.motion_status = Status.status

    def calculate_intermediates(self, GCode):
        code = GCode[0]
        x_dest = float(GCode[1])
        y_dest = float(GCode[2])
        z_dest = float(GCode[3])
        codes = []
        x = float(self.location.x)
        y = float(self.location.y)

        x_distance = abs(x - x_dest)
        y_distance = abs(y - y_dest)

        angle = math.atan2(y_distance, x_distance)
        x_inc = 5 * math.cos(angle)
        y_inc = 5 * math.sin(angle)
        print("x-increment {} y-increment{}".format(round(x_inc, 5), round(y_inc, 5)))


        while abs(x_dest - x) > x_inc or abs(y_dest - y) > y_inc:
            if x_dest - (x) > 0:
                x += x_inc
            elif x_dest - (x) < 0:
                x -= x_inc
            if y_dest - (y ) > 0:
                y += y_inc 
            elif y_dest - (y ) < 0:
                y -= y_inc 
            next_code = "{} {} {} 0".format(code, round(x, 5), round(y, 5))
            print(next_code)
            codes.append(next_code)
            time.sleep(0.1)

        if not math.isclose(x, x_dest, abs_tol=0.001) or not math.isclose(y, y_dest, abs_tol=0.001):
            x = x_dest
            y = y_dest
            codes.append("{} {} {} 0".format(code, round(x, 5), round(y, 5)))

        for code in codes:
            self.publisher.publish(code)
            self.publish_rate.sleep() 
        
        while not (math.isclose(self.location.x, x_dest, abs_tol=0.01) and math.isclose(self.location.y, y_dest, abs_tol=0.01)):
            print("current location: {} {} destination: {} {}                          MotionNode".format(self.location.x, self.location.y, x_dest, y_dest))
            time.sleep(1)
        
        print("current location: {} {}                           MotionNode".format(self.location.x, self.location.y))


    def receive_waypoint(self, req: MotionService):
        """Receives a waypoint from the ProgramNode, splits up the distance and publishes a series of codes to GCodeFeed
        Wait until destination is reached or the movement errors out and send the resposne to the ProgramNode"""
        print(req)
        self.motion_status = f"Executing {req.program}"
        # Local vars for calcualting intermediate destinations
        codes = []
        x = float(self.location.x)
        y = float(self.location.y)

        x_dest = req.x * GCODE_SCALE
        y_dest = req.y * GCODE_SCALE

        x_distance = abs(x - x_dest)
        y_distance = abs(y - y_dest)

        angle = math.atan2(y_distance, x_distance)
        x_inc = 5 * math.cos(angle)
        y_inc = 5 * math.sin(angle)
        print("x-increment {} y-increment{}".format(round(x_inc, 5), round(y_inc, 5)))


        while abs(x_dest - x) > x_inc or abs(y_dest - y) > y_inc:
            if x_dest - (x) > 0:
                x += x_inc
            elif x_dest - (x) < 0:
                x -= x_inc
            if y_dest - (y ) > 0:
                y += y_inc 
            elif y_dest - (y ) < 0:
                y -= y_inc 
            next_code = "G00 {} {} 0".format(round(x, 5), round(y, 5))
            print(next_code)
            codes.append(next_code)
            time.sleep(0.1)

        if not math.isclose(x, x_dest, abs_tol=0.001) or not math.isclose(y, y_dest, abs_tol=0.001):
            x = x_dest
            y = y_dest
            codes.append("G00 {} {} 0".format(round(x, 5), round(y, 5)))

        for code in codes:
            self.publisher.publish(code)
            self.publish_rate.sleep()

        # Monitor location until destination reached, then send response to ProgramNode
        # TODO: add in error handling
        while not (math.isclose(self.location.x, x_dest, abs_tol=0.01) and math.isclose(self.location.y, y_dest, abs_tol=0.01)):
            print("current location: {} {} destination: {} {}                          MotionNode".format(self.location.x, self.location.y, x_dest, y_dest))
            time.sleep(1)
        
        print("current location: {} {}                           MotionNode".format(self.location.x, self.location.y))
        print("motion status at end, ", self.motion_status)
        if req.program == None:
            print("program in None", req.program)
            self.motion_status = 'idle'
        return MotionServiceResponse("ok")

    def receive_manual_operation(self, req: ManualService):
        print("motion_status in receive manual", self.motion_status)
        if self.motion_status != "idle":
            return ManualServiceResponse(f"Busy: {self.motion_status}")
        else:
            self.single_codes.put(req.GCode)
            print(req)
            return ManualServiceResponse(f"{req.GCode} received")
