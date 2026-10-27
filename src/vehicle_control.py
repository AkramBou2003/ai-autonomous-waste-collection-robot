"""Control the left and right motor pairs through an L298N."""
from __future__ import annotations
import time

try:
    import RPi.GPIO as GPIO
except ImportError:  # Allows imports/tests on non-Raspberry Pi computers.
    GPIO = None

class L298NDrive:
    def __init__(self, speed: float = 35.0, frequency: int = 100):
        if GPIO is None:
            raise RuntimeError("RPi.GPIO is available only on a compatible Raspberry Pi setup.")
        if not 0 <= speed <= 100:
            raise ValueError("speed must be between 0 and 100")
        self.speed = speed
        self.ENA, self.IN1, self.IN2 = 12, 16, 18
        self.ENB, self.IN3, self.IN4 = 13, 22, 24
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for pin in (self.ENA,self.IN1,self.IN2,self.ENB,self.IN3,self.IN4):
            GPIO.setup(pin, GPIO.OUT)
        self.left_pwm = GPIO.PWM(self.ENA, frequency)
        self.right_pwm = GPIO.PWM(self.ENB, frequency)
        self.left_pwm.start(0); self.right_pwm.start(0)
        self.stop()

    def _side(self, a: int, b: int, direction: int):
        if direction > 0:
            GPIO.output(a, GPIO.HIGH); GPIO.output(b, GPIO.LOW)
        elif direction < 0:
            GPIO.output(a, GPIO.LOW); GPIO.output(b, GPIO.HIGH)
        else:
            GPIO.output(a, GPIO.LOW); GPIO.output(b, GPIO.LOW)

    def drive(self, left: int, right: int, speed: float | None = None):
        """Set each side to -1 (reverse), 0 (stop), or 1 (forward)."""
        if left not in (-1,0,1) or right not in (-1,0,1):
            raise ValueError("left and right must be -1, 0, or 1")
        duty = self.speed if speed is None else max(0.0, min(100.0, speed))
        self._side(self.IN1,self.IN2,left); self._side(self.IN3,self.IN4,right)
        self.left_pwm.ChangeDutyCycle(duty if left else 0)
        self.right_pwm.ChangeDutyCycle(duty if right else 0)

    def forward(self): self.drive(1,1)
    def backward(self): self.drive(-1,-1)
    def turn_left(self): self.drive(-1,1)
    def turn_right(self): self.drive(1,-1)
    def stop(self): self.drive(0,0)

    def close(self):
        try: self.stop()
        finally:
            self.left_pwm.stop(); self.right_pwm.stop(); GPIO.cleanup()
