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
- `POST /api/analysis` - Run analysis

## WebSocket

- `WS /ws/plots?token=<jwt>` - Real-time plot notifications

## Architecture

Single FastAPI service running:
- REST APIs (all routes on `/api/*`)
- WebSockets (all on `/ws/*`)
- Kafka consumers (background tasks)

All on one port for easy deployment.