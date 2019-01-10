import picamera
import time
import datetime as dt
from PIL import Image
import math


cam = picamera.PiCamera()

cam.ISO = 800
cam.shutter_speed = 1
# cam.color_effects = (128, 128)

#capture the photo and save it
cam.start_preview()
time.sleep(5)
cam.capture("pic.png")
cam.stop_preview()

# 2 is the aperture of camera, and b a constant for further calculus
b = 2*2 / (cam.shutter_speed)

#calculate exposure value of the image, an attribute of independent pixels as well
ev = math.log2(b)

#calculate the light value of the image 
lv = ev + math.log2(cam.ISO/100)

#calculate the maximum lux value of the image if all pixels were total white 
totalux = 16 # looking for a formula rather than a converting table
#power is the total light power consumed by the captured area of Earth and is the sum of the powers of all pixels of that image
power = 0


im = Image.open("pic.png")

width, height = im.size

#calculate the light power of each pixel
for x in range(width):
    for y in range(height):
        rgb = im.getpixel((x,y))
        lumin = 0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2]
        #lux = rgb[0] * 16 / 255
        lum = lumin * 4 * math.pi * 0.75
        power = power + (lum / 100)

print (power)
        


