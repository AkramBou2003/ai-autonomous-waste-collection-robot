# Electronics

The report lists the following components:

- Raspberry Pi 4
- Raspberry Pi Camera Module V2
- L298N motor driver
- Four DC motors
- Four servos for the arm

## GPIO pins recorded in the report

| Part | Signal | BCM GPIO |
|---|---|---:|
| L298N | ENA | 12 |
| L298N | IN1 | 16 |
| L298N | IN2 | 18 |
| L298N | ENB | 13 |
| L298N | IN3 | 22 |
| L298N | IN4 | 24 |
| Shoulder (MG995) | Servo | 5 |
| Elbow | Servo | 6 |
| Wrist | Servo | 19 |
| Gripper | Servo | 26 |

The report mentions a 12 V supply for the L298N. Check the actual circuit and motor specifications before connecting power. These pin assignments are transcribed from the report and have not been checked against a live robot.

## Important

- Do not power motors or servos directly from Raspberry Pi GPIO.
- Use a suitable external supply for the servos and motors.
- Connect grounds as required for the control signals.
- GPIO pins use 3.3 V logic and are not 5 V tolerant.
- Test with the wheels lifted and the arm unloaded first.
- Keep a physical power switch within reach.

The camera module is connected to the Raspberry Pi camera connector. The Python code can also be tested with a USB camera supported by OpenCV.
