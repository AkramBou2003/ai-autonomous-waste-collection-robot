# Tests and limitations

The code follows this sequence:

1. Read an image from the camera.
2. Use pretrained YOLOv3 to find the COCO `bottle` class.
3. Select the largest bottle box.
4. Turn the vehicle to bring the bottle near the image centre.
5. Move forward until the box reaches a chosen size.
6. Stop and, if enabled, run the preset arm sequence.

The COCO model detects bottles in general and does not determine whether an object is recyclable or safe to collect. Bounding-box size is only an approximate indication of distance. The arm angles need to be calibrated on the actual mechanism, and the complete system should be tested on the robot before operation.

## Test steps

1. Test the detection script on a saved image.
2. Check the camera on the Raspberry Pi.
3. Test each motor with the wheels lifted.
4. Check each servo separately with the arm unloaded.
5. Test turning and approach at low speed, with the arm disabled.
6. Adjust the stop threshold for the camera and bottle being used.
7. Test the arm sequence only after checking the angles.

Do not leave the robot running without supervision. This version has no obstacle avoidance.
