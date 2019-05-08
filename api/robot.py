import RPi.GPIO as GPIO


class Robot(object):
    # Repris de la classe AlphaBot2, fourni avec le robot
    _AIN1 = 12
    _AIN2 = 13
    _BIN1 = 20
    _BIN2 = 21
    _ENA = 6
    _ENB = 26

    _MAX_DUTY_CYCLE = 100
    _MIN_DUTY_CYCLE = -100

    _MARGIN_FOR_BALL = 15

    def __init__(self, speed=30):
        self.speed = speed

        # Repris de la classe AlphaBot2, fourni avec le robot
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self._AIN1, GPIO.OUT)
        GPIO.setup(self._AIN2, GPIO.OUT)
        GPIO.setup(self._BIN1, GPIO.OUT)
        GPIO.setup(self._BIN2, GPIO.OUT)
        GPIO.setup(self._ENA, GPIO.OUT)
        GPIO.setup(self._ENB, GPIO.OUT)
        self.PWMA = GPIO.PWM(self._ENA, 500)
        self.PWMB = GPIO.PWM(self._ENB, 500)
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

        if (right >= 0) and (right <= self._MAX_DUTY_CYCLE):
            GPIO.output(self._AIN1, GPIO.HIGH)
            GPIO.output(self._AIN2, GPIO.LOW)
            self.PWMA.ChangeDutyCycle(right)
        elif (right < 0) and (right >= self._MIN_DUTY_CYCLE):
            GPIO.output(self._AIN1, GPIO.LOW)
            GPIO.output(self._AIN2, GPIO.HIGH)
            self.PWMA.ChangeDutyCycle(0 - right)
        if (left >= 0) and (left <= self._MAX_DUTY_CYCLE):
            GPIO.output(self._BIN1, GPIO.HIGH)
            GPIO.output(self._BIN2, GPIO.LOW)
            self.PWMB.ChangeDutyCycle(left)
        elif (left < 0) and (left >= self._MIN_DUTY_CYCLE):
            GPIO.output(self._BIN1, GPIO.LOW)
            GPIO.output(self._BIN2, GPIO.HIGH)
            self.PWMB.ChangeDutyCycle(0 - left)

    def forward(self):
        self.PWMA.ChangeDutyCycle(self.speed)
        self.PWMB.ChangeDutyCycle(self.speed)
        GPIO.output(self._AIN1, GPIO.LOW)
        GPIO.output(self._AIN2, GPIO.HIGH)
        GPIO.output(self._BIN1, GPIO.LOW)
        GPIO.output(self._BIN2, GPIO.HIGH)

    def stop(self):
        self.PWMA.ChangeDutyCycle(0)
        self.PWMB.ChangeDutyCycle(0)
        GPIO.output(self._AIN1, GPIO.LOW)
        GPIO.output(self._AIN2, GPIO.LOW)
        GPIO.output(self._BIN1, GPIO.LOW)
        GPIO.output(self._BIN2, GPIO.LOW)

    def backward(self):
        self.PWMA.ChangeDutyCycle(self.speed)
        self.PWMB.ChangeDutyCycle(self.speed)
        GPIO.output(self._AIN1, GPIO.HIGH)
        GPIO.output(self._AIN2, GPIO.LOW)
        GPIO.output(self._BIN1, GPIO.HIGH)
        GPIO.output(self._BIN2, GPIO.LOW)

    def left(self):
        self.PWMA.ChangeDutyCycle(self.speed)
        self.PWMB.ChangeDutyCycle(self.speed)
        GPIO.output(self._AIN1, GPIO.HIGH)
        GPIO.output(self._AIN2, GPIO.LOW)
        GPIO.output(self._BIN1, GPIO.LOW)
        GPIO.output(self._BIN2, GPIO.HIGH)

    def right(self):
        self.PWMA.ChangeDutyCycle(self.speed)
        self.PWMB.ChangeDutyCycle(self.speed)
        GPIO.output(self._AIN1, GPIO.LOW)
        GPIO.output(self._AIN2, GPIO.HIGH)
        GPIO.output(self._BIN1, GPIO.HIGH)
        GPIO.output(self._BIN2, GPIO.LOW)

    def go_to_ball(self, ball_center_x):
        if ball_center_x > self._MARGIN_FOR_BALL:
            self.right()
        elif ball_center_x < -self._MARGIN_FOR_BALL:
            self.left()
        else:
            self.forward()

    def change_speed(self, new_speed):
        self.speed = float(new_speed)

    @staticmethod
    def gpio_cleanup():
        GPIO.cleanup()
