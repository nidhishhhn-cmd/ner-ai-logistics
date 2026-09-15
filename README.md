# NER AI Logistics Intelligence Platform

**Ministry of Development of North Eastern Region (MDoNER) — Hackathon MVP**

An AI-powered logistics intelligence platform for India's North Eastern Region that helps government officials and logistics operators optimize routes, monitor accessibility, manage disruptions, and gain data-driven insights.

---

## 🌐 Live URLs (After Starting)

| Service | URL |
|---------|-----|
| **Frontend (Web App)** | http://localhost:8000 |
| **API Documentation** | http://localhost:8000/api/docs |
| **API Health** | http://localhost:8000/api/health |
| **ReDoc** | http://localhost:8000/api/redoc |

---

## 🔑 Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@nerlogistics.demo | Demo@123 |
| **Operator** | operator@nerlogistics.demo | Operator@123 |

> ⚠️ These are demo credentials for hackathon demonstration only.

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- pip

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the Server

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**The application auto-initializes** — tables are created and demo data is seeded on first start.

### 3. Open the App

Open your browser and navigate to: **http://localhost:8000**

---

## 🏗 Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI entrypoint + static serving
│   ├── database/
│   │   ├── connection.py    # SQLAlchemy setup (SQLite/PostgreSQL)
│   │   └── seeder.py        # Demo data seeder (auto-runs on startup)
│   ├── models/
│   │   └── models.py        # SQLAlchemy ORM models
│   ├── schemas/
│   │   └── schemas.py       # Pydantic request/response schemas
│   ├── routers/
│   │   ├── auth.py          # Login, register, JWT
│   │   ├── routes.py        # Route optimization (AI scoring)
│   │   ├── geography.py     # States, cities, global search
│   │   ├── hubs.py          # Logistics hubs CRUD
│   │   ├── alerts.py        # Alerts with filtering
│   │   ├── analytics.py     # State-level analytics
│   │   ├── insights.py      # AI-generated insights
│   │   ├── dashboard.py     # KPI endpoints
│   │   └── feedback.py      # User feedback
│   └── services/
│       ├── ai_service.py    # AI route scoring engine
│       └── auth_service.py  # JWT + bcrypt
└── static/
    └── index.html           # Complete React SPA (single file)
```

---

## 🤖 How the AI Route Scoring Works

The recommendation engine uses a **transparent weighted multi-criteria model**:

```
Score = w_acc * accessibility + w_time * (1 - time_normalized) + 
        w_risk * (1 - risk_normalized) + w_cost * (1 - cost_normalized) + 
        w_dis * disruption_score
```

### Default Weights (Balanced Priority):
| Factor | Weight |
|--------|--------|
| Accessibility | 30% |
| Travel Time | 25% |
| Risk | 20% |
| Cost | 15% |
| Disruption | 10% |

### Weight Shifting by Priority:
| Priority | Top Factor |
|----------|-----------|
| Fastest | Travel Time (50%) |
| Cheapest | Cost (45%) |
| Safest | Risk (45%) |
| Most Accessible | Accessibility (50%) |
| Balanced | Even distribution |

Active alerts reduce the disruption score by -25 points per alert on the route.

---

## 🗺 Implemented Features

| Feature | Status |
|---------|--------|
| Landing page | ✅ |
| Login / Register (JWT) | ✅ |
| Main Dashboard (KPIs) | ✅ |
| Smart Route Planner | ✅ |
| AI Route Optimization | ✅ |
| Route Comparison Cards | ✅ |
| Interactive Leaflet Map | ✅ |
| Route lines on map | ✅ |
| Hub/alert markers on map | ✅ |
| AI Explanation text | ✅ |
| Weight visualization | ✅ |
| Accessibility Map | ✅ |
| State accessibility scores | ✅ |
| Logistics Hubs page | ✅ |
| Hub detail modal | ✅ |
| Hub search & filter | ✅ |
| Alerts page | ✅ |
| Alert filtering by severity | ✅ |
| Analytics dashboard | ✅ |
| 6 Recharts charts | ✅ |
| AI Insights page | ✅ |
| Data-driven insights | ✅ |
| Settings page | ✅ |
| Settings persistence | ✅ |
| Global search | ✅ |
| Loading/error/empty states | ✅ |
| Responsive design | ✅ |
| Demo data (auto-seeded) | ✅ |
| Docker Compose | ✅ |

---

## 📊 API Reference

### Authentication
```
POST /api/auth/login      - Login with email/password
POST /api/auth/register   - Register new account  
GET  /api/auth/me         - Get current user
PUT  /api/auth/me         - Update user profile
```

### Routes
```
GET  /api/routes          - List routes (filters: origin_id, dest_id, mode)
POST /api/routes/optimize - AI route optimization
GET  /api/routes/{id}     - Get route details
```

### Geography
```
GET  /api/states          - All 8 NE states
GET  /api/cities          - Cities (filter: state_id, major_only)
GET  /api/search?q=       - Global search
```

### Infrastructure
```
GET  /api/hubs            - Logistics hubs (search, status filters)
GET  /api/hubs/{id}       - Hub details
GET  /api/alerts          - Alerts (severity, category, active filters)
```

### Analytics & Intelligence
```
GET  /api/analytics/accessibility - State-level analytics
GET  /api/analytics/routes        - Route statistics
GET  /api/insights                - AI-generated insights
GET  /api/dashboard/kpis          - Dashboard KPI metrics
```

### Utility
```
GET  /api/health          - System health check
POST /api/feedback        - Submit route feedback
```

---

## 🌍 NER Data Included

- **8 States**: Assam, Arunachal Pradesh, Manipur, Meghalaya, Mizoram, Nagaland, Tripura, Sikkim
- **17 Cities**: Guwahati, Shillong, Imphal, Aizawl, Kohima, Itanagar, Agartala, Gangtok, Silchar, Dibrugarh, Tinsukia, Dimapur, Jorhat, Tezpur, Pasighat, Lumding, Jiribam
- **16 Routes**: Including NH-2, NH-6, NH-8, NH-29, NH-37, NH-39, NH-54, NH-102, NH-202, air routes
- **8 Logistics Hubs**: Guwahati, Silchar, Dimapur, Agartala, Imphal, Aizawl, Shillong, Gangtok
- **10 Active Alerts**: Landslides, floods, road closures, border delays, construction

---

## 🔮 Simulated vs Live Data

| Component | Status |
|-----------|--------|
| Route data | Simulated (realistic NER parameters) |
| State accessibility scores | Simulated (based on actual road density data) |
| Alert data | Simulated (representative of real NER disruptions) |
| Hub data | Simulated (based on real hub locations) |
| Weather conditions | Derived from route metrics |
| AI scoring | Deterministic algorithm (fully functional) |
| JWT authentication | Live |
| Map tiles | Live (OpenStreetMap) |

---

## 🐳 Docker Setup

```bash
docker-compose up --build
```

---

## 🔧 Environment Variables

```env
DATABASE_URL=sqlite:///./ner_logistics.db    # Or postgresql://...
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=optional-for-llm-insights
```

---

## 🎯 Hackathon Demo Flow (3-5 minutes)

1. Open http://localhost:8000 → Landing page
2. Click "Open Dashboard" → Login with demo credentials
3. See KPI overview: 16 routes, 8 states, 10 active alerts
4. Navigate to "Smart Routes" (sidebar)
5. Select Origin: **Guwahati** → Destination: **Imphal**
6. Mode: Road, Priority: Balanced → Click "Find Optimal Route"
7. Watch 2-3 routes appear with AI scores and map lines
8. See AI explanation for the recommended route
9. Change Priority to "Safest" → Re-run → See weights shift
10. Navigate to Alerts → Filter by "Critical"
11. Navigate to Analytics → See 6 live charts
12. Navigate to AI Insights → See 9 data-driven insights
13. Navigate to Logistics Hubs → Click a hub for detailed modal
14. Navigate to Settings → Update preferences → Save

---

## 🚀 Future Improvements

- PostgreSQL migration for production
- Real-time weather API integration (IMD, OpenWeatherMap)
- NHAI live traffic API integration  
- National highway GIS data for accurate route drawing
- LLM-powered AI insights (OpenAI/Gemini integration ready)
- Mobile app (React Native)
- Multi-language support (Assamese, Hindi)
- Government cargo tracking integration
- Real logistics operator feedback loops
