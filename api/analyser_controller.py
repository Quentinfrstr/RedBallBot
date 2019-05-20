import requests
import sys
from api.image_analyser import ImageAnalyser
from datetime import datetime
from skimage import io as scikit_io

# Constantes pour les requêtes
URL_GET_IMAGE = '/get_image'
URL_SET_BALL_INFOS = '/set_ball_infos/'
BALL_NOT_FOUND = 'None'

# Constantes pour l'analyses d'images
MIN_RADIUS = 7
MAX_RADIUS = 150
NUMBER_BEST_CIRCLE = 5
STEP_RADIUS = 1
RATIO_RESCALE = 0.1

analyser = ImageAnalyser()
url_robot = sys.argv[1]


def get_most_likely_circle():
    """Obtient le cercle le plus proche de clui qui a été analysé la dernière fois

    Returns
    -------
    tuple
        Le centre et le rayon du cercle le plus probable
    """

    # Valeur exagérée pour qu'il y est obligatoirement un cercle plus proche
    right_circle = (1000, 1000)
    for c in possible_circle:
        if abs(last_circle[0] - c[0]) < right_circle[0] and abs(last_circle[1] - c[1]) < \
                right_circle[0]:
            right_circle = c

    return right_circle


def get_last_image():
    """Récupère la dernière image capturé par la caméra du robot
    Transforme l'image en ndarray
    Redimensionne l'image pour un traitement plus rapide
    
    Returns
    -------
    ndarray
        Image reçue
    """
    image_received = None

    try:
        image_received = scikit_io.imread(url_robot + URL_GET_IMAGE)
        image_received = analyser.image_rescale(image=image_received, ratio=RATIO_RESCALE)
    except:
        print('Connexion au serveur impossible')

    return image_received


def send_ball_infos(ball_infos_to_send):
    """Envoi les informations de la balle obbtenus par l'analyse

    Parameters
    ----------
    ball_infos_to_send : tuple

    Returns
    -------
    str
        Informations à envoyer au roboz
    """
    if ball_infos_to_send == BALL_NOT_FOUND:
        requests.get(url_robot + URL_SET_BALL_INFOS + ball_infos_to_send)
    else:

        result = str(int(ball_infos_to_send[0] / RATIO_RESCALE)) + ';' + str(
            int(ball_infos_to_send[1] / RATIO_RESCALE)) + ';' + str(int(ball_infos_to_send[2] / RATIO_RESCALE))
        print(result)
        requests.get(url_robot + URL_SET_BALL_INFOS + result)


def check_possible_circles(image_to_check):
    """Analyse les différents cercles présents sur l'image
    Garde seulement les rouges

    Parameters
    ----------
    image_to_check : ndarray
        Image à analyser

    Returns
    -------
    list
        Contient tous les cercles possibles

    """
    global MIN_RADIUS, MAX_RADIUS, NUMBER_BEST_CIRCLE, STEP_RADIUS
    kept_circles = []
    image_red_detected = analyser.get_red_in_image(image_to_check)
    for center_x, center_y, radius in analyser.get_circle_center(
            image=image_to_check, min_radius=MIN_RADIUS, max_radius=MAX_RADIUS, number_best_circle=NUMBER_BEST_CIRCLE,
            step_radius=STEP_RADIUS):
        circy, circx = analyser.get_pixels_circles(center_y=center_y, center_x=center_x, radius=radius)

        if analyser.is_red_circle(image=image_red_detected, circx=circx, circy=circy):
            kept_circles.append((center_x, center_y, radius))

    return kept_circles


while True:
    elapsed_time = datetime.now()
    last_circle = (0, 0, 0)
    possible_circle = []

    image = get_last_image()
    if image is not None:
        possible_circle = check_possible_circles(image)

    if len(possible_circle) == 0:
        send_ball_infos(BALL_NOT_FOUND)
    else:
        last_circle = get_most_likely_circle()
        send_ball_infos(last_circle)

    print(datetime.now() - elapsed_time)
