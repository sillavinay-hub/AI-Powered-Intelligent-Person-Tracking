import cv2
import numpy as np

def calculate_face_quality(face_crop: np.ndarray) -> float:
    """
    Computes face image quality metric combining:
    1. Sharpness / Blur (Laplacian variance)
    2. Illumination / Contrast (mean & std deviation)
    3. Spatial resolution (minimum pixel size)
    Returns normalized quality score [0.0, 1.0].
    """
    if face_crop is None or face_crop.size == 0:
        return 0.0

    h, w = face_crop.shape[:2]
    # Resolution score (penalize faces smaller than 64x64)
    min_dim = min(h, w)
    res_score = min(1.0, min_dim / 80.0)

    # Convert to grayscale
    if len(face_crop.shape) == 3:
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    else:
        gray = face_crop

    # Sharpness via Laplacian variance
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    # Typical sharp face has lap_var > 100
    sharpness_score = min(1.0, lap_var / 120.0)

    # Illumination score
    mean_val = float(np.mean(gray))
    if mean_val < 30.0:
        illum_score = mean_val / 30.0
    elif mean_val > 225.0:
        illum_score = max(0.0, (255.0 - mean_val) / 30.0)
    else:
        illum_score = 1.0

    # Contrast score
    std_val = float(np.std(gray))
    contrast_score = min(1.0, std_val / 40.0)

    # Weighted quality score
    quality = (0.35 * sharpness_score) + (0.30 * res_score) + (0.20 * illum_score) + (0.15 * contrast_score)
    return round(float(np.clip(quality, 0.0, 1.0)), 3)
