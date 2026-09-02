from typing import List, Optional
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.schemas.alert import AlertResponse, AlertUpdate
from backend.services.anomaly_service import anomaly_service
from backend.services.export_service import export_service
from backend.utils.security import require_operator

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

@router.get("", response_model=List[AlertResponse])
def get_alerts(status: Optional[str] = None, db: Session = Depends(get_db)):
    return anomaly_service.get_all_alerts(db, status_filter=status)

@router.put("/{alert_id}/status", response_model=AlertResponse)
def update_alert_status(alert_id: int, status_in: AlertUpdate, db: Session = Depends(get_db), user=Depends(require_operator)):
    return anomaly_service.update_alert_status(alert_id, status_in.status, db)

@router.get("/export/csv")
def export_alerts_csv(db: Session = Depends(get_db)):
    csv_data = export_service.export_alerts_csv(db)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=alerts_log.csv"}
    )
