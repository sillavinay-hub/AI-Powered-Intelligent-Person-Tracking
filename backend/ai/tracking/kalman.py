import numpy as np

class KalmanBoxTracker:
    """
    Kalman filter for tracking single bounding box in image space.
    State: [x, y, a, h, vx, vy, va, vh]
    """
    count = 0

    def __init__(self, bbox: list):
        # bbox: [x1, y1, x2, y2]
        self.id = KalmanBoxTracker.count + 1
        KalmanBoxTracker.count += 1

        self.time_since_update = 0
        self.history = []
        self.hits = 1
        self.hit_streak = 1
        self.age = 0

        # Initialize state [cx, cy, a, h]
        w = max(1.0, float(bbox[2] - bbox[0]))
        h = max(1.0, float(bbox[3] - bbox[1]))
        cx = bbox[0] + w / 2.0
        cy = bbox[1] + h / 2.0
        a = w / h

        self.x = np.array([cx, cy, a, h, 0, 0, 0, 0], dtype=float).reshape((8, 1))

        # Covariance matrices
        self.P = np.diag([10, 10, 10, 10, 10000, 10000, 10000, 10000]).astype(float)
        self.F = np.eye(8, dtype=float)
        for i in range(4):
            self.F[i, i + 4] = 1.0

        self.H = np.zeros((4, 8), dtype=float)
        for i in range(4):
            self.H[i, i] = 1.0

        self.R = np.diag([1, 1, 10, 10]).astype(float)
        self.Q = np.eye(8, dtype=float) * 0.01

    def update(self, bbox: list):
        self.time_since_update = 0
        self.history = []
        self.hits += 1
        self.hit_streak += 1

        w = max(1.0, float(bbox[2] - bbox[0]))
        h = max(1.0, float(bbox[3] - bbox[1]))
        cx = bbox[0] + w / 2.0
        cy = bbox[1] + h / 2.0
        a = w / h
        z = np.array([cx, cy, a, h], dtype=float).reshape((4, 1))

        y = z - np.dot(self.H, self.x)
        S = np.dot(self.H, np.dot(self.P, self.H.T)) + self.R
        K = np.dot(self.P, np.dot(self.H.T, np.linalg.inv(S)))
        self.x = self.x + np.dot(K, y)
        self.P = self.P - np.dot(K, np.dot(self.H, self.P))

    def predict(self) -> list:
        # Predict next state
        if (self.x[6] + self.x[2]) <= 0:
            self.x[6] = 0.0
        self.x = np.dot(self.F, self.x)
        self.P = np.dot(self.F, np.dot(self.P, self.F.T)) + self.Q
        self.age += 1
        if self.time_since_update > 0:
            self.hit_streak = 0
        self.time_since_update += 1
        self.history.append(self.get_state())
        return self.history[-1]

    def get_state(self) -> list:
        # Convert [cx, cy, a, h] -> [x1, y1, x2, y2]
        cx, cy, a, h = self.x[0, 0], self.x[1, 0], max(1e-4, self.x[2, 0]), max(1.0, self.x[3, 0])
        w = a * h
        x1 = cx - w / 2.0
        y1 = cy - h / 2.0
        x2 = cx + w / 2.0
        y2 = cy + h / 2.0
        return [int(x1), int(y1), int(x2), int(y2)]
