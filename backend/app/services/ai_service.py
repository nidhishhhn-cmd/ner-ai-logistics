"""
AI Route Scoring Service
Implements a transparent weighted scoring model for route recommendation.
"""
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.models import Route, City, Alert


PRIORITY_WEIGHTS = {
    "balanced": {
        "accessibility": 0.30,
        "travel_time": 0.25,
        "risk": 0.20,
        "cost": 0.15,
        "disruption": 0.10,
    },
    "fastest": {
        "accessibility": 0.10,
        "travel_time": 0.50,
        "risk": 0.15,
        "cost": 0.15,
        "disruption": 0.10,
    },
    "cheapest": {
        "accessibility": 0.15,
        "travel_time": 0.15,
        "risk": 0.15,
        "cost": 0.45,
        "disruption": 0.10,
    },
    "safest": {
        "accessibility": 0.20,
        "travel_time": 0.10,
        "risk": 0.45,
        "cost": 0.10,
        "disruption": 0.15,
    },
    "most_accessible": {
        "accessibility": 0.50,
        "travel_time": 0.15,
        "risk": 0.15,
        "cost": 0.10,
        "disruption": 0.10,
    },
}


def get_route_disruptions(route: Route, alerts: List[Alert]) -> int:
    """Count active alerts affecting this route."""
    count = 0
    for alert in alerts:
        if alert.affected_route_ids:
            try:
                ids = json.loads(alert.affected_route_ids)
                if route.id in ids:
                    count += 1
            except Exception:
                pass
    return count


def normalize_value(value: float, min_val: float, max_val: float, invert: bool = False) -> float:
    """Normalize a value to 0-100 range, optionally inverting (lower=better)."""
    if max_val == min_val:
        return 50.0
    normalized = (value - min_val) / (max_val - min_val) * 100
    if invert:
        normalized = 100 - normalized
    return max(0.0, min(100.0, normalized))


def get_weather_condition(disruptions: int, risk_score: float, terrain_difficulty: float) -> str:
    """Determine weather condition label from route metrics."""
    if disruptions >= 2 or risk_score > 70:
        return "Severe"
    elif disruptions == 1 or risk_score > 45:
        return "Moderate"
    elif terrain_difficulty > 60:
        return "Variable"
    else:
        return "Clear"


def calculate_cargo_cost_multiplier(cargo_type: Optional[str], cargo_weight_kg: Optional[float]) -> float:
    """Adjust cost based on cargo type and weight."""
    multiplier = 1.0
    type_multipliers = {
        "perishable": 1.35,  # refrigerated transport
        "fragile": 1.25,
        "heavy": 1.40,
        "general": 1.0,
    }
    if cargo_type:
        multiplier *= type_multipliers.get(cargo_type, 1.0)
    if cargo_weight_kg:
        if cargo_weight_kg > 1000:
            multiplier *= 1.3
        elif cargo_weight_kg > 500:
            multiplier *= 1.15
        elif cargo_weight_kg > 100:
            multiplier *= 1.05
    return multiplier


def score_routes(
    routes: List[Route],
    alerts: List[Alert],
    priority: str = "balanced",
    cargo_type: Optional[str] = None,
    cargo_weight_kg: Optional[float] = None,
    origin_city: Optional[City] = None,
    destination_city: Optional[City] = None,
) -> List[Dict[str, Any]]:
    """
    Score and rank routes using weighted multi-criteria scoring.
    Returns sorted list (best first) with full score breakdowns.
    """
    weights = PRIORITY_WEIGHTS.get(priority, PRIORITY_WEIGHTS["balanced"])
    cargo_multiplier = calculate_cargo_cost_multiplier(cargo_type, cargo_weight_kg)

    # Gather raw values for normalization
    times = [r.base_travel_time_hours for r in routes]
    costs = [r.base_cost_inr * cargo_multiplier for r in routes]
    distances = [r.distance_km for r in routes]

    min_time, max_time = min(times), max(times)
    min_cost, max_cost = min(costs), max(costs)
    min_dist, max_dist = min(distances), max(distances)

    scored = []
    for route in routes:
        disruptions = get_route_disruptions(route, alerts)
        actual_cost = route.base_cost_inr * cargo_multiplier

        # Normalize component scores
        acc_score = route.accessibility_score  # Already 0-100
        time_score = normalize_value(route.base_travel_time_hours, min_time, max_time, invert=True)
        risk_score = normalize_value(route.risk_score, 0, 100, invert=True)  # Lower risk = better
        cost_score = normalize_value(actual_cost, min_cost, max_cost, invert=True)
        disruption_score = max(0, 100 - (disruptions * 25))  # -25 per disruption

        # Apply disruption penalty to time
        disruption_time_penalty = disruptions * 1.5
        actual_time = route.base_travel_time_hours + disruption_time_penalty

        # Overall weighted score
        overall = (
            weights["accessibility"] * acc_score +
            weights["travel_time"] * time_score +
            weights["risk"] * risk_score +
            weights["cost"] * cost_score +
            weights["disruption"] * disruption_score
        )

        waypoints_latlng = []
        if route.waypoints_json:
            try:
                waypoints_latlng = json.loads(route.waypoints_json)
            except Exception:
                pass

        # Get city names for waypoints
        origin_name = origin_city.name if origin_city else "Origin"
        dest_name = destination_city.name if destination_city else "Destination"

        weather = get_weather_condition(disruptions, route.risk_score, route.terrain_difficulty)

        scored.append({
            "route_id": route.id,
            "route_name": route.name,
            "origin": origin_name,
            "destination": dest_name,
            "waypoints": [origin_name, dest_name],
            "distance_km": round(route.distance_km, 1),
            "travel_time_hours": round(actual_time, 1),
            "cost_inr": round(actual_cost),
            "accessibility_score": round(acc_score, 1),
            "risk_score": round(route.risk_score, 1),
            "road_quality": round(route.road_quality_score, 1),
            "terrain_difficulty": round(route.terrain_difficulty, 1),
            "disruption_count": disruptions,
            "weather_condition": weather,
            "transport_mode": route.transport_mode,
            "overall_score": round(overall, 1),
            "component_scores": {
                "accessibility": round(acc_score, 1),
                "travel_time": round(time_score, 1),
                "risk": round(risk_score, 1),
                "cost": round(cost_score, 1),
                "disruption": round(disruption_score, 1),
            },
            "waypoints_latlng": waypoints_latlng,
            "is_recommended": False,  # Set after sorting
        })

    # Sort by overall score descending
    scored.sort(key=lambda x: x["overall_score"], reverse=True)
    if scored:
        scored[0]["is_recommended"] = True
        scored[0]["explanation"] = generate_explanation(scored, priority, weights)

    return scored


def generate_explanation(scored: List[Dict], priority: str, weights: Dict) -> str:
    """Generate a natural language explanation for the recommendation."""
    if not scored:
        return "No routes available."

    best = scored[0]
    alternatives = scored[1:] if len(scored) > 1 else []

    priority_labels = {
        "balanced": "balanced optimization",
        "fastest": "speed priority",
        "cheapest": "cost efficiency",
        "safest": "maximum safety",
        "most_accessible": "highest accessibility",
    }

    reason_parts = []

    # Key strengths of recommended route
    if best["accessibility_score"] >= 80:
        reason_parts.append(f"excellent accessibility ({best['accessibility_score']:.0f}/100)")
    if best["risk_score"] <= 30:
        reason_parts.append(f"low risk ({best['risk_score']:.0f}/100)")
    elif best["risk_score"] <= 50:
        reason_parts.append(f"moderate-low risk ({best['risk_score']:.0f}/100)")
    if best["disruption_count"] == 0:
        reason_parts.append("zero active disruptions")
    if best["travel_time_hours"] == min(r["travel_time_hours"] for r in scored):
        reason_parts.append(f"fastest travel time ({best['travel_time_hours']:.1f}h)")

    # Compare to alternatives
    comparisons = []
    if alternatives:
        alt = alternatives[0]
        acc_diff = best["accessibility_score"] - alt["accessibility_score"]
        if abs(acc_diff) >= 5:
            if acc_diff > 0:
                comparisons.append(f"{abs(acc_diff):.0f}% better accessibility than {alt['route_name'].split(' (')[0]}")
            else:
                comparisons.append(f"despite lower accessibility, compensated by other factors")

        risk_diff = alt["risk_score"] - best["risk_score"]
        if risk_diff > 5:
            comparisons.append(f"significantly lower disruption risk than alternatives")

        time_diff = best["travel_time_hours"] - alt["travel_time_hours"]
        if abs(time_diff) >= 1:
            if time_diff > 0:
                comparisons.append(f"{abs(time_diff):.1f}h longer but safer")
            else:
                comparisons.append(f"{abs(time_diff):.1f}h faster than next option")

        dist_diff = best["distance_km"] - alt["distance_km"]
        if abs(dist_diff) >= 20 and time_diff <= 0:
            if dist_diff > 0:
                comparisons.append(f"despite being {abs(dist_diff):.0f} km longer")

    # Construct explanation
    label = priority_labels.get(priority, "optimization")
    base = f"Route scored {best['overall_score']:.0f}/100 using {label}"

    if reason_parts:
        base += f", driven by: {', '.join(reason_parts[:2])}"
    if comparisons:
        base += f". {'. '.join(comparisons[:2]).capitalize()}."

    if best["disruption_count"] > 0:
        base += f" Note: {best['disruption_count']} active alert(s) affecting this route — factor in additional delays."

    return base
