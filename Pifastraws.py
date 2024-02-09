#!/usr/bin/env python3
import time
import os, subprocess
import signal
import datetime
import glob
import sys
from gpiozero import Button
import cv2
import numpy as np
import shutil

#v0.02

# setup
framerate  = 200   # fps
pre_frames = 100   # Minimum Number of PRE Frames
v_length   = 10000 # in mS
ram_limit  = 150   # in MB, stops if RAM below this
width      = 640   # frame width 
height     = 480   # frame height


# specify trigger button
trigger    = Button(21)

# setup directories
Home_Files  = []
Home_Files.append(os.getlogin())
pic_dir = "/home/" + Home_Files[0]+ "/Pictures/"

# clear ram
print("Clearing RAM...")
pics = glob.glob('/run/shm/*.raw')
for tt in range(0,len(pics)):
    os.remove(pics[tt])
pics = glob.glob('/run/shm/*.jpg')
for tt in range(0,len(pics)):
    os.remove(pics[tt])
   
# start camera with subprocess
print("Starting Camera...")
command = "rpicam-raw -n -t 0 --segment 1 --framerate " + str(framerate) + " -o /run/shm/temp_%06d.raw --width " + str(width) + " --height " + str(height)
s = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
poll = s.poll()
while poll != None:
    print("waiting...")
    poll = s.poll()

print("Capturing Pre-Frames...")
while len(pics) < pre_frames:
    pics = glob.glob('/run/shm/temp*.raw')
print("Pre-Frames captured...")
print("Trigger when ready...")

run = 0

# check ram
st = os.statvfs("/run/shm/")
freeram = (st.f_bavail * st.f_frsize)/1100000

# main loop
while run == 0 and freeram > ram_limit:
   
    # check ram and stop if full
    st = os.statvfs("/run/shm/")
    freeram = (st.f_bavail * st.f_frsize)/1100000
    if freeram < ram_limit:
        run = 1
        
    # read temp files
    pics = glob.glob('/run/shm/temp*.raw')
    # DELETE OLD FRAMES
    for tt in range(pre_frames,len(pics)-1):
        os.remove(pics[tt])
   
    # trigger from button
    if trigger.is_pressed:
        now = datetime.datetime.now()
        timestamp = now.strftime("%y%m%d_%H%M%S_%f")
        w = len(pics)
        print("Triggered...", timestamp)
       
        # capture for v_length
        start = time.monotonic()
        st = os.statvfs("/run/shm/")
        freeram = (st.f_bavail * st.f_frsize)/1100000
        while time.monotonic() - start < v_length/1000 and freeram > ram_limit:
            st = os.statvfs("/run/shm/")
            freeram = (st.f_bavail * st.f_frsize)/1100000
        
        # stop camera subprocess
        os.killpg(s.pid, signal.SIGTERM)
        
        # rename frames 
        yr = timestamp[0:2]
        mh = timestamp[2:4]
        dy = timestamp[4:6]
        hr = int(timestamp[7:9])
        mn = int(timestamp[9:11])
        sc = int(timestamp[11:13])
        ms = int(timestamp[14:21])
        fx = 1
        pics = glob.glob('/run/shm/temp*.raw')
        pics.reverse()
        
        # calculate times for file name
        for x in range(0,len(pics)):
            mc = ms + ((x - w) * int(1000000/framerate))
            sc2 = sc
            mn2 = mn
            hr2 = hr
            while mc > 999999:
                sc2 += 1
                mc -= 1000000
                if sc2 > 59:
                    sc2 = 0
                    mn2 += 1
                    if mn2 > 59:
                        hr2 += 1
                        mn2 = 0
                        if hr2 > 23:
                            hr2 = 0
            while mc < 0:
                sc2 -= 1
                mc += 1000000
                if sc2 < 0:
                    sc2 = 59
                    mn2 -= 1
                    if mn2 < 0:
                        hr2 -= 1
                        mn2 = 59
                        if hr2 < 0:
                           hr2 = 23
            md = "00000" + str(mc)
            mo = str(mn2)
            if len(mo) < 2:
                mo = "0" + mo
            sd = str(sc2)
            if len(sd) < 2:
                sd = "0" + sd
            hs = str(hr2)
            if len(hs) < 2:
                hs = "0" + hs
            timestamp = hs+mo+sd+"_"+str(md)[-6:]
            if x == w:
                trig = timestamp
            # rename file
            if os.path.exists(pics[x]):
                os.rename(pics[x],pics[x][0:9] + timestamp + '.raw')
                fx +=1
       
        # show trigger frame
        fd = open('/run/shm/' + trig + '.raw', 'rb')
        f = np.fromfile (fd,dtype=np.uint8,count=-1)
        f = f.reshape(int(f.size/5),5)
        f  = np.delete(f, 4, 1)
        im = f.reshape((height,width))
        fd.close()
        cv2.imshow(trig + '.raw',im)
        
        # wait for a key press
        print( "Press ESC to exit, Any other key to restart")
        k = cv2.waitKey(0)
        if k == 27:    # Esc key to stop
            print("Exit")
            os.killpg(s.pid, signal.SIGTERM)
            cv2.destroyAllWindows()
            sys.exit()
        
        # clear ram of temp files
        print("Clearing temp files from RAM...")
        pics = glob.glob('/run/shm/temp*.raw')
        for tt in range(0,len(pics)):
            os.remove(pics[tt])

        # move RAM Files to SD card
        vpics = glob.glob('/run/shm/*.raw')
        for xx in range(0,len(vpics)):
             if not os.path.exists(pic_dir + vpics[xx][9:]):
                 shutil.move(vpics[xx],pic_dir)
        
        # restart camera with subprocess
        print("Starting Camera...")
        command = "rpicam-raw -n -t 0 --segment 1 --framerate " + str(framerate) + " -o /run/shm/temp_%06d.raw --width " + str(width) + " --height " + str(height)
        s = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
        poll = s.poll()
        while poll != None:
            print("waiting...")
            poll = s.poll()
        print("Capturing Pre-Frames...")
        while len(pics) < pre_frames:
            pics = glob.glob('/run/shm/temp*.raw')
        print("Pre-Frames captured...")
        print("Trigger when ready...")
            
# stop camera subprocess if running
poll = s.poll()
if poll == None:
    os.killpg(s.pid, signal.SIGTERM)
        
    
