"""
Routes Router - Smart Route Planning & Optimization
Provides high-precision exact road geometry, curved flight arcs,
railway corridors, and multimodal transit routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import math

from app.database.connection import get_db
from app.models.models import Route, City, Alert
from app.schemas.schemas import RouteOptimizeRequest, RouteOptimizeResponse, RouteOut, RouteScore
from app.services.ai_service import score_routes, PRIORITY_WEIGHTS
from app.services.routing_engine import (
    get_exact_road_route,
    generate_flight_arc,
    generate_rail_corridor,
    haversine_distance,
    interpolate_curved_path
)

router = APIRouter(prefix="/api/routes", tags=["routes"])


@router.get("", response_model=List[RouteOut])
def get_routes(
    origin_id: Optional[int] = Query(None),
    destination_id: Optional[int] = Query(None),
    transport_mode: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Route).filter(Route.is_active == True)
    if origin_id:
        query = query.filter(Route.origin_city_id == origin_id)
    if destination_id:
        query = query.filter(Route.destination_city_id == destination_id)
    if transport_mode:
        query = query.filter(Route.transport_mode == transport_mode)
    return query.all()


@router.get("/{route_id}", response_model=RouteOut)
def get_route(route_id: int, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.post("/optimize", response_model=RouteOptimizeResponse)
def optimize_route(request: RouteOptimizeRequest, db: Session = Depends(get_db)):
    # Validate cities
    origin = db.query(City).filter(City.id == request.origin_city_id).first()
    destination = db.query(City).filter(City.id == request.destination_city_id).first()

    if not origin:
        raise HTTPException(status_code=404, detail="Origin city not found")
    if not destination:
        raise HTTPException(status_code=404, detail="Destination city not found")
    if origin.id == destination.id:
        raise HTTPException(status_code=400, detail="Origin and destination must be different")

    # Generate high-precision exact routes with real turn-by-turn geometry, flight arcs, and rail corridors
    routes = _build_realistic_routes(origin, destination, request.transport_mode)

    if not routes:
        raise HTTPException(
            status_code=404,
            detail=f"No routes could be constructed between {origin.name} and {destination.name}"
        )

    # Get active alerts
    active_alerts = db.query(Alert).filter(Alert.is_active == True).all()

    # Score routes using multi-criteria weighted AI scoring
    scored = score_routes(
        routes=routes,
        alerts=active_alerts,
        priority=request.priority,
        cargo_type=request.cargo_type,
        cargo_weight_kg=request.cargo_weight_kg,
        origin_city=origin,
        destination_city=destination,
    )

    if not scored:
        raise HTTPException(status_code=404, detail="No routes could be scored")

    recommended_id = scored[0]["route_id"]
    explanation = scored[0].get("explanation", "Best overall route based on selected priority.")
    weights = PRIORITY_WEIGHTS.get(request.priority, PRIORITY_WEIGHTS["balanced"])

    route_scores = [RouteScore(**r) for r in scored]

    return RouteOptimizeResponse(
        routes=route_scores,
        recommended_route_id=recommended_id,
        explanation=explanation,
        priority_used=request.priority,
        weights_used=weights,
    )


def _build_realistic_routes(origin: City, destination: City, transport_mode: Optional[str]) -> List[Route]:
    """
    Constructs high-precision realistic route options with:
    - Exact turn-by-turn road geometry (via OSRM road network)
    - Curved geodesic flight arcs for air transport
    - Railway corridor alignments for rail freight
    - Seamless multimodal transit options
    """
    # 1. Exact Road Geometry (Turn-by-turn road network)
    road_pts, road_dist, road_time = get_exact_road_route(
        origin.lat, origin.lng, destination.lat, destination.lng
    )

    # 2. Flight Arc (Great circle curve)
    air_pts, air_dist, air_time = generate_flight_arc(
        origin.lat, origin.lng, destination.lat, destination.lng
    )

    # 3. Rail Corridor
    rail_pts, rail_dist, rail_time = generate_rail_corridor(
        origin.lat, origin.lng, destination.lat, destination.lng,
        origin.name, destination.name
    )

    # State accessibility estimation
    origin_acc = origin.state.accessibility_score if origin.state else 78.0
    dest_acc = destination.state.accessibility_score if destination.state else 75.0
    avg_acc = (origin_acc + dest_acc) / 2.0

    routes = []

    # --- PRIMARY ROAD HIGHWAY ---
    r1 = Route(
        id=101,
        name=f"{origin.name} → {destination.name} (Primary National Highway)",
        origin_city_id=origin.id,
        destination_city_id=destination.id,
        transport_mode="road",
        distance_km=road_dist,
        base_travel_time_hours=road_time,
        base_cost_inr=round(road_dist * 18.0),
        accessibility_score=round(avg_acc, 1),
        risk_score=round(max(20.0, 95.0 - avg_acc), 1),
        road_quality_score=round(min(92.0, avg_acc + 5), 1),
        terrain_difficulty=round(max(15.0, 100.0 - avg_acc), 1),
        waypoints_json=json.dumps(road_pts),
        is_active=True
    )

    # --- ALTERNATIVE ROAD CORRIDOR ---
    alt_pts = interpolate_curved_path(origin.lat, origin.lng, destination.lat, destination.lng, num_points=50, roughness=0.06)
    alt_dist = round(road_dist * 1.12, 1)
    alt_time = round(road_time * 1.18, 1)
    r2 = Route(
        id=102,
        name=f"{origin.name} → {destination.name} (Alternative Regional Corridor)",
        origin_city_id=origin.id,
        destination_city_id=destination.id,
        transport_mode="road",
        distance_km=alt_dist,
        base_travel_time_hours=alt_time,
        base_cost_inr=round(alt_dist * 19.5),
        accessibility_score=round(max(40.0, avg_acc - 8), 1),
        risk_score=round(min(80.0, 95.0 - avg_acc + 12), 1),
        road_quality_score=round(max(40.0, avg_acc - 12), 1),
        terrain_difficulty=round(min(85.0, 100.0 - avg_acc + 15), 1),
        waypoints_json=json.dumps(alt_pts),
        is_active=True
    )

    # --- AIR CARGO FLIGHT ROUTE ---
    r_air = Route(
        id=201,
        name=f"{origin.name} ✈ {destination.name} (Air Freight Direct Corridor)",
        origin_city_id=origin.id,
        destination_city_id=destination.id,
        transport_mode="air",
        distance_km=air_dist,
        base_travel_time_hours=air_time,
        base_cost_inr=round(air_dist * 26.0),
        accessibility_score=94.0,  # Airport terminals maintain high standard accessibility
        risk_score=12.0,            # Immune to road landslides, highway flooding, blockades
        road_quality_score=98.0,
        terrain_difficulty=10.0,
        waypoints_json=json.dumps(air_pts),
        is_active=True
    )

    # --- RAIL FREIGHT CORRIDOR ---
    r_rail = Route(
        id=301,
        name=f"{origin.name} 🚆 {destination.name} (NFR Railway Freight Corridor)",
        origin_city_id=origin.id,
        destination_city_id=destination.id,
        transport_mode="rail",
        distance_km=rail_dist,
        base_travel_time_hours=rail_time,
        base_cost_inr=round(rail_dist * 8.5),  # Bulk rail freight is highly cost-effective
        accessibility_score=86.0,
        risk_score=24.0,
        road_quality_score=90.0,
        terrain_difficulty=35.0,
        waypoints_json=json.dumps(rail_pts),
        is_active=True
    )

    # --- MULTIMODAL ROUTE (Rail Trunk + Road Feeder) ---
    multi_dist = round((rail_dist * 0.65) + (road_dist * 0.35), 1)
    multi_time = round((rail_time * 0.60) + (road_time * 0.40) + 1.2, 1)  # 1.2h transfer handling
    # Combine first half of rail with second half of road
    mid_idx_rail = len(rail_pts) // 2
    mid_idx_road = len(road_pts) // 2
    multi_pts = rail_pts[:mid_idx_rail] + road_pts[mid_idx_road:]
    r_multi = Route(
        id=401,
        name=f"{origin.name} 🔀 {destination.name} (Multimodal Rail-Highway Transit)",
        origin_city_id=origin.id,
        destination_city_id=destination.id,
        transport_mode="multimodal",
        distance_km=multi_dist,
        base_travel_time_hours=multi_time,
        base_cost_inr=round(multi_dist * 12.0),
        accessibility_score=88.0,
        risk_score=28.0,
        road_quality_score=85.0,
        terrain_difficulty=40.0,
        waypoints_json=json.dumps(multi_pts),
        is_active=True
    )

    # Filter or prioritize based on transport_mode requested
    mode = (transport_mode or "road").lower()
    if mode == "road":
        routes = [r1, r2]  # Primary National Highway + Alternative Regional Highway
    elif mode == "air":
        routes = [r_air]   # Direct Air Freight Corridor
    elif mode == "rail":
        routes = [r_rail, r_multi]  # Rail Freight Corridor + Multimodal Rail-Road
    elif mode == "multimodal":
        routes = [r_multi, r1, r_rail, r_air]  # Compare all 4 modalities side-by-side
    else:
        routes = [r1, r2, r_air, r_rail, r_multi]

    return routes
