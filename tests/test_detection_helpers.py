"""Small tests for pure helper functions; these do not require YOLO weights."""
import tempfile
import unittest
from pathlib import Path

from src.bottle_detection import load_classes, get_output_layer_names


class FakeNet:
    def getLayerNames(self):
        return ["conv_1", "yolo_1", "conv_2", "yolo_2"]

    def getUnconnectedOutLayers(self):
        return [[2], [4]]


class DetectionHelperTests(unittest.TestCase):
    def test_load_classes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "classes.names"
            path.write_text("person\nbottle\n", encoding="utf-8")
            self.assertEqual(load_classes(path), ["person", "bottle"])

    def test_output_layer_names(self):
        self.assertEqual(get_output_layer_names(FakeNet()), ["yolo_1", "yolo_2"])


if __name__ == "__main__":
    unittest.main()
