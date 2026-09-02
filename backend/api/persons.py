from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.schemas.person import PersonResponse, RegistrationResponse
from backend.schemas.detection import MovementTimelineItem
from backend.services.person_service import person_service
from backend.models.person import MovementHistory, Person
from backend.utils.security import require_admin, require_operator

router = APIRouter(prefix="/api/persons", tags=["Persons"])

@router.get("", response_model=List[PersonResponse])
def list_persons(db: Session = Depends(get_db)):
    return person_service.get_all_persons(db)

@router.post("/register", response_model=RegistrationResponse)
async def register_person(
    file: UploadFile = File(...),
    person_code: str = Form(...),
    full_name: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user=Depends(require_operator)
):
    """
    Primary Research Requirement: Single-reference-image registration.
    Extracts face & body embeddings, assesses quality score, and stores reference model.
    """
    image_bytes = await file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    return person_service.register_person(
        image_bytes=image_bytes,
        person_code=person_code.strip().upper(),
        full_name=full_name,
        notes=notes,
        db=db
    )

@router.get("/{person_id}")
def get_person_dossier(person_id: int, db: Session = Depends(get_db)):
    return person_service.get_person_dossier(person_id, db)

@router.delete("/{person_id}")
def delete_person(person_id: int, db: Session = Depends(get_db), user=Depends(require_admin)):
    person_service.delete_person(person_id, db)
    return {"message": f"Person ID {person_id} and biometric profiles purged."}

@router.get("/{person_id}/timeline", response_model=List[MovementTimelineItem])
def get_person_timeline(person_id: int, db: Session = Depends(get_db)):
    movements = db.query(MovementHistory).filter(
        MovementHistory.person_id == person_id
    ).order_by(MovementHistory.entry_time.asc()).all()
    return [m.to_dict() for m in movements]
