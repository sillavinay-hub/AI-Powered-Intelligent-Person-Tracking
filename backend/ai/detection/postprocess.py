import numpy as np
from typing import List, Tuple

def non_max_suppression(boxes: np.ndarray, scores: np.ndarray, iou_threshold: float = 0.45) -> List[int]:
    """
    Standard Non-Maximum Suppression (NMS) for bounding boxes.
    boxes format: [x1, y1, x2, y2]
    """
    if len(boxes) == 0:
        return []

    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = scores.argsort()[::-1]

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)

        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        inter = w * h

        ovr = inter / (areas[i] + areas[order[1:]] - inter)
        inds = np.where(ovr <= iou_threshold)[0]
        order = order[inds + 1]

    return keep

def scale_coords(boxes: np.ndarray, orig_shape: Tuple[int, int], target_shape: Tuple[int, int]) -> np.ndarray:
    """Rescale coordinates from target_shape back to orig_shape (height, width)."""
    if len(boxes) == 0:
        return boxes
    gain_y = orig_shape[0] / target_shape[0]
    gain_x = orig_shape[1] / target_shape[1]

    boxes[:, [0, 2]] *= gain_x
    boxes[:, [1, 3]] *= gain_y
    return boxes
