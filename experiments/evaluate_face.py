#!/usr/bin/env python3
import sys
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.ai.face.recognition import FaceRecognitionEngine

def main():
    print("Evaluating ArcFace Biometric Module...")
    engine = FaceRecognitionEngine(device="cpu")
    
    np.random.seed(42)
    # Generate mock faces and embeddings
    ref_face = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
    emb_ref = engine.generate_face_embedding(ref_face)

    # Identical image
    sim_same, conf_same, status_same = engine.compare_face_embeddings(emb_ref, emb_ref)
    print(f"Self-similarity test: score={sim_same:.4f}, status={status_same}")

    # Random different image
    diff_face = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
    emb_diff = engine.generate_face_embedding(diff_face)
    sim_diff, conf_diff, status_diff = engine.compare_face_embeddings(emb_ref, emb_diff)
    print(f"Disjoint identity test: score={sim_diff:.4f}, status={status_diff}")

    assert sim_same > 0.99, "Self-similarity must be ~1.0"
    assert sim_diff < 0.70, "Disjoint embeddings must have lower similarity"
    print("Face recognition evaluation: PASSED")

if __name__ == "__main__":
    main()
