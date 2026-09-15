"""
Dashboard/KPI Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import State, Route, LogisticsHub, Alert

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/kpis")
def get_kpis(db: Session = Depends(get_db)):
    routes = db.query(Route).filter(Route.is_active == True).all()
    hubs = db.query(LogisticsHub).all()
    alerts = db.query(Alert).filter(Alert.is_active == True).all()
    states = db.query(State).all()

    avg_acc = sum(s.accessibility_score for s in states) / len(states) if states else 0
    high_risk = sum(1 for r in routes if r.risk_score > 60)
    critical_alerts = sum(1 for a in alerts if a.severity == "critical")
    avg_time = sum(r.base_travel_time_hours for r in routes) / len(routes) if routes else 0

    return {
        "active_routes": len(routes),
        "avg_accessibility": round(avg_acc, 1),
        "high_risk_routes": high_risk,
        "logistics_hubs": len(hubs),
        "active_alerts": len(alerts),
        "critical_alerts": critical_alerts,
        "avg_delivery_time_hours": round(avg_time, 1),
        "total_states": len(states),
        "data_source": "Demo Data (Simulated)"
    }
