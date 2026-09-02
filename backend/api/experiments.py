from fastapi import APIRouter
from pydantic import BaseModel
from backend.schemas.experiment import ExperimentComparisonResponse, ExperimentRunRequest
from backend.ai.fusion.experiment_runner import experiment_runner
from backend.ai.fusion.multimodal_fusion import fusion_engine
from backend.config import settings

router = APIRouter(prefix="/api/experiments", tags=["Experiments"])

class WeightUpdateRequest(BaseModel):
    w_face: float
    w_reid: float
    w_temp: float
    w_cam: float

@router.get("/results", response_model=ExperimentComparisonResponse)
def get_benchmark_results():
    return experiment_runner.run_benchmark(num_samples=80)

@router.post("/run", response_model=ExperimentComparisonResponse)
def run_benchmark(request: ExperimentRunRequest):
    return experiment_runner.run_benchmark(num_samples=request.num_test_sequences)

@router.get("/weights")
def get_fusion_weights():
    return {
        "w_face": fusion_engine.w_face,
        "w_reid": fusion_engine.w_reid,
        "w_temp": fusion_engine.w_temp,
        "w_cam": fusion_engine.w_cam,
        "identity_threshold": fusion_engine.identity_threshold
    }

@router.post("/weights")
def update_fusion_weights(req: WeightUpdateRequest):
    fusion_engine.update_weights(
        w_face=req.w_face,
        w_reid=req.w_reid,
        w_temp=req.w_temp,
        w_cam=req.w_cam
    )
    return {
        "message": "Fusion weights updated successfully.",
        "active_weights": {
            "w_face": fusion_engine.w_face,
            "w_reid": fusion_engine.w_reid,
            "w_temp": fusion_engine.w_temp,
            "w_cam": fusion_engine.w_cam
        }
    }
