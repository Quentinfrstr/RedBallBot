from skimage import color
from skimage.transform import hough_circle, hough_circle_peaks, rescale
from skimage.feature import canny
from skimage.draw import circle
from skimage.util import img_as_ubyte

import numpy as np


class ImageAnalyser(object):

    def __init__(self):
        pass

    def get_circle_center(self, image, min_radius, max_radius, step_radius, number_best_circle):
        pass

    def get_pixels_circles(self, center_x, center_y, radius):
        pass

    def is_red_circle(self, image, circx, circy):
        pass

    def get_center_image(self, image):
        pass

    def image_rescale(self, image, ratio):
        pass
