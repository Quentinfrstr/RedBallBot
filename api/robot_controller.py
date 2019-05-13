from flask import Flask, send_file, render_template, Response

from picamera import PiCamera
from api.streaming_output import StreamingOutput

from api.robot import Robot
from api.image_analyser import ImageAnalyser

import io

# Constantes des AppRoute Flask
URL_SEND_CMD = '/send_cmd/<cmd>'
URL_CHANGE_SPEED = '/change_speed/<new_speed>'
URL_SET_BALL_INFOS = '/set_ball_infos/<ball_infos>'
URL_INDEX = '/'
URL_GET_IMAGE = '/get_image'
URL_VIDEO_STREAM = '/video_stream'
URL_GET_BALL_INFOS = '/get_ball_infos'

# Constantes des commande du controller
CMD_FORWARD = 'forward'
CMD_BACKWARD = 'backward'
CMD_LEFT = 'left'
CMD_RIGHT = 'right'
CMD_STOP = 'stop'

# Constantes de la caméra
CAMERA_RESOLUTION = (820, 616)
CAMERA_ROTATION = 180
CAMERA_SATURATION = 60
CAMERA_BRIGHTNESS = 40

# Constantes de déplacement
MARGIN_FORWARD = 75
app = Flask(__name__)

robot = Robot()
is_auto_mode = False

camera = PiCamera()
camera.resolution = CAMERA_RESOLUTION
output = StreamingOutput()
camera.rotation = CAMERA_ROTATION
camera.saturation = CAMERA_SATURATION
camera.brightness = CAMERA_BRIGHTNESS
camera.start_recording(output, format='mjpeg')

analyser = ImageAnalyser()
last_ball_infos = None


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


@app.route(URL_GET_BALL_INFOS)
def get_ball_infos():
    """
    Obtient les dernières informations de la position de la balle
    Disponible par adresse http
    :return: Retourne center_x;center_y;radius
    si la position de la balle est connue
    Sinon, envoie None
    """
    if last_ball_infos is not None:
        result = str(last_ball_infos[0]) + ';' + str(last_ball_infos[1]) + ';' + str(last_ball_infos[2])
    else:
        result = 'None'
    return result, 200


@app.route(URL_SET_BALL_INFOS)
def set_ball_infos(ball_infos):
    """
    Défini les dernières informations de la balle (son centre et son rayon)
    :param ball_infos: Centre X, Centre Y et rayon de la balle sous forme centre_x;centre_y;rayon
    :return: Renvoi un code 200
    """
    global last_ball_infos
    if ball_infos != 'None':
        robot.stop()
        last_ball_infos = str(ball_infos).split(';')

        go_to_ball(int(last_ball_infos[0]))
    else:
        last_ball_infos = None
        robot.left()

    return 'Done', 200


@app.route(URL_SEND_CMD)
def send_cmd(cmd):
    """
    Permet de commander le robot a distance avec les commandes suivante :
        - forward
        - backward
        - left
        - right
        - stop
    :param cmd: Commande que le robot doit effectuer
    :return: Renvoi un code 200
    """
    if cmd == CMD_FORWARD:
        robot.forward()
    elif cmd == CMD_BACKWARD:
        robot.backward()
    elif cmd == CMD_LEFT:
        robot.left()
    elif cmd == CMD_RIGHT:
        robot.right()
    elif cmd == CMD_STOP:
        robot.stop()

    return 'Done', 200


@app.route(URL_CHANGE_SPEED)
def change_speed(new_speed):
    """
    Permet de modifier la vitesse du robot
    :param new_speed: Valeur entre 0 et 100 de la vitesse
    :return: Renvoi un code 200
    """
    robot.change_speed(new_speed)
    return 'Done', 200


def go_to_ball(ball_center_x):
    """
    Commande le robot pour qu'il aille a la balle
    :param ball_center_x: Centre X de la balle
    """
    image_center = (CAMERA_RESOLUTION[0] / 2, CAMERA_RESOLUTION[1] / 2)

    if ball_center_x > image_center[0] + MARGIN_FORWARD:
        robot.right()
    elif ball_center_x < image_center[0] - MARGIN_FORWARD:
        robot.left()
    else:
        robot.forward()


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded='True', port='5000')
