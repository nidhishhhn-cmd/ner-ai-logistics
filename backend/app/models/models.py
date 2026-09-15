"""
SQLAlchemy Models for NER Logistics Platform
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base
import enum


class TransportMode(str, enum.Enum):
    road = "road"
    rail = "rail"
    air = "air"
    multimodal = "multimodal"


class AlertSeverity(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class AlertCategory(str, enum.Enum):
    weather = "weather"
    road_closure = "road_closure"
    landslide = "landslide"
    flood = "flood"
    traffic = "traffic"
    construction = "construction"
    infrastructure = "infrastructure"
    border_checkpoint = "border_checkpoint"


class State(Base):
    __tablename__ = "states"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    capital = Column(String(100))
    area_sq_km = Column(Float)
    population = Column(Integer)
    accessibility_score = Column(Float, default=75.0)
    road_density = Column(Float)  # km per 100 sq km
    lat = Column(Float)
    lng = Column(Float)
    created_at = Column(DateTime, server_default=func.now())

    cities = relationship("City", back_populates="state")


class City(Base):
    __tablename__ = "cities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"))
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    population = Column(Integer)
    is_major = Column(Boolean, default=False)
    has_airport = Column(Boolean, default=False)
    has_railway = Column(Boolean, default=False)
    connectivity_score = Column(Float, default=70.0)
    created_at = Column(DateTime, server_default=func.now())

    state = relationship("State", back_populates="cities")


class Route(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    origin_city_id = Column(Integer, ForeignKey("cities.id"))
    destination_city_id = Column(Integer, ForeignKey("cities.id"))
    transport_mode = Column(String(20), default="road")
    distance_km = Column(Float)
    base_travel_time_hours = Column(Float)
    base_cost_inr = Column(Float)
    accessibility_score = Column(Float)
    risk_score = Column(Float)  # 0-100 (lower is safer)
    road_quality_score = Column(Float)
    terrain_difficulty = Column(Float)  # 0-100 (lower is easier)
    waypoints_json = Column(Text)  # JSON array of [lat,lng] waypoints
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    origin = relationship("City", foreign_keys=[origin_city_id])
    destination = relationship("City", foreign_keys=[destination_city_id])


class LogisticsHub(Base):
    __tablename__ = "logistics_hubs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"))
    hub_type = Column(String(50), default="multimodal")
    connectivity_score = Column(Float)
    road_connectivity = Column(Float)
    rail_connectivity = Column(Float)
    air_connectivity = Column(Float)
    storage_capacity_tons = Column(Float)
    storage_available_percent = Column(Float)
    status = Column(String(20), default="active")
    lat = Column(Float)
    lng = Column(Float)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    city = relationship("City")


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(50))
    severity = Column(String(20))
    location = Column(String(200))
    state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
    affected_route_ids = Column(Text)  # JSON array of route IDs
    description = Column(Text)
    recommended_action = Column(Text)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    starts_at = Column(DateTime)
    ends_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class RouteAnalysis(Base):
    __tablename__ = "route_analyses"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100))
    origin_city_id = Column(Integer, ForeignKey("cities.id"))
    destination_city_id = Column(Integer, ForeignKey("cities.id"))
    transport_mode = Column(String(20))
    priority = Column(String(30))
    cargo_type = Column(String(30), nullable=True)
    cargo_weight_kg = Column(Float, nullable=True)
    recommended_route_id = Column(Integer, ForeignKey("routes.id"), nullable=True)
    ai_score = Column(Float)
    explanation = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class UserFeedback(Base):
    __tablename__ = "user_feedback"
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=True)
    rating = Column(Integer)  # 1-5
    comment = Column(Text)
    user_email = Column(String(200))
    created_at = Column(DateTime, server_default=func.now())


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, nullable=False)
    full_name = Column(String(200))
    hashed_password = Column(String(200))
    role = Column(String(50), default="operator")
    is_active = Column(Boolean, default=True)
    default_transport_mode = Column(String(20), default="road")
    default_priority = Column(String(30), default="balanced")
    theme = Column(String(20), default="dark")
    notifications_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
