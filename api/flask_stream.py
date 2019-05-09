from flask import Flask, send_file, render_template, Response
from picamera import PiCamera
from api.streaming_output import StreamingOutput

import io

# Constantes des AppRoute Flask
URL_INDEX = '/'
URL_GET_IMAGE = '/get_image'
URL_VIDEO_STREAM = '/video_stream'

# Constantes de la caméra
CAMERA_RESOLUTION = (int(1640 / 2), int(1232 / 2))
CAMERA_ROTATION = 180
CAMERA_SATURATION = 50

app = Flask(__name__)

camera = PiCamera()
camera.resolution = CAMERA_RESOLUTION
output = StreamingOutput()
camera.rotation = CAMERA_ROTATION
camera.saturation = CAMERA_SATURATION
camera.start_recording(output, format='mjpeg')


@app.route(URL_INDEX)
def index():
    """
    Renvoi la page index.html pour que l'utilisateur puisse avoir accès
    au contrôle du robot et au flux vidéo
    :return: Page index.html
    """
    return render_template('index.html')


@app.route(URL_VIDEO_STREAM)
def video_stream():
    """
    Permet d'obtenir le flux vidéo de la caméra quand le buffer est disponible
    :return: Envoi la dernière image quand celle-ci est disponible
    """
    return Response(output.gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route(URL_GET_IMAGE)
def get_image():
    """
    Obtient la dernière image capturé par la caméra
    :return: Envoi sous forme de fichier la dernière image de la caméra
    """
    frame = output.frame
    return send_file(io.BytesIO(frame), mimetype='image/jpeg', as_attachment=False)


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded='True', port='5000')
