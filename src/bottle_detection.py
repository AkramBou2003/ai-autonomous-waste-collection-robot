"""Detect bottles in an image with YOLOv3 and OpenCV."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import cv2
import numpy as np


def load_classes(names_path: str | Path) -> list[str]:
    """Load one class name per line."""
    path = Path(names_path)
    if not path.is_file():
        raise FileNotFoundError(f"Class names file not found: {path}")
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_yolo(config_path: str | Path, weights_path: str | Path) -> cv2.dnn_Net:
    """Load a YOLO network from configuration and weights files."""
    config_path, weights_path = Path(config_path), Path(weights_path)
    if not config_path.is_file():
        raise FileNotFoundError(f"YOLO config not found: {config_path}")
    if not weights_path.is_file():
        raise FileNotFoundError(f"YOLO weights not found: {weights_path}")
    return cv2.dnn.readNetFromDarknet(str(config_path), str(weights_path))


def get_output_layer_names(net: cv2.dnn_Net) -> list[str]:
    """Get the YOLO output layer names."""
    layer_names = net.getLayerNames()
    indices = np.asarray(net.getUnconnectedOutLayers()).flatten()
    return [layer_names[int(index) - 1] for index in indices]


def detect_bottles(
    image: np.ndarray,
    net: cv2.dnn_Net,
    classes: list[str],
    confidence_threshold: float = 0.50,
    nms_threshold: float = 0.40,
    input_size: tuple[int, int] = (416, 416),
) -> list[dict[str, Any]]:
    """Return detected bottles and their positions in the image."""
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("Input image is empty or was not loaded correctly.")
    if not 0 <= confidence_threshold <= 1:
        raise ValueError("confidence_threshold must be between 0 and 1.")
    if not 0 <= nms_threshold <= 1:
        raise ValueError("nms_threshold must be between 0 and 1.")
    if "bottle" not in classes:
        raise ValueError("The provided class list does not contain 'bottle'.")

    height, width = image.shape[:2]
    blob = cv2.dnn.blobFromImage(
        image, scalefactor=1 / 255.0, size=input_size,
        mean=(0, 0, 0), swapRB=True, crop=False
    )
    net.setInput(blob)
    outputs = net.forward(get_output_layer_names(net))

    bottle_class_id = classes.index("bottle")
    boxes: list[list[int]] = []
    confidences: list[float] = []

    for output in outputs:
        for detection in output:
            if len(detection) <= 5 + bottle_class_id:
                continue
            objectness = float(detection[4])
            class_score = float(detection[5 + bottle_class_id])
            confidence = objectness * class_score
            if confidence < confidence_threshold:
                continue

            center_x = int(float(detection[0]) * width)
            center_y = int(float(detection[1]) * height)
            box_width = int(float(detection[2]) * width)
            box_height = int(float(detection[3]) * height)
            x = max(0, int(center_x - box_width / 2))
            y = max(0, int(center_y - box_height / 2))
            box_width = max(0, min(box_width, width - x))
            box_height = max(0, min(box_height, height - y))
            if box_width == 0 or box_height == 0:
                continue

            boxes.append([x, y, box_width, box_height])
            confidences.append(confidence)

    if not boxes:
        return []

    indices = cv2.dnn.NMSBoxes(boxes, confidences, confidence_threshold, nms_threshold)
    kept = np.asarray(indices).flatten().astype(int).tolist() if len(indices) else []

    detections: list[dict[str, Any]] = []
    for index in kept:
        x, y, box_width, box_height = boxes[index]
        detections.append({
            "label": "bottle",
            "x": x,
            "y": y,
            "width": box_width,
            "height": box_height,
            "confidence": confidences[index],
        })
    return detections


def annotate_image(image: np.ndarray, detections: list[dict[str, Any]]) -> np.ndarray:
    """Return a copy of the image with detection boxes and scores."""
    annotated = image.copy()
    for detection in detections:
        x, y = detection["x"], detection["y"]
        w, h = detection["width"], detection["height"]
        score = detection["confidence"] * 100
        cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(
            annotated, f'{detection["label"]}: {score:.1f}%',
            (x, max(20, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
            (0, 255, 0), 2, cv2.LINE_AA
        )
    return annotated


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect bottles in a still image using YOLOv3.")
    parser.add_argument("--image", required=True, help="Path to the input image.")
    parser.add_argument("--config", required=True, help="Path to yolov3.cfg.")
    parser.add_argument("--weights", required=True, help="Path to yolov3.weights.")
    parser.add_argument("--names", required=True, help="Path to coco.names.")
    parser.add_argument("--output", default="output/detection.jpg", help="Output image path.")
    parser.add_argument("--confidence", type=float, default=0.50, help="Confidence threshold (0-1).")
    parser.add_argument("--nms", type=float, default=0.40, help="NMS threshold (0-1).")
    args = parser.parse_args()

    image = cv2.imread(args.image)
    if image is None:
        raise FileNotFoundError(f"Could not read input image: {args.image}")

    classes = load_classes(args.names)
    net = load_yolo(args.config, args.weights)
    detections = detect_bottles(image, net, classes, args.confidence, args.nms)
    annotated = annotate_image(image, detections)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output_path), annotated):
        raise OSError(f"Could not write output image: {output_path}")

    print(f"Detected {len(detections)} bottle(s).")
    for number, detection in enumerate(detections, start=1):
        print(
            f'{number}. {detection["label"]} '
            f'confidence={detection["confidence"]:.3f} '
            f'box=({detection["x"]}, {detection["y"]}, '
            f'{detection["width"]}, {detection["height"]})'
        )
    print(f"Saved annotated image to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
