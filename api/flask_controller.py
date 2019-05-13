from flask import Flask
from robot import Robot
from api.image_analyser import ImageAnalyser

URL_SEND_CMD = '/send_cmd/<cmd>'
URL_GET_LAST_BALL_INFOS = '/get_last_ball_infos'
URL_CHANGE_SPEED = '/change_speed/<new_speed>'
URL_SET_BALL_INFOS = '/set_ball_infos/<ball_infos>'
URL_LOCAL_SET_BALL_INFOS = '/local_set_ball_infos/<ball_infos>'

CMD_FORWARD = 'forward'
CMD_BACKWARD = 'backward'
CMD_LEFT = 'left'
CMD_RIGHT = 'right'
CMD_STOP = 'stop'

CAMERA_RESOLUTION = (int(1640 / 2), int(1232 / 2))

app = Flask(__name__)

robot = Robot()
is_auto_mode = False

analyser = ImageAnalyser()
last_ball_infos = None


@app.route(URL_GET_LAST_BALL_INFOS)
def get_last_ball_infos():
    """
    Obtient les dernières informations de la position de la balle
    Disponible par adresse http
    :return:
    Retourne center_x;center_y;radius si la position de la balle est connue
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
    if ball_center_x > image_center[0] + 100:
        robot.right()
    elif ball_center_x < image_center[0] - 100:
        robot.left()
    else:
        robot.forward()


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded='True', port='5001')
