"""
States and Cities Router
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.connection import get_db
from app.models.models import State, City
from app.schemas.schemas import StateOut, CityOut, SearchResult

router = APIRouter(tags=["geography"])


@router.get("/api/states", response_model=List[StateOut])
def get_states(db: Session = Depends(get_db)):
    return db.query(State).all()


@router.get("/api/states/{state_id}", response_model=StateOut)
def get_state(state_id: int, db: Session = Depends(get_db)):
    state = db.query(State).filter(State.id == state_id).first()
    if not state:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="State not found")
    return state


@router.get("/api/cities", response_model=List[CityOut])
def get_cities(
    state_id: Optional[int] = Query(None),
    major_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    query = db.query(City)
    if state_id:
        query = query.filter(City.state_id == state_id)
    if major_only:
        query = query.filter(City.is_major == True)
    cities = query.all()
    result = []
    for c in cities:
        state_name = c.state.name if c.state else None
        result.append(CityOut(
            id=c.id, name=c.name, state_id=c.state_id,
            state_name=state_name,
            lat=c.lat, lng=c.lng, population=c.population,
            is_major=c.is_major, has_airport=c.has_airport,
            has_railway=c.has_railway, connectivity_score=c.connectivity_score
        ))
    return result


@router.get("/api/cities/{city_id}", response_model=CityOut)
def get_city(city_id: int, db: Session = Depends(get_db)):
    c = db.query(City).filter(City.id == city_id).first()
    if not c:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="City not found")
    return CityOut(
        id=c.id, name=c.name, state_id=c.state_id,
        state_name=c.state.name if c.state else None,
        lat=c.lat, lng=c.lng, population=c.population,
        is_major=c.is_major, has_airport=c.has_airport,
        has_railway=c.has_railway, connectivity_score=c.connectivity_score
    )


@router.get("/api/search", response_model=List[SearchResult])
def search(q: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    results = []
    q_lower = q.lower()

    cities = db.query(City).all()
    for c in cities:
        if q_lower in c.name.lower():
            state_name = c.state.name if c.state else ""
            results.append(SearchResult(
                type="city", id=c.id, name=c.name,
                subtitle=f"{state_name} • {'Major' if c.is_major else 'City'}",
                url=f"/routes?city={c.id}"
            ))

    states = db.query(State).all()
    for s in states:
        if q_lower in s.name.lower():
            results.append(SearchResult(
                type="state", id=s.id, name=s.name,
                subtitle=f"State • Capital: {s.capital}",
                url=f"/analytics?state={s.code}"
            ))

    from app.models.models import Route, LogisticsHub, Alert
    routes = db.query(Route).all()
    for r in routes:
        if q_lower in r.name.lower():
            results.append(SearchResult(
                type="route", id=r.id, name=r.name,
                subtitle=f"{r.transport_mode.title()} • {r.distance_km:.0f} km",
                url=f"/routes?route={r.id}"
            ))

    hubs = db.query(LogisticsHub).all()
    for h in hubs:
        if q_lower in h.name.lower():
            results.append(SearchResult(
                type="hub", id=h.id, name=h.name,
                subtitle=f"Hub • {h.hub_type} • Score: {h.connectivity_score:.0f}",
                url=f"/hubs?hub={h.id}"
            ))

    alerts = db.query(Alert).filter(Alert.is_active == True).all()
    for a in alerts:
        if q_lower in a.title.lower() or q_lower in a.location.lower():
            results.append(SearchResult(
                type="alert", id=a.id, name=a.title,
                subtitle=f"{a.severity.upper()} • {a.category.replace('_', ' ').title()}",
                url=f"/alerts?alert={a.id}"
            ))

    return results[:20]
