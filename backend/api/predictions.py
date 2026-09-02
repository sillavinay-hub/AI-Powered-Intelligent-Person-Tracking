from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.services.prediction_service import prediction_service

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])

@router.get("/{person_id}")
def get_movement_prediction(person_id: int, db: Session = Depends(get_db)):
    """
    Returns Markov transition prediction of the next camera destination for the target person.
    """
    return prediction_service.predict_next_camera(person_id, db)
