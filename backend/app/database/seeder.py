"""
Database Seeder - Realistic NER Demo Data
All data is deterministic and representative of the North Eastern Region
"""
import json
import bcrypt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.models import State, City, Route, LogisticsHub, Alert, User


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def seed_database(db: Session):
    """Seed all tables if empty."""
    if db.query(User).count() > 0:
        print("Database already seeded, skipping...")
        return

    print("Seeding database with NER demo data...")

    # ---- STATES ----
    states_data = [
        {"name": "Assam", "code": "AS", "capital": "Dispur", "area_sq_km": 78438, "population": 31205576,
         "accessibility_score": 88.5, "road_density": 45.2, "lat": 26.2006, "lng": 92.9376},
        {"name": "Arunachal Pradesh", "code": "AR", "capital": "Itanagar", "area_sq_km": 83743, "population": 1383727,
         "accessibility_score": 62.3, "road_density": 12.8, "lat": 28.2180, "lng": 94.7278},
        {"name": "Manipur", "code": "MN", "capital": "Imphal", "area_sq_km": 22327, "population": 2855794,
         "accessibility_score": 71.4, "road_density": 28.6, "lat": 24.6637, "lng": 93.9063},
        {"name": "Meghalaya", "code": "ML", "capital": "Shillong", "area_sq_km": 22429, "population": 2966889,
         "accessibility_score": 79.2, "road_density": 32.1, "lat": 25.4670, "lng": 91.3662},
        {"name": "Mizoram", "code": "MZ", "capital": "Aizawl", "area_sq_km": 21081, "population": 1097206,
         "accessibility_score": 73.8, "road_density": 22.4, "lat": 23.1645, "lng": 92.9376},
        {"name": "Nagaland", "code": "NL", "capital": "Kohima", "area_sq_km": 16579, "population": 1978502,
         "accessibility_score": 76.1, "road_density": 30.5, "lat": 26.1584, "lng": 94.5624},
        {"name": "Tripura", "code": "TR", "capital": "Agartala", "area_sq_km": 10486, "population": 3673917,
         "accessibility_score": 85.7, "road_density": 48.3, "lat": 23.9408, "lng": 91.9882},
        {"name": "Sikkim", "code": "SK", "capital": "Gangtok", "area_sq_km": 7096, "population": 610577,
         "accessibility_score": 74.6, "road_density": 25.7, "lat": 27.5330, "lng": 88.5122},
    ]

    state_objs = {}
    for s in states_data:
        obj = State(**s)
        db.add(obj)
        db.flush()
        state_objs[s["code"]] = obj

    # ---- CITIES ----
    cities_data = [
        {"name": "Guwahati", "state_code": "AS", "lat": 26.1445, "lng": 91.7362, "population": 962334,
         "is_major": True, "has_airport": True, "has_railway": True, "connectivity_score": 94.2},
        {"name": "Shillong", "state_code": "ML", "lat": 25.5788, "lng": 91.8933, "population": 354759,
         "is_major": True, "has_airport": True, "has_railway": False, "connectivity_score": 82.5},
        {"name": "Imphal", "state_code": "MN", "lat": 24.8170, "lng": 93.9368, "population": 268243,
         "is_major": True, "has_airport": True, "has_railway": False, "connectivity_score": 71.3},
        {"name": "Aizawl", "state_code": "MZ", "lat": 23.7307, "lng": 92.7173, "population": 293416,
         "is_major": True, "has_airport": True, "has_railway": False, "connectivity_score": 68.7},
        {"name": "Kohima", "state_code": "NL", "lat": 25.6701, "lng": 94.1101, "population": 99039,
         "is_major": True, "has_airport": False, "has_railway": False, "connectivity_score": 72.1},
        {"name": "Itanagar", "state_code": "AR", "lat": 27.0844, "lng": 93.6053, "population": 59490,
         "is_major": True, "has_airport": True, "has_railway": False, "connectivity_score": 61.4},
        {"name": "Agartala", "state_code": "TR", "lat": 23.8315, "lng": 91.2868, "population": 438724,
         "is_major": True, "has_airport": True, "has_railway": True, "connectivity_score": 86.8},
        {"name": "Gangtok", "state_code": "SK", "lat": 27.3314, "lng": 88.6138, "population": 100286,
         "is_major": True, "has_airport": False, "has_railway": False, "connectivity_score": 70.2},
        {"name": "Silchar", "state_code": "AS", "lat": 24.8333, "lng": 92.7789, "population": 228985,
         "is_major": True, "has_airport": True, "has_railway": True, "connectivity_score": 79.4},
        {"name": "Dibrugarh", "state_code": "AS", "lat": 27.4728, "lng": 94.9120, "population": 154296,
         "is_major": True, "has_airport": True, "has_railway": True, "connectivity_score": 81.2},
        {"name": "Tinsukia", "state_code": "AS", "lat": 27.4924, "lng": 95.3543, "population": 125022,
         "is_major": False, "has_airport": False, "has_railway": True, "connectivity_score": 73.6},
        {"name": "Dimapur", "state_code": "NL", "lat": 25.9096, "lng": 93.7274, "population": 379117,
         "is_major": True, "has_airport": True, "has_railway": True, "connectivity_score": 83.9},
        {"name": "Jorhat", "state_code": "AS", "lat": 26.7465, "lng": 94.2026, "population": 153889,
         "is_major": False, "has_airport": True, "has_railway": True, "connectivity_score": 78.3},
        {"name": "Tezpur", "state_code": "AS", "lat": 26.6338, "lng": 92.7926, "population": 100013,
         "is_major": False, "has_airport": True, "has_railway": False, "connectivity_score": 74.7},
        {"name": "Pasighat", "state_code": "AR", "lat": 28.0674, "lng": 95.3277, "population": 29642,
         "is_major": False, "has_airport": True, "has_railway": False, "connectivity_score": 56.2},
        {"name": "Lumding", "state_code": "AS", "lat": 25.7470, "lng": 93.1747, "population": 51234,
         "is_major": False, "has_airport": False, "has_railway": True, "connectivity_score": 71.8},
        {"name": "Jiribam", "state_code": "MN", "lat": 24.8007, "lng": 93.1192, "population": 25000,
         "is_major": False, "has_airport": False, "has_railway": False, "connectivity_score": 52.4},
    ]

    city_objs = {}
    for c in cities_data:
        obj = City(
            name=c["name"],
            state_id=state_objs[c["state_code"]].id,
            lat=c["lat"], lng=c["lng"],
            population=c["population"],
            is_major=c["is_major"],
            has_airport=c["has_airport"],
            has_railway=c["has_railway"],
            connectivity_score=c["connectivity_score"]
        )
        db.add(obj)
        db.flush()
        city_objs[c["name"]] = obj

    def city_id(name):
        return city_objs[name].id

    # ---- ROUTES ----
    routes_data = [
        {
            "name": "Guwahati - Shillong Highway (NH-6)",
            "origin": "Guwahati", "destination": "Shillong",
            "transport_mode": "road",
            "distance_km": 98.0, "base_travel_time_hours": 2.5, "base_cost_inr": 1800,
            "accessibility_score": 88.0, "risk_score": 22.0, "road_quality_score": 85.0, "terrain_difficulty": 35.0,
            "waypoints_json": json.dumps([[26.1445,91.7362],[25.9500,91.8000],[25.7800,91.8500],[25.5788,91.8933]])
        },
        {
            "name": "Guwahati - Dimapur - Imphal (NH-2/NH-39)",
            "origin": "Guwahati", "destination": "Imphal",
            "transport_mode": "road",
            "distance_km": 520.0, "base_travel_time_hours": 12.5, "base_cost_inr": 8400,
            "accessibility_score": 71.0, "risk_score": 42.0, "road_quality_score": 68.0, "terrain_difficulty": 60.0,
            "waypoints_json": json.dumps([[26.1445,91.7362],[25.9096,93.7274],[25.2000,93.8000],[24.8170,93.9368]])
        },
        {
            "name": "Guwahati - Imphal via Jiribam (NH-37/NH-102)",
            "origin": "Guwahati", "destination": "Imphal",
            "transport_mode": "road",
            "distance_km": 555.0, "base_travel_time_hours": 14.0, "base_cost_inr": 9200,
            "accessibility_score": 65.0, "risk_score": 55.0, "road_quality_score": 61.0, "terrain_difficulty": 72.0,
            "waypoints_json": json.dumps([[26.1445,91.7362],[25.0000,92.5000],[24.8007,93.1192],[24.8170,93.9368]])
        },
        {
            "name": "Guwahati - Imphal (Air Route)",
            "origin": "Guwahati", "destination": "Imphal",
            "transport_mode": "air",
            "distance_km": 340.0, "base_travel_time_hours": 1.5, "base_cost_inr": 5200,
            "accessibility_score": 92.0, "risk_score": 8.0, "road_quality_score": 95.0, "terrain_difficulty": 5.0,
            "waypoints_json": json.dumps([[26.1445,91.7362],[25.4800,92.8500],[24.8170,93.9368]])
        },
        {
            "name": "Guwahati - Agartala (NH-8 via Lumding)",
            "origin": "Guwahati", "destination": "Agartala",
            "transport_mode": "road",
            "distance_km": 590.0, "base_travel_time_hours": 13.0, "base_cost_inr": 9500,
            "accessibility_score": 82.0, "risk_score": 28.0, "road_quality_score": 80.0, "terrain_difficulty": 38.0,
            "waypoints_json": json.dumps([[26.1445,91.7362],[25.7470,93.1747],[24.5000,92.0000],[23.8315,91.2868]])
        },
        {
            "name": "Guwahati - Agartala (Rail via Lumding)",
            "origin": "Guwahati", "destination": "Agartala",
            "transport_mode": "rail",
            "distance_km": 620.0, "base_travel_time_hours": 16.0, "base_cost_inr": 4200,
            "accessibility_score": 86.0, "risk_score": 18.0, "road_quality_score": 92.0, "terrain_difficulty": 20.0,
            "waypoints_json": json.dumps([[26.1445,91.7362],[25.7470,93.1747],[24.8333,92.7789],[23.8315,91.2868]])
        },
        {
            "name": "Guwahati - Kohima (NH-29)",
            "origin": "Guwahati", "destination": "Kohima",
            "transport_mode": "road",
            "distance_km": 350.0, "base_travel_time_hours": 9.0, "base_cost_inr": 5800,
            "accessibility_score": 73.0, "risk_score": 38.0, "road_quality_score": 71.0, "terrain_difficulty": 55.0,
            "waypoints_json": json.dumps([[26.1445,91.7362],[25.9096,93.7274],[25.6701,94.1101]])
        },
        {
            "name": "Shillong - Silchar (NH-6)",
            "origin": "Shillong", "destination": "Silchar",
            "transport_mode": "road",
            "distance_km": 220.0, "base_travel_time_hours": 6.0, "base_cost_inr": 3600,
            "accessibility_score": 74.0, "risk_score": 45.0, "road_quality_score": 70.0, "terrain_difficulty": 58.0,
            "waypoints_json": json.dumps([[25.5788,91.8933],[25.2000,92.3000],[24.8333,92.7789]])
        },
        {
            "name": "Dimapur - Imphal (NH-39)",
            "origin": "Dimapur", "destination": "Imphal",
            "transport_mode": "road",
            "distance_km": 215.0, "base_travel_time_hours": 5.5, "base_cost_inr": 3400,
            "accessibility_score": 69.0, "risk_score": 48.0, "road_quality_score": 65.0, "terrain_difficulty": 63.0,
            "waypoints_json": json.dumps([[25.9096,93.7274],[25.4000,93.8000],[24.8170,93.9368]])
        },
        {
            "name": "Dimapur - Kohima (NH-29)",
            "origin": "Dimapur", "destination": "Kohima",
            "transport_mode": "road",
            "distance_km": 74.0, "base_travel_time_hours": 2.0, "base_cost_inr": 1200,
            "accessibility_score": 78.0, "risk_score": 30.0, "road_quality_score": 76.0, "terrain_difficulty": 45.0,
            "waypoints_json": json.dumps([[25.9096,93.7274],[25.8000,94.0000],[25.6701,94.1101]])
        },
        {
            "name": "Agartala - Silchar (NH-8)",
            "origin": "Agartala", "destination": "Silchar",
            "transport_mode": "road",
            "distance_km": 185.0, "base_travel_time_hours": 5.0, "base_cost_inr": 2900,
            "accessibility_score": 81.0, "risk_score": 25.0, "road_quality_score": 79.0, "terrain_difficulty": 30.0,
            "waypoints_json": json.dumps([[23.8315,91.2868],[24.3000,92.0000],[24.8333,92.7789]])
        },
        {
            "name": "Jorhat - Dibrugarh (NH-37)",
            "origin": "Jorhat", "destination": "Dibrugarh",
            "transport_mode": "road",
            "distance_km": 58.0, "base_travel_time_hours": 1.5, "base_cost_inr": 900,
            "accessibility_score": 87.0, "risk_score": 15.0, "road_quality_score": 88.0, "terrain_difficulty": 18.0,
            "waypoints_json": json.dumps([[26.7465,94.2026],[27.1000,94.5000],[27.4728,94.9120]])
        },
        {
            "name": "Guwahati - Tezpur - Itanagar (NH-15)",
            "origin": "Guwahati", "destination": "Itanagar",
            "transport_mode": "road",
            "distance_km": 390.0, "base_travel_time_hours": 9.5, "base_cost_inr": 6200,
            "accessibility_score": 64.0, "risk_score": 50.0, "road_quality_score": 62.0, "terrain_difficulty": 68.0,
            "waypoints_json": json.dumps([[26.1445,91.7362],[26.6338,92.7926],[27.0844,93.6053]])
        },
        {
            "name": "Imphal - Aizawl (NH-202)",
            "origin": "Imphal", "destination": "Aizawl",
            "transport_mode": "road",
            "distance_km": 320.0, "base_travel_time_hours": 10.0, "base_cost_inr": 5100,
            "accessibility_score": 62.0, "risk_score": 58.0, "road_quality_score": 58.0, "terrain_difficulty": 75.0,
            "waypoints_json": json.dumps([[24.8170,93.9368],[24.3000,93.2000],[23.7307,92.7173]])
        },
        {
            "name": "Guwahati - Gangtok (Via Siliguri)",
            "origin": "Guwahati", "destination": "Gangtok",
            "transport_mode": "road",
            "distance_km": 440.0, "base_travel_time_hours": 11.0, "base_cost_inr": 7100,
            "accessibility_score": 76.0, "risk_score": 35.0, "road_quality_score": 74.0, "terrain_difficulty": 52.0,
            "waypoints_json": json.dumps([[26.1445,91.7362],[26.5000,89.5000],[26.7000,88.4000],[27.3314,88.6138]])
        },
        {
            "name": "Silchar - Aizawl (NH-54)",
            "origin": "Silchar", "destination": "Aizawl",
            "transport_mode": "road",
            "distance_km": 190.0, "base_travel_time_hours": 6.0, "base_cost_inr": 3100,
            "accessibility_score": 67.0, "risk_score": 52.0, "road_quality_score": 63.0, "terrain_difficulty": 70.0,
            "waypoints_json": json.dumps([[24.8333,92.7789],[24.2000,92.7000],[23.7307,92.7173]])
        },
    ]

    route_objs = {}
    for r in routes_data:
        obj = Route(
            name=r["name"],
            origin_city_id=city_id(r["origin"]),
            destination_city_id=city_id(r["destination"]),
            transport_mode=r["transport_mode"],
            distance_km=r["distance_km"],
            base_travel_time_hours=r["base_travel_time_hours"],
            base_cost_inr=r["base_cost_inr"],
            accessibility_score=r["accessibility_score"],
            risk_score=r["risk_score"],
            road_quality_score=r["road_quality_score"],
            terrain_difficulty=r["terrain_difficulty"],
            waypoints_json=r["waypoints_json"]
        )
        db.add(obj)
        db.flush()
        route_objs[r["name"]] = obj

    # ---- LOGISTICS HUBS ----
    hubs_data = [
        {
            "name": "Guwahati Multimodal Logistics Hub",
            "city": "Guwahati",
            "hub_type": "multimodal",
            "connectivity_score": 94.2, "road_connectivity": 96.0, "rail_connectivity": 92.0,
            "air_connectivity": 95.0, "storage_capacity_tons": 5000.0, "storage_available_percent": 72.0,
            "status": "active", "lat": 26.1445, "lng": 91.7362,
            "description": "Primary gateway hub for NER. Handles bulk cargo, perishables, and e-commerce fulfillment."
        },
        {
            "name": "Silchar Logistics Park",
            "city": "Silchar",
            "hub_type": "road_rail",
            "connectivity_score": 79.4, "road_connectivity": 80.0, "rail_connectivity": 82.0,
            "air_connectivity": 76.0, "storage_capacity_tons": 1800.0, "storage_available_percent": 65.0,
            "status": "active", "lat": 24.8333, "lng": 92.7789,
            "description": "Key southern Assam hub serving Barak Valley and links to Mizoram."
        },
        {
            "name": "Dimapur Integrated Freight Terminal",
            "city": "Dimapur",
            "hub_type": "multimodal",
            "connectivity_score": 83.9, "road_connectivity": 85.0, "rail_connectivity": 88.0,
            "air_connectivity": 79.0, "storage_capacity_tons": 2200.0, "storage_available_percent": 58.0,
            "status": "active", "lat": 25.9096, "lng": 93.7274,
            "description": "Strategic hub connecting Nagaland, Manipur corridor. Rail terminus for NE freight."
        },
        {
            "name": "Agartala Tripura Logistics Centre",
            "city": "Agartala",
            "hub_type": "multimodal",
            "connectivity_score": 86.8, "road_connectivity": 88.0, "rail_connectivity": 87.0,
            "air_connectivity": 85.0, "storage_capacity_tons": 2000.0, "storage_available_percent": 80.0,
            "status": "active", "lat": 23.8315, "lng": 91.2868,
            "description": "Gateway hub for South Asian connectivity via Bangladesh. High storage availability."
        },
        {
            "name": "Imphal Logistics Hub",
            "city": "Imphal",
            "hub_type": "air_road",
            "connectivity_score": 71.3, "road_connectivity": 68.0, "rail_connectivity": 40.0,
            "air_connectivity": 88.0, "storage_capacity_tons": 900.0, "storage_available_percent": 55.0,
            "status": "active", "lat": 24.8170, "lng": 93.9368,
            "description": "Primary hub for Manipur. Relies heavily on air freight due to terrain challenges."
        },
        {
            "name": "Aizawl Distribution Centre",
            "city": "Aizawl",
            "hub_type": "road",
            "connectivity_score": 68.7, "road_connectivity": 70.0, "rail_connectivity": 20.0,
            "air_connectivity": 78.0, "storage_capacity_tons": 600.0, "storage_available_percent": 68.0,
            "status": "active", "lat": 23.7307, "lng": 92.7173,
            "description": "Main distribution centre for Mizoram. Road-dependent, limited rail access."
        },
        {
            "name": "Shillong Meghalaya Freight Hub",
            "city": "Shillong",
            "hub_type": "road",
            "connectivity_score": 82.5, "road_connectivity": 84.0, "rail_connectivity": 45.0,
            "air_connectivity": 80.0, "storage_capacity_tons": 1200.0, "storage_available_percent": 70.0,
            "status": "active", "lat": 25.5788, "lng": 91.8933,
            "description": "Central hub for Meghalaya. Near Guwahati for rail connections."
        },
        {
            "name": "Gangtok Sikkim Trade Facilitation Centre",
            "city": "Gangtok",
            "hub_type": "road",
            "connectivity_score": 70.2, "road_connectivity": 72.0, "rail_connectivity": 35.0,
            "air_connectivity": 60.0, "storage_capacity_tons": 400.0, "storage_available_percent": 75.0,
            "status": "limited", "lat": 27.3314, "lng": 88.6138,
            "description": "Mountain hub for Sikkim. Seasonal weather constraints limit operations. Near Nathu La."
        },
    ]

    for h in hubs_data:
        obj = LogisticsHub(
            name=h["name"],
            city_id=city_id(h["city"]),
            hub_type=h["hub_type"],
            connectivity_score=h["connectivity_score"],
            road_connectivity=h["road_connectivity"],
            rail_connectivity=h["rail_connectivity"],
            air_connectivity=h["air_connectivity"],
            storage_capacity_tons=h["storage_capacity_tons"],
            storage_available_percent=h["storage_available_percent"],
            status=h["status"],
            lat=h["lat"], lng=h["lng"],
            description=h["description"]
        )
        db.add(obj)

    # ---- ALERTS ----
    now = datetime.utcnow()
    alerts_data = [
        {
            "title": "Landslide Warning: Dimapur-Kohima Highway",
            "category": "landslide",
            "severity": "critical",
            "location": "NH-29, Mao Gate, Nagaland",
            "state_code": "NL",
            "description": "Heavy rainfall has triggered multiple landslides on NH-29 between Dimapur and Kohima. Road partially blocked. Clearance expected in 24-48 hours.",
            "recommended_action": "Avoid NH-29. Use Dimapur-Imphal alternative via Senapati. Keep monitoring.",
            "lat": 25.78, "lng": 94.02,
            "affected_route_ids": json.dumps([7, 9]),
            "starts_at": now - timedelta(hours=6)
        },
        {
            "title": "Flood Warning: Brahmaputra Basin",
            "category": "flood",
            "severity": "high",
            "location": "Lower Assam, Guwahati",
            "state_code": "AS",
            "description": "Water level of Brahmaputra rising. Low-lying NH areas near Guwahati may experience temporary flooding. Cargo delays anticipated.",
            "recommended_action": "Pre-position cargo at higher-elevation hubs. Activate contingency routing via Meghalaya.",
            "lat": 26.10, "lng": 91.50,
            "affected_route_ids": json.dumps([1, 5]),
            "starts_at": now - timedelta(hours=12)
        },
        {
            "title": "Heavy Rainfall Alert: Shillong-Silchar Corridor",
            "category": "weather",
            "severity": "high",
            "location": "Meghalaya-Assam Border Region",
            "state_code": "ML",
            "description": "IMD forecasts extremely heavy rainfall over Meghalaya and southern Assam for next 72 hours. Visibility reduced. Road conditions deteriorating.",
            "recommended_action": "Night driving prohibited on Shillong-Silchar section. Allow 50% extra travel time buffer.",
            "lat": 25.20, "lng": 92.20,
            "affected_route_ids": json.dumps([8]),
            "starts_at": now - timedelta(hours=2)
        },
        {
            "title": "Road Closure: Imphal-Aizawl NH-202",
            "category": "road_closure",
            "severity": "critical",
            "location": "Kangpokpi District, Manipur",
            "state_code": "MN",
            "description": "NH-202 closed due to road widening and bridge repair work. Single-lane alternate road available but restricted to vehicles under 5 tons.",
            "recommended_action": "Heavy cargo must route via Jiribam-Silchar. Light vehicles use alternate single-lane road.",
            "lat": 24.40, "lng": 93.60,
            "affected_route_ids": json.dumps([14]),
            "starts_at": now - timedelta(days=2),
            "ends_at": now + timedelta(days=14)
        },
        {
            "title": "Traffic Congestion: Guwahati City Entry",
            "category": "traffic",
            "severity": "medium",
            "location": "Jalukbari, Guwahati",
            "state_code": "AS",
            "description": "Heavy vehicular congestion at Jalukbari intersection. Logistics vehicles experiencing 3-4 hour delays during peak hours (7AM-10AM, 5PM-8PM).",
            "recommended_action": "Schedule logistics vehicle movement during off-peak hours. Use Bypass Road via Azara.",
            "lat": 26.15, "lng": 91.66,
            "affected_route_ids": json.dumps([1, 2, 5, 13, 15]),
            "starts_at": now - timedelta(days=1)
        },
        {
            "title": "Infrastructure Maintenance: Agartala Airport",
            "category": "infrastructure",
            "severity": "medium",
            "location": "Maharaja Bir Bikram Airport, Agartala",
            "state_code": "TR",
            "description": "Runway resurfacing work underway. Air cargo operations reduced to 6 flights/day. Prior slot booking mandatory.",
            "recommended_action": "Book cargo slots 48 hours in advance. Overflow cargo to redirect via Chittagong port.",
            "lat": 23.8872, "lng": 91.2400,
            "affected_route_ids": json.dumps([5]),
            "starts_at": now - timedelta(days=3),
            "ends_at": now + timedelta(days=10)
        },
        {
            "title": "Border Checkpoint Delay: Moreh-Tamu",
            "category": "border_checkpoint",
            "severity": "medium",
            "location": "Moreh, Manipur-Myanmar Border",
            "state_code": "MN",
            "description": "Enhanced documentation verification at Moreh-Tamu border for commercial vehicles. Average wait time increased to 6-8 hours.",
            "recommended_action": "Ensure all documentation pre-cleared. Use express clearance counter for APEDA-registered exporters.",
            "lat": 24.2340, "lng": 94.2880,
            "affected_route_ids": json.dumps([3]),
            "starts_at": now - timedelta(hours=18)
        },
        {
            "title": "Construction: NH-37 Widening Project",
            "category": "construction",
            "severity": "low",
            "location": "Jorhat to Dibrugarh section, NH-37",
            "state_code": "AS",
            "description": "4-lane widening in progress. Day-time single lane operation. Convoy movement organized every 2 hours.",
            "recommended_action": "Join convoys at scheduled timings. Night movement unrestricted.",
            "lat": 27.10, "lng": 94.55,
            "affected_route_ids": json.dumps([12]),
            "starts_at": now - timedelta(days=30),
            "ends_at": now + timedelta(days=60)
        },
        {
            "title": "Foggy Conditions: Dibrugarh-Tinsukia Stretch",
            "category": "weather",
            "severity": "low",
            "location": "Upper Assam",
            "state_code": "AS",
            "description": "Dense fog expected in early mornings (5AM-9AM) for next 3 days. Reduced visibility to <50m.",
            "recommended_action": "Delay early morning departures by 2 hours. Use hazard lights and low beam.",
            "lat": 27.45, "lng": 95.10,
            "affected_route_ids": json.dumps([12]),
            "starts_at": now
        },
        {
            "title": "Flash Flood Alert: Jiribam Corridor",
            "category": "flood",
            "severity": "high",
            "location": "Jiribam, Manipur",
            "state_code": "MN",
            "description": "Barak River tributary flooding. Jiribam-Imphal National Highway intermittently blocked by flash flooding.",
            "recommended_action": "Suspend convoys. Monitor NHAI updates every 4 hours. Emergency reroute via Senapati.",
            "lat": 24.80, "lng": 93.12,
            "affected_route_ids": json.dumps([3]),
            "starts_at": now - timedelta(hours=4)
        },
    ]

    for a in alerts_data:
        obj = Alert(
            title=a["title"],
            category=a["category"],
            severity=a["severity"],
            location=a["location"],
            state_id=state_objs[a["state_code"]].id,
            description=a["description"],
            recommended_action=a["recommended_action"],
            lat=a.get("lat"),
            lng=a.get("lng"),
            affected_route_ids=a.get("affected_route_ids"),
            is_active=True,
            starts_at=a["starts_at"],
            ends_at=a.get("ends_at")
        )
        db.add(obj)

    # ---- ADMIN USER ----
    admin = User(
        email="admin@nerlogistics.demo",
        full_name="Admin User (Demo)",
        hashed_password=hash_password("Demo@123"),
        role="admin",
        is_active=True,
        default_transport_mode="road",
        default_priority="balanced",
        theme="dark",
        notifications_enabled=True
    )
    db.add(admin)

    # Operator user
    operator = User(
        email="operator@nerlogistics.demo",
        full_name="Logistics Operator",
        hashed_password=hash_password("Operator@123"),
        role="operator",
        is_active=True,
        default_transport_mode="road",
        default_priority="fastest",
        theme="dark",
        notifications_enabled=True
    )
    db.add(operator)

    db.commit()
    print("Database seeded successfully!")
