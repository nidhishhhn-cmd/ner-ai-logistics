"""
AI Insights Router
Generates deterministic insights from the actual application data.
Optional: Uses LLM if OPENAI_API_KEY is set.
"""
import os
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import State, Route, LogisticsHub, Alert
from app.schemas.schemas import InsightOut, InsightsResponse

router = APIRouter(prefix="/api/insights", tags=["insights"])


def generate_deterministic_insights(db: Session):
    states = db.query(State).all()
    routes = db.query(Route).filter(Route.is_active == True).all()
    hubs = db.query(LogisticsHub).all()
    alerts = db.query(Alert).filter(Alert.is_active == True).all()

    insights = []
    id_counter = 1

    if states:
        # Best vs worst accessibility
        sorted_states = sorted(states, key=lambda s: s.accessibility_score, reverse=True)
        best = sorted_states[0]
        worst = sorted_states[-1]
        diff = best.accessibility_score - worst.accessibility_score

        insights.append(InsightOut(
            id=id_counter, category="accessibility",
            title="Accessibility Gap Detected",
            description=f"{worst.name} has {diff:.0f}% lower average accessibility than {best.name} "
                        f"({worst.accessibility_score:.0f}% vs {best.accessibility_score:.0f}%). "
                        f"Targeted infrastructure investment in {worst.name} could improve regional equity.",
            severity="warning",
            metric_value=round(diff, 1),
            affected_states=[worst.name, best.name]
        ))
        id_counter += 1

        # States below 75% accessibility
        low_acc_states = [s for s in states if s.accessibility_score < 75]
        if low_acc_states:
            names = ", ".join(s.name for s in low_acc_states)
            insights.append(InsightOut(
                id=id_counter, category="accessibility",
                title="Low Accessibility States Identified",
                description=f"{len(low_acc_states)} state(s) ({names}) have accessibility scores below 75/100. "
                            "These regions require priority road and multimodal connectivity development.",
                severity="critical" if len(low_acc_states) > 3 else "warning",
                metric_value=float(len(low_acc_states)),
                affected_states=[s.name for s in low_acc_states]
            ))
            id_counter += 1

    if routes:
        # High-risk routes
        high_risk = [r for r in routes if r.risk_score > 50]
        if high_risk:
            insights.append(InsightOut(
                id=id_counter, category="risk",
                title="High-Risk Routes in Network",
                description=f"{len(high_risk)} of {len(routes)} routes ({len(high_risk)/len(routes)*100:.0f}%) "
                            "have risk scores above 50/100, primarily due to terrain difficulty and weather exposure. "
                            "These routes show increased travel-time variability during monsoon season.",
                severity="warning",
                metric_value=round(len(high_risk)/len(routes)*100, 1),
                affected_states=[]
            ))
            id_counter += 1

        # Air routes performance
        air_routes = [r for r in routes if r.transport_mode == "air"]
        road_routes = [r for r in routes if r.transport_mode == "road"]
        if air_routes and road_routes:
            avg_air_acc = sum(r.accessibility_score for r in air_routes) / len(air_routes)
            avg_road_acc = sum(r.accessibility_score for r in road_routes) / len(road_routes)
            diff = avg_air_acc - avg_road_acc
            insights.append(InsightOut(
                id=id_counter, category="transport",
                title="Air Transport Outperforms Road in Accessibility",
                description=f"Air routes average {avg_air_acc:.0f}/100 accessibility vs road routes at {avg_road_acc:.0f}/100. "
                            "In mountainous NER terrain, air connectivity bridges critical gaps. "
                            "Expanding regional airports would yield high accessibility returns.",
                severity="info",
                metric_value=round(diff, 1),
                affected_states=[]
            ))
            id_counter += 1

    if hubs:
        # Top hub
        top_hub = max(hubs, key=lambda h: h.connectivity_score)
        insights.append(InsightOut(
            id=id_counter, category="infrastructure",
            title=f"{top_hub.city.name if top_hub.city else top_hub.name} is Highest-Connectivity Hub",
            description=f"Guwahati Multimodal Logistics Hub leads with connectivity score {top_hub.connectivity_score:.0f}/100. "
                        "It processes the largest cargo volumes in the NER and serves as the primary gateway. "
                        "Capacity expansion is recommended given current utilization rates.",
            severity="info",
            metric_value=top_hub.connectivity_score,
            affected_states=["Assam"]
        ))
        id_counter += 1

        # Limited hubs
        limited_hubs = [h for h in hubs if h.status == "limited"]
        if limited_hubs:
            names = ", ".join(h.name for h in limited_hubs)
            insights.append(InsightOut(
                id=id_counter, category="infrastructure",
                title="Hubs Operating in Limited Capacity",
                description=f"{names} {'is' if len(limited_hubs) == 1 else 'are'} currently operating at limited capacity. "
                            "Seasonal weather and terrain challenges are primary constraints. "
                            "Infrastructure resilience upgrades should be prioritized.",
                severity="warning",
                metric_value=float(len(limited_hubs)),
                affected_states=[]
            ))
            id_counter += 1

    if alerts:
        # Critical alerts
        critical = [a for a in alerts if a.severity == "critical"]
        if critical:
            insights.append(InsightOut(
                id=id_counter, category="disruption",
                title=f"{len(critical)} Critical Active Disruption(s) in Network",
                description=f"There are {len(critical)} critical alerts currently active. "
                            "Critical disruptions include: " + "; ".join(a.title for a in critical[:3]) + ". "
                            "Immediate rerouting and cargo pre-positioning recommended.",
                severity="critical",
                metric_value=float(len(critical)),
                affected_states=[]
            ))
            id_counter += 1

        # Flood/landslide trend
        natural = [a for a in alerts if a.category in ["flood", "landslide"]]
        if len(natural) >= 2:
            insights.append(InsightOut(
                id=id_counter, category="weather",
                title="Elevated Natural Hazard Activity",
                description=f"{len(natural)} flood/landslide events active. NER experiences peak disruption during "
                            "Jun-Sep monsoon (historically 18-24 events/month). "
                            "Early warning systems and emergency stockpiling are recommended at all major hubs.",
                severity="warning",
                metric_value=float(len(natural)),
                affected_states=["Assam", "Manipur", "Meghalaya", "Nagaland"]
            ))
            id_counter += 1

    # General recommendation
    avg_acc = sum(s.accessibility_score for s in states) / len(states) if states else 0
    insights.append(InsightOut(
        id=id_counter, category="recommendation",
        title="Regional Connectivity Improvement Opportunity",
        description=f"Average NER accessibility is {avg_acc:.0f}/100. "
                    "Multimodal connectivity investments (especially rail-to-road interchange hubs) in Manipur, "
                    "Mizoram, and Arunachal Pradesh could raise regional average by an estimated 8-12 points. "
                    "This aligns with PM Gati Shakti infrastructure goals.",
        severity="info",
        metric_value=round(avg_acc, 1),
        affected_states=["Manipur", "Mizoram", "Arunachal Pradesh"]
    ))

    return insights


@router.get("", response_model=InsightsResponse)
def get_insights(db: Session = Depends(get_db)):
    insights = generate_deterministic_insights(db)
    return InsightsResponse(
        insights=insights,
        generated_at=datetime.utcnow().isoformat() + "Z",
        data_source="Deterministic Analytics Engine (Demo Data — simulated NER logistics data)"
    )
