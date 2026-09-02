from pydantic import BaseModel

class DetectionConfig(BaseModel):
    confidence_threshold: float = 0.45
    iou_threshold: float = 0.45
    target_class_id: int = 0  # COCO class 0 is 'person'
    input_size: tuple = (640, 640)
    device: str = "cpu"
    max_detections: int = 50
