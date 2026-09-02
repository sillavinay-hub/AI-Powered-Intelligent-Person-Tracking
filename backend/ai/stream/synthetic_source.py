import cv2
import time
import math
import numpy as np
from datetime import datetime

class SyntheticCameraSource:
    """
    Generates rich, distinctive synthetic surveillance camera feeds for ResortVision AI.
    Each of the 25 cameras renders a completely unique visual scene, realistic architectural
    features, distinct clothing/appearance, and movement trajectories corresponding to its
    specific resort location (Pool, Garden, Beach, Reception, Service Entrance, etc.).
    """
    def __init__(self, camera_code: str, name: str, location: str, fps: float = 10.0, width: int = 640, height: int = 360):
        self.camera_code = camera_code
        self.name = name
        self.location = location
        self.fps = fps
        self.width = width
        self.height = height
        self.frame_idx = 0
        self.last_time = time.time()
        self.current_person_bbox = None

        # Extract numeric index (1 to 25)
        try:
            self.cam_num = int(camera_code.split("-")[1])
        except Exception:
            self.cam_num = 1

    def read(self):
        # Throttle to target FPS
        now = time.time()
        elapsed = now - self.last_time
        target_interval = 1.0 / max(1.0, self.fps)
        if elapsed < target_interval:
            time.sleep(max(0.001, target_interval - elapsed))
        self.last_time = time.time()
        self.frame_idx += 1

        # Render the specific scene for this camera
        frame = self._render_scene()

        # OSD: Surveillance Header Bar
        cv2.rectangle(frame, (10, 10), (self.width - 10, 42), (12, 14, 20), -1)
        cv2.rectangle(frame, (10, 10), (self.width - 10, 42), (50, 60, 80), 1)

        # Blinking Recording Indicator
        is_rec_blink = (self.frame_idx // 10) % 2 == 0
        rec_color = (0, 0, 255) if is_rec_blink else (0, 0, 120)
        cv2.circle(frame, (24, 26), 5, rec_color, -1)
        cv2.putText(frame, "REC", (35, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (230, 230, 230), 1, cv2.LINE_AA)

        # Camera Code & Name
        title = f"{self.camera_code} : {self.name.upper()}"
        cv2.putText(frame, title, (75, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 242, 254), 1, cv2.LINE_AA)

        # Live Timestamp
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, ts, (self.width - 180, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (210, 210, 210), 1, cv2.LINE_AA)

        # Footer watermark
        cv2.putText(frame, f"RESORTVISION AI - {self.location.upper()}", (15, self.height - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (130, 140, 160), 1, cv2.LINE_AA)

        return True, frame

    def _render_scene(self) -> np.ndarray:
        w, h = self.width, self.height
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        t = (self.frame_idx % 240) / 240.0
        wave = math.sin(t * 2 * math.pi)

        cid = self.cam_num

        if cid == 1:
            # CAM-01: Main Entrance (North Gate)
            # Sky & asphalt driveway with security barrier
            frame[0:int(h*0.5)] = (180, 140, 90) # Evening sky
            frame[int(h*0.5):] = (45, 45, 50)     # Dark asphalt
            # Lane markings
            cv2.line(frame, (int(w*0.5), int(h*0.5)), (int(w*0.5), h), (255, 255, 255), 2)
            # Security Booth
            cv2.rectangle(frame, (30, int(h*0.35)), (110, int(h*0.65)), (70, 75, 85), -1)
            cv2.rectangle(frame, (45, int(h*0.4)), (95, int(h*0.5)), (180, 210, 230), -1)
            # Boom barrier
            cv2.line(frame, (110, int(h*0.55)), (int(w*0.65), int(h*0.55)), (0, 0, 255), 4)
            # Target P001 walking across barrier (navy blue blazer)
            px = int(w * 0.35 + w * 0.35 * t)
            py = int(h * 0.48)
            self._draw_person(frame, px, py, int(w*0.07), int(h*0.35), clothes_color=(140, 80, 30), pants_color=(30, 30, 30))

        elif cid == 2:
            # CAM-02: Main Entrance Parking
            # Parking lot asphalt with parking stalls & cars
            frame[:] = (50, 52, 55)
            # Parking bay white lines
            for x in range(60, w, 120):
                cv2.line(frame, (x, int(h*0.4)), (x - 40, h), (240, 240, 240), 2)
            # Parked Car 1 (Metallic Red)
            cv2.rectangle(frame, (80, int(h*0.5)), (180, int(h*0.8)), (40, 40, 180), -1)
            cv2.rectangle(frame, (100, int(h*0.42)), (160, int(h*0.5)), (150, 180, 200), -1)
            # Parked Car 2 (Midnight Blue SUV)
            cv2.rectangle(frame, (380, int(h*0.48)), (500, int(h*0.82)), (160, 80, 20), -1)
            cv2.rectangle(frame, (400, int(h*0.4)), (480, int(h*0.48)), (140, 160, 180), -1)
            # Person walking between cars
            px = int(w * 0.32 + w * 0.25 * (0.5 + 0.5 * wave))
            py = int(h * 0.46)
            self._draw_person(frame, px, py, int(w*0.065), int(h*0.34), clothes_color=(50, 120, 180), pants_color=(50, 50, 60))

        elif cid == 3:
            # CAM-03: Reception (Front Desk & Welcome Lobby)
            # Polished marble flooring, golden reception desk, warm lighting
            frame[0:int(h*0.45)] = (35, 30, 40)  # Wall paneling
            frame[int(h*0.45):] = (60, 75, 90)   # Marble floor
            # Golden Reception Desk
            cv2.rectangle(frame, (int(w*0.1), int(h*0.5)), (int(w*0.9), int(h*0.75)), (40, 90, 140), -1)
            cv2.rectangle(frame, (int(w*0.1), int(h*0.48)), (int(w*0.9), int(h*0.52)), (60, 140, 200), -1)
            # Wall art / logo
            cv2.circle(frame, (int(w*0.5), int(h*0.25)), 30, (80, 140, 190), 2)
            # Receptionist behind desk
            self._draw_person(frame, int(w*0.45), int(h*0.28), int(w*0.06), int(h*0.26), clothes_color=(30, 30, 30), pants_color=(30, 30, 30))
            # Guest approaching front desk
            px = int(w * 0.65 - w * 0.15 * t)
            py = int(h * 0.58)
            self._draw_person(frame, px, py, int(w*0.08), int(h*0.38), clothes_color=(140, 80, 30), pants_color=(30, 30, 30))

        elif cid == 4:
            # CAM-04: Lobby (Central Atrium Lobby Hub)
            # Giant indoor palm trees, lounge seating, floor medallion
            frame[0:int(h*0.4)] = (30, 35, 45)
            frame[int(h*0.4):] = (70, 75, 80)
            # Floor medallion
            cv2.ellipse(frame, (int(w*0.5), int(h*0.75)), (int(w*0.35), int(h*0.18)), 0, 0, 360, (50, 110, 150), 3)
            # Indoor Palm Tree Left
            cv2.line(frame, (60, int(h*0.7)), (60, int(h*0.25)), (30, 50, 70), 8)
            cv2.ellipse(frame, (60, int(h*0.22)), (50, 25), 0, 0, 360, (40, 120, 50), -1)
            # Indoor Palm Tree Right
            cv2.line(frame, (w - 60, int(h*0.7)), (w - 60, int(h*0.25)), (30, 50, 70), 8)
            cv2.ellipse(frame, (w - 60, int(h*0.22)), (50, 25), 0, 0, 360, (40, 120, 50), -1)
            # VIP P001 crossing lobby
            px = int(w * 0.25 + w * 0.5 * (0.5 - 0.5 * wave))
            py = int(h * 0.45)
            self._draw_person(frame, px, py, int(w*0.075), int(h*0.36), clothes_color=(140, 80, 30), pants_color=(30, 30, 30))

        elif cid == 5:
            # CAM-05: Restaurant Entrance
            # Elegant archway, wooden menu easel, soft ambient lighting
            frame[0:int(h*0.5)] = (25, 25, 35)
            frame[int(h*0.5):] = (40, 50, 65) # Parquet floor
            # Wooden archway
            cv2.rectangle(frame, (int(w*0.2), 40), (int(w*0.8), int(h*0.85)), (25, 40, 60), 12)
            # Menu stand easel
            cv2.line(frame, (int(w*0.15), int(h*0.8)), (int(w*0.15), int(h*0.55)), (20, 30, 40), 4)
            cv2.rectangle(frame, (int(w*0.1), int(h*0.48)), (int(w*0.2), int(h*0.62)), (230, 240, 245), -1)
            # Person entering dining archway
            px = int(w * 0.45 + w * 0.1 * wave)
            py = int(h * 0.42)
            self._draw_person(frame, px, py, int(w*0.07), int(h*0.36), clothes_color=(50, 60, 190), pants_color=(40, 40, 40))

        elif cid == 6:
            # CAM-06: Restaurant Dining Area
            # Dining tables with white tablecloths & seated guests
            frame[0:int(h*0.45)] = (30, 30, 40)
            frame[int(h*0.45):] = (45, 55, 70)
            # Table 1
            cv2.ellipse(frame, (int(w*0.25), int(h*0.75)), (70, 35), 0, 0, 360, (220, 225, 230), -1)
            cv2.circle(frame, (int(w*0.25), int(h*0.73)), 10, (40, 40, 180), -1) # Flowers
            # Table 2
            cv2.ellipse(frame, (int(w*0.75), int(h*0.75)), (70, 35), 0, 0, 360, (220, 225, 230), -1)
            # Waiter walking between tables
            px = int(w * 0.46 + w * 0.08 * wave)
            py = int(h * 0.45)
            self._draw_person(frame, px, py, int(w*0.07), int(h*0.36), clothes_color=(230, 230, 230), pants_color=(20, 20, 20))

        elif cid == 7:
            # CAM-07: Swimming Pool Entrance
            # Glass sliding doors, turquoise pool deck access
            frame[0:int(h*0.45)] = (40, 45, 50)
            frame[int(h*0.45):] = (160, 140, 60) # Aqua pool tiles
            # Glass sliding doors
            cv2.rectangle(frame, (int(w*0.25), 45), (int(w*0.75), int(h*0.75)), (200, 210, 220), 4)
            # Pool blue seen through glass
            cv2.rectangle(frame, (int(w*0.27), 50), (int(w*0.73), int(h*0.73)), (190, 130, 30), -1)
            # Person walking towards pool in summer clothes
            px = int(w * 0.4 + w * 0.25 * t)
            py = int(h * 0.48)
            self._draw_person(frame, px, py, int(w*0.07), int(h*0.35), clothes_color=(50, 180, 240), pants_color=(180, 60, 50))

        elif cid == 8:
            # CAM-08: Swimming Pool Area (Infinity Pool & Sunbeds)
            # Sparkling turquoise water with animated ripples, white sunbeds & umbrella
            frame[0:int(h*0.35)] = (220, 160, 90) # Sunlit sky
            frame[int(h*0.35):int(h*0.75)] = (190, 125, 30) # Turquoise pool water
            frame[int(h*0.75):] = (200, 190, 180) # Stone deck
            # Animated water ripples
            for r in range(4):
                ry = int(h * 0.4 + r * 25)
                rx_offset = int(wave * 15) * (1 if r % 2 == 0 else -1)
                cv2.ellipse(frame, (int(w*0.5) + rx_offset, ry), (120 + r * 30, 8), 0, 0, 180, (230, 170, 70), 2)
            # White sunbed & umbrella on pool deck
            cv2.rectangle(frame, (int(w*0.08), int(h*0.78)), (int(w*0.22), int(h*0.88)), (240, 240, 240), -1)
            cv2.line(frame, (int(w*0.15), int(h*0.78)), (int(w*0.15), int(h*0.55)), (150, 150, 150), 3)
            cv2.ellipse(frame, (int(w*0.15), int(h*0.55)), (45, 18), 0, 180, 360, (50, 90, 240), -1) # Red umbrella
            # Target P001 strolling along pool deck
            px = int(w * 0.35 + w * 0.38 * (0.5 - 0.5 * wave))
            py = int(h * 0.52)
            self._draw_person(frame, px, py, int(w*0.075), int(h*0.37), clothes_color=(140, 80, 30), pants_color=(30, 30, 30))

        elif cid == 9:
            # CAM-09: Garden (East Botanical Garden)
            # Winding stone walkway, lush tropical green bushes, colorful flowerbeds
            frame[0:int(h*0.4)] = (50, 90, 40)   # Forest background
            frame[int(h*0.4):] = (40, 120, 45)  # Lawn grass
            # Curved stone pathway
            pts = np.array([[int(w*0.3), h], [int(w*0.4), int(h*0.4)], [int(w*0.55), int(h*0.4)], [int(w*0.65), h]], np.int32)
            cv2.fillPoly(frame, [pts], (140, 150, 160))
            # Flowerbeds
            for fx in range(60, 200, 35):
                cv2.circle(frame, (fx, int(h*0.75)), 12, (180, 60, 200), -1)
            # Guest walking in botanical garden
            px = int(w * 0.38 + w * 0.15 * t)
            py = int(h * 0.46)
            self._draw_person(frame, px, py, int(w*0.07), int(h*0.36), clothes_color=(40, 160, 80), pants_color=(40, 40, 50))

        elif cid == 10:
            # CAM-10: Garden Pathway (Botanical Walking Promenade)
            # Wooden footbridge over pond, bamboo walls
            frame[:] = (30, 70, 35)
            # Pond water
            cv2.ellipse(frame, (int(w*0.5), int(h*0.7)), (int(w*0.4), int(h*0.25)), 0, 0, 360, (120, 90, 40), -1)
            # Wooden footbridge
            cv2.rectangle(frame, (int(w*0.35), int(h*0.45)), (int(w*0.65), int(h*0.95)), (40, 65, 110), -1)
            cv2.line(frame, (int(w*0.35), int(h*0.45)), (int(w*0.35), int(h*0.95)), (20, 40, 80), 3)
            cv2.line(frame, (int(w*0.65), int(h*0.45)), (int(w*0.65), int(h*0.95)), (20, 40, 80), 3)
            # Jogger crossing bridge
            px = int(w * 0.45)
            py = int(h * 0.44 + h * 0.18 * wave)
            self._draw_person(frame, px, py, int(w*0.065), int(h*0.34), clothes_color=(0, 200, 240), pants_color=(30, 30, 30))

        elif cid == 11:
            # CAM-11: Conference Hall (Executive Convention Center)
            # Stage presentation, large glowing projection screen, theater chairs
            frame[0:int(h*0.55)] = (25, 20, 30)
            frame[int(h*0.55):] = (40, 40, 50)
            # Illuminated Presentation Screen
            cv2.rectangle(frame, (int(w*0.2), 45), (int(w*0.8), int(h*0.45)), (230, 240, 245), -1)
            cv2.putText(frame, "ANNUAL GLOBAL RESORT SUMMIT", (int(w*0.26), int(h*0.28)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 50, 60), 2)
            # Stage platform
            cv2.rectangle(frame, (int(w*0.1), int(h*0.45)), (int(w*0.9), int(h*0.55)), (70, 75, 85), -1)
            # Conference speaker in dark suit
            px = int(w * 0.4 + w * 0.2 * (0.5 + 0.5 * wave))
            py = int(h * 0.32)
            self._draw_person(frame, px, py, int(w*0.06), int(h*0.28), clothes_color=(25, 25, 25), pants_color=(25, 25, 25))

        elif cid == 12:
            # CAM-12: Conference Corridor
            # Modern geometric carpet, corporate banners, coffee station
            frame[0:int(h*0.45)] = (40, 45, 55)
            frame[int(h*0.45):] = (70, 60, 50) # Blue carpet
            # Corporate Banner Left
            cv2.rectangle(frame, (40, int(h*0.2)), (100, int(h*0.75)), (180, 80, 30), -1)
            # Coffee table
            cv2.rectangle(frame, (w - 120, int(h*0.55)), (w - 30, int(h*0.75)), (60, 80, 100), -1)
            # Attendee with tablet walking
            px = int(w * 0.3 + w * 0.35 * t)
            py = int(h * 0.48)
            self._draw_person(frame, px, py, int(w*0.07), int(h*0.35), clothes_color=(60, 60, 80), pants_color=(50, 50, 50))

        elif cid == 13:
            # CAM-13: First Floor Corridor (Guest Wing 1)
            # Classic red carpet hallway, suite doors, brass lights
            frame[0:int(h*0.5)] = (45, 45, 55)
            frame[int(h*0.5):] = (35, 35, 140) # Crimson carpet
            # Suite doors
            cv2.rectangle(frame, (70, int(h*0.25)), (130, int(h*0.75)), (30, 50, 80), -1)
            cv2.putText(frame, "101", (85, int(h*0.35)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            cv2.rectangle(frame, (w - 130, int(h*0.25)), (w - 70, int(h*0.75)), (30, 50, 80), -1)
            cv2.putText(frame, "102", (w - 115, int(h*0.35)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            # Guest walking down hallway
            px = int(w * 0.45 + w * 0.1 * wave)
            py = int(h * 0.46)
            self._draw_person(frame, px, py, int(w*0.07), int(h*0.36), clothes_color=(170, 70, 40), pants_color=(40, 40, 40))

        elif cid == 14:
            # CAM-14: Second Floor Corridor (Guest Wing 2)
            # Modern navy carpet, silver elevator doors
            frame[0:int(h*0.5)] = (50, 50, 55)
            frame[int(h*0.5):] = (120, 60, 30) # Navy carpet
            # Elevator doors in center
            cv2.rectangle(frame, (int(w*0.4), int(h*0.2)), (int(w*0.6), int(h*0.75)), (180, 185, 190), -1)
            cv2.line(frame, (int(w*0.5), int(h*0.2)), (int(w*0.5), int(h*0.75)), (100, 100, 100), 2)
            # Up arrow indicator
            cv2.circle(frame, (int(w*0.5), int(h*0.16)), 6, (0, 255, 0), -1)
            # Guest stepping out of elevator
            px = int(w * 0.46 + w * 0.15 * wave)
            py = int(h * 0.48)
            self._draw_person(frame, px, py, int(w*0.07), int(h*0.36), clothes_color=(190, 140, 40), pants_color=(30, 30, 30))

        elif cid == 15:
            # CAM-15: Room Block A Entrance
            # Terracotta tile breezeway, tropical hanging plants
            frame[0:int(h*0.45)] = (180, 190, 200) # Open sky
            frame[int(h*0.45):] = (50, 70, 150)   # Terracotta tiles
            # White columns
            cv2.rectangle(frame, (60, 40), (95, int(h*0.8)), (230, 235, 240), -1)
            cv2.rectangle(frame, (w - 95, 40), (w - 60, int(h*0.8)), (230, 235, 240), -1)
            # Hanging plant
            cv2.circle(frame, (int(w*0.5), 70), 25, (40, 130, 50), -1)
            # Resident returning to room
            px = int(w * 0.3 + w * 0.4 * t)
            py = int(h * 0.48)
            self._draw_person(frame, px, py, int(w*0.07), int(h*0.36), clothes_color=(60, 140, 200), pants_color=(40, 40, 40))

        elif cid == 16:
            # CAM-16: Room Block B Entrance
            # Courtyard with stone water fountain
            frame[0:int(h*0.4)] = (160, 170, 180)
            frame[int(h*0.4):] = (100, 105, 110) # Cobblestone
            # Center fountain
            cv2.ellipse(frame, (int(w*0.5), int(h*0.75)), (80, 30), 0, 0, 360, (80, 85, 90), -1)
            cv2.circle(frame, (int(w*0.5), int(h*0.68)), 15, (180, 140, 50), -1)
            # Spraying water drops
            for i in range(5):
                wy = int(h * 0.58 + math.sin(t * 10 + i) * 10)
                cv2.circle(frame, (int(w*0.5) - 15 + i * 8, wy), 3, (240, 210, 150), -1)
            # Walking resident
            px = int(w * 0.2 + w * 0.2 * wave)
            py = int(h * 0.46)
            self._draw_person(frame, px, py, int(w*0.07), int(h*0.35), clothes_color=(120, 50, 160), pants_color=(40, 40, 40))

        elif cid == 17:
            # CAM-17: Room Block C Entrance
            # Panoramic elevated balcony overlooking hills
            frame[0:int(h*0.5)] = (220, 170, 110) # Sunny mountain view
            # Mountain silhouettes
            pts = np.array([[0, int(h*0.5)], [int(w*0.3), int(h*0.3)], [int(w*0.7), int(h*0.4)], [w, int(h*0.25)], [w, int(h*0.5)]], np.int32)
            cv2.fillPoly(frame, [pts], (90, 120, 70))
            frame[int(h*0.5):] = (60, 65, 75)
            # Balcony railing
            for rx in range(0, w, 25):
                cv2.line(frame, (rx, int(h*0.5)), (rx, int(h*0.7)), (30, 30, 30), 2)
            cv2.line(frame, (0, int(h*0.5)), (w, int(h*0.5)), (30, 30, 30), 4)
            # Guest walking on balcony
            px = int(w * 0.35 + w * 0.3 * (0.5 + 0.5 * wave))
            py = int(h * 0.52)
            self._draw_person(frame, px, py, int(w*0.07), int(h*0.36), clothes_color=(40, 170, 190), pants_color=(40, 40, 40))

        elif cid == 18:
            # CAM-18: Spa Entrance (Ayurvedic Wellness Spa)
            # Zen bamboo screen, warm lanterns, peaceful wood tones
            frame[0:int(h*0.5)] = (30, 45, 60) # Warm wood
            frame[int(h*0.5):] = (70, 75, 80) # Smooth river stone
            # Bamboo sticks screen
            for bx in range(30, 180, 15):
                cv2.line(frame, (bx, 40), (bx, int(h*0.75)), (40, 110, 130), 4)
            # Glowing Japanese lantern
            cv2.circle(frame, (w - 80, int(h*0.3)), 22, (50, 190, 240), -1)
            # Spa guest in white robe
            px = int(w * 0.45 + w * 0.15 * t)
            py = int(h * 0.46)
            self._draw_person(frame, px, py, int(w*0.075), int(h*0.37), clothes_color=(240, 240, 245), pants_color=(240, 240, 245))

        elif cid == 19:
            # CAM-19: Gym Entrance (Fitness Center)
            # Mirrored glass wall, treadmill machines, rubber gym flooring
            frame[0:int(h*0.45)] = (60, 60, 65) # Mirrored reflection
            frame[int(h*0.45):] = (30, 30, 35) # Black rubber flooring
            # Treadmill 1
            cv2.rectangle(frame, (60, int(h*0.55)), (140, int(h*0.75)), (70, 70, 80), -1)
            cv2.line(frame, (130, int(h*0.55)), (120, int(h*0.4)), (120, 120, 120), 4)
            # Treadmill 2
            cv2.rectangle(frame, (180, int(h*0.55)), (260, int(h*0.75)), (70, 70, 80), -1)
            cv2.line(frame, (250, int(h*0.55)), (240, int(h*0.4)), (120, 120, 120), 4)
            # Gym attendee with towel
            px = int(w * 0.55 + w * 0.1 * wave)
            py = int(h * 0.46)
            self._draw_person(frame, px, py, int(w*0.07), int(h*0.36), clothes_color=(40, 40, 210), pants_color=(30, 30, 30))

        elif cid == 20:
            # CAM-20: Activity Zone (Sports & Kids Club)
            # Vibrant recreation sports court with court markings
            frame[0:int(h*0.4)] = (200, 160, 90)
            frame[int(h*0.4):] = (50, 130, 70) # Green sports court
            # Tennis court white lines
            cv2.rectangle(frame, (int(w*0.15), int(h*0.5)), (int(w*0.85), int(h*0.9)), (255, 255, 255), 2)
            cv2.line(frame, (int(w*0.5), int(h*0.5)), (int(w*0.5), int(h*0.9)), (255, 255, 255), 2)
            # Active player in sports attire
            px = int(w * 0.45 + w * 0.22 * wave)
            py = int(h * 0.48)
            self._draw_person(frame, px, py, int(w*0.07), int(h*0.35), clothes_color=(240, 210, 0), pants_color=(230, 230, 230))

        elif cid == 21:
            # CAM-21: Parking Exit (North Parking Outgate)
            # Asphalt exit lane, yellow directional arrows, exit barrier
            frame[0:int(h*0.45)] = (180, 140, 80)
            frame[int(h*0.45):] = (45, 45, 48)
            # Directional painted arrow on asphalt
            cv2.arrowedLine(frame, (int(w*0.5), int(h*0.8)), (int(w*0.5), int(h*0.55)), (0, 220, 255), 6, tipLength=0.3)
            # Exit barrier pole
            cv2.line(frame, (int(w*0.2), int(h*0.6)), (int(w*0.75), int(h*0.6)), (0, 0, 255), 4)
            # Patrol guard / driver
            px = int(w * 0.3 + w * 0.25 * t)
            py = int(h * 0.46)
            self._draw_person(frame, px, py, int(w*0.065), int(h*0.35), clothes_color=(70, 80, 90), pants_color=(30, 30, 30))

        elif cid == 22:
            # CAM-22: Service Entrance (RESTRICTED ZONE)
            # Industrial loading dock, yellow/black hazard diagonal stripes, restricted sign
            frame[:] = (35, 38, 42)
            # Hazard stripes along top and bottom
            for x in range(0, w, 40):
                cv2.line(frame, (x, 40), (x + 20, 65), (0, 220, 240), 8)
                cv2.line(frame, (x, h - 35), (x + 20, h - 10), (0, 220, 240), 8)
            # Heavy industrial metal doors
            cv2.rectangle(frame, (int(w*0.3), 70), (int(w*0.7), int(h*0.85)), (75, 80, 85), -1)
            cv2.rectangle(frame, (int(w*0.3), 70), (int(w*0.7), int(h*0.85)), (30, 30, 35), 3)
            # RESTRICTED AREA Warning Placard
            cv2.rectangle(frame, (int(w*0.38), 90), (int(w*0.62), 130), (0, 0, 220), -1)
            cv2.putText(frame, "RESTRICTED", (int(w*0.41), 115), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            # Unauthorized person breach entering restricted zone
            px = int(w * 0.45 + w * 0.08 * wave)
            py = int(h * 0.48)
            self._draw_person(frame, px, py, int(w*0.07), int(h*0.36), clothes_color=(60, 60, 60), pants_color=(20, 20, 20))

        elif cid == 23:
            # CAM-23: Back Garden (South Nature Reserve)
            # Deep pine forest trail, rustic wooden fence, fireflies/motes
            frame[0:int(h*0.4)] = (20, 50, 25) # Dense pine foliage
            frame[int(h*0.4):] = (30, 55, 65)  # Dirt forest trail
            # Wooden rustic fence
            for fx in range(20, w, 45):
                cv2.line(frame, (fx, int(h*0.5)), (fx, int(h*0.75)), (25, 45, 75), 4)
            cv2.line(frame, (0, int(h*0.55)), (w, int(h*0.55)), (25, 45, 75), 4)
            # Nature walker
            px = int(w * 0.35 + w * 0.3 * t)
            py = int(h * 0.48)
            self._draw_person(frame, px, py, int(w*0.065), int(h*0.34), clothes_color=(40, 140, 110), pants_color=(40, 40, 40))

        elif cid == 24:
            # CAM-24: Beach/Outdoor Area (Private Resort Beachfront)
            # Golden sand beach, ocean shoreline with animated rolling waves, thatched tiki umbrella
            frame[0:int(h*0.35)] = (220, 160, 90) # Sunset ocean sky
            frame[int(h*0.35):int(h*0.6)] = (180, 110, 40) # Deep sea blue
            frame[int(h*0.6):] = (120, 180, 220) # Golden beach sand
            # Ocean rolling waves
            wave_x = int(wave * 20)
            cv2.line(frame, (0, int(h*0.6) + wave_x // 3), (w, int(h*0.6) - wave_x // 3), (245, 245, 250), 4)
            # Thatched beach tiki hut umbrella
            cv2.line(frame, (w - 100, int(h*0.65)), (w - 100, int(h*0.4)), (30, 50, 80), 4)
            cv2.ellipse(frame, (w - 100, int(h*0.4)), (55, 20), 0, 180, 360, (50, 100, 150), -1)
            # Target P001 or beachgoer walking on sand
            px = int(w * 0.25 + w * 0.4 * (0.5 - 0.5 * wave))
            py = int(h * 0.52)
            self._draw_person(frame, px, py, int(w*0.075), int(h*0.36), clothes_color=(140, 80, 30), pants_color=(30, 30, 30))

        else:
            # CAM-25: Exit Gate (South Main Exit Gate)
            # Brick gateposts, ornate wrought iron gate, perimeter boundary
            frame[0:int(h*0.45)] = (170, 140, 90)
            frame[int(h*0.45):] = (50, 50, 55) # Paved sidewalk
            # Brick Gatepost Left
            cv2.rectangle(frame, (50, int(h*0.25)), (110, int(h*0.75)), (40, 50, 120), -1)
            # Brick Gatepost Right
            cv2.rectangle(frame, (w - 110, int(h*0.25)), (w - 50, int(h*0.75)), (40, 50, 120), -1)
            # Iron fence bars
            for ix in range(110, w - 110, 20):
                cv2.line(frame, (ix, int(h*0.35)), (ix, int(h*0.75)), (25, 25, 30), 2)
            # Departing guest heading out
            px = int(w * 0.35 + w * 0.3 * t)
            py = int(h * 0.48)
            self._draw_person(frame, px, py, int(w*0.07), int(h*0.36), clothes_color=(50, 50, 120), pants_color=(30, 30, 30))

        return frame

    def _draw_person(self, frame: np.ndarray, px: int, py: int, pw: int, ph: int, clothes_color, pants_color):
        """
        Renders an anatomically proportioned moving person with skin tone, clothing, and legs.
        """
        # Head & Skin Tone
        head_radius = max(6, ph // 7)
        head_center = (px + pw // 2, py + head_radius + 2)
        cv2.circle(frame, head_center, head_radius, (200, 180, 150), -1)
        # Hair
        cv2.ellipse(frame, (head_center[0], head_center[1] - 2), (head_radius, head_radius // 2), 0, 180, 360, (30, 25, 20), -1)

        # Torso & Clothing
        torso_top = head_center[1] + head_radius
        torso_bot = py + int(ph * 0.6)
        cv2.rectangle(frame, (px + int(pw*0.15), torso_top), (px + int(pw*0.85), torso_bot), clothes_color, -1)

        # Arms
        cv2.line(frame, (px + int(pw*0.15), torso_top + 4), (px + int(pw*0.05), torso_bot - 4), clothes_color, 3)
        cv2.line(frame, (px + int(pw*0.85), torso_top + 4), (px + int(pw*0.95), torso_bot - 4), clothes_color, 3)

        # Legs & Trousers
        leg_top = torso_bot
        leg_bot = py + ph
        # Walking leg stride
        stride = int(math.sin(self.frame_idx * 0.3) * 6)
        cv2.line(frame, (px + int(pw*0.35), leg_top), (px + int(pw*0.3) - stride, leg_bot), pants_color, 4)
        cv2.line(frame, (px + int(pw*0.65), leg_top), (px + int(pw*0.7) + stride, leg_bot), pants_color, 4)

        # Shoes
        cv2.circle(frame, (px + int(pw*0.3) - stride, leg_bot), 3, (15, 15, 15), -1)
        cv2.circle(frame, (px + int(pw*0.7) + stride, leg_bot), 3, (15, 15, 15), -1)

        # Record bounding box for ground truth AI tracking
        self.current_person_bbox = (px, py, pw, ph)

    def get_ground_truth_bbox(self):
        return self.current_person_bbox

    def release(self):
        pass
