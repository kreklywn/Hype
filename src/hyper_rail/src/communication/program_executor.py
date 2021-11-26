#!/usr/bin/env python3

# This class watches for programs to be added to the queue and executes them as the come in.
# FIXME: change the name of this file and move to a better spot

import rospy
import time
from threading import Thread
from queue import Queue
from hyper_rail.srv import PathService, PathServiceRequest, MotionService, SensorService
from hyper_rail.msg import MotionStatus
from stitcher import HRStitcher
from db_queries import DatabaseReader
import ast
import os

class Watcher:
    def __init__(self, q, publisher):
        self.q = q
        self.response_status = ""
        self.program_status = "idle"
        self.w = ""
        self.publisher = publisher
        self.test_program = [{'x': 10, 'y': 15}, {'x': 16, 'y': 21}, {'x': 2, 'y': 13}]
        self.test_program2 = [{'x': 3, 'y': 7, 'action': 1}, {'x': 2, 'y': 4, 'action': 2}, {'x': 8, 'y':9, 'action': 3}]
        self.home_program = [{'x': 0, 'y': 0}]
        self.db = ""

    def watch(self):
        while True:
            if not self.q.empty():
                if self.motion_status == 'idle':
                    self.db = DatabaseReader()
                    program = self.q.get()
                    self.program_status = f"executing: program {program}"
                    status = self.execute(program)
                    print(status)
                    # self.execute(self.home_program)
                    del self.db

    def update_motion_status(self, Status: MotionStatus):
        self.motion_status = Status.status 

    # sends the x, y coordinates of a waypoint to the the motion node
    def goTo(self, x, y, program):
        rospy.wait_for_service('motion_service')
        try:
            message = rospy.ServiceProxy('motion_service', MotionService)
            resp1 = message(x, y, program)
            return resp1.status
        except rospy.ServiceException as e:
            print("Service call failed: %s"%e)
    
    # sends the action to the sensor node
    def sensorAction(self, program_run_id, run_waypoint_id, action):
        print("action: ", action)
        if action == "temperature":
            srv = 'sensor_service'
        elif action == "image":
            srv = 'camera_service'
        elif action == "humidity":
            print("Humidity not available")
            return 
        elif action == "lux":
            print("Lux not available")
            return

        rospy.wait_for_service(srv)
        try:
            message = rospy.ServiceProxy(srv, SensorService)
            resp1 = message(program_run_id, run_waypoint_id, str(action))
            print("%s returned: %s"%(srv, resp1.status))
            return resp1.status
        except rospy.ServiceException as e:
            print("Service call failed: %s"%e)

    def execute(self, program):
        # 1. get waypoints for the specified program
        print("program: {}".format(program))
        waypoints = self.db.get_waypoints_for_program(program)
        run_id = self.db.create_program_run(program)

        # 2. Execute each waypoint/action
        w_count = 0
        for w in waypoints:
            run_waypoint_id = self.db.create_run_waypoint_id(w['id'], run_id, w['x'], w['y'], w['z'])
            print(f"\nExecuting waypoint {w['id']}, actions: {w['actions']}\n")
            actions = ast.literal_eval(w['actions'])
            # for action in actions:
            #     print(action)

            if w_count < len(waypoints):
                status = self.goTo(w['x'], w['y'], program)
            else:
                status = self.goTo(w['x'], w['y'], None)
            #TODO: Need to create run waypoints to send to camera node

            threads = []
            for action in actions:
                threads.append(Thread(target = self.sensorAction, args=(run_id, run_waypoint_id, action,)))
                # if action == "temperature":
                #     threads.append(Thread(target = self.sensorAction, args=(run_id, run_waypoint_id, 1,)))
                #     threads[-1].daemon = True
                # elif action == "image":
                #     threads.append(Thread(target = self.sensorAction, args=(run_id, run_waypoint_id, 2,)))
                #     threads[-1].daemon = True
                # elif action == "humidity":
                #     threads.append(Thread(target = self.sensorAction, args=(run_id, run_waypoint_id, 3,)))
                #     threads[-1].daemon = True
                # elif action == "lux":
                #     threads.append(Thread(target = self.sensorAction, args=(run_id, run_waypoint_id, 4,)))
                #     threads[-1].daemon = True

            
            for t in threads:
                t.start()
            
            for t in threads:
                t.join()

            self.db.update_run_waypoint_id_finished(run_waypoint_id)
            w_count += 1
        
        # 3. Create stitched image
        run_id = 10
        image_types = self.db.get_image_types_for_program_run(run_id)
        print(image_types)
        for t in image_types:

            #TODO: Need to handle each type of image - get image types for program run. for each type, stitch
            # TODO: run_id is being set here for testing with mock data. Remove this line for implementation
            paths = self.db.get_image_paths(run_id, t['image_type'])
            relative_paths = []
            for path in paths:
                relative_paths.append(f"{run_id}/{t['image_type']}/{path}")
            print(relative_paths)
            dir = f"{run_id}/{t['image_type']}"

            outfile = f"{t['image_type']}_stitch.tiff"
            stitcher = HRStitcher(paths, outfile, dir)
            stitcher.stitch()

        self.db.update_program_run_finished(run_id)
        # TODO: Add update to include the finished_at time for program_run
        # TODO: add error handling
        return 'ok'
