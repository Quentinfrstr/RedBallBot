# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import requests
from threading import Condition, Timer
from PIL import Image, ImageDraw
import math


class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

        self.ball_infos = None

    def write(self, buf):
        # Check si c'est une signature jpeg
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

    def gen(self):
        while True:
            frame = self.frame
            image = Image.open(io.BytesIO(frame))
            try:
                r = requests.get('http://192.168.137.227:5001/get_last_ball_infos')

                if r.text != 'None':
                    ball_infos = str(r.text).split(';')
                    self.ball_infos = ball_infos

                    image = self.add_green_square_in_stream(image, int(self.ball_infos[0]), int(self.ball_infos[1]),
                                                            int(self.ball_infos[2]))
            except requests.exceptions.ConnectionError:
                print('Erreur de connexion')

            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='jpeg')
            img_byte_arr = img_byte_arr.getvalue()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + img_byte_arr + b'\r\n')

    @staticmethod
    def add_green_square_in_stream(image, circle_center_x=500, circle_center_y=500, radius=100):

        width, height = image.size
        image_center = (width / 2, height / 2)

        d = ImageDraw.Draw(image)

        top_left = (circle_center_x - radius, circle_center_y - radius)
        top_right = (circle_center_x + radius, circle_center_y - radius)
        bottom_left = (circle_center_x - radius, circle_center_y + radius)
        bottom_right = (circle_center_x + radius, circle_center_y + radius)

        line_color = (0, 255, 0)

        d.line([top_left, top_right, bottom_right, bottom_left, top_left], fill=line_color, width=3)
        d.line([image_center, (circle_center_x, circle_center_y)], fill=line_color, width=2)
        d.text(image_center, str(StreamingOutput.distance_between_points(image_center, (circle_center_x, circle_center_y))), line_color, width=2)
        return image

    @staticmethod
    def distance_between_points(point_one, point_two):
        return math.sqrt(math.pow(point_two[0] - point_one[0], 2) + math.pow(point_two[1] - point_one[1], 2))
