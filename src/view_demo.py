import time

from sense_hat import SenseHat

from draw_constants import *
from create_view import *

def main():
    sense = SenseHat()
    sense.set_pixels(create_view(exclamation_sign_shape, [RED, BLUE]))

    time.sleep(5)
    sense.clear()

    sense.set_pixels(create_view(question_sign_shape, [GREEN, BLUE]))

    time.sleep(5)
    sense.clear()

if __name__ == "__main__":
    main()
