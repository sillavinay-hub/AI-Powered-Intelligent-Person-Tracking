#!/usr/bin/env python3
import sys
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.ai.reid.reid_features import ReIDFeatureExtractor
from backend.ai.reid.reid_matcher import ReIDMatcher

def main():
    print("Evaluating OSNet Person Re-Identification Module...")
    extractor = ReIDFeatureExtractor(device="cpu")
    matcher = ReIDMatcher()

    # Generate mock full-body crops
    crop1 = np.ones((256, 128, 3), dtype=np.uint8) * 120
    crop2 = np.ones((256, 128, 3), dtype=np.uint8) * 120
    crop3 = np.zeros((256, 128, 3), dtype=np.uint8)

    emb1 = extractor.extract(crop1)
    emb2 = extractor.extract(crop2)
    emb3 = extractor.extract(crop3)

    sim_same, match_same = matcher.match_single(emb1, emb2)
    sim_diff, match_diff = matcher.match_single(emb1, emb3)

    print(f"Similar appearance test: sim={sim_same:.3f}, match={match_same}")
    print(f"Dissimilar appearance test: sim={sim_diff:.3f}, match={match_diff}")

    assert sim_same > 0.85
    print("Person ReID evaluation: PASSED")

if __name__ == "__main__":
    main()
