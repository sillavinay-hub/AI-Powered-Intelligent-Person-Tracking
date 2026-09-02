import numpy as np
from typing import List, Dict, Any, Tuple
from backend.config import settings

class ReIDMatcher:
    """
    Person Re-Identification Matcher using Cosine Similarity Metric.
    Supports 1-to-1 comparison and 1-to-N gallery ranking (Rank-1, Rank-5).
    """
    @staticmethod
    def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
        v1_norm = np.linalg.norm(v1)
        v2_norm = np.linalg.norm(v2)
        if v1_norm == 0 or v2_norm == 0:
            return 0.0
        sim = float(np.dot(v1, v2) / (v1_norm * v2_norm))
        # Map from [-1, 1] to [0, 1]
        return max(0.0, min(1.0, (sim + 1.0) / 2.0))

    @classmethod
    def match_single(cls, reference_emb: np.ndarray, detected_emb: np.ndarray) -> Tuple[float, bool]:
        """
        Compares single reference embedding with detected candidate embedding.
        Returns: (similarity_score, is_match)
        """
        sim = cls.cosine_similarity(reference_emb, detected_emb)
        is_match = (sim >= settings.REID_THRESHOLD)
        return round(sim, 3), is_match

    @classmethod
    def rank_gallery(cls, query_emb: np.ndarray, gallery: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ranks gallery candidates by similarity to query embedding.
        Each gallery item is a dict with 'person_id', 'person_code', 'embedding'.
        """
        results = []
        for item in gallery:
            emb = np.array(item["embedding"], dtype=float)
            score = cls.cosine_similarity(query_emb, emb)
            results.append({
                "person_id": item.get("person_id"),
                "person_code": item.get("person_code"),
                "similarity": round(score, 3),
                "is_match": (score >= settings.REID_THRESHOLD)
            })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results

reid_matcher = ReIDMatcher()
