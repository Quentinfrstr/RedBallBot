# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
from threading import Condition
from PIL import Image, ImageDraw


class StreamingOutput(object):
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

            #if circle_infos is not None:
            image = self.add_green_square_in_stream(image)
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='jpeg')
            img_byte_arr = img_byte_arr.getvalue()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + img_byte_arr + b'\r\n')

    @staticmethod
    def add_green_square_in_stream(image, circle_center_x=500, circle_center_y=500, radius=100):
        d = ImageDraw.Draw(image)

        top_left = (circle_center_x - radius, circle_center_y - radius)
        top_right = (circle_center_x + radius, circle_center_y - radius)
        bottom_left = (circle_center_x - radius, circle_center_y + radius)
        bottom_right = (circle_center_x + radius, circle_center_y + radius)

        line_color = (0, 255, 0)

        d.line([top_left, top_right, bottom_right, bottom_left, top_left], fill=line_color, width=3)

        return image
