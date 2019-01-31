import picamera
import time
import datetime
from PIL import Image
import math
import logging
from logzero import logger
import datetime
import os
import ephem
import reverse_geocoder as rg
from ephem import readtle, degree

# Extract current directory path.
dir_path = os.path.dirname(os.path.realpath(__file__))

# Latest TLE data for ISS location
name = "ISS(ZARYA)"
line1 = "1 25544U 98067A   18336.32716814  .00001474  00000-0  29615-4 0  9996"
line2 = "2 25544  51.6401 260.8120 0005200 105.4624 347.8845 15.54045418144664"
iss = ephem.readtle(name, line1, line2)

# The minimal value of the RGB color values for a Pixel to be considered 'close' to white.
MIN_WHITE_STEP = 225
# The maximum difference between the RGB values of a Pixel for it to not be 
MAX_RGB_DIFFERENCE = 10

# Checks if a Pixel's color is 'close' to white, by checking the minimum color value 
# and the maximum difference between them.
def is_close_to_white(pixel):
    min_value = min(pixel.red, pixel.green, pixel.blue)
    max_value = max(pixel.red, pixel.green, pixel.blue)

    return min_value             > MIN_WHITE_STEP and \
           max_value - min_value > MAX_RGB_DIFFERENCE

# Takes a photo and saves it at the specified path.
def take_photo(cam, relative_path):
    cam.capture(relative_path);
    
# Calculates the percentage of close to white pixels from an image.
# The percentage is used to aproximate the amount of clouds that can be seen across the image.
def get_cloud_percentage(image):
    white_pixels = 0

    for x in range(image.width):
        for y in range(image.height):
            if (is_close_to_white(image.getpixel(x, y))):
                white_pixels += 1

    return white_pixels / (image.width * image.height)

# Calculate a further needed constant (TODO ???)
def get_b(cam):
    # TODO: What are 2.9 and 10000000?
    b = 2.9 * 2.9 * 1000000/ (cam.exposure_speed)

    return b

# Calculate the exposure value of the camera.
def get_ev(cam):
    b = get_b(cam)

    return math.log2(b)

# Calculate the total lux of the earth area if all pixels of its specific image were white.
def get_totalux(cam):
    ev = calculate_ev(cam)

    # TODO : What is 2.5 ?
    return math.pow(2, ev) * 2.5

# Calculate the light power consumed in a region according to an image and the camera.
def get_light_power(image, cam):
    power = 0

    for x in range(image.width):
        for y in range(image.height):

            pixel = image.getpixel((x,y))
            luminance = 0.299 * pixel.red + 0.587 * pixel.green + 0.114 * pixel.blue;
            
            # TODO : Explain
            lum = get_totalux(cam) * luminance / 255 * 4 * math.pi * 400000 * 400000

            power = power + lum

    # TODO : Explain
    return power/30720000000000

def setup_cam(cam):
    cam.resolution = (640, 480)

# The angle at which twilight appears. (???)
TWILIGHT_ANGLE = 5

# Returns time period (Day / Night), using ISS data.
def get_time_period(iss):
    observer = ephem.Observer()

    observer.lat = iss.sublat
    observer.long = iss.sublong
    observer.elevation = 0

    sun.compute(observer)
    sun_angle = math_degrees(sun.alt)

    return "DAY" if sun_angle > twilight else "NIGHT"

def main():
    #Create a datetime variable to store the start time
    start_time = datetime.datetime.now()
    #Create a datetime variable to store the current time
    now_time = datetime.datetime.now()

    # Get sun data.
    sun = ephem.Sun()

    # Setup camera
    cam = picamera.PiCamera()
    setup_cam(cam);

    # Set log file.
    logzero.logfile(dir_path + "data.csv")

    # Set custom formatter.
    formatter = logging.Formatter('%(name)s - %(asctime)-15s - %(levelname)s: %(message)s')
    logzero.formatter(formatter)

    csv_file = open('data.csv', 'wb')
    writer = csv.writer(csv_file)

    # Write CSV header.
    writer.writeheader("Number, Time, Latitude, Longitude, Location, Cloud Percentage, Light Power");

    # How many minutes to run the loop for.
    LOOP_TIME = 60

    # Run the code for less than 
    while (now_time < start_time + datetime.timedelta(minutes = LOOP_TIME)):
        photo_count = 0

        # Compute the current location of the ISS.
        iss.compute()
                
        # Get the country below ISS at the moment.
        pos = (iss.sublat / degree, iss.sublong / degree)
        location = rg.search(pos)

        time = get_time_period(iss);

        # Calculate the percentage of clouds in an image during daylight.
        if (time == "DAY"):
            cam.exposure_mode = 'auto'

            try:
                photo_path = "photo_" + str(photo_count) + ".jpg"
                take_photo(cam, photo_path)
                
                image = Image.open(photo_path)
                    
                cloud_percentage = get_cloud_percentage(image)

                logger.info("%s, %s, %s, %s, %s", photo_counter, datetime.datetime.now().time()),
                                                  iss.sublat, iss.sublong, cloud_percentage))
            except Exception as exception:
                logger.error("An error occured: " + str(exception))
                
        # Calculate the total light power of a terrestrial area photographed during night.
        else:
            cam.exposure_mode = 'night'
            
            try:
                photo_path = "photo_" + str(photo_count) + ".jpg"
                take_photo(cam, photo_counter)

                image = Image.open(photo_path)
                        
                light_power = get_light_power(image, camera)

                logger.info("%s, %s, %s, %s, %s", photo_counter, datetime.datetime.now().time()),
                                                  iss.sublat, iss.sublong, light_power))
                    
            except Exception as exception:
                logger.error("An error occured: " + str(exception))

                time.sleep(30)

                now_time = datetime.datetime.now()
                photo_count += 1
    
if __name__ == "__main__":
    main()
