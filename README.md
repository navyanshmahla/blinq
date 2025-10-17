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
│   │   └── analysis.py      # Analysis endpoints
│   ├── websockets/          # WebSocket endpoints
│   │   └── plots.py         # Plot notifications
│   └── background/          # Background tasks
│       └── kafka_consumers.py  # Kafka consumers
├── agent/                   # AI agents
│   └── agents/
│       └── plotter.py       # Plotting agent
├── message_broker/          # Kafka abstraction
│   ├── config.py           # Kafka configuration
│   ├── producer.py         # Message producer
│   └── consumer.py         # Message consumer
├── auth/                    # Authentication
│   └── websocket_auth.py   # WebSocket JWT auth
└── db/                      # Database (future)
```

## Running the Application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/plots` - List plots
- `POST /api/plots` - Create plot
- `POST /api/data/upload` - Upload CSV
- `GET /api/data/query` - Query data
- `POST /api/analysis` - Run analysis (accepts CSV file + query, returns response/cost/is_plotting)

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

## NOTE:
Any interaction with the frontend happens through the backend ie backend acts as the middleware. All the APIs are through that. For frontend in case of image plots, it gets routed through backend. Websockets are prolly not needed. 

# TODOs:
1. Backend APIs
2. DB 
3. Auth
4. Frontend of the app