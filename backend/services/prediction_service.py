from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.models.person import Person, MovementHistory
from backend.models.camera import Camera, CameraTransition
from backend.models.detection import PredictionResult
from backend.services.transition_service import transition_service
from backend.utils.logger import logger

class MovementPredictionService:
    """
    Predicts the next probable camera destination using a 1st-Order Markov Chain Model.
    Clearly marks outputs as predictive estimates with probabilistic confidence.
    """
    def predict_next_camera(self, person_id: int, db: Session) -> Dict[str, Any]:
        person = db.query(Person).filter(Person.id == person_id).first()
        if not person:
            return {"error": "Person not found"}

        # Find latest movement record
        last_movement = db.query(MovementHistory).filter(
            MovementHistory.person_id == person.id
        ).order_by(MovementHistory.entry_time.desc()).first()

        if not last_movement or not last_movement.camera:
            # Fallback to CAM-01 Entrance if no history
            first_cam = db.query(Camera).filter(Camera.camera_code == "CAM-01").first()
            curr_cam_id = first_cam.id if first_cam else 1
            curr_code = first_cam.camera_code if first_cam else "CAM-01"
            curr_loc = first_cam.location if first_cam else "Main Entrance"
        else:
            curr_cam_id = last_movement.camera.id
            curr_code = last_movement.camera.camera_code
            curr_loc = last_movement.camera.location

        # Find outgoing transitions from current camera
        transitions = db.query(CameraTransition).filter(
            CameraTransition.from_camera_id == curr_cam_id
        ).all()

        candidates = []
        total_prob = sum(t.transition_probability for t in transitions) if transitions else 0.0

        for t in transitions:
            norm_p = (t.transition_probability / total_prob) if total_prob > 0 else 0.5
            target_cam = db.query(Camera).filter(Camera.id == t.to_camera_id).first()
            if target_cam:
                candidates.append({
                    "camera_id": target_cam.id,
                    "camera_code": target_cam.camera_code,
                    "name": target_cam.name,
                    "location": target_cam.location,
                    "probability": round(norm_p, 3)
                })

        candidates.sort(key=lambda x: x["probability"], reverse=True)

        if len(candidates) > 0:
            top = candidates[0]
            predicted_code = top["camera_code"]
            predicted_name = top["name"]
            predicted_loc = top["location"]
            prob = top["probability"]
            target_cam_id = top["camera_id"]
        else:
            # Fallback
            predicted_code = "CAM-04"
            predicted_name = "Lobby"
            predicted_loc = "Central Atrium Lobby"
            prob = 0.50
            target_cam_id = curr_cam_id

        # Record prediction result in database
        pred_record = PredictionResult(
            person_id=person.id,
            current_camera_id=curr_cam_id,
            predicted_camera_id=target_cam_id,
            probability=prob,
            timestamp=datetime.utcnow()
        )
        db.add(pred_record)
        db.commit()

        return {
            "person_id": person.id,
            "person_code": person.person_code,
            "full_name": person.full_name,
            "current_camera": curr_code,
            "current_location": curr_loc,
            "predicted_camera": predicted_code,
            "predicted_name": predicted_name,
            "predicted_location": predicted_loc,
            "probability": prob,
            "confidence_percentage": f"{int(prob * 100)}%",
            "all_candidates": candidates,
            "timestamp": datetime.utcnow().isoformat(),
            "disclaimer": "NOTE: This output is an algorithmic Markov-chain prediction based on resort topology and historical flows, not a certified physical observation."
        }

prediction_service = MovementPredictionService()
