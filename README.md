# Pifastraws

written for Pi4 and pi v2 or v3 camera.

Captures raw frames to ram (later copied to sd card under /Pictures/date). 

When started puts frames in a buffer until triggered, by a button on gpio21 to gnd, and then captures raws for a set time. 

Buffered raws and captured raws then renamed to time of capture eg 123456_076578 means 12:34:56.076578.

Debayers trigger image for showing

v2 camera: 640x480 upto 200fps or 1920x1080 upto 47fps

v3 camera: 1536x864 upto 120fps

To EXIT press ESC when image appears, other key to capture again

you need to install opencv with sudo apt install python3-opencv

