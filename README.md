# Pifastraws

written for Pi4 and pi v2 camera.

Captures raw files to ram (later copied to sd card). When started puts images in a buffer until triggered, by a button on gpio21 to gnd, and then captures raws for a set time. 

Buffered raws and captured raws them renamed to time of capture eg 123456_076578 means 12:34:56.076578.

Debayers trigger image for showing

640x480 upto 200fps or 1920x1080 upto 47fps

