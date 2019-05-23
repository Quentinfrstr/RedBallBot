from flask import Flask, send_file, render_template, Response

from picamera import PiCamera
from streaming_output import StreamingOutput
from threading import Timer
from robot import Robot

import io

# Constantes des AppRoute Flask
URL_SEND_CMD = '/send_cmd/<cmd>'
URL_CHANGE_SPEED = '/change_speed/<new_speed>'
URL_SET_BALL_INFOS = '/set_ball_infos/<ball_infos>'
URL_INDEX = '/'
URL_GET_IMAGE = '/get_image'
URL_VIDEO_STREAM = '/video_stream'
URL_GET_BALL_INFOS = '/get_ball_infos'
URL_SET_COMPENSATION = '/set_compensation/<compensation>'
URL_SET_ROBOT_MODE = '/set_robot_mode/<mode>'

# Constantes des commande du controller
CMD_FORWARD = 'forward'
CMD_BACKWARD = 'backward'
CMD_LEFT = 'left'
CMD_RIGHT = 'right'
CMD_STOP = 'stop'

# Constantes de la caméra
CAMERA_RESOLUTION = (640, 480)
CAMERA_ROTATION = 180
CAMERA_SATURATION = 60
CAMERA_BRIGHTNESS = 40

# Constantes de déplacement
MARGIN_FORWARD = 75
MAX_RADIUS_FOR_WIN = 170

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
last_ball_infos = None


@app.route(URL_INDEX)
def index():
    """Renvoi la page index.html pour que l'utilisateur puisse avoir accès
    au contrôle du robot et au flux vidéo

    Returns
    -------
    html page
        Le template html de la page d'index
    """
    return render_template('index.html')


@app.route(URL_VIDEO_STREAM)
def video_stream():
    """Permet d'obtenir le flux vidéo de la caméra quand le buffer est disponible

    Returns
    -------
    Image jpeg
        Envoi la dernière image quand celle-ci est disponible
    """
    return Response(output.gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route(URL_GET_IMAGE)
def get_image():
    """ Obtient la dernière image capturé par la caméra

    Returns
    -------
    Image jpeg
        Envoi sous forme de fichier la dernière image de la caméra
    """
    frame = output.frame
    return send_file(io.BytesIO(frame), mimetype='image/jpeg', as_attachment=False)


@app.route(URL_GET_BALL_INFOS)
def get_ball_infos():
    """Obtient les dernières informations de la position de la balle
    Disponible par adresse http

    Returns
    -------
    tupple
        tupple qui contient le centre X,Y de la balle et son rayon
        ou
        None si aucune balle n'est trouvé
    """

    if last_ball_infos is not None:
        result = str(last_ball_infos[0]) + ';' + str(last_ball_infos[1]) + ';' + str(last_ball_infos[2])
    else:
        result = 'None'
    return result, 200


@app.route(URL_SET_BALL_INFOS)
def set_ball_infos(ball_infos):
    """Défini les dernières informations de la balle (son centre et son rayon)

    Parameters
    ----------
    ball_infos : str
        Centre X, Centre Y et rayon de la balle sous forme de string centre_x;centre_y;rayon

    Returns
    -------
    str
        Renvoi un code 200 en cas de réussite
    """
    global last_ball_infos
    if ball_infos != 'None':
        last_ball_infos = str(ball_infos).split(';')
        print(last_ball_infos[2])
        if is_auto_mode and int(last_ball_infos[2]) < MAX_RADIUS_FOR_WIN:
            go_to_ball(int(last_ball_infos[0]))
        elif is_auto_mode:
            robot.stop()
            robot.beep_on()
            t = Timer(0.5, robot.beep_off)
            t.start()

    else:
        robot.beep_off()
        last_ball_infos = None
        if is_auto_mode:
            robot.left()

    return 'Done', 200


@app.route(URL_SEND_CMD)
def send_cmd(cmd):
    """Permet de commander le robot a distance avec les commandes suivante :
        - forward
        - backward
        - left
        - right
        - stop

    Parameters
    ----------
    cmd : str
        Commande que le robot doit effectuer

    Returns
    -------
    str
        Renvoi un code 200 en cas de réussite
    """
    if not is_auto_mode:
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


@app.route(URL_SET_ROBOT_MODE)
def set_robot_mode(mode):
    """Défini le mode de déplacement du robot
        - auto
        - manuel
    Parameters
    ----------
    mode : str
        Le mode de déplacement du robot

    Returns
    -------
    str
        Renvoi un code 200 en cas de réussite
    """
    robot.stop()
    global is_auto_mode
    is_auto_mode = mode == 'auto'


@app.route(URL_CHANGE_SPEED)
def change_speed(new_speed):
    """Permet de modifier la vitesse du robot

    Parameters
    ----------
    new_speed : str
        Valeur entre 0 et 100 de la vitesse

    Returns
    -------
    str
        Renvoi un code 200 en cas de réussite
    """
    robot.change_speed(new_speed)
    return 'Done', 200


@app.route(URL_SET_COMPENSATION)
def set_compensation(compensation):
    """ Défini le ratio de compensation des moteurs
        Permet de corriger les défaillances matérielles

    Parameters
    ----------
    compensation : str
        Valeur des ratios de compensations des moteurs

    Returns
    -------
    str
        Renvoi un code 200 en cas de réussite
    """
    compensations = compensation.split(';')
    print(compensation)
    robot.set_compensation(float(compensations[0]), float(compensations[1]))
    return 'Done', 200


def go_to_ball(ball_center_x):
    """Commande le robot pour qu'il aille à la balle

    Parameters
    ----------
    ball_center_x : int
        Centre de la balle en X
    """
    image_center = (CAMERA_RESOLUTION[0] / 2, CAMERA_RESOLUTION[1] / 2)
    diff_speed = int((ball_center_x - image_center[0]) * 0.01)
    print(diff_speed)
    if ball_center_x > image_center[0] + MARGIN_FORWARD:
        robot.forward_with_modification(robot.speed + diff_speed, robot.speed - diff_speed)
    elif ball_center_x < image_center[0] - MARGIN_FORWARD:
        robot.forward_with_modification(robot.speed + diff_speed, robot.speed - diff_speed)
    else:
        robot.forward()


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded='True', port='5000')
