from typing import List, Dict, Optional
from pydantic import BaseModel

class ExperimentMetrics(BaseModel):
    experiment_id: str
    name: str
    description: str
    weights: Dict[str, float]
    accuracy: float
    precision: float
    recall: float
    reid_rank1: float
    reid_map: float
    idf1: float
    hota: float
    mota: float
    id_switches: int
    fps: float
    latency_ms: float

class ExperimentRunRequest(BaseModel):
    num_test_sequences: int = 100
    dataset_split: str = "synthetic_resort_benchmark"

class ExperimentComparisonResponse(BaseModel):
    timestamp: str
    dataset: str
    num_samples: int
    experiments: List[ExperimentMetrics]
    research_conclusion: str
