Executive summary

NovaDrive Motors MCP Tools and Frontend is a small Python-based backend (MCP server) paired with a Streamlit frontend. It exposes a set of vehicle-related tools via JSON-RPC (MCP) so an LLM-powered agent can orchestrate business tasks like listing vehicles, finding dealerships, scheduling visits, and retrieving customer info.
The frontend launches and communicates with the MCP server process, and coordinates a multi-agent conversation where a receptionist routes requests to sales or maintenance agents. All tool calls come through the MCP layer, ensuring a consistent, auditable interface for the LLM.
The system is designed to be adaptable: you can run the backend with Cloudflare’s LLM (as originally) or swap in OpenAI’s GPT models via a lightweight wrapper. It also includes debugging aids for diagnosing transport issues (notably JSON-RPC framing problems).
Core components and how they fit together

MCP server (server_agent.py)
Exposes a collection of tools (endpoints) that the LLM-based agents can call. Examples include listing vehicles, fetching dealerships, listing sellers for a dealership, getting customer info, and scheduling visits.
Acts as the authoritative source of truth for the tool logic and the data queries (e.g., database queries).
Can be configured to use different LLM backends (Cloudflare LLM or OpenAI) via a pluggable wrapper, so you can switch provider without changing the orchestration logic.
Frontend UI (chat_multi_agent.py)
Built with Streamlit, it provides a chat-like interface for users.
It manages an embedded MCP process that runs server_agent.py. This isolates the UI from the backend’s lifecycle and avoids direct in-process coupling.
Implements a multi-agent orchestration flow: a ReceptionAgent routes user requests to SalesAgent or MaintenanceAgent, and the agents coordinate tool usage to fulfill user intents.
Ensures that all interactions with the backend go through the MCP layer, keeping a consistent protocol and helpful logging.
Agent system (agents package)
Defines the conceptual agents: ReceptionAgent, SalesAgent, and MaintenanceAgent.
Each agent is configured with instructions (role, goals, constraints) and a model settings profile demanding tool usage (never guess; always call tools when needed).
The Runner orchestrates the dialogue, choosing tools, invoking them through MCP, and aggregating results for the user.
LLM backends (Cloudflare LLM or OpenAI)
The current setup can be wired to Cloudflare’s LLM or swapped to OpenAI’s GPT models via a lightweight wrapper.
The OpenAI path is designed to be drop-in with minimal changes to the rest of the architecture.
Data flow and interaction model

User action: a user types a message in the Streamlit chat UI.
UI orchestration: the UI spins up or reuses an MCP-backed server process to handle the request and then uses the agent Runner to generate responses.
Agent reasoning: the ReceptionAgent decides which other agent should handle the request (Sales vs Maintenance) and instructs the path forward.
Tool invocation: the chosen agent invokes tools via MCP (e.g., get_available_vehicles, get_dealerships, schedule_visit_for_purchase).
Results: tool results are returned through MCP to the agent, which composes a response for the user.
Response to user: the UI displays the assistant’s reply and any tool results, updating the chat history accordingly.
Transport/diagnostics: the system includes logging for tracing the end-to-end flow and diagnosing JSON-RPC framing issues (EOF/invalid JSON), with an option to enable verbose transport logs.
Configuration and environment

Environment variables and configuration
Database connection details for the vehicle-related data (host, port, name, user, password).
LLM provider credentials and configuration (Cloudflare or OpenAI) including API keys and optional model endpoints/base URLs.
Optional diagnostic knobs like verbose MCP transport logging and raw-input diagnostics to aid debugging.
.env and secrets
Secrets are kept out of source control; use a .env file or your environment manager. Do not commit real credentials.
A template .env.sample helps new developers know what to provide.
OpenAI integration (if you swap providers)
You can configure an OpenAI wrapper to talk to GPT-4 or GPT-3.5-turbo, with optional Azure/OpenAI base URLs for customization.
The rest of the system (agents, tool definitions, and orchestration) remains the same; only the LLM backend changes.
Deployment and run instructions (high level)

Start the MCP server
Run the server_agent module through the MCP runner (the exact command depends on your setup).
Run the frontend UI
Launch the Streamlit app (chat_multi_agent.py) which will manage user interaction and talk to the MCP server via the embedded process runner.
End-to-end flow
User input goes to the UI, which delegates reasoning to the multi-agent system.
The MCP server handles tool calls and returns structured results.
The UI renders the assistant’s reply and any tool outputs.
Testing and debugging

End-to-end tests
You can verify end-to-end transport by using a minimal test client that exercises a single tool (e.g., get_available_vehicles) through MCP to confirm the transport path works outside the UI.
Common issues
EOF or invalid JSON: usually a transport framing issue between UI and MCP. Enable verbose MCP logs to inspect raw payloads and adjust logging level.
Timeouts: may indicate backend slowdowns, network latency, or misconfigured rate limits. Use a local test client to isolate the backend from the UI.
Observability
Logs are organized to show tool invocations, agent route decisions, and any exceptions with stack traces.
mcp_debug.log contains transport-level details when enabled, helping pinpoint framing issues.
Security and best practices

Secrets management
Do not commit API keys or DB credentials. Use environment variables or a secret manager and keep a .env file out of version control.
Access control
If deploying publicly, consider securing the MCP endpoints and the UI against unauthorized access.
Dependency hygiene
Use a virtual environment and pin dependencies via requirements.txt to ensure reproducible installations.
Data handling
Be mindful of PII in customer data and comply with any applicable data protection policies.
Extensibility and maintenance

Adding tools
The MCP server is designed to expose additional vehicle-related tools in a straightforward way. New endpoints can be added without changing the UI or the agent logic.
Adding agents
You can extend the agent suite by adding more specialized agents or adjusting their handoffs and instructions.
Swapping LLMs
The architecture supports swapping the LLM provider with minimal disruption, enabling experiments with different models or providers.
Glossary (quick references)

MCP: A JSON-RPC based transport layer used to expose tools (endpoints) to the LLM-driven orchestrator.
Agent: A role in the multi-agent system (Reception, Sales, Maintenance) that reasons about user intent and decides which tools to call.
Runner: The orchestrator that drives the conversation, calls tools, and returns results to the UI.
OpenAI/LlM wrapper: A thin adapter that abstracts the details of the LLM API, allowing you to switch providers with minimal changes to the rest of the codebase.
EOF / invalid JSON: Common transport issues where the input stream ends unexpectedly or the payload is not valid JSON, often caused by framing mismatches between front-end and back-end.
