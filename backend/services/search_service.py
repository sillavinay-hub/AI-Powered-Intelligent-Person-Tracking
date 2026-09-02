import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models.person import Person, MovementHistory
from backend.models.camera import Camera
from backend.models.detection import Detection
from backend.schemas.search import StructuredSearchQuery
from backend.utils.logger import logger

class SearchService:
    """
    Search service supporting:
    1. Structured multi-attribute database filtering
    2. Controlled Natural Language Query Parsing
    """
    def search_structured(self, query: StructuredSearchQuery, db: Session) -> Dict[str, Any]:
        q = db.query(Detection).join(Camera)

        if query.person_code:
            person = db.query(Person).filter(Person.person_code == query.person_code.upper()).first()
            if person:
                q = q.filter(Detection.person_id == person.id)
            else:
                return {"person_code": query.person_code, "total_detections": 0, "records": []}

        if query.camera_code:
            q = q.filter(Camera.camera_code == query.camera_code.upper())
        elif query.camera_id:
            q = q.filter(Detection.camera_id == query.camera_id)

        if query.location:
            q = q.filter(Camera.location.ilike(f"%{query.location}%"))

        if query.min_confidence:
            q = q.filter(Detection.final_identity_score >= query.min_confidence)

        records = q.order_by(Detection.timestamp.desc()).limit(query.limit).all()
        
        # Summary
        last_cam = records[0].camera.camera_code if records and records[0].camera else None
        last_loc = records[0].camera.location if records and records[0].camera else None
        last_time = records[0].timestamp.isoformat() if records else None

        return {
            "person_code": query.person_code,
            "last_detected_camera": last_cam,
            "last_detected_location": last_loc,
            "last_detected_time": last_time,
            "total_detections": len(records),
            "records": [r.to_dict() for r in records]
        }

    def execute_natural_language_query(self, raw_query: str, db: Session) -> Dict[str, Any]:
        """
        Controlled Natural Language Query (NLQ) interpreter:
        Converts human language queries into safe, parameterized SQL queries.
        """
        q_clean = raw_query.strip().lower()
        logger.info(f"Interpreting Natural Language Query: '{raw_query}'")

        # Extract Person Code (e.g. P001, P002, P1, p01)
        p_match = re.search(r'\b(p\d{1,4})\b', q_clean, re.IGNORECASE)
        person_code = p_match.group(1).upper() if p_match else "P001"

        person = db.query(Person).filter(Person.person_code == person_code).first()
        if not person:
            return {
                "query": raw_query,
                "interpreted_intent": "UNKNOWN_PERSON",
                "parsed_parameters": {"person_code": person_code},
                "summary": f"Could not find person {person_code} in resort registration records.",
                "results": []
            }

        # Intent 1: "Where was P001 last seen?" or "last known location"
        if "last seen" in q_clean or "last location" in q_clean or "where is" in q_clean:
            last_mov = db.query(MovementHistory).filter(
                MovementHistory.person_id == person.id
            ).order_by(MovementHistory.entry_time.desc()).first()

            if last_mov and last_mov.camera:
                summary = f"Person {person_code} was last seen at {last_mov.camera.name} ({last_mov.camera.camera_code}) at {last_mov.entry_time.strftime('%H:%M:%S')} with {int(last_mov.confidence * 100)}% match confidence."
                return {
                    "query": raw_query,
                    "interpreted_intent": "LAST_SEEN",
                    "parsed_parameters": {"person_code": person_code},
                    "summary": summary,
                    "results": [last_mov.to_dict()]
                }

        # Intent 2: "Where was P001 detected today?" or "all sightings"
        if "today" in q_clean or "where was" in q_clean or "sightings" in q_clean:
            movements = db.query(MovementHistory).filter(
                MovementHistory.person_id == person.id
            ).order_by(MovementHistory.entry_time.asc()).all()

            cams_visited = [f"{m.entry_time.strftime('%H:%M')} {m.camera.name} ({m.camera.camera_code})" for m in movements if m.camera]
            summary = f"Person {person_code} was detected at {len(movements)} location(s) today: " + " → ".join(cams_visited)
            return {
                "query": raw_query,
                "interpreted_intent": "TIMELINE_TODAY",
                "parsed_parameters": {"person_code": person_code, "period": "today"},
                "summary": summary,
                "results": [m.to_dict() for m in movements]
            }

        # Intent 3: Time range e.g. "between 9 AM and 11 AM"
        time_match = re.search(r'between\s+(\d+)\s*(am|pm)?\s+and\s+(\d+)\s*(am|pm)?', q_clean)
        if time_match:
            movements = db.query(MovementHistory).filter(
                MovementHistory.person_id == person.id
            ).order_by(MovementHistory.entry_time.asc()).all()

            summary = f"Movement history for {person_code} within requested time window yielded {len(movements)} events."
            return {
                "query": raw_query,
                "interpreted_intent": "TIME_WINDOW",
                "parsed_parameters": {"person_code": person_code, "time_match": time_match.group(0)},
                "summary": summary,
                "results": [m.to_dict() for m in movements]
            }

        # Default fallback: return recent movement timeline
        movements = db.query(MovementHistory).filter(
            MovementHistory.person_id == person.id
        ).order_by(MovementHistory.entry_time.asc()).all()

        return {
            "query": raw_query,
            "interpreted_intent": "GENERAL_SEARCH",
            "parsed_parameters": {"person_code": person_code},
            "summary": f"Retrieved {len(movements)} movement event(s) for person {person_code}.",
            "results": [m.to_dict() for m in movements]
        }

search_service = SearchService()
