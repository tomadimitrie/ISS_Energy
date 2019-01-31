import picamera
import time
import datetime as dt
from PIL import Image
import math
import logging
from logzero import logger
import datetime
import os
import ephem
import reverse_geocoder as rg
from ephem import readtle, degree

CONST_LOW_APPROXIMATION = 0.8
CONST_UPPER_APPROXIMATION = 1.2
number_of_white_pixels = 0

# Latest TLE data for ISS location
name = "ISS(ZARYA)"
line1 = "1 25544U 98067A   18336.32716814  .00001474  00000-0  29615-4 0  9996"
line2 = "2 25544  51.6401 260.8120 0005200 105.4624 347.8845 15.54045418144664"
iss = ephem.readtle(name, line1, line2)


#verify if a pixel is a shade close to white depending on the RGB properties
def aprox(x, y, z):
    if(x == 0 or y == 0 or z == 0):
        return False
    if((CONST_LOW_APPROXIMATION < x / y) and (x / y < CONST_UPPER_APPROXIMATION) and  (CONST_LOW_APPROXIMATION < x / z) and (x / z< CONST_UPPER_APPROXIMATION) and (CONST_LOW_APPROXIMATION<y/z) and (y / z < CONST_UPPER_APPROXIMATION)):
       return True
    return False

#take a photo and save it
def take_photo(cam, photo_counter):
    
    cam.capture("photo_"+ str(photo_counter)+".jpg")
    
#calculate the percentage of "white" pixels in a captured image (the percentage of clouds in the sky)
def calculate_percentage(im, number_of_white_pixels):
    width, height = im.size
    for x in range(width):
        for y in range(height):
            rgb = im.getpixel((x,y))
            if(aprox(rgb[0], rgb[1], rgb[2])):
               number_of_white_pixels = number_of_white_pixels + 1
    percentage = number_of_white_pixels / (width * height)
    return percentage

#calculate a further needed constant
def calculate_b(cam):
    b = 2.9*2.9 * 1000000/ (cam.exposure_speed)
    return b

#calculate the exposure value of the photo taken
def calculate_ev(b):
    ev = math.log2(b)
    return ev

#calculate the total lux of the earth area if all pixels of its specific image were white
def calculate_totalux(ev):
    totalux = math.pow(2,ev) * 2.5
    return totalux

#calculate the light power consumed in the taken photo
def calculate_light_power(width, height, totalux, im):
    power = 0
    for x in range(width):
        for y in range(height):
            rgb = im.getpixel((x,y))
            lumin = 0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2]
        
            lum = totalux*lumin/255 * 4 * math.pi * 400000 * 400000
            power = power + lum
    return power/30720000000000
    
def main():
    
    #Create a datetime variable to store the start time
    start_time = datetime.datetime.now()

    #Create a datetime variable to store the current time
    now_time = datetime.datetime.now()
    sun = ephem.Sun()
    twilight = math.radians(-6)
    
    #Set up camera
    cam = picamera.PiCamera()
    cam.resolution = (640, 480)
    
    #Set some local parameters to zero
    photo_counter = 0
    number_of_white_pixels = 0
    
    #write the heading of the data csv which we will build from observations and calculus
    f = open('data01.csv', 'a')
    f.write("no, time, lat, long, location, whitePerc, lightPower\n")
    
    #run the code for less than three hours
    while(now_time < start_time + datetime.timedelta(minutes=176)):
                #compute the current location of the ISS with each loop
                iss.compute()
                
                #get the country below ISS at the moment
                pos = (iss.sublat / degree, iss.sublong / degree)
                location = rg.search(pos)
                
                #calculate if it's day time or night time
                observer = ephem.Observer()
                observer.lat = iss.sublat
                observer.long = iss.sublong
                observer.elevation = 0
                sun.compute(observer)
                sun_angle = math.degrees(sun.alt)
                day_or_night = "Day" if sun_angle > twilight else "Night"
                
                #calculate the clouds percentage of a day photograph and save it in the csv file
                if(day_or_night == "Day"):
                    photo_counter = photo_counter + 1
                    power = 0
                    number_of_white_pixels = 0
                    perc = 0
                    cam.exposure_mode = 'auto'
                    try:
                        take_photo(cam, photo_counter)
                        im = Image.open("photo_"+str(photo_counter)+".jpg")
                        perc = calculate_percentage(im, number_of_white_pixels)
                        
                        f.write( str(photo_counter) + ", " + str(datetime.datetime.now().time()) + ", " + str(iss.sublat) + ", " + str(iss.sublong) + ", " + str(location) + ", " + str(perc) + ", "+ str(power) + "\n")
                    
                    except Exception as e:
                        logger.error("An error occured: " + str(e))
                
                #calculate the total light power of a terrestrial area photographed during night
                if(day_or_night == "Night"):
                    photo_counter = photo_counter + 1
                    perc = 0
                    power = 0
                    cam.exposure_mode = 'night'
                    try:
                        take_photo(cam, photo_counter)
                        im = Image.open("photo_"+str(photo_counter)+".jpg")
                        b = calculate_b(cam)
                        ev = calculate_ev(b)
                        totalux = calculate_totalux(ev)
                        width, height = im.size
                        power = calculate_light_power(width, height, totalux, im)
                        
                        f.write(str(photo_counter) + ", " + str(datetime.datetime.now().time()) + ", " + str(iss.sublat) + ", " + str(iss.sublong) + ", " + str(location) + ", " + str(perc) + ", "+ str(power) + "\n")
                    
                    except Exception as e:
                        logger.error("An error occured: " + str(e))

                time.sleep(30)
                now_time = datetime.datetime.now()
    
    
    
if __name__ == "__main__":
    main()



