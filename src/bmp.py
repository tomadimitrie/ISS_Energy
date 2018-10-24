from struct import *

class Pixel:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

class FileHeader:
    def read(self, input_file):
        input_file.seek(0)

        self.file_marker_1 = input_file.read(1)
        self.file_marker_2 = input_file.read(1)

        self.bmp_size = input_file.read(4)

        self.unused_1 = input_file.read(2)
        self.unused_2 = input_file.read(2)

        self.image_data_offset = input_file.read(4)

    def write(self, output_file):
        output_file.seek(0)

        output_file.write(self.file_marker_1)
        output_file.write(self.file_marker_2)

        output_file.write(self.bmp_size)

        output_file.write(self.unused_1)
        output_file.write(self.unused_2)

        output_file.write(self.image_data_offset)

class ImageHeader:
    def read(self, input_file):
        input_file.seek(14)

        self.header_size = input_file.read(4)

        self.width = input_file.read(4)
        self.height = input_file.read(4)

        self.planes = input_file.read(2)
        self.bits_per_pixel = input_file.read(2)

        self.compression_type = input_file.read(4)
        self.image_size = input_file.read(4)

        self.pixel_per_meter_x = input_file.read(4)
        self.pixel_per_meter_y = input_file.read(4)

        self.used_color_map_entries = input_file.read(4)
        self.significant_colors = input_file.read(4)

    def write(self, output_file):
        output_file.seek(14)

        output_file.write(self.header_size)

        output_file.write(self.width)
        output_file.write(self.height)

        output_file.write(self.planes)
        output_file.write(self.bits_per_pixel)

        output_file.write(self.compression_type)
        output_file.write(self.image_size)

        output_file.write(self.pixel_per_meter_x)
        output_file.write(self.pixel_per_meter_y)

        output_file.write(self.used_color_map_entries)
        output_file.write(self.significant_colors)

class BMPImage:
    file_header = FileHeader()
    image_header = ImageHeader()

    pixels = []

    def __readPixels(self, input_file):
        input_file.seek(self.image_data_offset)

        for pixel_index in range(0, self.width * self.height):
            pixel_data = unpack("BBB", input_file.read(3))

            new_pixel = Pixel(pixel_data[0], pixel_data[1], pixel_data[2])

            self.pixels.append(new_pixel)

            if (pixel_index and self.width % pixel_index == 0):
                padding = self.required_padding

                while (padding):
                    input_file.read(1)

                    padding -= 1


    def __init__(self, file_path):
        with open(file_path, "rb") as input_file:
            self.file_header.read(input_file)
            self.image_header.read(input_file)

            self.width = unpack("I", self.image_header.width)[0]
            self.height = unpack("I", self.image_header.height)[0]

            self.image_data_offset = unpack("I", self.file_header.image_data_offset)[0]

            self.subpixels_per_line = self.width * 3

            padding = 4 - self.subpixels_per_line % 4
            self.required_padding = 0 if (self.subpixels_per_line % 4 == 0) else padding

            self.__readPixels(input_file)

    def __writePixels(self, output_file):
        output_file.seek(self.image_data_offset)

        for pixel_index in range(0, self.width * self.height):
            output_file.write(pack("BBB", self.pixels[pixel_index].red, \
                                          self.pixels[pixel_index].green, \
                                          self.pixels[pixel_index].blue))

            if (pixel_index and self.width % pixel_index == 0):
                padding = self.required_padding

                while (padding):
                    output_file.write(pack("B", 0))

                    padding -= 1


    def write(self, output_path):
        with open(output_path, "wb") as output_file:
            self.file_header.write(output_file)
            self.image_header.write(output_file)

            self.__writePixels(output_file)
