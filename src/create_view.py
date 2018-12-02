from draw_constants import *

def create_view(sign_shape, color):
    sign = []

    for height_index in range(0, SCREEN_HEIGHT):
         for width_index in range(0, SCREEN_WIDTH):
            if sign_shape[height_index * SCREEN_WIDTH + width_index] == 0:
                sign.append(BLACK)
            else:
                if len(color) < sign_shape[height_index * SCREEN_WIDTH + width_index]:
                    sign.append(BLACK)
                else:
                    sign.append(color[sign_shape[height_index * SCREEN_WIDTH + width_index] - 1])

    return sign
