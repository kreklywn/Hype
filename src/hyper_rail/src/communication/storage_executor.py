#!/usr/bin/env python3

# This is a storage class that is used to store and get paths for camera and sensor

import rospy
import time
import os
from threading import Thread
from queue import Queue
from hyper_rail.srv import PathService, PathServiceRequest, MotionService, SensorService
from pathlib import Path 
# remember to change this directory
PATH = "/home/peter/"

# def add_new_dirs(data_dir, program_name, run_count):
#         full_path =  PATH + data_dir + '/' + program_name + '/' + run_count + '/'
#         if not os.path.exists(full_path):
#             print(full_path)
#             os.makedirs(full_path)
#         return full_path
        
class Storage:
    def __init__(self, camera_dir = '', sensor_dir = ''):
        self.camera_dir = camera_dir
        self.sensor_dir = sensor_dir

    
    def add_new_dirs(self):
        full_path =  PATH + self.camera_dir
        if not os.path.exists(full_path):
            print(full_path)
            os.makedirs(full_path)
        return full_path
    
    def get_sensor_path(self):      # TODO- find a new name or find a way to add sensor_dir
        return self.camera_dir
