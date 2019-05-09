from skimage import color
from skimage.transform import hough_circle, hough_circle_peaks, rescale
from skimage.feature import canny
from skimage.draw import circle
from skimage.util import img_as_ubyte

import numpy as np


class ImageAnalyser(object):
    MAX_VAlUE_RGB = 255

    def __init__(self):
        pass

    @staticmethod
    def get_circle_center(image, min_radius, max_radius, step_radius, number_best_circle):
        """
        Cherche les cercles présent dans l'image
        :param image: Image à analyser
        :param min_radius: Rayon minimum du cercle
        :param max_radius: Rayon maximum du cercle
        :param step_radius: Pas entre les rayons
        :param number_best_circle: Nombre de cercles à retourner
        :return: Retourne les informations sur les cercles (center_x, center_y, radius)
        """
        img = color.rgb2gray(image)
        image = img_as_ubyte(img)

        # Détecte les bords d'une forme grâce à un dérivé de la fonction gaussienne
        # Possibilité de modifier la precision en modifiant le sigma
        # Utilise des seuils d'hystère afin d'éviter le bruit
        edges = canny(image, sigma=3, low_threshold=10, high_threshold=50)

        hough_radii = np.arange(min_radius, max_radius, step_radius)

        hough_res = hough_circle(edges, hough_radii)

        # Sélectionne les N cercles les plus probables (N = numberBestCircle)
        accums, cx, cy, radii = hough_circle_peaks(hough_res, hough_radii,
                                                   total_num_peaks=number_best_circle, min_xdistance=20,
                                                   min_ydistance=20)

        return zip(accums, cx, cy, radii)

    @staticmethod
    def get_pixels_circles(center_x, center_y, radius):
        """
        Récupère tous les pixels du cercle
        :param center_x: Centre du cercle en X
        :param center_y: Center du cercle en Y
        :param radius: Rayon du cercle
        :return Coordonnées des pixels dans le cercle
        """
        return circle(center_y, center_x, radius)

    def is_red_circle(self, image, circx, circy):
        """
        Détermine si, en moyenne, le rouge est dominant dans le cercle
        :param image: L'image en couleur (float 0.1 to 1.0)
        :param circx: Tous les points x du cercle (Aire)
        :param circy: Tous les points y du cercle (Aire)
        :return: True -> Le cercle est déterminé comme rouge
        False -> Le cercle n'est pas suffisamment rouge
        """

        r_total = []
        g_total = []
        b_total = []

        avg_r = 0
        avg_g = 0
        avg_b = 0

        for x, y in zip(circx, circy):
            try:
                r, g, b = image[y, x]
                r_total.append(r)
                g_total.append(g)
                b_total.append(b)
            except IndexError:
                print('Partie du rond en dehors de l\'image')

        try:
            avg_r = sum(r_total) / len(r_total) * self.MAX_VAlUE_RGB
            avg_g = sum(g_total) / len(g_total) * self.MAX_VAlUE_RGB
            avg_b = sum(b_total) / len(b_total) * self.MAX_VAlUE_RGB
        except ArithmeticError:
            print('Tentative de division par 0')

        # Conditions inventées "au hasard". Marche plutôt bien
        return avg_r > avg_b + avg_g + 30 and avg_r > 200

    @staticmethod
    def get_center_image(image):
        """
        Obtient la position (x,y) du centre de l'image
        :param image: Image souhaitée
        :return: Centre (x,y) de l'image
        """
        image_center_x = round(len(image[0]) / 2)
        image_center_y = round(len(image) / 2)
        image_center = (image_center_x, image_center_y)

        return image_center

    @staticmethod
    def image_rescale(image, ratio):
        """
        Re dimensionne l'image avec le ratio demandé
        :param image: Image sous forme de tableau
        :param ratio: Ratio de re dimensionnement
        :return: Image re dimensionné sous forme de tableau
        """
        return rescale(image, ratio, anti_aliasing=True)
