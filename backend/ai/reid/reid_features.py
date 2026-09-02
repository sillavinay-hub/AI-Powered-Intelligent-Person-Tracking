import cv2
import numpy as np
import torch
from typing import Optional
from backend.ai.reid.reid_model import OSNetReID
from backend.config import settings
from backend.utils.logger import logger

class ReIDFeatureExtractor:
    """
    Extracts 512-dimensional deep visual features from full-body person crops
    using OSNet backbone with spatial color-partitioning.
    """
    def __init__(self, device: Optional[str] = None):
        self.device = device or settings.resolved_device
        self.model = OSNetReID(embedding_dim=512)
        self.model.eval()
        self.model.to(self.device)
        logger.info(f"Initialized OSNet ReID Feature Extractor on device: {self.device}")

    def extract(self, person_crop: np.ndarray) -> np.ndarray:
        """
        Extracts 512-D L2-normalized ReID embedding from full-body person crop.
        """
        if person_crop is None or person_crop.size == 0:
            return np.zeros(512, dtype=np.float32)

        # Standard ReID input: 256 height x 128 width
        crop_resized = cv2.resize(person_crop, (128, 256), interpolation=cv2.INTER_LINEAR)
        rgb = cv2.cvtColor(crop_resized, cv2.COLOR_BGR2RGB)

        # Normalize with ImageNet mean & std
        tensor = torch.from_numpy(rgb).permute(2, 0, 1).float() / 255.0
        mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
        tensor = (tensor - mean) / std
        tensor = tensor.unsqueeze(0).to(self.device)

        with torch.no_grad():
            emb = self.model(tensor)
            emb = emb.cpu().numpy().flatten()

        # Multi-region color stripe descriptors (upper torso, lower body)
        # Upper torso (25% to 60% height)
        upper_torso = crop_resized[64:154, :]
        lower_body = crop_resized[154:240, :]

        hsv_upper = cv2.cvtColor(upper_torso, cv2.COLOR_BGR2HSV)
        hsv_lower = cv2.cvtColor(lower_body, cv2.COLOR_BGR2HSV)

        hist_up = cv2.calcHist([hsv_upper], [0, 1], None, [8, 8], [0, 180, 0, 256]).flatten()
        hist_low = cv2.calcHist([hsv_lower], [0, 1], None, [8, 8], [0, 180, 0, 256]).flatten()

        spatial_feat = np.concatenate([hist_up, hist_low])
        spatial_feat = spatial_feat / (np.linalg.norm(spatial_feat) + 1e-6)

        # Blend first 128 elements with spatial color histogram
        emb[:128] = 0.6 * emb[:128] + 0.4 * spatial_feat
        # Re-normalize to unit length
        emb = emb / (np.linalg.norm(emb) + 1e-6)

        return emb.astype(np.float32)

# Global singleton
reid_extractor = ReIDFeatureExtractor()
