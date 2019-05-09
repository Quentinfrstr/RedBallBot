import requests
import io
import numpy as np
from api.image_analyser import ImageAnalyser
from PIL import Image

_URL_GET_IMAGE = 'http://192.168.137.227:5000/get_image'
_URL_SET_BALL_INFOS = 'http://192.168.137.227:5001/set_ball_infos'

analyser = ImageAnalyser()


def get_most_likely_circle():
    """
    Obtient le cercle le plus proche de celui qui a été analysé la dernière fois.
    :return: Le centre du cercle le plus probable
    """

    # Valeur exagéré pour qu'il y est obligatoirement un cercle plus proche
    right_circle = (1000, 1000)
    for c in possible_circle:
        if abs(last_circle[0] - c[0]) < right_circle[0] and abs(last_circle[1] - c[1]) < \
                right_circle[0]:
            right_circle = c

    return right_circle


while True:
    possible_circle = []
    last_circle = (0, 0)

    r = requests.get(_URL_GET_IMAGE, stream=True, timeout=0.500)
    image = Image.open(io.BytesIO(r.content))
    image = np.asarray(image)
    image = analyser.image_rescale(image=image, ratio=0.1)
    image_center = analyser.get_center_image(image=image)

    for accums, center_x, center_y, radius in analyser.get_circle_center(
            image=image, min_radius=2, max_radius=100, number_best_circle=10, step_radius=1):
        circy, circx = analyser.get_pixels_circles(center_y=center_y, center_x=center_x, radius=radius)

        if analyser.is_red_circle(image=image, circx=circx, circy=circy):
            possible_circle.append((center_x, center_y, radius))

    if len(possible_circle) == 0:
        requests.get(_URL_SET_BALL_INFOS + '/None')

    else:
        last_circle = get_most_likely_circle()
        ball_infos = str(last_circle[0]*10) + ';' + str(last_circle[1]*10) + ';' + str(last_circle[2]*10)
        requests.get(_URL_SET_BALL_INFOS + '/' + ball_infos)
        print(ball_infos)
