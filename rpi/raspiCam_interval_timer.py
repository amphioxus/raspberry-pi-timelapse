#!/usr/bin/env python

"""
Take a picture with the RaspiCam every -i seconds, -n times

Written for Raspberry Pi 2 Model B
PRETTY_NAME="Raspbian GNU/Linux 7 (wheezy)"
NAME="Raspbian GNU/Linux"
VERSION_ID="7"
VERSION="7 (wheezy)"


Resolutions tested:
1024x768
1920x1080
2592x1944

Start it like this for taking 1200 pictures, one every 15 seconds:

nohup python /home/pi/bin/raspiCam_interval_timer_v2.py -i 15 -n 1200 -t /home/pi/timelapse/ &

Pictures will be saved in the `timelapse` folder.

Armin Hinterwirth
"""

import argparse, sys, os
from threading import Thread
import time
from datetime import datetime
import picamera

ISO = 400
FRAMERATE = 15


def take_image(camera, targetpath):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        filename = 'image_{}.jpg'.format( timestamp )
        filename = os.path.join( targetpath, filename )
        camera.capture(filename)
        print('Done. Image file saved as {}'.format(filename))


def set_cam_gains(camera):
    print('Calculating initial gain values')
    # Wait for the automatic gain control to settle
    time.sleep(2)
    camera.capture('testimage.jpg')
    # Now get the values for later use:
    shutterspeed = camera.exposure_speed
    awb_gains = camera.awb_gains
    # analog_gain = camera.analog_gain
    return (shutterspeed, awb_gains)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Interval snapshooter')
    parser.add_argument('-r', '--resolution', default='1920x1080', help='Resolution in widthxheight pixel. E.g. 1024x768, 1920x1080, 2592x1944 (maximum)')
    parser.add_argument('-i', '--interval', default=0, type=int,help="Interval. I.e. delay before taking another snapshot; in seconds. If zero, only take one picture. Minimum delay: 10 seconds.")
    parser.add_argument('-n', '--n_images', default=10, type=int,help="If delay is not zero, how many pictures to take before quitting.")
    parser.add_argument('-t', '--outputpath', default=os.getcwd(), help='Target path for images.')
    # get the arguments:
    args = parser.parse_args()
    interval = args.interval
    res = args.resolution
    res = res.split('x',1)
    try:
        resolution = (int( res[0] ), int( res[1]) )
        print('Resolution: {}'.format( args.resolution ))
    except:
        print('Error setting resolution.')
        sys.exit(1)
    targetpath = args.outputpath
    print('Output folder: {}'.format( targetpath ))
    
    # Fix camera gain settings by taking test image:
    with picamera.PiCamera() as camera:
        camera.resolution = resolution
        camera.rotation = 180
        camera.exposure_mode = 'night'
        camera.framerate = FRAMERATE
        camera.iso = ISO
        
        cs = set_cam_gains(camera)
        print('Settings gathered:')
        print(cs[0])
        print(cs[1])
        camera.shutter_speed = cs[0]
        camera.exposure_mode = 'off'
        camera.awb_mode = 'off'
        camera.awb_gains = cs[1]
        if interval > 0:
            print('Interval: {} seconds'.format(interval))
            n = args.n_images
            print('Taking {} pictures'.format( n ))
            for i in range(n):
                print("Taking image {}/{} ... ".format( i+1, n ))
                # timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
                # filename = 'image_{}.jpg'.format( timestamp )
                # filename = os.path.join( targetpath, filename )
                # camera.capture(filename)
                # print('Done. Image file saved as {}'.format(filename))
                thread = Thread(target = take_image, 
                                args = (camera, targetpath, ))
                thread.start()
                if not i+1 == n:
                    print('Waiting {} seconds'.format( args.interval ))
                    time.sleep( args.interval )
                thread.join()
            print('DONE !!!!')
        else:
            pass