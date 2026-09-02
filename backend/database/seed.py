import json
from datetime import datetime, timedelta
from backend.database.session import SessionLocal, engine, Base
from backend.models.user import User
from backend.models.camera import Camera, CameraTransition
from backend.models.person import Person, PersonEmbedding, MovementHistory
from backend.models.detection import Detection, PredictionResult
from backend.models.alert import Alert
from backend.models.log import SystemLog
from backend.utils.security import get_password_hash
from backend.utils.logger import logger

RESORT_CAMERAS = [
    {"camera_code": "CAM-01", "name": "Main Entrance", "location": "North Gate Entrance", "map_x": 50.0, "map_y": 6.0},
    {"camera_code": "CAM-02", "name": "Main Entrance Parking", "location": "North Parking Area", "map_x": 24.0, "map_y": 10.0},
    {"camera_code": "CAM-03", "name": "Reception", "location": "Front Desk & Welcome Lobby", "map_x": 50.0, "map_y": 18.0},
    {"camera_code": "CAM-04", "name": "Lobby", "location": "Central Atrium Lobby", "map_x": 50.0, "map_y": 30.0},
    {"camera_code": "CAM-05", "name": "Restaurant Entrance", "location": "Dining Hallway Entrance", "map_x": 74.0, "map_y": 28.0},
    {"camera_code": "CAM-06", "name": "Restaurant Dining Area", "location": "Grand Buffet & Dining Hall", "map_x": 88.0, "map_y": 28.0},
    {"camera_code": "CAM-07", "name": "Swimming Pool Entrance", "location": "Pool Deck Access", "map_x": 78.0, "map_y": 48.0},
    {"camera_code": "CAM-08", "name": "Swimming Pool Area", "location": "Infinity Pool & Sunbeds", "map_x": 86.0, "map_y": 56.0},
    {"camera_code": "CAM-09", "name": "Garden", "location": "East Botanical Garden", "map_x": 26.0, "map_y": 32.0},
    {"camera_code": "CAM-10", "name": "Garden Pathway", "location": "Botanical Walking Promenade", "map_x": 26.0, "map_y": 54.0},
    {"camera_code": "CAM-11", "name": "Conference Hall", "location": "Executive Convention Center", "map_x": 76.0, "map_y": 14.0},
    {"camera_code": "CAM-12", "name": "Conference Hall Corridor", "location": "Convention Foyer", "map_x": 76.0, "map_y": 8.0},
    {"camera_code": "CAM-13", "name": "First Floor Corridor", "location": "Guest Wing 1 Access", "map_x": 50.0, "map_y": 44.0},
    {"camera_code": "CAM-14", "name": "Second Floor Corridor", "location": "Guest Wing 2 Access", "map_x": 50.0, "map_y": 58.0},
    {"camera_code": "CAM-15", "name": "Room Block A Entrance", "location": "Villas 101-120 Entrance", "map_x": 38.0, "map_y": 44.0},
    {"camera_code": "CAM-16", "name": "Room Block B Entrance", "location": "Villas 201-220 Entrance", "map_x": 62.0, "map_y": 44.0},
    {"camera_code": "CAM-17", "name": "Room Block C Entrance", "location": "Suites 301-315 Entrance", "map_x": 50.0, "map_y": 72.0},
    {"camera_code": "CAM-18", "name": "Spa Entrance", "location": "Ayurvedic Wellness Spa", "map_x": 90.0, "map_y": 42.0},
    {"camera_code": "CAM-19", "name": "Gym Entrance", "location": "Fitness Center Entrance", "map_x": 74.0, "map_y": 66.0},
    {"camera_code": "CAM-20", "name": "Activity Zone", "location": "Sports & Kids Club", "map_x": 36.0, "map_y": 66.0},
    {"camera_code": "CAM-21", "name": "Parking Exit", "location": "North Parking Outgate", "map_x": 16.0, "map_y": 38.0},
    {"camera_code": "CAM-22", "name": "Service Entrance", "location": "Kitchen & Staff Backdoor", "map_x": 90.0, "map_y": 14.0}, # Restricted
    {"camera_code": "CAM-23", "name": "Back Garden", "location": "South Nature Reserve", "map_x": 22.0, "map_y": 82.0},
    {"camera_code": "CAM-24", "name": "Beach/Outdoor Area", "location": "Private Resort Beachfront", "map_x": 88.0, "map_y": 78.0},
    {"camera_code": "CAM-25", "name": "Exit Gate", "location": "South Main Exit Gate", "map_x": 50.0, "map_y": 92.0},
]

# Directed transition graph pairs (from_code, to_code, min_sec, max_sec, prob)
TRANSITION_PAIRS = [
    ("CAM-01", "CAM-02", 10.0, 180.0, 0.40),
    ("CAM-01", "CAM-03", 5.0, 120.0, 0.60),
    ("CAM-02", "CAM-01", 10.0, 180.0, 0.50),
    ("CAM-02", "CAM-21", 20.0, 300.0, 0.50),
    ("CAM-03", "CAM-01", 10.0, 120.0, 0.30),
    ("CAM-03", "CAM-04", 5.0, 90.0, 0.70),
    ("CAM-04", "CAM-03", 5.0, 90.0, 0.20),
    ("CAM-04", "CAM-05", 15.0, 120.0, 0.25),
    ("CAM-04", "CAM-07", 20.0, 150.0, 0.20),
    ("CAM-04", "CAM-09", 15.0, 120.0, 0.15),
    ("CAM-04", "CAM-11", 15.0, 120.0, 0.10),
    ("CAM-04", "CAM-13", 10.0, 100.0, 0.10),
    ("CAM-05", "CAM-04", 15.0, 120.0, 0.40),
    ("CAM-05", "CAM-06", 5.0, 60.0, 0.55),
    ("CAM-05", "CAM-22", 15.0, 90.0, 0.05), # Restricted access link
    ("CAM-06", "CAM-05", 5.0, 60.0, 0.60),
    ("CAM-06", "CAM-24", 20.0, 180.0, 0.40),
    ("CAM-07", "CAM-04", 20.0, 150.0, 0.40),
    ("CAM-07", "CAM-08", 5.0, 60.0, 0.60),
    ("CAM-08", "CAM-07", 5.0, 60.0, 0.45),
    ("CAM-08", "CAM-18", 15.0, 120.0, 0.25),
    ("CAM-08", "CAM-24", 25.0, 200.0, 0.30),
    ("CAM-09", "CAM-04", 15.0, 120.0, 0.45),
    ("CAM-09", "CAM-10", 10.0, 120.0, 0.35),
    ("CAM-09", "CAM-20", 20.0, 180.0, 0.20),
    ("CAM-10", "CAM-09", 10.0, 120.0, 0.45),
    ("CAM-10", "CAM-23", 25.0, 240.0, 0.55),
    ("CAM-11", "CAM-04", 15.0, 120.0, 0.60),
    ("CAM-11", "CAM-12", 5.0, 60.0, 0.40),
    ("CAM-12", "CAM-11", 5.0, 60.0, 0.90),
    ("CAM-13", "CAM-04", 10.0, 100.0, 0.40),
    ("CAM-13", "CAM-14", 10.0, 80.0, 0.25),
    ("CAM-13", "CAM-15", 5.0, 50.0, 0.20),
    ("CAM-13", "CAM-16", 5.0, 50.0, 0.15),
    ("CAM-14", "CAM-13", 10.0, 80.0, 0.60),
    ("CAM-14", "CAM-17", 8.0, 60.0, 0.40),
    ("CAM-15", "CAM-13", 5.0, 50.0, 0.90),
    ("CAM-16", "CAM-13", 5.0, 50.0, 0.90),
    ("CAM-17", "CAM-14", 8.0, 60.0, 0.90),
    ("CAM-18", "CAM-08", 15.0, 120.0, 0.50),
    ("CAM-18", "CAM-19", 10.0, 90.0, 0.50),
    ("CAM-19", "CAM-18", 10.0, 90.0, 0.50),
    ("CAM-19", "CAM-20", 15.0, 120.0, 0.50),
    ("CAM-20", "CAM-09", 20.0, 180.0, 0.40),
    ("CAM-20", "CAM-19", 15.0, 120.0, 0.35),
    ("CAM-20", "CAM-24", 30.0, 240.0, 0.25),
    ("CAM-21", "CAM-02", 20.0, 300.0, 0.40),
    ("CAM-21", "CAM-25", 25.0, 240.0, 0.60),
    ("CAM-22", "CAM-05", 15.0, 90.0, 0.50),
    ("CAM-22", "CAM-25", 30.0, 200.0, 0.50),
    ("CAM-23", "CAM-10", 25.0, 240.0, 0.40),
    ("CAM-23", "CAM-24", 20.0, 180.0, 0.35),
    ("CAM-23", "CAM-25", 25.0, 200.0, 0.25),
    ("CAM-24", "CAM-08", 25.0, 200.0, 0.30),
    ("CAM-24", "CAM-06", 20.0, 180.0, 0.30),
    ("CAM-24", "CAM-23", 20.0, 180.0, 0.20),
    ("CAM-24", "CAM-25", 25.0, 200.0, 0.20),
    ("CAM-25", "CAM-21", 25.0, 240.0, 0.30),
    ("CAM-25", "CAM-23", 25.0, 200.0, 0.30),
    ("CAM-25", "CAM-24", 25.0, 200.0, 0.40),
]

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 1. Seed Users if not existing
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            logger.info("Seeding initial users (admin, operator, viewer)...")
            users = [
                User(username="admin", email="admin@resortvision.ai", hashed_password=get_password_hash("admin123"), role="ADMIN"),
                User(username="operator", email="operator@resortvision.ai", hashed_password=get_password_hash("operator123"), role="OPERATOR"),
                User(username="viewer", email="viewer@resortvision.ai", hashed_password=get_password_hash("viewer123"), role="VIEWER"),
            ]
            db.add_all(users)
            db.commit()

        # 2. Seed 25 Cameras if not existing
        cam_count = db.query(Camera).count()
        if cam_count == 0:
            logger.info("Seeding 25 Resort Cameras...")
            cam_objs = {}
            for item in RESORT_CAMERAS:
                cam = Camera(
                    camera_code=item["camera_code"],
                    name=item["name"],
                    location=item["location"],
                    rtsp_url=f"rtsp://demo.stream/{item['camera_code'].lower()}",
                    source_type="DEMO",
                    map_x=item["map_x"],
                    map_y=item["map_y"],
                    status="ONLINE",
                    ai_enabled=True,
                    fps=10.0
                )
                db.add(cam)
                db.flush()
                cam_objs[item["camera_code"]] = cam

            db.commit()

            # 3. Seed Camera Transitions
            logger.info("Seeding Camera Transition Graph...")
            transitions = []
            for from_code, to_code, min_s, max_s, prob in TRANSITION_PAIRS:
                if from_code in cam_objs and to_code in cam_objs:
                    transitions.append(CameraTransition(
                        from_camera_id=cam_objs[from_code].id,
                        to_camera_id=cam_objs[to_code].id,
                        min_duration_sec=min_s,
                        max_duration_sec=max_s,
                        transition_probability=prob
                    ))
            db.add_all(transitions)
            db.commit()

        # 4. Seed Demo Person (P001) & Historical Movements
        p1 = db.query(Person).filter(Person.person_code == "P001").first()
        if not p1:
            logger.info("Seeding Demo Person P001 and historical movement timeline...")
            p1 = Person(
                person_code="P001",
                full_name="Alexander Vance (Registered VIP)",
                notes="Authorized VIP Guest registered via single reference image.",
                reference_image_path="uploads/references/P001_ref.jpg",
                status="ACTIVE"
            )
            db.add(p1)
            db.flush()

            # Add dummy 512-D unit embedding vectors for demo person
            import numpy as np
            np.random.seed(42)
            face_vec = np.random.randn(512).astype(float)
            face_vec /= np.linalg.norm(face_vec)
            reid_vec = np.random.randn(512).astype(float)
            reid_vec /= np.linalg.norm(reid_vec)

            emb_face = PersonEmbedding(person_id=p1.id, embedding_type="FACE", vector_json=json.dumps(face_vec.tolist()), quality_score=0.94)
            emb_reid = PersonEmbedding(person_id=p1.id, embedding_type="REID", vector_json=json.dumps(reid_vec.tolist()), quality_score=0.91)
            db.add_all([emb_face, emb_reid])

            # Seed movement history: CAM-01 (09:15) -> CAM-03 (09:21) -> CAM-04 (09:34) -> CAM-06 (09:52) -> CAM-08 (10:42)
            cam_map = {c.camera_code: c for c in db.query(Camera).all()}
            now = datetime.utcnow()
            today_morning = now.replace(hour=9, minute=0, second=0, microsecond=0)

            history_events = [
                ("CAM-01", today_morning + timedelta(minutes=15, seconds=22), 95, 0.94),
                ("CAM-03", today_morning + timedelta(minutes=21, seconds=40), 140, 0.92),
                ("CAM-04", today_morning + timedelta(minutes=34, seconds=10), 210, 0.95),
                ("CAM-06", today_morning + timedelta(minutes=52, seconds=5), 480, 0.89),
                ("CAM-08", today_morning + timedelta(hours=1, minutes=42, seconds=17), 620, 0.91),
            ]

            for c_code, entry_t, dur, conf in history_events:
                if c_code in cam_map:
                    cam = cam_map[c_code]
                    exit_t = entry_t + timedelta(seconds=dur)
                    mh = MovementHistory(
                        person_id=p1.id,
                        camera_id=cam.id,
                        entry_time=entry_t,
                        exit_time=exit_t,
                        duration_sec=dur,
                        confidence=conf
                    )
                    db.add(mh)

                    # Add corresponding detection record
                    det = Detection(
                        camera_id=cam.id,
                        person_id=p1.id,
                        local_track_id=17,
                        global_person_id="P001",
                        timestamp=entry_t,
                        bbox_x=0.45,
                        bbox_y=0.25,
                        bbox_width=0.15,
                        bbox_height=0.55,
                        face_similarity=conf + 0.02,
                        reid_similarity=conf - 0.03,
                        temporal_score=0.96,
                        camera_score=0.95,
                        final_identity_score=conf,
                        is_matched=True
                    )
                    db.add(det)

            # Seed demo anomaly alert: CAM-22 Service Entrance access
            if "CAM-22" in cam_map:
                alert = Alert(
                    alert_type="RESTRICTED_ZONE",
                    person_id=p1.id,
                    camera_id=cam_map["CAM-22"].id,
                    timestamp=now - timedelta(minutes=14),
                    confidence=0.91,
                    status="NEW",
                    details_json=json.dumps({"reason": "Person entered restricted service entrance", "zone": "Staff Kitchen Access"})
                )
                db.add(alert)

            # Seed system log
            slog = SystemLog(
                level="INFO",
                module="SYSTEM",
                message="ResortVision AI Database initialized with 25 cameras, transitions, and baseline users.",
                metadata_json=json.dumps({"cameras": 25, "seed_version": "1.0"})
            )
            db.add(slog)
            db.commit()

        logger.info("Database initialization and seed complete!")
    except Exception as e:
        db.rollback()
        logger.error(f"Error during DB seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
