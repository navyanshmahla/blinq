from prometheus_client import Counter, Histogram, Gauge

http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'path', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'path'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

login_attempts_total = Counter(
    'login_attempts_total',
    'Total login attempts',
    ['status']
)

signup_attempts_total = Counter(
    'signup_attempts_total',
    'Total signup attempts',
    ['status']
)

token_refresh_total = Counter(
    'token_refresh_total',
    'Total token refresh attempts',
    ['status']
)

csv_uploads_total = Counter(
    'csv_uploads_total',
    'Total CSV file uploads'
)

conversations_created_total = Counter(
    'conversations_created_total',
    'Total conversations created'
)

active_conversations = Gauge(
    'active_conversations',
    'Number of active conversations (not expired)'
)

analysis_requests_total = Counter(
    'analysis_requests_total',
    'Total analysis requests',
    ['status']
)

analysis_duration_seconds = Histogram(
    'analysis_duration_seconds',
    'Analysis request duration in seconds',
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['operation'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

database_errors_total = Counter(
    'database_errors_total',
    'Total database errors',
    ['operation']
)
