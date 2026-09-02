import io
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.session import SessionLocal
from backend.models.user import User
from backend.models.camera import Camera
from backend.models.person import Person
from backend.ai.fusion.multimodal_fusion import fusion_engine

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["system"] == "ResortVision AI"
    assert data["total_cameras"] == 25

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"

def test_auth_login():
    # Test valid login
    response = client.post(
        "/api/auth/token",
        data={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["role"] == "ADMIN"

    # Test invalid login
    bad_res = client.post(
        "/api/auth/token",
        data={"username": "admin", "password": "wrongpassword"}
    )
    assert bad_res.status_code == 401

def test_cameras_list():
    response = client.get("/api/cameras")
    assert response.status_code == 200
    cameras = response.json()
    assert len(cameras) >= 25
    camera_codes = [c["camera_code"] for c in cameras]
    assert "CAM-01" in camera_codes
    assert "CAM-25" in camera_codes

def test_camera_map_graph():
    response = client.get("/api/cameras/map/graph")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) >= 25

def test_camera_test_connection():
    response = client.post("/api/cameras/1/test")
    assert response.status_code == 200
    data = response.json()
    assert data["camera_code"] == "CAM-01"
    assert "latency_ms" in data

def test_persons_list():
    response = client.get("/api/persons")
    assert response.status_code == 200
    persons = response.json()
    assert len(persons) >= 1
    codes = [p["person_code"] for p in persons]
    assert "P001" in codes

def test_person_registration_and_timeline():
    # Login as operator
    token_res = client.post(
        "/api/auth/token",
        data={"username": "operator", "password": "operator123"}
    )
    token = token_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Generate synthetic 100x100 RGB image for registration
    import numpy as np
    import cv2
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(img, (50, 40), 25, (200, 180, 150), -1)
    cv2.rectangle(img, (30, 65), (70, 100), (120, 50, 50), -1)
    _, buffer = cv2.imencode('.jpg', img)

    test_code = "P999"
    # Ensure test_code is clean
    db = SessionLocal()
    existing = db.query(Person).filter(Person.person_code == test_code).first()
    if existing:
        db.delete(existing)
        db.commit()
    db.close()

    # Register
    files = {"file": ("test_ref.jpg", buffer.tobytes(), "image/jpeg")}
    data = {"person_code": test_code, "full_name": "Test VIP Guest", "notes": "Registered during unit test."}
    reg_res = client.post("/api/persons/register", headers=headers, data=data, files=files)
    assert reg_res.status_code == 200
    reg_data = reg_res.json()
    assert reg_data["person_code"] == test_code

    # Verify timeline retrieval
    t_res = client.get(f"/api/timeline/{test_code}")
    assert t_res.status_code == 200

def test_multimodal_fusion_logic():
    # Case 1: High face + High ReID + High Temporal + High Cam
    fused_match = fusion_engine.fuse(
        face_sim=0.92,
        reid_sim=0.88,
        face_valid=True,
        camera_transition_prob=0.90,
        temporal_score=0.95
    )
    assert fused_match["is_matched"] is True
    assert fused_match["status"] == "MATCH"
    assert fused_match["final_score"] >= 0.85

    # Case 2: Face turned away (face_valid=False) but ReID + Temporal match
    fused_turned = fusion_engine.fuse(
        face_sim=0.0,
        reid_sim=0.85,
        face_valid=False,
        camera_transition_prob=0.88,
        temporal_score=0.90
    )
    assert fused_turned["is_matched"] is True

    # Case 3: Complete impostor
    fused_impostor = fusion_engine.fuse(
        face_sim=0.15,
        reid_sim=0.20,
        face_valid=True,
        camera_transition_prob=0.10,
        temporal_score=0.10
    )
    assert fused_impostor["is_matched"] is False
    assert fused_impostor["status"] == "UNKNOWN"

def test_natural_language_search():
    # Query 1: Last seen
    res1 = client.post("/api/search/nlp", json={"query": "Where was P001 last seen?"})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["interpreted_intent"] == "LAST_SEEN"
    assert "P001" in data1["summary"]

    # Query 2: Today sightings
    res2 = client.post("/api/search/nlp", json={"query": "Where was P001 detected today?"})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["interpreted_intent"] == "TIMELINE_TODAY"

def test_structured_search():
    res = client.post(
        "/api/search/structured",
        json={"person_code": "P001", "limit": 10}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["person_code"] == "P001"
    assert data["total_detections"] > 0

def test_alerts_and_predictions():
    # Alerts
    a_res = client.get("/api/alerts")
    assert a_res.status_code == 200
    alerts = a_res.json()
    assert len(alerts) >= 1

    # Prediction for P001
    p_res = client.get("/api/predictions/1")
    assert p_res.status_code == 200
    pred = p_res.json()
    assert "predicted_camera" in pred
    assert "probability" in pred
    assert "disclaimer" in pred

def test_analytics_dashboard():
    res = client.get("/api/analytics/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert data["total_cameras"] == 25
    assert data["tracked_persons"] >= 1
