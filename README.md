# Temporal QnA Agent with MCP and Azure OpenAI

Question & Answer (Q&A) system that uses **Temporal** for workflow orchestration, **Model Context Protocol (MCP)** for semantic document search, and **Azure OpenAI** with the **OpenAI Agents SDK** for intelligent response generation.

## 🏗️ Architecture

The project consists of:

- **Temporal Workflows**: Durable and resilient orchestration of question and answer flow
- **MCP Server**: Server that exposes semantic search tools via Model Context Protocol
- **Azure OpenAI**: LLM (GPT-4o) for response generation and embeddings for vector search
- **OpenAI Agents SDK**: Framework for creating intelligent agents with tools
- **FastAPI**: REST API for workflow interaction
- **Streamlit**: Web Interface for end users

## 📋 Features

- ✅ Workflow orchestration with Temporal
- ✅ Semantic document search using embeddings
- ✅ Agents with tool access (MCP)
- ✅ REST API for integration
- ✅ Interactive Web Interface
- ✅ Persistent conversation history
- ✅ Asynchronous and scalable processing

## 🚀 Prerequisites

- **Python 3.10+**
- **Temporal Server** (local via Docker or remote)
- **Azure OpenAI** (endpoint and API keys)
- **Docker** (optional, to run Temporal locally)

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/temporal-qna-agent.git
cd temporal-qna-agent
```

### 2. Create virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit the .env file with your Azure OpenAI credentials
```

### 4. Start the Temporal Server (if local)

```bash
# Using Docker Compose (see section below)
docker-compose up -d temporal
```

Or via [Temporal CLI](https://docs.temporal.io/cli):

```bash
temporal server start-dev
```

### 5. Generate search index embeddings

```bash
python database/utils.py
```

## 🎯 How to Use

### Run all components

#### 1. Worker (Terminal 1)
```bash
python worker.py
```

#### 2. FastAPI API (Terminal 2)
```bash
python api/main.py
# Or using uvicorn:
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. Streamlit Frontend (Terminal 3)
```bash
streamlit run frontend/app.py
```

#### 4. Access the application
- Frontend: http://localhost:8501
- API Docs: http://localhost:8000/docs

### Use via API

```bash
# Start a workflow
curl -X POST http://localhost:8000/workflows/start \
  -H "Content-Type: application/json" \
  -d '{"workflow_id": "qna-001"}'

# Send a question
curl -X POST http://localhost:8000/workflows/qna-001/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What are the best Python libraries for APIs?"}'

# Get history
curl http://localhost:8000/workflows/qna-001/history
```

## 📁 Project Structure

```
.
├── activities/          # Temporal Activities (MCP search)
│   └── activities.py
├── api/                 # FastAPI REST API
│   └── main.py
├── database/            # Document index and embeddings
│   ├── index.json
│   ├── search_index.json
│   └── utils.py
├── frontend/            # Streamlit Interface
│   └── app.py
├── tools/               # Utilities (LLM client)
│   └── llm_client.py
├── workflows/           # Temporal Workflows
│   └── workflow.py
├── connection.py        # Standalone Temporal client
├── mcp_server.py        # MCP Server for search
├── worker.py            # Temporal Worker
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## 🐳 Docker Compose

```bash
# Start Temporal + PostgreSQL
docker-compose up -d

# Stop services
docker-compose down
```

## 🔧 Configuration

All configurations are done via environment variables in the `.env` file:

- `AZURE_API_BASE`: Azure OpenAI endpoint
- `AZURE_API_KEY`: API key
- `AZURE_DEPLOYMENT`: Deployment name (e.g., gpt-4o)
- `AZURE_EMBEDDINGS_*`: Embeddings configurations
- `TEMPORAL_ADDRESS`: Temporal server address
- `TEMPORAL_TASK_QUEUE`: Task queue

## 🧪 Testing the Project

1. Make sure the Temporal Server is running
2. Run the worker: `python worker.py`
3. In another terminal, run the test client: `python connection.py`
4. Or use the API/Frontend as described in the "How to Use" section

## 📚 Additional Documentation

- [Temporal Docs](https://docs.temporal.io/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-sdk)
- [Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is under the MIT license. See the [LICENSE](LICENSE) file for more details.

## 👤 Author

Your Name - [@your_github](https://github.com/your-username)