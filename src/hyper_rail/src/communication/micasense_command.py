
"""
code taken from https://micasense.github.io/rededge-api/
Need to edit specific image names below, but should work if we want to delete everything on SD"""
#Edit the following two variables to match your camera's ethernet IP for "host"
#and the path to your external storage device for "path"
#Please note the formatting, keep the "/" on the end
HOST = "http://192.168.1.83/"

import requests
import time
import logging, traceback
from datetime import datetime
import os
import json
import re
# from natsort import natsorted

TEST_WP_INFO = {"x": 8, "y": 9, "action": 3, "wp_id": 3, "path": "/program_data/firstprogram/1/"}
TEST_FILE_RESPONSE =  {
        "status" : "complete",
        "id" : "i89jfi73irj49f74",
        "time" : "2014-10-08T20:27:16.321Z",
        "jpeg_cache_path" : {
            "1" : "/images/i89jfi73irj49f74_1.jpg",
            "2" : "/images/i89jfi73irj49f74_2.jpg",
            "5" : "/images/i89jfi73irj49f74_5.jpg"
        },
        "raw_cache_path" : {
            "1" : "/images/i89jfi73irj49f74_1.tif",
            "2" : "/images/i89jfi73irj49f74_2.tif",
            "5" : "/images/i89jfi73irj49f74_5.tif"
        },
        "jpeg_storage_path" : {
            "1" : "/files/0021SET/000/IMG_0000_1.jpg",
            "2" : "/files/0021SET/000/IMG_0000_2.jpg",
            "3" : "/files/0021SET/000/IMG_0000_3.jpg",
            "4" : "/files/0021SET/000/IMG_0000_4.jpg"
        },
        "raw_storage_path" : {
            "1" : "/files/0021SET/000/IMG_0000_1.tif",
            "2" : "/files/0021SET/000/IMG_0000_2.tif",
            "3" : "/files/0021SET/000/IMG_0000_3.tif",
            "4" : "/files/0021SET/000/IMG_0000_4.tif"
        }
    }

def store_SD_photos(wp_info = TEST_WP_INFO):
    # storage_path_files = get_capture(id)
    # replace this with get_capture(id)
    storage_path_files = TEST_FILE_RESPONSE
    # get the directory path for run from param
    rededge_file_transfer(storage_path_files, wp_info)


def rededge_file_transfer(r, wp_info):
    # grab everything in capture path 
    add_images(r['raw_storage_path'], wp_info)


def add_images(image_paths, path):
    print(image_paths)
    print(path)
    # iterates through dictionary and write to running program path directories
    count = 1
    for key in image_paths:
        image_name_path = image_paths[str(count)].split('/')
        print(image_paths[str(count)])
        try:
            r = requests.get(HOST + image_paths[str(count)], stream=True,  timeout=(1, 3)) # this makes a request to get data from SD
            print(HOST + image_paths[str(count)])
            # get image name
            with open(path + image_name_path[4], 'wb') as f:
                for chunk in r.iter_content(10240):
                    f.write(chunk)
        
            # TODO: post the image to the sql-Lite database
            # requests.post()

            r = requests.get(HOST + "deletefile/%s" %image_paths[str(count)], timeout=(1, 3) )
            count = count + 1        
        except requests.exceptions.RequestException as e:
            print("Error: " + str(e))

def get_capture(id):
    # get the /capture/:id
    url = HOST + '/capture/' + id
    try:
        r = requests.get(url, timeout=1)
        # // return a json object
        r = json.dumps(r)
        return r
    except requests.exceptions.RequestException:
        print('Waiting for camera response')

def get_logs(files, folder_index, path):
    print('Grabbing diag & paramlog')
    for n in range(0,2):
        r = requests.get(HOST + "files/%s/%s" % (folder_index, files.json()['files'][n]['name']), stream=True)
        print(files.json()['files'][n]['name'])
        with open(path + "%s/%s" % (folder_index, files.json()['files'][n]['name']), 'wb') as f:
            for chunk in r.iter_content(10240):
                f.write(chunk)
        r = requests.get(HOST + "deletefile/%s/%s" % (folder_index, files.json()['files'][n]['name'])) 

def new_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)
