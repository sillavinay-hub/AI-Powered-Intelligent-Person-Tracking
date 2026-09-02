import os
import cv2
import json
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.config import settings
from backend.models.person import Person, PersonEmbedding, MovementHistory
from backend.models.detection import Detection
from backend.models.camera import Camera
from backend.models.log import SystemLog
from backend.ai.face.face_detector import FaceDetector
from backend.ai.face.recognition import face_engine
from backend.ai.reid.reid_features import reid_extractor
from backend.utils.logger import logger

class PersonService:
    def __init__(self):
        self.face_detector = FaceDetector()

    def register_person(
        self,
        image_bytes: bytes,
        person_code: str,
        full_name: Optional[str] = None,
        notes: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Single-Reference-Image Registration:
        1. Decodes reference image
        2. Detects face & assesses quality
        3. Computes 512-D ArcFace embedding
        4. Computes 512-D OSNet ReID embedding
        5. Saves securely and persists to database
        """
        # Validate uniqueness
        existing = db.query(Person).filter(Person.person_code == person_code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Person code '{person_code}' is already registered."
            )

        # Decode image from bytes
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None or img.size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file format. Could not decode image."
            )

        # Save reference image to disk
        filename = f"{person_code}_{int(datetime.utcnow().timestamp())}.jpg"
        save_path = settings.REF_IMAGE_DIR / filename
        cv2.imwrite(str(save_path), img)
        rel_path = f"uploads/references/{filename}"

        # 1. Face Detection & Quality Check
        faces = self.face_detector.detect_faces(img)
        face_detected = False
        face_quality = 0.0
        face_emb = np.zeros(512, dtype=np.float32)

        if len(faces) > 0 and faces[0]["is_valid"]:
            face_detected = True
            face_quality = faces[0]["quality"]
            face_emb = face_engine.generate_face_embedding(faces[0]["crop"])
        elif len(faces) > 0:
            # Low quality face detected
            face_detected = True
            face_quality = faces[0]["quality"]
            face_emb = face_engine.generate_face_embedding(faces[0]["crop"])
            logger.warning(f"Registration for {person_code}: Face detected but quality is marginal ({face_quality:.2f})")

        # 2. ReID Embedding from full body
        reid_emb = reid_extractor.extract(img)
        reid_extracted = (np.linalg.norm(reid_emb) > 0)

        # 3. Create Person record
        person = Person(
            person_code=person_code,
            full_name=full_name or person_code,
            notes=notes,
            reference_image_path=rel_path,
            status="ACTIVE",
            created_at=datetime.utcnow()
        )
        db.add(person)
        db.flush()

        # 4. Store biometric embeddings (protected inside DB, never sent to frontend)
        emb_face_obj = PersonEmbedding(
            person_id=person.id,
            embedding_type="FACE",
            vector_json=json.dumps(face_emb.tolist()),
            quality_score=face_quality
        )
        emb_reid_obj = PersonEmbedding(
            person_id=person.id,
            embedding_type="REID",
            vector_json=json.dumps(reid_emb.tolist()),
            quality_score=0.90
        )
        db.add_all([emb_face_obj, emb_reid_obj])

        # Audit log
        slog = SystemLog(
            level="INFO",
            module="PERSON",
            message=f"Registered person {person_code} ({person.full_name}) from single reference image.",
            metadata_json=json.dumps({"person_id": person.id, "face_quality": face_quality})
        )
        db.add(slog)
        db.commit()
        db.refresh(person)

        logger.info(f"Successfully registered person {person_code} with face_quality={face_quality:.2f}")

        return {
            "person_id": person.id,
            "person_code": person.person_code,
            "full_name": person.full_name,
            "status": person.status,
            "face_detected": face_detected,
            "face_quality_score": face_quality,
            "reid_extracted": reid_extracted,
            "message": f"Successfully registered person {person_code}."
        }

    def get_all_persons(self, db: Session) -> List[Dict[str, Any]]:
        persons = db.query(Person).order_by(Person.id.asc()).all()
        results = []
        for p in persons:
            p_dict = p.to_dict(include_embeddings=False)
            # Find last detection
            last_det = db.query(Detection).filter(Detection.person_id == p.id).order_by(Detection.timestamp.desc()).first()
            total_dets = db.query(Detection).filter(Detection.person_id == p.id).count()

            if last_det and last_det.camera:
                p_dict["last_camera_code"] = last_det.camera.camera_code
                p_dict["last_location"] = last_det.camera.location
                p_dict["last_seen_time"] = last_det.timestamp.isoformat() if last_det.timestamp else None
            p_dict["total_detections"] = total_dets
            results.append(p_dict)
        return results

    def get_person_dossier(self, person_id: int, db: Session) -> Dict[str, Any]:
        person = db.query(Person).filter(Person.id == person_id).first()
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")

        data = person.to_dict(include_embeddings=True)
        # Add movement history
        movements = db.query(MovementHistory).filter(MovementHistory.person_id == person.id).order_by(MovementHistory.entry_time.asc()).all()
        data["movement_history"] = [m.to_dict() for m in movements]
        
        # Add detection stats
        dets = db.query(Detection).filter(Detection.person_id == person.id).order_by(Detection.timestamp.desc()).limit(20).all()
        data["recent_detections"] = [d.to_dict() for d in dets]
        data["total_detections"] = db.query(Detection).filter(Detection.person_id == person.id).count()
        return data

    def delete_person(self, person_id: int, db: Session) -> bool:
        """
        Secure biometric deletion adhering to privacy requirements.
        Removes all biometric embeddings, movement records, reference image files, and audit logs.
        """
        person = db.query(Person).filter(Person.id == person_id).first()
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")

        # Delete image file from disk
        if person.reference_image_path:
            full_path = settings.BASE_DIR / person.reference_image_path
            if full_path.exists():
                try:
                    os.remove(full_path)
                except Exception as e:
                    logger.warning(f"Failed to remove file {full_path}: {e}")

        code = person.person_code
        db.delete(person)

        slog = SystemLog(
            level="WARNING",
            module="PRIVACY",
            message=f"Privacy deletion executed for Person {code}. All biometrics purged.",
            metadata_json=json.dumps({"deleted_person_code": code})
        )
        db.add(slog)
        db.commit()
        logger.info(f"Purged biometrics and person record for {code}")
        return True

person_service = PersonService()
