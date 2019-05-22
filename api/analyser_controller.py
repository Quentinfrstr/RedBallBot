import requests
import sys
from api.image_analyser import ImageAnalyser
from skimage import io as scikit_io
from datetime import datetime

class AnalyserController(object):
    """
        Une classe utilisé pour l'analyse d'image

        Attributes
        ----------
        URL_GET_IMAGE : str
            URL sur le serveur pour récupérer l'image
        URL_SET_BALL_INFOS : str
            URL sur le serveur pour définir les nouvelles informations de la balle
        BALL_NOT_FOUND : str
            chaine de caractère définissant si la balle a été trouvée
        MIN_RADIUS : int
            Rayon minimum des cercles
        MAX_RADIUS : int
            Rayon maximum des cercles
        NUMBER_BEST_CIRCLE : int
            Nombre de cercles à obtenir par analyse
        STEP_RADIUS : int
            Nombre de pixel entre chaque rayon
        RATIO_RESCALE : float
            Ratio de redimmensionnement d'image
        analyser : ImageAnalyser
            Objet permettant l'analyse d'image
        url_robot : str
            URL du serveur
        possible_circle : list
            La liste de tous les cercles rouges dans la dernière image analysée.
        Methods
        -------
        get_most_likely_circle(self)
            Obtient le cercle le plus grand de la liste
        get_last_image(self)
            Récupère la dernière image capturée par la caméra du robot
            Transforme l'image en ndarray
            Redimensionne l'image pour un traitement plus rapide
        send_ball_infos(self, ball_infos_to_send)
            Envoi les informations de la balle obbtenus par l'analyse
        check_possible_circles(self, image_to_check)
            Analyse les différents cercles présents sur l'image
        """

    # Constantes pour les requêtes
    URL_GET_IMAGE = '/get_image'
    URL_SET_BALL_INFOS = '/set_ball_infos/'
    BALL_NOT_FOUND = 'None'

    # Constantes pour l'analyses d'images
    MIN_RADIUS = 5
    MAX_RADIUS = 80
    NUMBER_BEST_CIRCLE = 5
    STEP_RADIUS = 1
    RATIO_RESCALE = 0.1

    analyser = ImageAnalyser()

    def __init__(self, url):
        """ Constructeur de la classe

        Parameters
        ----------
        url : str
            URL du robot à controler
        """
        self.url_robot = url
        self.possible_circle = []

    def get_most_likely_circle(self):
        """Obtient le cercle le plus grand de la liste.

        Returns
        -------
        tuple
            Le centre et le rayon du cercle le plus probable
        """

        # Valeur exagérée pour qu'il y est obligatoirement un cercle plus proche
        right_circle = (0, 0, 0)
        for c in self.possible_circle:
            if c[2] >= right_circle[2]:
                right_circle = c

        return right_circle

    def get_last_image(self):
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
            image_received = scikit_io.imread(self.url_robot + self.URL_GET_IMAGE)
            image_received = self.analyser.image_rescale(image=image_received, ratio=self.RATIO_RESCALE)
        except requests.exceptions.ConnectionError:
            print('Connexion au serveur impossible')

        return image_received

    def send_ball_infos(self, ball_infos_to_send):
        """Envoi les informations de la balle obbtenus par l'analyse

        Parameters
        ----------
        ball_infos_to_send : tuple
            Informations de la balle à envoyer

        Returns
        -------
        str
            Informations à envoyer au roboz
        """
        try:
            if ball_infos_to_send == self.BALL_NOT_FOUND:
                requests.get(self.url_robot + self.URL_SET_BALL_INFOS + ball_infos_to_send)
            else:

                result = str(int(ball_infos_to_send[0] / self.RATIO_RESCALE)) + ';' + str(
                    int(ball_infos_to_send[1] / self.RATIO_RESCALE)) + ';' + str(
                    int(ball_infos_to_send[2] / self.RATIO_RESCALE))
                print(result)
                requests.get(self.url_robot + self.URL_SET_BALL_INFOS + result)
        except requests.exceptions.ConnectionError:
            print('Serveur indisponible')

    def check_possible_circles(self, image_to_check):
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
        kept_circles = []
        image_red_detected = self.analyser.get_red_in_image(image_to_check)
        for center_x, center_y, radius in self.analyser.get_circle_center(
                image=image_to_check, min_radius=self.MIN_RADIUS, max_radius=self.MAX_RADIUS,
                number_best_circle=self.NUMBER_BEST_CIRCLE,
                step_radius=self.STEP_RADIUS):
            circy, circx = self.analyser.get_pixels_circles(center_y=center_y, center_x=center_x, radius=radius)

            if self.analyser.is_red_circle(image=image_red_detected, circx=circx, circy=circy):
                kept_circles.append((center_x, center_y, radius))

        return kept_circles


if __name__ == '__main__':
    controller = AnalyserController(sys.argv[1])
    while True:
        elapsed_time = datetime.now()
        last_circle = (0, 0, 0)
        controller.possible_circle = []

        image = controller.get_last_image()
        if image is not None:
            controller.possible_circle = controller.check_possible_circles(image)

        if len(controller.possible_circle) == 0:
            controller.send_ball_infos(controller.BALL_NOT_FOUND)
        else:
            last_circle = controller.get_most_likely_circle()
            controller.send_ball_infos(last_circle)

        print(datetime.now() - elapsed_time)
