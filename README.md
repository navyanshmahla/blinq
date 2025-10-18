# Blinq

Data analysis and plotting platform with real-time WebSocket notifications.

## Project Structure

```
Blinq/
├── app/                      # Main FastAPI application
│   ├── main.py              # Central entry point (uvicorn app.main:app)
│   ├── routers/             # REST API endpoints
│   │   ├── plots.py         # Plot management
│   │   ├── data.py          # Data upload/query
│   │   ├── analysis.py      # Analysis endpoints (calls agent API)
│   │   ├── auth.py          # Authentication (login/register)
│   │   ├── billing.py       # Billing and usage tracking
│   │   └── user.py          # User profile and query history
│   └── background/          # Background tasks
│       └── kafka_consumers.py  # Kafka consumers for plot notifications
├── agent/                   # AI agents
│   ├── agents/
│   │   ├── main_agent.py    # Main orchestrator agent
│   │   └── analysis.py      # Analysis and plotting agent (unified)
│   ├── tools/
│   │   └── tools.py         # SQL and data exploration tools
│   └── prompts/
│       └── prompts.py       # LLM prompts
├── message_broker/          # Kafka abstraction
│   ├── config.py           # Kafka configuration
│   ├── producer.py         # Message producer (singleton)
│   └── consumer.py         # Message consumer base class
├── auth/                    # Authentication (future)
│   ├── jwt_handler.py      # JWT token creation/verification
│   ├── dependencies.py     # get_current_user() dependency
│   └── password.py         # Password hashing
└── db/                      # Database (future)
    ├── database.py         # SQLAlchemy connection
    ├── models.py           # User, QueryHistory, Transaction models
    └── crud.py             # Database operations
```

## Running the Application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Core
- `GET /health` - Health check

### Authentication (Future)
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (returns JWT)

### Analysis
- `POST /api/analysis/` - Run analysis (CSV file + query → response/cost/is_plotting/request_id)

### User Management (Future)
- `GET /api/user/profile` - Get user profile
- `GET /api/user/queries` - Get query history

### Billing (Future)
- `GET /api/billing/usage` - Get usage stats
- `GET /api/billing/history` - Get billing history

### Data & Plots (Future)
- `POST /api/data/upload` - Upload CSV
- `GET /api/data/query` - Query data
- `GET /api/plots` - List plots
- `POST /api/plots` - Create plot

## Architecture

Single FastAPI service running:
- REST APIs (all routes on `/api/*`)
- Kafka consumers (background tasks for plot notifications)
- Backend acts as middleware between frontend and agent API

All on one port for easy deployment.

**Flow:**
1. Frontend → Backend → Agent API (`/api/analysis`)
2. Agent API processes data (SQL/plotting)
3. If plotting: Agent → Kafka → Backend listens → Frontend
4. If analysis: Agent → Backend → Frontend

## Design Principles

1. **Backend as Middleware**: All frontend interactions go through backend
2. **Modular Architecture**: Separate folders for agents, auth, db, message_broker for easy swapping
3. **Request ID Correlation**: Match async plot notifications to requests without WebSockets
4. **Single Service**: Everything runs on one port for easy deployment

## Development Roadmap

### Phase 1: Foundation ✅
- [x] Agent API implementation (main_agent, analysis_agent)
- [x] Kafka message broker setup
- [x] Request ID correlation for plots

### Phase 2: Database & Auth (Next)
- [x] Set up SQLAlchemy with PostgreSQL/SQLite
- [x] User, QueryHistory, Transaction models
- [x] JWT authentication (login/register)
- [x] Protected endpoints with `get_current_user` dependency

### Phase 3: Core Features
- [x] Query history tracking
- [ ] Usage and billing tracking
- [x] Plot retrieval by request_id

### Phase 4: Polish
- [ ] Rate limiting
- [ ] Error handling and logging
- [ ] Frontend development
- [ ] Deployment configuration

# TODO
- Frontend code up

Long term plan-> include `fastapi-auth` rather than scratch implementation as its done now