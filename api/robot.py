import RPi.GPIO as GPIO


class Robot(object):
    """
        Une classe utilisé pour les déplacements du robot
        Une partie du code est reprise de la classe AlphaBot2
        ...

        Attributes
        ----------
        AIN1 : int
            pin du GPIO 1 du moteur gauche
        AIN2 : int
            pin du GPIO 2 du moteur gauche
        BIN1 : int
            pin du GPIO 1 du moteur droit
        BIN2 : int
            pin du GPIO 2 du moteur droit
        ENA : int
            pin du PWM du moteur gauche
        ENB : int
            pin du PWM du moteur droit
        MAX_DUTY_CICLE : int
            Valeur maxmimum du rapport cyclique
        MIN_DUTY_CYCLE : int
            Valeur minimale du rapport cyclique
        speed : int
            Vitesse du robot
        compensation_left : float
            Compensation du moteur gauche
        compensation_right : float
            Compensation du moteur droit

        Methods
        -------
        set_motor(self, left, right)
            Défini le rapport cyclique du moteur droite et gauche
        forward_with_modification(self, left, right)
            Fait avancé le robot, possibilité de modifier la valeur cyclique des moteurs
        forward(self)
            Fait avancer le robot
        stop(self)
            Arrête le robot
        backward(self)
            Fait reculer le robot
        left(self)
            Fait tourné le robot vers la gauche
        right(self)
            Fait tourné le robot vers la droite
        change_speed(self, new_speed)
            Change la vitesse du robot
        set_compensation(self, left, right)
            Défini la compensation de puissance des moteurs pour palier au défaut matériel
        gpio_cleanup() : staticmethod
            Nettoye les GPIO du robot
        __del__()
            Nettoye les GPIO du robot à la fin du processus
        """

    # Valeurs des pins reprient de la classe AlphaBot2
    AIN1 = 12
    AIN2 = 13
    BIN1 = 20
    BIN2 = 21
    ENA = 6
    ENB = 26

    MAX_DUTY_CYCLE = 100
    MIN_DUTY_CYCLE = -100

    def __init__(self, speed=30):
        """
        Parameters
        ----------
        speed : int
            La vitesse du robot
        """
        self.speed = speed
        self.compensation_left = 1
        self.compensation_right = 1

        # Repris de la classe AlphaBot2, fourni avec le robot
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.AIN1, GPIO.OUT)
        GPIO.setup(self.AIN2, GPIO.OUT)
        GPIO.setup(self.BIN1, GPIO.OUT)
        GPIO.setup(self.BIN2, GPIO.OUT)
        GPIO.setup(self.ENA, GPIO.OUT)
        GPIO.setup(self.ENB, GPIO.OUT)
        self.PWMA = GPIO.PWM(self.ENA, 500)
        self.PWMB = GPIO.PWM(self.ENB, 500)
        self.PWMA.start(self.speed)
        self.PWMB.start(self.speed)
        self.stop()

    def set_motor(self, left, right):
        """Défini la vitesse et la direction des moteurs du robot

        La direction change en fonction de la valeur (positive ou négative)

        Parameters
        ----------
        left : int
            Vitesse du moteur gauche
        right : int
            Vitesse du moteur droit

        """

        if (right >= 0) and (right <= self.MAX_DUTY_CYCLE):
            GPIO.output(self.AIN1, GPIO.HIGH)
            GPIO.output(self.AIN2, GPIO.LOW)
            self.PWMA.ChangeDutyCycle(right)
        elif (right < 0) and (right >= self.MIN_DUTY_CYCLE):
            GPIO.output(self.AIN1, GPIO.LOW)
            GPIO.output(self.AIN2, GPIO.HIGH)
            self.PWMA.ChangeDutyCycle(0 - right)
        if (left >= 0) and (left <= self.MAX_DUTY_CYCLE):
            GPIO.output(self.BIN1, GPIO.HIGH)
            GPIO.output(self.BIN2, GPIO.LOW)
            self.PWMB.ChangeDutyCycle(left)
        elif (left < 0) and (left >= self.MIN_DUTY_CYCLE):
            GPIO.output(self.BIN1, GPIO.LOW)
            GPIO.output(self.BIN2, GPIO.HIGH)
            self.PWMB.ChangeDutyCycle(0 - left)

    def forward_with_modification(self, left, right):
        """ Fait avancé le robot, possibilité de modifier la valeur cyclique des moteurs

        Parameters
        ----------
        left : int
            Vitesse du moteur gauche
        right : int
            Vitesse du moteur droit

        """
        self.PWMA.ChangeDutyCycle(left * self.compensation_left)
        self.PWMB.ChangeDutyCycle(right * self.compensation_right)
        GPIO.output(self.AIN1, GPIO.LOW)
        GPIO.output(self.AIN2, GPIO.HIGH)
        GPIO.output(self.BIN1, GPIO.LOW)
        GPIO.output(self.BIN2, GPIO.HIGH)

    def forward(self):
        """ Fait avancer le robot
        Méthode reprise de AlphaBot2

        """
        self.PWMA.ChangeDutyCycle(self.speed * self.compensation_left)
        self.PWMB.ChangeDutyCycle(self.speed * self.compensation_right)
        GPIO.output(self.AIN1, GPIO.LOW)
        GPIO.output(self.AIN2, GPIO.HIGH)
        GPIO.output(self.BIN1, GPIO.LOW)
        GPIO.output(self.BIN2, GPIO.HIGH)

    def stop(self):
        """ Fait s'arrêter le robot
        Méthode reprise de AlphaBot2

        """
        self.PWMA.ChangeDutyCycle(0)
        self.PWMB.ChangeDutyCycle(0)
        GPIO.output(self.AIN1, GPIO.LOW)
        GPIO.output(self.AIN2, GPIO.LOW)
        GPIO.output(self.BIN1, GPIO.LOW)
        GPIO.output(self.BIN2, GPIO.LOW)

    def backward(self):
        """ Fait reculer le robot
        Méthode reprise de AlphaBot2

        """
        self.PWMA.ChangeDutyCycle(self.speed)
        self.PWMB.ChangeDutyCycle(self.speed)
        GPIO.output(self.AIN1, GPIO.HIGH)
        GPIO.output(self.AIN2, GPIO.LOW)
        GPIO.output(self.BIN1, GPIO.HIGH)
        GPIO.output(self.BIN2, GPIO.LOW)

    def left(self):
        """Fait tourner le robot vers la gauche
        Méthode reprise de AlphaBot2

        """
        self.PWMA.ChangeDutyCycle(self.speed)
        self.PWMB.ChangeDutyCycle(self.speed)
        GPIO.output(self.AIN1, GPIO.HIGH)
        GPIO.output(self.AIN2, GPIO.LOW)
        GPIO.output(self.BIN1, GPIO.LOW)
        GPIO.output(self.BIN2, GPIO.HIGH)

    def right(self):
        """Fait tourner le robot vers la droite
        Méthode reprise de la classe AlphaBot2

        """
        self.PWMA.ChangeDutyCycle(self.speed)
        self.PWMB.ChangeDutyCycle(self.speed)
        GPIO.output(self.AIN1, GPIO.LOW)
        GPIO.output(self.AIN2, GPIO.HIGH)
        GPIO.output(self.BIN1, GPIO.HIGH)
        GPIO.output(self.BIN2, GPIO.LOW)

    def change_speed(self, new_speed):
        """Permet de modifier la vitesse du robot

        Parameters
        ----------
        new_speed : int
            Nouvelle vitesse du robot

        """
        self.stop()
        self.speed = float(new_speed)

    def set_compensation(self, left, right):
        """ Défini la compensation des moteurs

        Parameters
        ----------
        left : float
            Ratio de compensation du moteur gauche
        right : float
            Ratio de compensation du moteur droit

        """
        self.stop()
        self.compensation_right = right
        self.compensation_left = left

    @staticmethod
    def gpio_cleanup():
        """
        Nettoye les GPIO

        """
        GPIO.cleanup()

    def __del__(self):
        """
        Effectué lorsque le programme s'arrête

        """
        self.gpio_cleanup()
