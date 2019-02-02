import picamera

import os
import time
import datetime 
import math

import reverse_geocoder
import ephem
from ephem import readtle, degree

import logging
import logzero
from logzero import logger

from PIL import Image
from sense_hat import SenseHat

# Extract current directory path.
dir_path = os.path.dirname(os.path.realpath(__file__))

# Latest TLE data for ISS location
name = "ISS(ZARYA)"
line1 = "1 25544U 98067A   18336.32716814  .00001474  00000-0  29615-4 0  9996"
line2 = "2 25544  51.6401 260.8120 0005200 105.4624 347.8845 15.54045418144664"
iss = ephem.readtle(name, line1, line2)

# Define some colors:
#yellow
y = [50, 50, 0]
#blue
b = [0, 0, 50]
#black
n = [0, 0, 0]

#Define some images for the sense hat:
day_image = [
    b, b, b, b, b, b, b, b,
    b, b, b, y, y, b, b, b,
    b, b, y, y, y, y, b, b,
    b, y, y, y, y, y, y, b,
    b, y, y, y, y, y, y, b,
    b, b, y, y, y, y, b, b,
    b, b, b, y, y, b, b, b,
    b, b, b, b, b, b, b, b,
    ]
night_image = [
    n, n, n, n, n, n, n, n,
    n, n, n, y, y, n, n, n,
    n, n, y, n, n, y, n, n,
    n, y, n, n, n, n, y, n,
    n, y, n, n, n, n, y, n,
    n, n, y, n, n, y, n, n,
    n, n, n, y, y, n, n, n,
    n, n, n, n, n, n, n, n,
    ]
    
    
# The minimal value of the GRAYSCALE value for a Pixel to be considered to have a light color
MIN_GRAYSCALE_STEP = 110
# The maximum difference between the RGB values of a Pixel for it to not be to "colorful"
MAX_RGB_DIFFERENCE = 10
# Focal ratio of the camera module V1
F_STOP = 2.9
# Approximative value of power of a lumen given by a light source
LUMENS_TO_WATT = 0.01
# The best ISO value for low light photography (best guess at which auto mode aims at) used for calculating the light value
ISO_LOW_LIGHT = 800

# Checks if a Pixel's color is 'close' to white, by checking the minimum grayscale value 
# and the maximum difference between them.
def is_close_to_white(pixel):
    min_value = min(pixel[0], pixel[1], pixel[2])
    max_value = max(pixel[0], pixel[1], pixel[2])

    return grayscale_value(pixel)             > MIN_GRAYSCALE_STEP and \
           max_value - min_value < MAX_RGB_DIFFERENCE

#returns the grayscale value of a given pixel, calculated using its RGB values
def grayscale_value(pixel):
    
    return 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]

# Takes a photo and saves it at the specified path.
def take_photo(cam, relative_path):
    
    cam.capture(str(dir_path) + "/" + str(relative_path));
    
# Calculates the percentage of close to white pixels from an image.
# The percentage is used to aproximate the amount of clouds that can be seen across the image.
def get_cloud_percentage(image):
    white_pixels = 0

    for x in range(image.width):
        for y in range(image.height):
            if (is_close_to_white(image.getpixel((x, y)))):
                white_pixels += 1

    return white_pixels / (image.width * image.height)

# CalculateS a further needed constant for the calculation of the exposure value
def get_b(cam):
    # the exposure speed is returned in microseconds, but we need it in second.
    #That is why we "divide" its value by 1000000
    b = F_STOP * F_STOP * 1000000/ (cam.exposure_speed)

    return b

# Calculate the exposure value of the camera.
def get_ev(cam):
    b = get_b(cam)

    return math.log2(b)

#calculate the LV of the photo, which is the exposure value relative to ISO/100
def get_lightvalue(cam):
    ev = get_ev(cam)
    
    return (ev + math.log2(ISO_LOW_LIGHT/100))

# Calculate the total lux of the earth area if all pixels of its specific image were white.
def get_totalux(cam):
    lv = get_lightvalue(cam)

    # This is a formula for the lux value of a light source, given its light value (relative exposure value)
    return math.pow(2, lv) * 2.5

# Calculate the light power consumed in a region according to an image and the camera.
def get_light_power(image, cam):
    power = 0

    for x in range(image.width):
        for y in range(image.height):

            pixel = image.getpixel((x,y))
            luminance = grayscale_value(pixel)
            
            # TODO : Explain
            lum = get_totalux(cam) * luminance / 255 * 4 * math.pi * 400000 * 400000

            power = power + lum

    # returns the power of the light source photographed in megawatts, relative to the number of pixels
    #The formula is for a very small light source, hence the relativity to the number of pixels is required
    return power/(image.width * image.height * 1000000 * LUMENS_TO_WATT)

def setup_cam(cam):
    cam.resolution = (640, 480)

# The angle at which the sun is visible, from "behind" Earth, resulted from atmospherical refraction of light
TWILIGHT_ANGLE = math.radians(-6)

# Returns time period (Day / Night), using ISS data.
def get_time_period(iss):
    observer = ephem.Observer()

    observer.lat = iss.sublat
    observer.long = iss.sublong
    
    observer.elevation = 0
    sun = ephem.Sun()
    sun.compute(observer)
    sun_angle = math.degrees(sun.alt)

    return "DAY" if sun_angle > TWILIGHT_ANGLE else "NIGHT"

def main():
    # Create a datetime variable to store the start time
    start_time = datetime.datetime.now()
    # Create a datetime variable to store the current time
    now_time = datetime.datetime.now()

    # Setup camera
    cam = picamera.PiCamera()
    setup_cam(cam)

    # Set log file.
    logzero.logfile(dir_path + "/data.csv")

    # Set custom formatter.
    formatter = logging.Formatter('%(name)s - %(asctime)-15s - %(levelname)s: %(message)s')
    logzero.formatter(formatter)

    # How many minutes to run the loop for.
    LOOP_TIME = 1
    photo_counter = 0
    sh = SenseHat()
    
    # Run the code for less than 
    while (now_time < start_time + datetime.timedelta(minutes = LOOP_TIME)):
        photo_counter+=1

        # Compute the current location of the ISS.
        iss.compute()
                
        # Get the country below ISS at the moment.
        pos = (iss.sublat / degree, iss.sublong / degree)
        location = reverse_geocoder.search(pos)

        time_period = get_time_period(iss);

        # Calculate the percentage of clouds in an image during daylight.
        if (time_period == "DAY"):
            cam.exposure_mode = 'auto'

            try:
                light_power = 0
                sh.set_pixels(day_image)
                
                photo_path = str("photo_") + str(photo_counter) + str(".jpg")
                
                take_photo(cam, photo_path)
                
                image = Image.open(photo_path)
                    
                cloud_percentage = get_cloud_percentage(image)
                logger.info("%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s", "photo no:", str(photo_counter), ", time:" , str(datetime.datetime.now().time()), ", day or night:" , str(time_period),
                                                  ", latitude:", str(iss.sublat), ", longitude:", str(iss.sublong), ", location:", str(location), ", cloud percentage(day):" , str(cloud_percentage), ", light power(night): ", str(light_power))
                 
            except Exception as exception:
                logger.error("An error occured: " + str(exception))
                
        # Calculate the total light power of a terrestrial area photographed during night.
        else:
            cam.exposure_mode = 'night'
            
            try:
                cloud_percentage = 0
                light_power = 0
                sh.set_pixels(day_image)
                
                photo_path = str("photo_") + str(photo_counter) + str(".jpg")
                
                take_photo(cam, photo_path)

                image = Image.open(photo_path)
                        
                light_power = get_light_power(image, cam)

                logger.info("%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s", "photo no:", str(photo_counter), ", time:" , str(datetime.datetime.now().time()), ", day or night:" , str(time_period),
                                                  ", latitude:", str(iss.sublat), ", longitude:", str(iss.sublong), ", location:", str(location), ", cloud percentage(day):" , str(cloud_percentage), ", light power(night): ", str(light_power))
                    
            except Exception as exception:
                logger.error("An error occured: " + str(exception))

        time.sleep(2)
    
        now_time = datetime.datetime.now()
            
    
if __name__ == "__main__":
    main()
