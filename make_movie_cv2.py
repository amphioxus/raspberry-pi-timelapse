#!/usr/bin/env python
    
#  Program to create a timelapse movie from an 
#  image sequence shot by my Raspberry Pi.
#  Depends on OpenCV (cv2)
#  
#  My RasPi usually takes one image 
#  every minute (scheduled with "crontab"), 
#  and saves it as a time-stamped JPG.
#
#  This script loads the JPGs contained in one 
#  directory, and creates an output movie (mp4).
#  It gives you the option of blending images in 
#  variable steps from img_t to img_t+1.
#  
#  Calling this script with the "-h" argument will
#  spit out help
    
import cv2
import numpy as np
import os
import argparse
import time
from datetime import datetime
    
PAUSE_T = 100 # defines pause for live-preview of movie
    
    
def parse_timestamp(ts, dateformat='%Y-%m-%d_%H%M'):
    """
    Parses a timestamp string and returns newly formatted
    strings used in the text overlay in a dictionary.
    """
    # e.g. 2018-02-09_1750
    # Create datetime object with the dateformat specified
    # in the dateformat argument:
    dt = datetime.strptime(ts, dateformat)
    return {'day': dt.strftime('%A'),
            'date': dt.strftime('%m-%d-%Y'),
            'time': dt.strftime('%H:%M')}
    

def overlay_text(txt, img, ll, fscale=1):
    """Use OpenCV to overlay text"""
    font                   = cv2.FONT_HERSHEY_DUPLEX
    bottomLeftCornerOfText = ll
    fontScale              = fscale
    fontColor              = (0,0,0) #(0,140,255) # BGR
    lineType               = 3
    
    cv2.putText(img, txt, 
    bottomLeftCornerOfText, 
    font, 
    fontScale,
    fontColor,
    lineType)
    
    
def format_timestamp(img, info, imgsize):
    """
    Change the text positions here to format time stamp to your liking.
    info is a dictionary containing the info to print here
    """
    overlay_text(info['mincounter'],
    img,
    ll=(40, imgsize[1]-40),
    fscale=3)
    
    overlay_text(info['day'],
    img,
    ll=(40, imgsize[1]-300),
    fscale=3)
    
    overlay_text(info['date'],
    img,
    ll=(50, imgsize[1]-240),
    fscale=1.5)
    
    overlay_text(info['time'], 
    img, 
    ll=(40, imgsize[1]-150),
    fscale=3)
    
    
def main():    
    P = argparse.ArgumentParser()
    P.add_argument('imgpath', nargs=1, 
        help='Path to the image files')
    P.add_argument('-o', '--output', 
    help='Output file name (Default: output.mp4)', 
    default='output.mp4')
    P.add_argument('-v', '--view', 
        help='View output', 
        action='store_true')
    P.add_argument('-t', '--test', 
        help='Test run only. Do not create video.', 
        action='store_true')
    P.add_argument('-b', '--blend', 
            help='Create (1 to 5) intermediate images between frames. Default: 0 (off)',  
            default=0, 
            type=int) 
    P.add_argument('--fps', 
        help='Frames per second (fps) for movie', 
        type=int, 
        default=12)
    P.add_argument('--timestamp_format', 
        help='Time stamp format; default: "Y-m-d_HM"',
        default='%Y-%m-%d_%H%M')
    P.add_argument('--ts', help='Show timestamp', action='store_true')
    ARGS = P.parse_args()
    
    imgpath = ARGS.imgpath[0]
    imgs = [i for i in os.listdir(imgpath) if i.endswith('.jpg')]
    imgs_sorted = imgs.sort()
    video_out = ARGS.output
    if not video_out.endswith('.mp4'):
        video_out += '.mp4'
    frame = cv2.imread(os.path.join(imgpath,imgs[0]))
    height, width, channels = frame.shape
    if ARGS.test:
        print('Testing only. No actual video file will be written.')
    if ARGS.blend:
        print('Blending ON. Creating {} intermediate images between each frame pair'.format(ARGS.blend))
    print('Information:')
    max_imgs = len(imgs)
    print('{} images found in target folder'.format(max_imgs))
    print('First image height: {}, width: {}'.format(height, width))
    print('All subsequent images have to have the same dimensions!')
    size = (width, height)
    if not ARGS.test:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        videowriter = cv2.VideoWriter()
        try:
            videowriter.open(video_out, fourcc, ARGS.fps, size)
            print('Opened video writer')
        except:
            print('Failed to open video writer')
    
    # go through all the images in the folder:
    for n,i in enumerate(imgs):
        print('Current image: {}'.format(i))
        curr_img = cv2.imread(os.path.join(imgpath,i))
        ds = os.path.splitext(i)[0]
        info = parse_timestamp(ds, dateformat=ARGS.timestamp_format)
        info['mincounter'] = '{:>3d} {:<s}'.format(n+1, 'min.')
        if ARGS.ts:
            format_timestamp(curr_img, info, (width, height))
    
        if ARGS.view:
            img_resized = cv2.resize(curr_img, 
                                    None, 
                                    fx = 0.5, 
                                    fy = 0.5, 
                                    interpolation = cv2.INTER_CUBIC)
            cv2.imshow('image', img_resized)
            cv2.waitKey(PAUSE_T)
        if not ARGS.test:
            videowriter.write(curr_img)
        # if no blending, we are done for this loop, otherwise:    
        if ARGS.blend and n < max_imgs-1:
            # create intermediate images
            print('Creating {} intermediate blends to image {}:'.format(ARGS.blend,
            imgs[n+1]))
            # image one is current one, also read next one:
            next_img = cv2.imread(os.path.join(imgpath, imgs[n+1]))
            # blending steps:
            delta_alpha = (float)(1/(ARGS.blend+1))
            alpha = 0.0 # init.                     
            for counter in range(0, ARGS.blend):
                alpha = alpha + delta_alpha     
                print('\tBlend alpha: {}'.format(alpha))
                blendimg = np.zeros((height, width, 3), np.uint8)
                cv2.addWeighted(curr_img, (1-alpha), next_img, alpha, 0, blendimg)
    
                if ARGS.ts:
                    format_timestamp(blendimg, info, (width, height))      
    
                if ARGS.view:
                    img_resized = cv2.resize(blendimg, 
                                            None, 
                                            fx = 0.5, 
                                            fy = 0.5, 
                                            interpolation = cv2.INTER_CUBIC)
                    cv2.imshow('image', img_resized)
                    cv2.waitKey(PAUSE_T)
                # write blended image to file:
                if not ARGS.test:
                    videowriter.write(blendimg)
    
    if not ARGS.test:    
        videowriter.release()  
    cv2.destroyAllWindows()     
    print('Done.')
    
    
if __name__ == "__main__":
    main()