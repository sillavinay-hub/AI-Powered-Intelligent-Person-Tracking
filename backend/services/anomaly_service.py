import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.models.alert import Alert
from backend.models.camera import Camera
from backend.models.person import Person
from backend.utils.logger import logger

RESTRICTED_CAMERAS = ["CAM-22"] # Service Entrance / Kitchen Staff Only

class AnomalyDetectionService:
    """
    Configurable Rule-Based Anomaly Detection Module.
    Monitors detections and creates structured alerts without subjective prejudice.
    """
    def check_detection_anomaly(
        self,
        camera_code: str,
        person_id: Optional[int],
        dwell_duration_sec: float,
        confidence: float,
        db: Session
    ) -> Optional[Alert]:
        cam = db.query(Camera).filter(Camera.camera_code == camera_code).first()
        if not cam:
            return None

        now = datetime.utcnow()
        recent_threshold = now - timedelta(seconds=60)
        existing_alert = db.query(Alert).filter(
            Alert.camera_id == cam.id,
            Alert.status == "NEW",
            Alert.timestamp >= recent_threshold
        ).first()
        if existing_alert:
            return None

        alert = None

        # Rule 1: Restricted Zone Access
        if camera_code in RESTRICTED_CAMERAS:
            alert = Alert(
                alert_type="RESTRICTED_ZONE",
                person_id=person_id,
                camera_id=cam.id,
                timestamp=now,
                confidence=0.92,
                status="NEW",
                details_json=json.dumps({
                    "rule": "Restricted Zone Access Violation",
                    "zone_name": cam.name,
                    "description": f"Target individual entered authorized-staff-only zone ({cam.location}).",
                    "severity": "HIGH"
                })
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)
            logger.warning(f"ALERT: Restricted Zone breach detected at {camera_code} by person {person_id}")
            return alert

        # Rule 2: Loitering Detection (> 300 seconds stationary/dwell)
        if dwell_duration_sec > 300.0 and camera_code in ["CAM-02", "CAM-21", "CAM-13", "CAM-14"]:
            alert = Alert(
                alert_type="LOITERING",
                person_id=person_id,
                camera_id=cam.id,
                timestamp=now,
                confidence=0.85,
                status="NEW",
                details_json=json.dumps({
                    "rule": "Extended Stationary Loitering",
                    "dwell_seconds": dwell_duration_sec,
                    "zone_name": cam.name,
                    "description": f"Target individual remained stationary for {int(dwell_duration_sec)}s exceeding the 300s limit.",
                    "severity": "MEDIUM"
                })
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)
            return alert

        # Rule 3: Unusual Hours (e.g. Swimming Pool between 22:00 and 06:00)
        if camera_code in ["CAM-07", "CAM-08"] and (now.hour >= 22 or now.hour < 6):
            alert = Alert(
                alert_type="UNUSUAL_TIME",
                person_id=person_id,
                camera_id=cam.id,
                timestamp=now,
                confidence=0.88,
                status="NEW",
                details_json=json.dumps({
                    "rule": "After-Hours Facility Access",
                    "zone_name": cam.name,
                    "description": f"Presence detected in pool facility during closed operational hours ({now.strftime('%H:%M')}).",
                    "severity": "MEDIUM"
                })
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)
            return alert

        return None

    def get_all_alerts(self, db: Session, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        query = db.query(Alert).order_by(Alert.timestamp.desc())
        if status_filter:
            query = query.filter(Alert.status == status_filter.upper())
        alerts = query.limit(100).all()
        return [a.to_dict() for a in alerts]

    def update_alert_status(self, alert_id: int, new_status: str, db: Session) -> Dict[str, Any]:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return {"error": "Alert not found"}
        alert.status = new_status.upper()
        db.commit()
        db.refresh(alert)
        return alert.to_dict()

anomaly_service = AnomalyDetectionService()
