from prometheus_client import Counter, Histogram

agent_llm_calls_total = Counter(
    'agent_llm_calls_total',
    'Total LLM API calls',
    ['model', 'status']
)

agent_llm_duration_seconds = Histogram(
    'agent_llm_duration_seconds',
    'LLM API call duration in seconds',
    ['model'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0]
)

agent_llm_cost_total = Counter(
    'agent_llm_cost_total',
    'Total LLM API cost in USD',
    ['model']
)

agent_sql_queries_total = Counter(
    'agent_sql_queries_total',
    'Total SQL queries executed',
    ['status']
)

agent_sql_duration_seconds = Histogram(
    'agent_sql_duration_seconds',
    'SQL query duration in seconds',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

agent_plot_generations_total = Counter(
    'agent_plot_generations_total',
    'Total plot generations',
    ['status']
)

agent_plot_duration_seconds = Histogram(
    'agent_plot_duration_seconds',
    'Plot generation duration in seconds',
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0]
)

agent_tool_calls_total = Counter(
    'agent_tool_calls_total',
    'Total agent tool calls',
    ['tool', 'status']
)

agent_execution_duration_seconds = Histogram(
    'agent_execution_duration_seconds',
    'Total agent execution duration in seconds',
    ['agent_type'],
    buckets=[1.0, 5.0, 10.0, 20.0, 30.0, 60.0, 120.0]
)

agent_errors_total = Counter(
    'agent_errors_total',
    'Total agent errors',
    ['agent_type', 'error_type']
)
