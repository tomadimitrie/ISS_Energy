import sys, os
from PIL import Image
from sense_hat import SenseHat
import picamera
import time
import datetime as dt
import ephem

name = "ISS(ZARYA)"
line1 = "1 25544U 98067A   18336.32716814  .00001474  00000-0  29615-4 0  9996"
line2 = "2 25544  51.6401 260.8120 0005200 105.4624 347.8845 15.54045418144664"
iss = ephem.readtle(name, line1, line2)
X = [0, 0, 255]
o = [255, 255, 255]
b = [0, 0, 0]
bl = [0, 255, 0]
question_mark = [
    o, o, o, X, X, o, o, o,
    o, o, X, o, o, X, o, o,
    o, o, o, o, o, X, o, o,
    o, o, o, o, X, o, o, o,
    o, o, o, X, o, o, o, o,
    o, o, o, X, o, o, o, o,
    o, o, o, o, o, o, o, o,
    o, o, o, X, o, o, o, o
    ]
exclamation_mark = [
    b, b, b, bl, bl, b, b, b,
    b, b, b, bl, bl, b, b, b,
    b, b, b, bl, bl, b, b, b,
    b, b, b, bl, bl, b, b, b,
    b, b, b, bl, bl, b, b, b,
    b, b, b, bl, bl, b, b, b,
    b, b, b, b,  b, b, b, b,
    b, b, b, bl, bl, b, b, b 
    ]
cam = picamera.PiCamera()
sense = SenseHat()
sense.set_pixels(question_mark)
cam.start_preview()

time.sleep(5)
cam.capture('toConvert.bmp')
cam.stop_preview()
iss.compute()
sense.clear()


basewidth = 8
img = Image.open('toConvert.bmp')
pix = img.load()
width, height = img.size
f = open('raport2.csv', 'a')
f.write("x, y, r, g, b, lat, long\n")

for i in range(0, width):
    for j in range(0, height):
        r, g, b = pix[i, j]
        f.write(str(i) + ", " + str(j) + ", " + str(r) + ", " + str(g) + ", " + str(b) + ", " + str(iss.sublat) + ", " + str(iss.sublong) + "\n")
f.close()
hsize = 8
sense.set_pixels(exclamation_mark)
time.sleep(5)
sense.clear()
img = img.resize((basewidth, hsize), Image.ANTIALIAS)
img.save('converted.bmp')


sense.load_image('converted.bmp')
sense.flip_v()
time.sleep(5)
sense.clear()

