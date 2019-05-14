# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import requests
from threading import Condition
from PIL import Image, ImageDraw


class StreamingOutput(object):
    IMAGE_FORMAT = 'jpeg'
    LINE_WIDTH = 3
    LINE_COLOR = (0, 255, 0)

    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

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

            r = requests.get('http://127.0.0.1:5000/get_ball_infos')

            if r.text != 'None':
                ball_infos = str(r.text).split(';')

                image = self.add_green_square_in_stream(image, int(ball_infos[0]), int(ball_infos[1]),
                                                        int(ball_infos[2]))

            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='jpeg')
            img_byte_arr = img_byte_arr.getvalue()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + img_byte_arr + b'\r\n')

    @staticmethod
    def add_green_square_in_stream(image, circle_center_x, circle_center_y, radius):
        width, height = image.size
        image_center = (width / 2, height / 2)

        d = ImageDraw.Draw(image)

        top_left = (circle_center_x - radius, circle_center_y - radius)
        top_right = (circle_center_x + radius, circle_center_y - radius)
        bottom_left = (circle_center_x - radius, circle_center_y + radius)
        bottom_right = (circle_center_x + radius, circle_center_y + radius)

        d.line([top_left, top_right, bottom_right, bottom_left, top_left], fill=StreamingOutput.LINE_COLOR,
               width=StreamingOutput.LINE_WIDTH)
        d.line([image_center, (circle_center_x, circle_center_y)], fill=StreamingOutput.LINE_COLOR,
               width=StreamingOutput.LINE_WIDTH)
        d.text(image_center,
               str(image_center[0] + circle_center_x),
               StreamingOutput.LINE_COLOR, width=StreamingOutput.LINE_WIDTH)
        return image
