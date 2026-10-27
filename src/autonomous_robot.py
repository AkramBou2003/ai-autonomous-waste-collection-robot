"""Camera-guided bottle approach and preset arm movement."""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2

try:
    from .bottle_detection import load_classes, load_yolo, detect_bottles, annotate_image
    from .vehicle_control import L298NDrive
except ImportError:
    from bottle_detection import load_classes, load_yolo, detect_bottles, annotate_image
    from vehicle_control import L298NDrive


def parse_args():
    parser = argparse.ArgumentParser(description="Camera-guided bottle collection demo")
    parser.add_argument('--config', default='models/yolov3.cfg')
    parser.add_argument('--weights', default='models/yolov3.weights')
    parser.add_argument('--names', default='models/coco.names')
    parser.add_argument('--camera', type=int, default=0, help='OpenCV camera index')
    parser.add_argument('--confidence', type=float, default=0.50)
    parser.add_argument('--center-tolerance', type=float, default=0.12,
                        help='Allowed horizontal error as a fraction of image width')
    parser.add_argument('--target-area', type=float, default=0.12,
                        help='Stop threshold: bounding-box area / frame area; calibrate experimentally')
    parser.add_argument('--speed', type=float, default=25, help='Forward/turn motor PWM duty cycle, 0..100')
    parser.add_argument('--search-speed', type=float, default=18,
                        help='Low PWM duty cycle while searching, 0..100')
    parser.add_argument('--confirm-frames', type=int, default=3,
                        help='Consecutive near-target frames required before pickup')
    parser.add_argument('--enable-arm', action='store_true',
                        help='Run the example fixed-angle arm sequence after stopping')
    parser.add_argument('--show', action='store_true', help='Display preview; requires a GUI')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not 0 <= args.speed <= 100 or not 0 <= args.search_speed <= 100:
        raise ValueError('Motor speeds must be between 0 and 100.')
    if args.confirm_frames < 1:
        raise ValueError('--confirm-frames must be at least 1.')
    if not 0 < args.target_area < 1:
        raise ValueError('--target-area must be between 0 and 1.')

    for file in (args.config, args.weights, args.names):
        if not Path(file).is_file():
            raise FileNotFoundError(f'Missing model file: {file}. See models/README.md')

    net = load_yolo(args.config, args.weights)
    classes = load_classes(args.names)
    camera = cv2.VideoCapture(args.camera)
    if not camera.isOpened():
        raise RuntimeError('Could not open camera. Check the camera connection and --camera index.')

    drive = None
    arm = None
    close_frames = 0
    try:
        drive = L298NDrive(speed=args.speed)
        if args.enable_arm:
            try:
                from .arm_controller import ServoArm
            except ImportError:
                from arm_controller import ServoArm
            arm = ServoArm()

        print('Camera-guided demo running. Stop with Ctrl+C; q also works with --show.')
        print('Safety note: no obstacle avoidance is implemented; supervise continuously.')
        while True:
            ok, frame = camera.read()
            if not ok or frame is None:
                drive.stop()
                raise RuntimeError('Camera frame unavailable; motors stopped.')

            height, width = frame.shape[:2]
            detections = detect_bottles(frame, net, classes, args.confidence)
            status = 'SEARCHING'

            if not detections:
                close_frames = 0
                drive.drive(-1, 1, speed=args.search_speed)
                status = 'SEARCHING - slow rotation (no obstacle sensing)'
            else:
                target = max(detections, key=lambda d: d['width'] * d['height'])
                center_x = target['x'] + target['width'] / 2
                area_ratio = (target['width'] * target['height']) / (width * height)
                horizontal_error = (center_x - width / 2) / width

                if area_ratio >= args.target_area:
                    drive.stop()
                    close_frames += 1
                    status = f'TARGET NEAR - confirming {close_frames}/{args.confirm_frames}'
                    if close_frames >= args.confirm_frames:
                        if arm is not None:
                            print('Target threshold reached; running preset arm sequence.')
                            arm.pickup_and_drop_demo()
                            print('Preset sequence complete. Robot stopped for inspection.')
                        else:
                            print('Target threshold reached. Vehicle stopped; arm disabled.')
                        break
                else:
                    close_frames = 0
                    if horizontal_error < -args.center_tolerance:
                        drive.drive(-1, 1, speed=args.speed)
                        status = 'ALIGNING LEFT'
                    elif horizontal_error > args.center_tolerance:
                        drive.drive(1, -1, speed=args.speed)
                        status = 'ALIGNING RIGHT'
                    else:
                        drive.forward()
                        status = 'APPROACHING BOTTLE'

            preview = annotate_image(frame, detections)
            cv2.putText(preview, status, (10, 28), cv2.FONT_HERSHEY_SIMPLEX,
                        0.55, (0, 255, 255), 2, cv2.LINE_AA)
            if args.show:
                cv2.imshow('Waste collection robot - press q to stop', preview)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            time.sleep(0.05)
    except KeyboardInterrupt:
        print('Interrupted by operator.')
    finally:
        if arm is not None:
            # The drive controller performs the shared GPIO cleanup afterward.
            arm.close(cleanup=(drive is None))
        if drive is not None:
            drive.close()
        camera.release()
        cv2.destroyAllWindows()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
