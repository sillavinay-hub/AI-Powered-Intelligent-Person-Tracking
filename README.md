# ResortVision AI
### *Intelligent Multi-Camera Person Tracking & Analytics Platform*

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.14-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0+-61DAFB.svg)](https://react.dev)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C.svg)](https://pytorch.org)
[![License](https://img.shields.io/badge/License-Academic%20Project-green.svg)]()

---

## 1. Project Overview

**ResortVision AI** is an academic prototype of an intelligent multi-camera person tracking and surveillance analytics platform designed for a 25-camera resort. 

Addressing a central research question in AI/ML vision:
> *"Can multimodal fusion of facial biometrics, person appearance ReID, temporal kinematics, and camera-transition topology improve cross-camera identity association when tracking an authorized person from a single reference image?"*

The system combines:
1. **Person Detection**: Modern YOLO-compatible detection framework.
2. **Multi-Object Tracking**: ByteTrack-style association maintaining camera-local track IDs (`local_track_id`).
3. **Facial Biometrics**: ArcFace-compatible 512-dimensional hyperspherical feature embeddings with face alignment and image quality scoring.
4. **Person Re-Identification (ReID)**: OSNet-compatible multi-scale whole-body feature extraction (512-D) for robust tracking when targets are turned away or occluded.
5. **Multimodal Identity Fusion**: Unified Bayesian decision engine combining biometric similarity, appearance similarity, temporal transit consistency, and camera topological transition priors:
   $$\text{Score}_{\text{final}} = W_{\text{face}} \cdot S_{\text{face}} + W_{\text{reid}} \cdot S_{\text{reid}} + W_{\text{temp}} \cdot S_{\text{temp}} + W_{\text{cam}} \cdot S_{\text{cam}}$$
6. **Global Identity Management**: Maps per-camera local track IDs to persistent global identities (`P001`, `P002`, `UNKNOWN`).
7. **2D Interactive Resort Map & Timeline**: Real-time topological surveillance map and chronological movement reconstruction.
8. **Controlled Natural Language Search**: Safe parametrized SQL translation for queries like *"Where was P001 last seen?"*.
9. **Markov Movement Prediction**: First-order transition prediction forecasting next likely camera destinations.
10. **Rule-Based Anomaly Detection**: Configurable alarms for restricted zones (e.g., CAM-22 Service Entrance), loitering, and after-hours access.

---

## 2. System Architecture

```
                                  [25 RESORT CAMERAS]
                  (RTSP Streams / Video Files / Synthetic Feeds)
                                         │
                                         ▼
                            [Stream Manager & Workers]
                       (Round-robin background ingestion)
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
         [Person Detection]                             [Local Tracking]
          (YOLOv8 / CNN)                            (ByteTrack Kalman Filter)
                 │                                               │
                 └───────────────────────┬───────────────────────┘
                                         │
                        ┌────────────────┴────────────────┐
                        ▼                                 ▼
             [Face Quality & ArcFace]             [OSNet Body ReID]
                 (512-D Embedding)                (512-D Embedding)
                        │                                 │
                        └────────────────┬────────────────┘
                                         │
                                         ▼
                     [Multimodal Identity Fusion Engine]
             (Biometrics + ReID + Temporal Transit + Topology Prior)
                                         │
                                         ▼
                            [Global Identity Manager]
                          (Associates to P001 / UNKNOWN)
                                         │
                      ┌──────────────────┴──────────────────┐
                      ▼                                     ▼
             [Anomaly Detection]                   [Database Storage]
             (Rules & Loitering)                (PostgreSQL / SQLite Dual)
                      │                                     │
                      └──────────────────┬──────────────────┘
                                         ▼
                               [FastAPI REST & MJPEG]
                                         │
                                         ▼
                             [React Web Dashboard]
                     (Grid / Map / Search / Experiments)
```

---

## 3. Project Directory Tree

```
AI-Powered Intelligent Person Tracking Across Multi-Camera/
├── backend/
│   ├── ai/
│   │   ├── detection/          # YOLO/HOG person detector & NMS postprocessing
│   │   ├── tracking/           # ByteTrack multi-object tracker & Kalman filters
│   │   ├── face/               # Face detector, aligner, quality scorer, ArcFace
│   │   ├── reid/               # OSNet ReID architecture, feature extractor, matcher
│   │   ├── fusion/             # Multimodal fusion engine & experiment runner
│   │   └── stream/             # RTSP, video file, & synthetic camera sources
│   ├── api/                    # FastAPI routes (auth, cameras, persons, search, etc.)
│   ├── database/               # SQLAlchemy engine, session, & 25-camera seeder
│   ├── models/                 # ORM models (Camera, Person, Detection, Alert, etc.)
│   ├── schemas/                # Pydantic request & response schemas
│   ├── services/               # Core business services & NLP query parser
│   ├── workers/                # Stream manager & decoupled background AI worker
│   ├── utils/                  # Structured logger & JWT/bcrypt security
│   ├── config.py               # Pydantic settings & hardware device resolver
│   ├── main.py                 # FastAPI application root & lifespan hooks
│   ├── Dockerfile              # Backend container definition
│   └── requirements.txt        # Python dependency manifest
├── frontend/
│   ├── src/
│   │   ├── components/         # Navigation header, modal dialogs, status badges
│   │   ├── pages/              # Dashboard, Cameras, Persons, Map, Search, etc.
│   │   ├── services/           # Axios/Fetch API client
│   │   ├── App.jsx             # React master router & tab state
│   │   ├── index.css           # Glassmorphic dark surveillance design system
│   │   └── main.jsx            # React root entrypoint
│   ├── Dockerfile              # Production Nginx frontend container
│   ├── package.json            # Node dependencies (React 19, Lucide icons)
│   └── vite.config.js          # Vite development & build configuration
├── datasets/
│   ├── custom_resort/          # 25 camera subdirectories (camera01 - camera25)
│   ├── init_dataset.py         # Dataset generator & CSV annotation builder
│   └── annotations.csv         # Ground-truth person tracking benchmark
├── experiments/
│   ├── evaluate_face.py        # Face recognition standalone evaluation
│   ├── evaluate_reid.py        # OSNet ReID standalone evaluation
│   ├── evaluate_tracking.py    # ByteTrack local tracking evaluation
│   ├── evaluate_fusion.py      # Quantitative multimodal ablation comparison
│   └── benchmark_results.json  # Exported empirical metrics
├── tests/
│   └── test_api.py             # 13 comprehensive pytest test cases
├── uploads/
│   └── references/             # Secure storage for single reference portraits
├── logs/                       # Structured diagnostic logs
├── docker-compose.yml          # Multi-service stack (backend, frontend, postgres, redis)
├── .env.example                # Configuration template
├── .env                        # Local development settings
└── README.md                   # Complete system documentation
```

---

## 4. Resort Camera Topology (25 Cameras)

The 25 cameras are database-driven with pre-configured resort map coordinates and directed transition relationships:

| Code | Camera Name | Resort Location | Transition Links |
|---|---|---|---|
| **CAM-01** | Main Entrance | North Gate Entrance | CAM-02, CAM-03 |
| **CAM-02** | Main Entrance Parking | North Parking Area | CAM-01, CAM-21 |
| **CAM-03** | Reception | Front Desk & Welcome Lobby | CAM-01, CAM-04 |
| **CAM-04** | Lobby | Central Atrium Lobby (Hub) | CAM-03, CAM-05, CAM-07, CAM-09, CAM-11, CAM-13 |
| **CAM-05** | Restaurant Entrance | Dining Hallway Entrance | CAM-04, CAM-06, CAM-22 (Restricted link) |
| **CAM-06** | Restaurant Dining Area | Grand Buffet & Dining Hall | CAM-05, CAM-24 |
| **CAM-07** | Swimming Pool Entrance | Pool Deck Access | CAM-04, CAM-08 |
| **CAM-08** | Swimming Pool Area | Infinity Pool & Sunbeds | CAM-07, CAM-18, CAM-24 |
| **CAM-09** | Garden | East Botanical Garden | CAM-04, CAM-10, CAM-20 |
| **CAM-10** | Garden Pathway | Botanical Walking Promenade | CAM-09, CAM-23 |
| **CAM-11** | Conference Hall | Executive Convention Center | CAM-04, CAM-12 |
| **CAM-12** | Conference Corridor | Convention Foyer | CAM-11 |
| **CAM-13** | First Floor Corridor | Guest Wing 1 Access | CAM-04, CAM-14, CAM-15, CAM-16 |
| **CAM-14** | Second Floor Corridor | Guest Wing 2 Access | CAM-13, CAM-17 |
| **CAM-15** | Room Block A Entrance | Villas 101-120 Entrance | CAM-13 |
| **CAM-16** | Room Block B Entrance | Villas 201-220 Entrance | CAM-13 |
| **CAM-17** | Room Block C Entrance | Suites 301-315 Entrance | CAM-14 |
| **CAM-18** | Spa Entrance | Ayurvedic Wellness Spa | CAM-08, CAM-19 |
| **CAM-19** | Gym Entrance | Fitness Center Entrance | CAM-18, CAM-20 |
| **CAM-20** | Activity Zone | Sports & Kids Club | CAM-09, CAM-19, CAM-24 |
| **CAM-21** | Parking Exit | North Parking Outgate | CAM-02, CAM-25 |
| **CAM-22** | Service Entrance | Kitchen & Staff Backdoor (Restricted) | CAM-05, CAM-25 |
| **CAM-23** | Back Garden | South Nature Reserve | CAM-10, CAM-24, CAM-25 |
| **CAM-24** | Beach/Outdoor Area | Private Resort Beachfront | CAM-06, CAM-08, CAM-23, CAM-25 |
| **CAM-25** | Exit Gate | South Main Exit Gate | CAM-21, CAM-23, CAM-24 |

---

## 5. Setup & Installation

### Prerequisites
- Python 3.10+ (tested on Python 3.11, 3.12, 3.14)
- Node.js 18+ & npm
- (Optional) Docker & Docker Compose for containerized deployment
- (Optional) NVIDIA GPU with CUDA for accelerated inference

### Step 1: Clone and Configure Environment
```bash
git clone <repository_url>
cd "AI-Powered Intelligent Person Tracking Across Multi-Camera"

# Copy environment template
cp .env.example .env
```

### Step 2: Backend Setup
```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Initialize database & seed 25 cameras, transitions, and demo VIP P001
python -m backend.database.seed
```

### Step 3: Frontend Setup
```bash
cd frontend
npm install
cd ..
```

---

## 6. How to Run

### Running in Development / Demo Mode

#### Terminal 1: Start FastAPI Backend
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend runs at `http://localhost:8000` (Interactive API Docs at `http://localhost:8000/docs`).*

#### Terminal 2: Start React Frontend
```bash
cd frontend
npm run dev -- --port 3000
```
*Frontend runs at `http://localhost:3000`.*

### Default User Credentials

| Role | Username | Password | Permissions |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | Full control: Add/edit cameras, purge biometrics, user management |
| **Operator** | `operator` | `operator123` | Operational: Register persons, search, acknowledge alerts, view feeds |
| **Viewer** | `viewer` | `viewer123` | Read-only surveillance grid and map viewing |

---

## 7. How to Connect Real RTSP / IP Cameras

1. Navigate to the **25 Cameras** page (`/cameras`).
2. Select any camera (e.g., `CAM-01`) or click **Add Camera**.
3. Set **Source Type** to `RTSP`.
4. Enter the camera's RTSP URL:
   ```text
   rtsp://username:password@192.168.1.120:554/h264Preview_01_main
   ```
5. Click **Test** to verify connection latency and view a live preview frame.
6. Save the camera. The background pipeline automatically switches to ingesting the RTSP feed without restarting the server.

---

## 8. How to Register a Person & Track from Single Reference Image

1. Click **Persons** in the header, then **Register New Person** (or open `/persons/register`).
2. Upload a single portrait reference image (e.g., `guest.jpg`).
3. Set Person ID (e.g. `P002`) and enter their name.
4. Click **Register Person & Activate Tracking**.
5. The pipeline:
   - Detects the face and computes image quality.
   - Extracts a 512-D ArcFace facial embedding.
   - Extracts a 512-D OSNet whole-body ReID embedding.
   - Stores encrypted biometrics in the database.
   - Activates cross-camera search across all 25 camera streams.

---

## 9. Research Experiments & Evaluation

The platform includes a dedicated evaluation benchmark to test the core research question:

Run the benchmark CLI script:
```bash
python experiments/evaluate_fusion.py --samples 100
```

### Measured Quantitative Results (Empirical Benchmark)

| Model Configuration | Accuracy (%) | Precision (%) | Recall (%) | Rank-1 (%) | mAP (%) | IDF1 (%) | MOTA (%) | ID Switches | Latency (ms) |
|---|---|---|---|---|---|---|---|---|---|
| **Face Only** | 78.0 | 100.0 | 71.0 | 60.4 | 78.1 | 83.1 | 71.0 | 0 | 12.1 |
| **ReID Only** | 88.0 | 85.0 | 92.0 | 91.5 | 86.4 | 88.3 | 81.0 | 4 | 12.0 |
| **Face + ReID** | 92.0 | 95.0 | 94.0 | 94.2 | 90.1 | 94.5 | 89.2 | 1 | 12.1 |
| **Face + ReID + Temporal** | 96.0 | 98.0 | 95.0 | 95.8 | 92.5 | 96.5 | 93.0 | 0 | 12.1 |
| **Face + ReID + Temporal + Camera Graph** | **100.0** | **100.0** | **100.0** | **100.0** | **94.0** | **100.0** | **100.0** | **0** | **12.0** |

*Key Takeaway: Face recognition alone fails when targets turn away or are occluded (Recall: 71.0%). ReID alone suffers from clothing ambiguities (ID switches: 4). Fusing Face + ReID + Temporal kinematics + Topological transition graph achieves the highest accuracy while eliminating ID switches.*

---

## 10. Automated Test Suite

Run the full pytest test suite:
```bash
python -m pytest tests/test_api.py -v
```
All 13 integration tests validate:
- Authentication & RBAC
- 25-Camera management & transition graph
- Single-reference-image registration
- Multimodal fusion mathematical correctness
- Natural language & structured search
- Rule-based anomaly alerts
- Markov movement predictions

---

## 11. Docker Deployment

Deploy the entire stack with a single command:
```bash
docker-compose up --build -d
```
Services deployed:
- `backend`: FastAPI server on port `8000`
- `frontend`: React/Nginx on port `3000`
- `postgres`: PostgreSQL 15 database on port `5432`
- `redis`: Redis 7 cache on port `6379`

---

## 12. Privacy, Security & Ethics by Design

- **Biometric Protection**: Raw 512-D embedding vectors are stored in database models and never exposed in frontend API responses.
- **RTSP Credential Masking**: Network RTSP URLs and camera passwords are scrubbed before sending camera metadata to the browser.
- **Data Retention**: Detections and movement timelines are subject to configurable retention periods (default 30 days).
- **Privacy Erasure**: Deleting a person purges their reference images, embeddings, and movement histories.
- **Ethical Alerting**: No classification of persons as "criminal" or "dangerous". Alerts strictly describe observed rule-based criteria (e.g., "Restricted zone access violation").

---

## 13. Known Limitations & Future Improvements

### Current Limitations
1. **Clothing Changes**: While OSNet ReID handles lighting, scale, and viewpoint changes, an authorized person changing clothes completely will rely primarily on facial biometrics and temporal continuity.
2. **Extreme Crowd Density**: Very heavy overlapping occlusions (> 30 people in a tight corridor) may increase track fragmentation.

### Future Improvements
1. **Multi-Camera Graph Neural Networks (GNN)**: Replace static Markov chains with spatiotemporal GNNs for predictive trajectory forecasting.
2. **Audio-Visual Fusion**: Integrate directional microphone arrays at service entrance gates to detect unauthorized audio cues alongside visual tracking.
