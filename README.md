# raspberry-pi-timelapse
Notes and scripts for making timelapse sequences using my old Raspberry Pi 2 B.

# Raspberry Pi

I'm using a regular RaspiCam on an old RPi 2 B. The script `rpi/raspiCam_interval_timer.py` can be used to take pictures at regular intervals, as specified with the `-i` argument. Image are saved in the folder specified with the `-t` argument, and the program stops after `-n` images have been taken.

I usually ssh into the RPi, and then start a 5-hour picture taking session (1200 pictures, every 15 seconds):

```bash
nohup python /home/pi/bin/raspiCam_interval_timer_v2.py -i 15 -n 1200 -t /home/pi/timelapse/ &
```

Once my timelapse is done (usually well before 5 hours) I kill the process manually.

File names follows the convention "YYYY-MM-DD_hhmmss.jpg", e.g. `image_2021-11-19_170038.jpg`. This allows the subsequent script to load the images in the correct order, and to determine timing information for the timestamp overlay.



## Rsync to local computer

I regularly rsync the images currently on the RPi (usually in the `~/timelaps` folder) using rsync, e.g.:

```bash
IP_ADDRESS=my-local-pi-address
rsync -ahv pi@$IP_ADDRESS:timelapse ~/my_local/project_folder
```



# Combine images into video

Once all images are on my local computer, I use a Python script (`make_movie_cv2.py`) to combine the individual frames into a video clip. This uses the OpenCV library.

If wanted,  subsequent images can be blended together, which adds additional video frames. The `--blend`, or `-b` argument determines how many intermediate images will be produced between two original image frames.

A timestamp is shown when the `--ts` argument is present. The exact format and location of this text overlay can only be changed in the code at this point (in the "format_timestamp" function). Using the `--test` argument is useful while trying to find the right placement for the overlay. In test mode, no output file is saved. 

An example of a timestamp overlay is shown here:

![screenshot_overlay](images/screenshot_overlay.jpg)



## Help output for the movie making script

```bash
python make_movie_cv2.py -h
usage: make_movie_cv2.py [-h] [-o OUTPUT] [-v] [-t] [-b BLEND] [--fps FPS]
                         [--timestamp_format TIMESTAMP_FORMAT] [--ts]
                         imgpath
 
positional arguments:
  imgpath               Path to the image files
 
optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file name (Default: output.mp4)
  -v, --view            View output
  -t, --test            Test run only. Do not create video.
  -b BLEND, --blend BLEND
                        Create (1 to 5) intermediate images between frames.
                        Default: 0 (off)
  --fps FPS             Frames per second (fps) for movie
  --timestamp_format TIMESTAMP_FORMAT
                        Time stamp format; default: "Y-m-d_HM"
  --ts                  Show timestamp
```

