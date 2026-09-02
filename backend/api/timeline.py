from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.models.person import Person, MovementHistory
from backend.services.export_service import export_service

router = APIRouter(prefix="/api/timeline", tags=["Timeline"])

@router.get("/{person_code}")
def get_timeline_by_code(person_code: str, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.person_code == person_code.upper()).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    movements = db.query(MovementHistory).filter(
        MovementHistory.person_id == person.id
    ).order_by(MovementHistory.entry_time.asc()).all()

    return {
        "person_code": person.person_code,
        "full_name": person.full_name,
        "total_stops": len(movements),
        "timeline": [m.to_dict() for m in movements]
    }

@router.get("/{person_code}/export/csv")
def export_timeline_csv(person_code: str, db: Session = Depends(get_db)):
    csv_data = export_service.export_timeline_csv(person_code, db)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={person_code}_timeline.csv"}
    )
