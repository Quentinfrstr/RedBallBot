from flask import Flask, make_response

from robot import Robot
from image_analyser import ImageAnalyser

_URL_SEND_CMD = '/send_cmd/<cmd>'
_URL_GET_LAST_BALL_INFOS = '/get_last_ball_infos'
_URL_CHANGE_SPEED = '/change_speed/<new_speed>'

_CMD_FORWARD = 'forward'
_CMD_BACKWARD = 'backward'
_CMD_LEFT = 'left'
_CMD_RIGHT = 'right'
_CMD_STOP = 'stop'

app = Flask(__name__)

robot = Robot()
is_auto_mode = False

analyser = ImageAnalyser()
last_ball_infos = None


@app.route(_URL_GET_LAST_BALL_INFOS)
def get_last_ball_infos():
    return 'Done', 200


@app.route(_URL_SEND_CMD)
def send_cmd(cmd):
    if cmd == _CMD_FORWARD:
        robot.forward()
    elif cmd == _CMD_BACKWARD:
        robot.backward()
    elif cmd == _CMD_LEFT:
        robot.left()
    elif cmd == _CMD_RIGHT:
        robot.right()
    elif cmd == _CMD_STOP:
        robot.stop()

    return 'Done', 200

@app.route(_URL_CHANGE_SPEED)
def change_speed(new_speed):
    robot.change_speed(new_speed)
    return 'Done', 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded='True', port='5001')
