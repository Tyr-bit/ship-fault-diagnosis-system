# image_handler.py
from ultralytics import YOLO
import tempfile
import os
from .config import YOLO_MODEL

_model = None

def get_yolo_model():
    global _model
    if _model is None:
        _model = YOLO(YOLO_MODEL)
    return _model

def detect_objects(image_bytes, conf_threshold=0.5):
    model = get_yolo_model()
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(image_bytes)
        tmp_path = f.name
    try:
        results = model(tmp_path)
        detected = []
        for box in results[0].boxes:
            if box.conf.item() > conf_threshold:
                cls_id = int(box.cls.item())
                obj_name = results[0].names[cls_id]
                detected.append(obj_name)
        if detected:
            return f"图片中检测到: {', '.join(set(detected))}"
        else:
            return "图片中未检测到明确物体"
    finally:
        os.unlink(tmp_path)