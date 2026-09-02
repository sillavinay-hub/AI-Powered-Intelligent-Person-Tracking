import networkx as nx
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from backend.models.camera import Camera, CameraTransition
from backend.utils.logger import logger

class CameraTransitionService:
    """
    Manages the 25-camera topological transition graph using NetworkX.
    Evaluates spatial feasibility and camera transition likelihood between camera pairs.
    """
    def __init__(self):
        self.graph = nx.DiGraph()
        self.is_initialized = False

    def build_graph(self, db: Session):
        self.graph.clear()
        cameras = db.query(Camera).all()
        for c in cameras:
            self.graph.add_node(
                c.id,
                camera_code=c.camera_code,
                name=c.name,
                location=c.location,
                map_x=c.map_x,
                map_y=c.map_y
            )

        transitions = db.query(CameraTransition).all()
        for t in transitions:
            self.graph.add_edge(
                t.from_camera_id,
                t.to_camera_id,
                min_sec=t.min_duration_sec,
                max_sec=t.max_duration_sec,
                prob=t.transition_probability,
                weight=1.0 / max(0.01, t.transition_probability)
            )

        self.is_initialized = True
        logger.info(f"Built Camera Transition Graph: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges.")

    def get_transition_score(self, from_cam_id: int, to_cam_id: int, db: Optional[Session] = None) -> float:
        """
        Returns transition probability prior [0.0 - 1.0].
        If same camera: 0.95.
        If direct edge exists: edge probability.
        If multi-hop path exists: compound probability.
        If disconnected: 0.05.
        """
        if from_cam_id == to_cam_id:
            return 0.95

        if not self.is_initialized and db is not None:
            self.build_graph(db)

        if not self.graph.has_node(from_cam_id) or not self.graph.has_node(to_cam_id):
            return 0.20

        # Direct transition
        if self.graph.has_edge(from_cam_id, to_cam_id):
            return self.graph[from_cam_id][to_cam_id].get("prob", 0.5)

        # Path search
        try:
            path = nx.shortest_path(self.graph, source=from_cam_id, target=to_cam_id, weight="weight")
            hops = len(path) - 1
            # Decay with number of topological hops
            prob = 0.5 * (0.6 ** (hops - 1))
            return max(0.05, float(prob))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return 0.05

    def get_expected_transition_time(self, from_cam_id: int, to_cam_id: int, db: Optional[Session] = None) -> Tuple[float, float]:
        """
        Returns (min_sec, max_sec) walking transit window.
        """
        if from_cam_id == to_cam_id:
            return 0.0, 0.0

        if not self.is_initialized and db is not None:
            self.build_graph(db)

        if self.graph.has_edge(from_cam_id, to_cam_id):
            edge = self.graph[from_cam_id][to_cam_id]
            return edge.get("min_sec", 5.0), edge.get("max_sec", 120.0)

        try:
            path = nx.shortest_path(self.graph, source=from_cam_id, target=to_cam_id)
            total_min = 0.0
            total_max = 0.0
            for u, v in zip(path[:-1], path[1:]):
                e = self.graph[u][v]
                total_min += e.get("min_sec", 10.0)
                total_max += e.get("max_sec", 120.0)
            return total_min, total_max
        except Exception:
            return 30.0, 600.0

    def get_map_graph(self, db: Session) -> Dict[str, Any]:
        """
        Serializes entire graph for frontend 2D Resort Map visualization.
        """
        if not self.is_initialized:
            self.build_graph(db)

        nodes = []
        cameras = db.query(Camera).all()
        for c in cameras:
            nodes.append({
                "id": c.id,
                "code": c.camera_code,
                "name": c.name,
                "location": c.location,
                "x": c.map_x,
                "y": c.map_y,
                "status": c.status,
                "ai_enabled": c.ai_enabled
            })

        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({
                "from": u,
                "to": v,
                "prob": round(data.get("prob", 0.5), 2),
                "min_sec": data.get("min_sec", 5.0),
                "max_sec": data.get("max_sec", 120.0)
            })

        return {
            "resort_name": "ResortVision Oasis Resort & Spa",
            "total_cameras": len(nodes),
            "nodes": nodes,
            "edges": edges
        }

transition_service = CameraTransitionService()
