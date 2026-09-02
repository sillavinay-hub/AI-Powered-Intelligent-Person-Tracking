import csv
import io
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.models.person import Person, MovementHistory
from backend.models.camera import Camera
from backend.models.alert import Alert
from backend.models.detection import Detection

class ExportService:
    @staticmethod
    def export_timeline_csv(person_code: str, db: Session) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ResortVision AI - Person Movement Timeline Export"])
        writer.writerow(["Export Timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")])
        writer.writerow(["Person Code", person_code])
        writer.writerow([])
        writer.writerow(["Event ID", "Camera Code", "Camera Name", "Location", "Entry Time", "Exit Time", "Dwell (s)", "Match Confidence"])

        person = db.query(Person).filter(Person.person_code == person_code.upper()).first()
        if person:
            movements = db.query(MovementHistory).filter(MovementHistory.person_id == person.id).order_by(MovementHistory.entry_time.asc()).all()
            for m in movements:
                writer.writerow([
                    m.id,
                    m.camera.camera_code if m.camera else "",
                    m.camera.name if m.camera else "",
                    m.camera.location if m.camera else "",
                    m.entry_time.strftime("%Y-%m-%d %H:%M:%S") if m.entry_time else "",
                    m.exit_time.strftime("%Y-%m-%d %H:%M:%S") if m.exit_time else "",
                    int(m.duration_sec),
                    f"{int(m.confidence * 100)}%"
                ])

        return output.getvalue()

    @staticmethod
    def export_alerts_csv(db: Session) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ResortVision AI - Security Alerts Audit Log Export"])
        writer.writerow(["Export Timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")])
        writer.writerow([])
        writer.writerow(["Alert ID", "Alert Type", "Status", "Person Code", "Camera Code", "Location", "Timestamp", "Confidence"])

        alerts = db.query(Alert).order_by(Alert.timestamp.desc()).all()
        for a in alerts:
            writer.writerow([
                a.id,
                a.alert_type,
                a.status,
                a.person.person_code if a.person else "UNKNOWN",
                a.camera.camera_code if a.camera else "",
                a.camera.location if a.camera else "",
                a.timestamp.strftime("%Y-%m-%d %H:%M:%S") if a.timestamp else "",
                f"{int(a.confidence * 100)}%"
            ])

        return output.getvalue()

export_service = ExportService()
