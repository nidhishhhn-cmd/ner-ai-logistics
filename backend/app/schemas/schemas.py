"""
Pydantic Schemas for NER Logistics Platform
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime


# ---- Auth Schemas ----
class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    default_transport_mode: str
    default_priority: str
    theme: str
    notifications_enabled: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    default_transport_mode: Optional[str] = None
    default_priority: Optional[str] = None
    theme: Optional[str] = None
    notifications_enabled: Optional[bool] = None


# ---- State Schemas ----
class StateOut(BaseModel):
    id: int
    name: str
    code: str
    capital: Optional[str]
    area_sq_km: Optional[float]
    population: Optional[int]
    accessibility_score: float
    road_density: Optional[float]
    lat: Optional[float]
    lng: Optional[float]

    class Config:
        from_attributes = True


# ---- City Schemas ----
class CityOut(BaseModel):
    id: int
    name: str
    state_id: int
    state_name: Optional[str] = None
    lat: float
    lng: float
    population: Optional[int]
    is_major: bool
    has_airport: bool
    has_railway: bool
    connectivity_score: float

    class Config:
        from_attributes = True


# ---- Route Schemas ----
class RouteOptimizeRequest(BaseModel):
    origin_city_id: int
    destination_city_id: int
    transport_mode: str = "road"
    priority: str = "balanced"
    cargo_type: Optional[str] = None
    cargo_weight_kg: Optional[float] = None


class RouteScore(BaseModel):
    route_id: int
    route_name: str
    origin: str
    destination: str
    waypoints: List[str]
    distance_km: float
    travel_time_hours: float
    cost_inr: float
    accessibility_score: float
    risk_score: float
    road_quality: float
    terrain_difficulty: float
    disruption_count: int
    weather_condition: str
    overall_score: float
    is_recommended: bool
    transport_mode: str
    explanation: Optional[str] = None
    waypoints_latlng: List[List[float]] = []


class RouteOptimizeResponse(BaseModel):
    routes: List[RouteScore]
    recommended_route_id: int
    explanation: str
    priority_used: str
    weights_used: dict


class RouteOut(BaseModel):
    id: int
    name: str
    origin_city_id: int
    destination_city_id: int
    transport_mode: str
    distance_km: float
    base_travel_time_hours: float
    base_cost_inr: float
    accessibility_score: float
    risk_score: float

    class Config:
        from_attributes = True


# ---- Hub Schemas ----
class HubOut(BaseModel):
    id: int
    name: str
    city_id: int
    city_name: Optional[str] = None
    state_name: Optional[str] = None
    hub_type: str
    connectivity_score: float
    road_connectivity: float
    rail_connectivity: float
    air_connectivity: float
    storage_capacity_tons: float
    storage_available_percent: float
    status: str
    lat: float
    lng: float
    description: Optional[str]

    class Config:
        from_attributes = True


# ---- Alert Schemas ----
class AlertOut(BaseModel):
    id: int
    title: str
    category: str
    severity: str
    location: str
    description: str
    recommended_action: Optional[str]
    affected_route_ids: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    is_active: bool
    starts_at: Optional[datetime]
    ends_at: Optional[datetime]

    class Config:
        from_attributes = True


# ---- Analytics Schemas ----
class StateAccessibility(BaseModel):
    state: str
    accessibility_score: float
    avg_delivery_time_hours: float
    route_count: int
    hub_count: int


class AnalyticsResponse(BaseModel):
    states: List[StateAccessibility]
    total_routes: int
    total_hubs: int
    active_alerts: int
    avg_accessibility: float
    transport_distribution: dict
    risk_distribution: dict
    monthly_disruptions: List[dict]


# ---- Insight Schemas ----
class InsightOut(BaseModel):
    id: int
    category: str
    title: str
    description: str
    severity: str  # info, warning, critical
    metric_value: Optional[float]
    affected_states: List[str]


class InsightsResponse(BaseModel):
    insights: List[InsightOut]
    generated_at: str
    data_source: str = "Deterministic Analytics Engine (Demo Data)"


# ---- Feedback Schemas ----
class FeedbackCreate(BaseModel):
    route_id: Optional[int] = None
    rating: int
    comment: Optional[str] = None
    user_email: Optional[str] = None


# ---- Search ----
class SearchResult(BaseModel):
    type: str  # city, state, route, hub, alert
    id: int
    name: str
    subtitle: Optional[str]
    url: str
