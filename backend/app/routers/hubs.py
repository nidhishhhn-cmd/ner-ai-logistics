"""
Logistics Hubs Router
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.connection import get_db
from app.models.models import LogisticsHub
from app.schemas.schemas import HubOut

router = APIRouter(prefix="/api/hubs", tags=["hubs"])


def hub_to_out(h: LogisticsHub) -> HubOut:
    return HubOut(
        id=h.id, name=h.name, city_id=h.city_id,
        city_name=h.city.name if h.city else None,
        state_name=h.city.state.name if h.city and h.city.state else None,
        hub_type=h.hub_type,
        connectivity_score=h.connectivity_score,
        road_connectivity=h.road_connectivity,
        rail_connectivity=h.rail_connectivity,
        air_connectivity=h.air_connectivity,
        storage_capacity_tons=h.storage_capacity_tons,
        storage_available_percent=h.storage_available_percent,
        status=h.status,
        lat=h.lat, lng=h.lng,
        description=h.description
    )


@router.get("", response_model=List[HubOut])
def get_hubs(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(LogisticsHub)
    if status:
        query = query.filter(LogisticsHub.status == status)
    hubs = query.all()
    if search:
        search_lower = search.lower()
        hubs = [h for h in hubs if search_lower in h.name.lower() or
                (h.city and search_lower in h.city.name.lower())]
    return [hub_to_out(h) for h in hubs]


@router.get("/{hub_id}", response_model=HubOut)
def get_hub(hub_id: int, db: Session = Depends(get_db)):
    hub = db.query(LogisticsHub).filter(LogisticsHub.id == hub_id).first()
    if not hub:
        raise HTTPException(status_code=404, detail="Hub not found")
    return hub_to_out(hub)
