# Projet : RedBallBot
# Auteur : Quentin Forestier
# Fichier : RedBallBot/api/image_analyser.py

__author__ = "Quentin Forestier"
__copyright__ = "Copyright 2019, RedBallBot2"
__version__ = "1.0.0"

from skimage import color
from skimage.transform import hough_circle, hough_circle_peaks, rescale
from skimage.feature import canny
from skimage.draw import circle
from skimage.util import img_as_ubyte

import numpy as np


class ImageAnalyser(object):
    """
    Une classe utilisé pour l'analyse d'image

    Attributes
    ----------
    MAX_VALUE_RGB : int
        Valeur maximal du RGB

    Methods
    -------
    get_circle_center(image, min_radius, max_radius, step_radius, number_best_circle)
        Détecte les cercles présents dans l'image

    get_pixels_circles(center_x, center_y, radius)
        Récupère tous les pixels du cercle demandé

    is_red_circle(self, image, circx, circy)
        Détecte si un rond contient du rouge

    get_red_in_image(image)
        Détecte le rouge de l'image et renvoi une nouvelle image modifié

    is_red_circle_old(image, circx, circy)
        Détecte si une balle est rouge

    get_center_image(image)
        Obtient la position x,y du centre de l'image

    image_rescale(image, ratio)
        Redimensionne l'image avec le ratio demandé
    """

    MAX_VAlUE_RGB = 255
    MIN_RED = 190

    def __init__(self):
        """Constructeur de la classe
        """
        pass

    @staticmethod
    def get_circle_center(image, min_radius, max_radius, step_radius, number_best_circle):
        """Détecte les cercles présents dans l'image

        Parameters
        ----------
        image: ndarray
            Image à analyser
        min_radius: int
            Rayon minimum des cercles
        max_radius : int
            Rayon maximum des cercles
        step_radius : int
            Pas entre les rayons des cercles
        number_best_circle : int
            Nombre de cercles à retourner (Choisi les N meilleurs)

        Returns
        -------
        tuple
            Retourne les informations sur les cercles (centre X, centre Y, rayon)
        """
        image = color.rgb2gray(image)
        image = img_as_ubyte(image)

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

        return zip(cx, cy, radii)

    @staticmethod
    def get_pixels_circles(center_x, center_y, radius):
        """Récupère tous les pixels du cercle demandé

        Parameters
        ----------
        center_x : int
            Centre en X du cercle
        center_y : int
            Centre en Y du cercle
        radius : int
            Rayon du cercle

        Returns
        -------
        ndarray of int
            Toutes les positions X,Y des pixels du cercle
        """
        return circle(center_y, center_x, radius)

    @staticmethod
    def is_red_circle(image, circx, circy):
        """

        Parameters
        ----------
        image : ndarray
            Image transformée par get_red_in_image
        circx : liste position de pixels en X
            Tous les pixels en X du rond
        circy : liste position de pixels en Y
            Tous les pixels en Y du rond
        Returns
        -------
        bool
            S'il y a plus de 50 pixels rouge dans l'image -> True
            S'il y a moins de 50 pixels rouge dans l'image -> False
        """
        counter = 0
        for x, y in zip(circx, circy):
            try:
                r, g, b = image[y, x]
                if r == 0 and g == 1 and b == 0:
                    counter += 1
            except IndexError:
                print('Erreur d\'index')
        return counter > 50

    @staticmethod
    def get_red_in_image(image):
        """ Transforme les pixels rouges en pixels verts pures

        Parameters
        ----------
        image : ndarray
            Image sous forme d'array numpy
        Returns
        -------
        ndarray
            Image transformée
        """
        image_slice_red = image[:, :, 0]
        image_slice_green = image[:, :, 1]
        image_slice_blue = image[:, :, 2]

        mask = (image_slice_red * ImageAnalyser.MAX_VAlUE_RGB > ImageAnalyser.MIN_RED) & (
                image_slice_red * ImageAnalyser.MAX_VAlUE_RGB > (
                image_slice_green * ImageAnalyser.MAX_VAlUE_RGB + image_slice_blue * ImageAnalyser.MAX_VAlUE_RGB) * 5)
        image[mask] = [0, 1, 0]

        return image

    @staticmethod
    def is_red_circle_old(image, circx, circy):
        """Détecte si une balle est rouge

        Parameters
        ----------
        image : ndarray
            Image à analyser
        circx : list de int
            Tous les pixels en X du rond
        circy : list de int
            Tous les pixels en Y du rond

        Returns
        -------
        bool
            Si le rond est rouge -> True
            Si le rond n'est pas rouge -> False
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
            avg_r = sum(r_total) / len(r_total) * ImageAnalyser.MAX_VAlUE_RGB
            avg_g = sum(g_total) / len(g_total) * ImageAnalyser.MAX_VAlUE_RGB
            avg_b = sum(b_total) / len(b_total) * ImageAnalyser.MAX_VAlUE_RGB
        except ArithmeticError:
            print('Tentative de division par 0')

        # Conditions inventées "au hasard". Marche plutôt bien
        return avg_r > avg_b + avg_g + 50 and avg_r > 200

    @staticmethod
    def get_center_image(image):
        """Obtient la position (x,y) du centre de l'image

        Parameters
        ----------
        image : ndarray
            Image souhaité

        Returns
        -------
        point
            Position X,Y du centre de l'image
        """
        image_center_x = round(len(image[0]) / 2)
        image_center_y = round(len(image) / 2)
        image_center = (image_center_x, image_center_y)

        return image_center

    @staticmethod
    def image_rescale(image, ratio):
        """Redimensionne l'image avec le ration demandé

        Parameters
        ----------
        image : ndarray
            Image a redimensionné
        ratio : float
            Ratio de redimensionnement

        Returns
        -------
        ndarray
            Image redimensionné
        """
        return rescale(image, ratio, anti_aliasing=True)
