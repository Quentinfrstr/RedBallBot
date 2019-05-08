from flask import Flask, send_file, render_template, Response

from picamera import PiCamera
from streaming_output import StreamingOutput

import io

# Constantes des AppRoute Flask
_URL_INDEX = '/'
_URL_GET_IMAGE = '/get_image'
_URL_VIDEO_STREAM = '/video_stream'

# Constantes de la caméra
_CAMERA_RESOLUTION = (int(1640/2), int(1232/2))

app = Flask(__name__)

camera = PiCamera()
camera.resolution = _CAMERA_RESOLUTION
output = StreamingOutput()
camera.start_recording(output, format='mjpeg')


@app.route(_URL_INDEX)
def index():
    return render_template('index.html')


@app.route(_URL_VIDEO_STREAM)
def video_stream():
    return Response(output.gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route(_URL_GET_IMAGE)
def get_image():
    frame = output.frame
    return send_file(io.BytesIO(frame), mimetype='image/jpeg', as_attachment=False)


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded='True', port='5000')
