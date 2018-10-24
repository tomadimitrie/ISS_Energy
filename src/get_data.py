#!/usr/bin/env python

from bmp import BMPImage

def parse_color_data(color, color_data, step_range, total_pixels):
    print('')

    print(color, ' values equal to 0 -> ', color_data[0], ' (', \
          '{0:.2f}'.format(color_data[0] / total_pixels * 100), '%)', sep = '')

    lower_range_bound = 1
    upper_range_bound = 1

    range_value = 0

    for color_index in range(1, 255):
        upper_range_bound += 1

        range_value += color_data[color_index]

        if upper_range_bound % step_range == 0:
            print(color, ' values between ', lower_range_bound - 1, ' and ', upper_range_bound, \
                  ' -> ', range_value, ' (', '{0:.2f}'.format(range_value / total_pixels * 100), '%)', \
                  sep = '')

            lower_range_bound += step_range

            range_value = 0

    print(color, ' values between ', lower_range_bound - 1, ' and ', 255, \
          ' -> ', range_value, ' (', '{0:.2f}'.format(range_value / total_pixels * 100), '%)', \
          sep = '')

def main():
    input_path = input('Input BMP file path: ')
    image = BMPImage(input_path)

    red = [0] * 256
    green = [0] * 256
    blue = [0] * 256

    for height_index in range(0, image.get_height()):
        for width_index in range(0, image.get_width()):
            pixel = image.get_pixel(width_index, height_index)

            red[pixel.get_red()] += 1
            green[pixel.get_green()] += 1
            blue[pixel.get_blue()] += 1

    total_pixels = image.get_width() * image.get_width()

    step_range = int(input('Choose a analysis step range (1 - 200) : '))

    parse_color_data('RED', red, step_range, total_pixels)
    parse_color_data('GREEN', green, step_range, total_pixels)
    parse_color_data('BLUE', blue, step_range, total_pixels)

if __name__ == "__main__":
    main()
