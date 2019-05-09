import RPi.GPIO as GPIO


class Robot(object):
    # Repris de la classe AlphaBot2, fourni avec le robot
    AIN1 = 12
    AIN2 = 13
    BIN1 = 20
    BIN2 = 21
    ENA = 6
    ENB = 26

    MAX_DUTY_CYCLE = 100
    MIN_DUTY_CYCLE = -100

    def __init__(self, speed=30):
        self.speed = speed

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
        """
        Méthodes fournis par les créateurs d'AlphaBot2
        Permet de changer le rapport cyclique de chaque roue
        :param left: Valeur du rapport cyclique de la roue gauche
        :param right: Valeur du rapport cyclique de la roue droite
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

    def forward(self):
        """
        Code repris de la classe AlphaBot2
        Fait avancer le robot
        """
        self.PWMA.ChangeDutyCycle(self.speed)
        self.PWMB.ChangeDutyCycle(self.speed)
        GPIO.output(self.AIN1, GPIO.LOW)
        GPIO.output(self.AIN2, GPIO.HIGH)
        GPIO.output(self.BIN1, GPIO.LOW)
        GPIO.output(self.BIN2, GPIO.HIGH)

    def stop(self):
        """
        Code repris de la classe AlphaBot2
        Fait s'arrêter le robot
        """
        self.PWMA.ChangeDutyCycle(0)
        self.PWMB.ChangeDutyCycle(0)
        GPIO.output(self.AIN1, GPIO.LOW)
        GPIO.output(self.AIN2, GPIO.LOW)
        GPIO.output(self.BIN1, GPIO.LOW)
        GPIO.output(self.BIN2, GPIO.LOW)

    def backward(self):
        """
        Code repris de la classe AlphaBot2
        Fait reculer le robot
        """
        self.PWMA.ChangeDutyCycle(self.speed)
        self.PWMB.ChangeDutyCycle(self.speed)
        GPIO.output(self.AIN1, GPIO.HIGH)
        GPIO.output(self.AIN2, GPIO.LOW)
        GPIO.output(self.BIN1, GPIO.HIGH)
        GPIO.output(self.BIN2, GPIO.LOW)

    def left(self):
        """
        Code repris de la classe AlphaBot2
        Fait tourner le robot vers la gauche
        """
        self.PWMA.ChangeDutyCycle(self.speed)
        self.PWMB.ChangeDutyCycle(self.speed)
        GPIO.output(self.AIN1, GPIO.HIGH)
        GPIO.output(self.AIN2, GPIO.LOW)
        GPIO.output(self.BIN1, GPIO.LOW)
        GPIO.output(self.BIN2, GPIO.HIGH)

    def right(self):
        """
        Code repris de la classe AlphaBot2
        Fait tourner le robot vers la droite
        """
        self.PWMA.ChangeDutyCycle(self.speed)
        self.PWMB.ChangeDutyCycle(self.speed)
        GPIO.output(self.AIN1, GPIO.LOW)
        GPIO.output(self.AIN2, GPIO.HIGH)
        GPIO.output(self.BIN1, GPIO.HIGH)
        GPIO.output(self.BIN2, GPIO.LOW)

    def change_speed(self, new_speed):
        """
        Permet de modifier la vitesse du robot
        :param new_speed: Nouvelle valeur de la vitesse
        """
        self.speed = float(new_speed)

    @staticmethod
    def gpio_cleanup():
        """
        Nettoye les GPIO
        """
        GPIO.cleanup()
