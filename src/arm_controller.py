"""Control the four servos of the robotic arm."""
from __future__ import annotations
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

class ServoArm:
    PINS = {"shoulder": 5, "elbow": 6, "wrist": 19, "gripper": 26}
    # Replace these values after testing each joint with the arm unloaded.
    POSE_HOME = {"shoulder": 90, "elbow": 90, "wrist": 90, "gripper": 30}
    POSE_APPROACH = {"shoulder": 65, "elbow": 115, "wrist": 90, "gripper": 30}
    POSE_GRAB = {"shoulder": 60, "elbow": 125, "wrist": 85, "gripper": 75}
    POSE_DROP = {"shoulder": 110, "elbow": 80, "wrist": 90, "gripper": 75}

    def __init__(self, frequency=50):
        if GPIO is None: raise RuntimeError("RPi.GPIO requires a compatible Raspberry Pi.")
        GPIO.setmode(GPIO.BCM); GPIO.setwarnings(False)
        self.pwms = {}
        for joint,pin in self.PINS.items():
            GPIO.setup(pin,GPIO.OUT); pwm=GPIO.PWM(pin,frequency); pwm.start(0); self.pwms[joint]=pwm

    def set_angle(self, joint, angle):
        if joint not in self.pwms: raise ValueError(f"Unknown joint: {joint}")
        if not 0 <= angle <= 180: raise ValueError("Angle must be 0..180")
        duty=2.5+(angle/180.0)*10.0
        self.pwms[joint].ChangeDutyCycle(duty)

    def pose(self, positions, pause=0.8):
        for joint,angle in positions.items(): self.set_angle(joint,angle)
        import time; time.sleep(pause)

    def pickup_and_drop_demo(self):
        """Run the preset pickup and release sequence."""
        self.pose(self.POSE_APPROACH); self.pose(self.POSE_GRAB)
        self.pose(self.POSE_DROP); self.set_angle("gripper",30)
        self.pose(self.POSE_HOME)

    def close(self, cleanup=True):
        for pwm in self.pwms.values():
            pwm.stop()
        if cleanup:
            GPIO.cleanup()
