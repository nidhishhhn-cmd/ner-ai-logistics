"""
Analytics Router
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from app.database.connection import get_db
from app.models.models import State, City, Route, LogisticsHub, Alert
from app.schemas.schemas import AnalyticsResponse, StateAccessibility

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/accessibility", response_model=AnalyticsResponse)
def get_accessibility_analytics(
    state_code: Optional[str] = Query(None),
    transport_mode: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    states = db.query(State).all()
    routes = db.query(Route).filter(Route.is_active == True).all()
    hubs = db.query(LogisticsHub).all()
    alerts = db.query(Alert).filter(Alert.is_active == True).all()

    state_stats = []
    for state in states:
        state_routes = [r for r in routes
                        if (r.origin and r.origin.state_id == state.id) or
                           (r.destination and r.destination.state_id == state.id)]
        state_hubs = [h for h in hubs if h.city and h.city.state_id == state.id]

        avg_time = 8.0
        if state_routes:
            avg_time = sum(r.base_travel_time_hours for r in state_routes) / len(state_routes)

        state_stats.append(StateAccessibility(
            state=state.name,
            accessibility_score=round(state.accessibility_score, 1),
            avg_delivery_time_hours=round(avg_time, 1),
            route_count=len(state_routes),
            hub_count=len(state_hubs)
        ))

    # Transport mode distribution
    mode_counts = {}
    for r in routes:
        mode_counts[r.transport_mode] = mode_counts.get(r.transport_mode, 0) + 1

    # Risk distribution
    low_risk = sum(1 for r in routes if r.risk_score < 33)
    med_risk = sum(1 for r in routes if 33 <= r.risk_score < 66)
    high_risk = sum(1 for r in routes if r.risk_score >= 66)

    # Monthly disruptions (simulated last 6 months)
    monthly = [
        {"month": "Apr", "disruptions": 8, "alerts": 5},
        {"month": "May", "disruptions": 12, "alerts": 9},
        {"month": "Jun", "disruptions": 18, "alerts": 14},
        {"month": "Jul", "disruptions": 24, "alerts": 19},
        {"month": "Aug", "disruptions": 22, "alerts": 17},
        {"month": "Sep", "disruptions": 15, "alerts": 10},
    ]

    avg_acc = sum(s.accessibility_score for s in state_stats) / len(state_stats) if state_stats else 0

    return AnalyticsResponse(
        states=state_stats,
        total_routes=len(routes),
        total_hubs=len(hubs),
        active_alerts=len(alerts),
        avg_accessibility=round(avg_acc, 1),
        transport_distribution=mode_counts,
        risk_distribution={"low": low_risk, "medium": med_risk, "high": high_risk},
        monthly_disruptions=monthly
    )


@router.get("/routes")
def get_route_analytics(db: Session = Depends(get_db)):
    routes = db.query(Route).filter(Route.is_active == True).all()
    return {
        "total": len(routes),
        "by_mode": {
            "road": sum(1 for r in routes if r.transport_mode == "road"),
            "rail": sum(1 for r in routes if r.transport_mode == "rail"),
            "air": sum(1 for r in routes if r.transport_mode == "air"),
            "multimodal": sum(1 for r in routes if r.transport_mode == "multimodal"),
        },
        "avg_distance_km": round(sum(r.distance_km for r in routes) / len(routes), 1) if routes else 0,
        "avg_travel_time_hours": round(sum(r.base_travel_time_hours for r in routes) / len(routes), 1) if routes else 0,
        "avg_accessibility_score": round(sum(r.accessibility_score for r in routes) / len(routes), 1) if routes else 0,
    }
