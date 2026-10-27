# Waste Collection Robot (2024)

This project was developed as a student project in 2024. The robot uses a Raspberry Pi 4, a camera and YOLOv3 to detect bottles. When a bottle is found, the camera image is used to guide the vehicle. Once the bottle is close enough in the image, the vehicle stops and the robotic arm follows a fixed sequence of servo angles.

The mechanical parts of the arm were designed with SolidWorks. Screenshots from the project report are in `assets/solidworks/`.

## Main parts

- `src/bottle_detection.py` - detects the COCO class `bottle` with YOLOv3 and OpenCV.
- `src/vehicle_control.py` - controls the left and right motor pairs through an L298N driver.
- `src/arm_controller.py` - controls the four arm servos with preset positions.
- `src/autonomous_robot.py` - connects camera detection, vehicle movement and the arm sequence.
- `notebooks/` - the Google Colab experiment for bottle detection.
- `docs/` - notes about the hardware and mechanical design.
- `assets/solidworks/` - images taken from the report.

## Hardware

- Raspberry Pi 4
- Raspberry Pi Camera Module V2
- Four DC motors and L298N motor driver
- Four servos: shoulder (MG995), elbow, wrist and gripper
- Robotic arm designed with SolidWorks

The pin numbers below are based on the project documentation. Check them against the actual circuit before powering the robot. Test and calibrate the software on the real robot before use.

## Bottle detection on a computer

Use Python 3.10 or 3.11. Install the packages:

```bash
python -m pip install -r requirements.txt
```

Put `yolov3.cfg`, `yolov3.weights` and `coco.names` in the `models/` folder. Then run:

```bash
python src/bottle_detection.py --image path/to/image.jpg --config models/yolov3.cfg --weights models/yolov3.weights --names models/coco.names --output output/detection.jpg
```

The model was already trained on COCO. It detects the general `bottle` class; it was not trained specifically for plastic litter.

## Running the robot code

On the Raspberry Pi, check the camera and wiring first. Test with the wheels lifted and at low speed. Keep the arm disabled until its servo angles have been checked.

```bash
python -m src.autonomous_robot --speed 20 --search-speed 15 --show
```

To run the example arm sequence after the vehicle stops:

```bash
python -m src.autonomous_robot --speed 20 --search-speed 15 --enable-arm
```

The YOLO files must be in `models/`. Use `--help` to see the available options.

## How the movement works

1. The vehicle turns slowly while searching for a bottle.
2. When YOLO detects one, the program selects the largest detected box.
3. The vehicle turns until the bottle is near the middle of the image.
4. It moves forward while the box is still small.
5. When the box reaches a set size for several frames, the vehicle stops.
6. If enabled, the arm moves through its preset positions to pick up and release the bottle.

The box size only gives a rough idea of distance. This version does not include obstacle avoidance, so tests must be supervised.

## Electrical notes

- Do not connect motors or servos directly to GPIO pins.
- Use a suitable external supply for motors and servos.
- Raspberry Pi GPIO uses 3.3 V logic.
- Keep a physical power switch accessible during tests.

## Tests

Run the simple software tests with:

```bash
python -m unittest discover -v
```

These tests do not check the physical robot.
