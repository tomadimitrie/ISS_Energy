import picamera
import time
import datetime as dt
from PIL import Image
import math
CONST_LOW_APPROXIMATION = 0.8
CONST_UPPER_APPROXIMATION = 1.2
cam = picamera.PiCamera()

def aprox(x, y, z):
    if(x == 0 or y == 0 or z == 0):
        return False
    if((CONST_LOW_APPROXIMATION < x / y) and (x / y < CONST_UPPER_APPROXIMATION) and  (CONST_LOW_APPROXIMATION < x / z) and (x / z< CONST_UPPER_APPROXIMATION) and (CONST_LOW_APPROXIMATION<y/z) and (y / z < CONST_UPPER_APPROXIMATION)):
       return True
    return False

def take_photo(cam):
    cam.start_preview()
    time.sleep(5)
    cam.capture("cloudss.png")
    cam.stop_preview()

def calculate_percentage(im, number_of_white_pixels):
    width, height = im.size
    for x in range(width):
        for y in range(height):
            rgb = im.getpixel((x,y))
            if(aprox(rgb[0], rgb[1], rgb[2])):
               number_of_white_pixels = number_of_white_pixels + 1
    percentage = number_of_white_pixels / (width * height)
    return percentage

def main():
    number_of_white_pixels = 0
    take_photo(cam)
    im = Image.open("cloudss.png")
    perc = calculate_percentage(im, number_of_white_pixels)
    print(perc)
    
if __name__ == "__main__":
    main()


