#!/usr/bin/env python3

# This class watches for programs to be added to the queue and executes them as the come in.
# FIXME: change the name of this file and move to a better spot

import rospy
import time
import json
import os
from threading import Thread
from queue import Queue
from hyper_rail.srv import PathService, PathServiceRequest, MotionService, SensorService
from pathlib import Path 
from communication.storage_executor import Storage 

PATH = "/home/peter/"

def add_new_dirs(data_dir, program_name, run_count):
        full_path =  PATH + data_dir + '/' + program_name + '/' + run_count + '/'
        if not os.path.exists(full_path):
            print(full_path)
            os.makedirs(full_path)
        return full_path
        
class Watcher:
    def __init__(self, q, publisher):
        self.q = q
        self.response_status = ""
        self.w = ""
        self.publisher = publisher
        self.test_program = [{'x': 10, 'y': 15}, {'x': 16, 'y': 21}, {'x': 2, 'y': 13}]
        self.test_program2 = [{'x': 3, 'y': 7, 'action': 1, 'wp_id': 1}, {'x': 2, 'y': 4, 'action': 2, 'wp_id': 2}, {'x': 8, 'y':9, 'action': 3, 'wp_id': 3}]
        self.home_program = [{'x': 0, 'y': 0}]

    def watch(self):
        while True:
            # FIXME: change to if not empty once working with database
            if not self.q.empty():
                program = self.q.get()
                status = self.execute(self.test_program2)
                print(status)
                self.execute(self.home_program)

    # sends the x, y coordinates of a waypoint to the the motion node
    def goTo(self, x, y):
        rospy.wait_for_service('motion_service')
        try:
            message = rospy.ServiceProxy('motion_service', MotionService)
            resp1 = message(x, y)
            return resp1.status
        except rospy.ServiceException as e:
            print("Service call failed: %s"%e)
    
    # sends the action to the sensor node
    def sensorAction(self, action, wp_json):
        print("action: ", action)
        if action == 1:
            srv = 'sensor_service'
        elif action == 2:
            srv = 'camera_service'
        rospy.wait_for_service(srv)
        try:
            # this is where the camera_service1 is being called made change
            message = rospy.ServiceProxy(srv, SensorService)
            resp1 = message(action = str(action), waypoint_info = wp_json)
            print("%s returned: %s"%(srv, resp1.status))
            return resp1.status
        except rospy.ServiceException as e:
            print("Service call failed: %s"%e)   # new_dir(program_run_dir)
    
    def execute(self, program):
        print("executing %s"%(program))
        # Program lookup will go here
        # waypoints = db.get(FROM waypoints WHERE programId == program)
        # for w in waypoints:
        # get the programs name, expicit name, how many times it has been run.
        
        # create direcotry for latest run given from waypoints database
        # should names of program and run count
        data_dir = 'program_data'
        program_name = 'firstprogram'
        run_count = '1'
        camera_dir = data_dir + '/' + program_name + '/' + run_count
        # sensor_path = add_new_dirs(data_dir  = 'program_data', program_name = 'firstProgram', run_count = '1')
        program_storage = Storage(camera_dir, '')
        for w in program:
            # Go to location
            print(w)
            status = self.goTo(w['x'], w['y'])
            # add path to waypoint
            w['path'] = program_storage.get_sensor_path()
            # convert waypoint info to json string
            wp_json = json.dumps(w)
            if 'action' in w:
                if w['action'] == 3:
                    t1 = Thread(target = self.sensorAction, args=(1, wp_json))
                    t2 = Thread(target = self.sensorAction, args=(2, wp_json))
                    t1.daemon = True
                    t2.daemon = True
                    t1.start()
                    t2.start()
                    t1.join()
                    t2.join()
                else:
                    # camera_service1
                    status = self.sensorAction(w['action'], wp_json)
        
        # TODO: add error handling
        return 'ok'
