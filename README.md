NovaDrive Motors MCP Tools and Frontend

A lightweight Python-based backend (MCP server) paired with a Streamlit frontend. It exposes vehicle-related tools via JSON-RPC (MCP) so an AI agent can orchestrate operations such as listing vehicles, finding dealerships, scheduling visits, and retrieving customer information. The design supports swapping the LLM provider (Cloudflare or OpenAI) with minimal changes to orchestration logic.

Table of Contents


What this project does

Core components

How data flows

Prerequisites

Repository structure

Installation and setup

Configuration

Run instructions

How to use

Debugging and troubleshooting

Testing

Security and best practices

Extensibility

Contributing

License

Support


What this project does


Provides a server (MCP) that exposes a suite of vehicle-related tools as endpoints.

Presents a user-friendly chat UI (Streamlit) that communicates with the MCP server through a managed process.

Enables an AI-driven multi-agent workflow (ReceptionAgent, SalesAgent, MaintenanceAgent) to route user requests through the appropriate tools.

Supports multiple LLM backends (Cloudflare LLM or OpenAI) via a pluggable interface, allowing experiments and cost considerations.

Includes debugging aids to diagnose JSON-RPC transport issues (EOF and invalid JSON) and to improve reliability.


Core components and how they fit together


MCP server (server_agent.py)

Exposes tool endpoints such as get_available_vehicles, get_dealerships, get_sellers_by_dealership, get_customer_info, schedule_visit_for_purchase, and schedule_visit_for_maintenance.

Serves as the authoritative backend for tool logic and data access.

Uses a pluggable LLM backend (Cloudflare LLM or OpenAI wrapper) to generate orchestration plans.




Frontend UI (chat_multi_agent.py)

Built with Streamlit to provide a chat-like interface.

Manages an embedded MCP server process, isolating UI and backend lifecycles.

Implements a multi-agent flow where the ReceptionAgent routes requests to SalesAgent or MaintenanceAgent and aggregates results for the user.




Agent system (agents)

Defines ReceptionAgent, SalesAgent, and MaintenanceAgent.

Each agent has role-specific instructions and a tool-first policy (use tools when needed, don’t guess).

A Runner coordinates dialogue, tool invocation through MCP, and response composition.




LLM backends

Cloudflare LLM (default) or a drop-in OpenAI-based wrapper.

The architecture is designed for easy swapping, with minimal changes to the rest of the system.





Data flow and interaction model


User action: A user types a message in the Streamlit chat UI.

UI orchestration: The UI starts or reuses an MCP-backed server process to handle the request and invokes the agent Runner.

Agent reasoning: ReceptionAgent decides which downstream agent should handle the request and what tooling to call.

Tool invocation: The chosen agent calls MCP endpoints (e.g., get_available_vehicles, schedule_visit_for_purchase).

Results: Tool outputs flow back through MCP to the agent, which composes a user-facing response.

Response: The UI presents the assistant’s reply along with any tool outputs.

Diagnostics: Detailed logging supports tracing the end-to-end flow and diagnosing framing issues in JSON-RPC.


Prerequisites


Git

Python 3.11–3.13 (tested with recent 3.x)

pip (Python package manager)

Optional: PostgreSQL server if you want database-backed tooling

On Windows, a terminal capable of running MCP and Python commands


Environment and secrets


Keep secrets out of version control. Use a .env file or a secret manager.

Template configuration is provided in .env.sample.


Repository structure (example)


server_agent.py          # MCP-backed server exposing tools

chat_multi_agent.py        # Streamlit frontend that uses MCPServerStdio

test_mcp_client.py         # Optional minimal MCP client for local tests

requirements.txt            # Python dependencies

.env.sample                 # Template for environment variables

README.md                    # This file

mcp_debug.log (optional)    # Generated during debugging (if enabled)


Installation and setup



Clone the repository


git clone https://github.com/your-org/your-repo.git

cd your-repo





Create and activate a virtual environment


Windows:

python -m venv venv

venv\Scripts\activate




macOS/Linux:

python3 -m venv venv

source venv/bin/activate








Install dependencies


pip install -r requirements.txt





Prepare environment variables


Copy the template and fill in values:

cp .env.sample .env

Edit .env with your real credentials








Optional: run a quick test client


python test_mcp_client.py

This helps verify end-to-end transport to the MCP server outside the UI.





Configuration (env.sample)


Database

DB_HOST=localhost

DB_PORT=5432

DB_NAME=novadrive

DB_USER=postgres

DB_PASSWORD=yourpassword




LLM provider (Cloudflare LLM or OpenAI wrapper)

For Cloudflare: CF_ACCOUNT_ID, CF_API_TOKEN

For OpenAI: OPENAI_API_KEY, OPENAI_ORGANIZATION (optional), OPENAI_API_BASE (optional, e.g., Azure OpenAI), OPENAI_MODEL (gpt-4, gpt-3.5-turbo)




Diagnostics

MCP_LOG_LEVEL (e.g., INFO, DEBUG)

DIAG_MCP_RAW (0 or 1; enable raw diagnostics)
Notes:




Do not commit real credentials. Use .env and add it to .gitignore.

If you’re not using Cloudflare LLM, you can omit CF_ variables.


Run instructions


Start the MCP server:

mcp run ./server_agent.py




Start the UI (if you use chat_multi_agent.py):

streamlit run chat_multi_agent.py




Access to the UI is typically http://localhost:8501 (default Streamlit port)


Usage


Typical flow:

User inputs a query (e.g., “Show me available vehicles”)

UI starts an MCP-backed server process and uses the agent Runner to orchestrate tool calls

The MCP server executes the required tools and returns results

The UI presents the assistant’s reply and tool outputs to the user





Debugging and troubleshooting


Symptom: EOF or invalid JSON

Likely a transport framing issue between UI and MCP. Enable verbose MCP logs (MCP_LOG_LEVEL=DEBUG) and inspect mcp_debug.log.




Symptom: Timeouts

Backend or network delays. Use a minimal test client to verify connectivity independently of the UI.




Observability

Logs capture tool invocations, agent routing, and exceptions with stack traces.

mcp_debug.log contains transport-level details when enabled.





Testing


End-to-end testing involves:

Running the MCP server in one terminal

Running a minimal test client (if available) to exercise a tool path

Running the Streamlit UI for UI-level end-to-end validation




Use the test_mcp_client.py script (if included) to exercise a simple endpoint like get_available_vehicles.


Security and best practices


Secrets management: never commit API keys or DB credentials. Use environment variables or secret managers.

Access control: consider securing MCP endpoints and the UI if deployed publicly.

Dependency hygiene: use a virtual environment and pin dependencies via requirements.txt.

Data handling: be mindful of PII and comply with applicable data protection policies.


Extensibility and maintainability


Adding tools: The MCP server is designed to expose new tools without changing the UI or agent logic.

Adding agents: Extend the agent suite by adding more specialized roles or adjusting handoff behavior.

Swapping LLMs: The system supports swapping the LLM provider with minimal disruption; only the wrapper and configuration may need adjustment.


Contributing


Fork the repository

Create a feature branch

Open a pull request with a descriptive summary

Include notes on testing and any new environment variables




