# Quick Start Guide - Temporal QnA Agent

## 🚀 Quick Installation

### 1. Clone and Setup

```bash
git clone <your-repository>
cd temporal-qna-agent
python setup.py
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your Azure OpenAI credentials
```

**Required variables in .env:**
- `AZURE_API_BASE` - Azure OpenAI endpoint
- `AZURE_API_KEY` - API key
- `AZURE_DEPLOYMENT` - Deployment name (e.g., gpt-4o)
- `AZURE_EMBEDDINGS_ENDPOINT` - Endpoint for embeddings
- `AZURE_EMBEDDINGS_API_KEY` - Key for embeddings
- `AZURE_EMBEDDINGS_DEPLOYMENT` - Embeddings deployment

### 3. Start the Temporal Server

```bash
docker-compose up -d
```

Wait ~30s for Temporal to initialize completely.

### 4. Generate the Embeddings

```bash
python database/utils.py
```

This command processes `database/index.json` and generates `database/search_index.json` with embeddings.

### 5. Run the Application

**Option A - Automated Script (Windows):**
```bash
run.bat
```

**Option B - Automated Script (Linux/Mac):**
```bash
bash run.sh
```

**Option C - Manual (3 separate terminals):**

Terminal 1 - Worker:
```bash
python worker.py
```

Terminal 2 - API:
```bash
python api/main.py
```

Terminal 3 - Frontend:
```bash
streamlit run frontend/app.py
```

### 6. Access the Application

- 🎨 **Frontend**: http://localhost:8501
- 🌐 **API Docs**: http://localhost:8000/docs
- 📊 **Temporal UI**: http://localhost:8080

## 📝 Basic Usage

### Via Frontend (Streamlit)

1. Access http://localhost:8501
2. Click on "Start Workflow"
3. Type your question
4. Wait for the response

### Via API

```bash
# Start workflow
curl -X POST http://localhost:8000/workflows/start \
  -H "Content-Type: application/json"

# Send question
curl -X POST http://localhost:8000/workflows/{workflow_id}/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the best Python library for APIs?"}'

# View history
curl http://localhost:8000/workflows/{workflow_id}/history
```

## 🛠️ Useful Commands

With Make (if available):
```bash
make help              # List commands
make setup             # Setup environment
make docker-up         # Start Temporal
make generate-embeddings  # Generate embeddings
make run-worker        # Start worker
make run-api           # Start API
make run-frontend      # Start frontend
```

## ❓ Troubleshooting

### Worker does not connect to Temporal

Check if Temporal is running:
```bash
docker-compose ps
curl http://localhost:8233
```

### Azure credentials error

Check if .env is configured correctly:
```bash
cat .env  # Linux/Mac
type .env # Windows
```

### Embeddings not found

Run:
```bash
python database/utils.py
```

And check if `database/search_index.json` was created.

### Port in use

If any port is in use, change in .env:
```
PORT=8001  # Changes API port from 8000 to 8001
```

## 📚 Complete Documentation

- [Complete README](README.md) - Detailed documentation
- [Architecture](ARCHITECTURE.md) - How the system works
- [Contributing](CONTRIBUTING.md) - How to contribute

## 💡 Next Steps

1. Add your own documents in `database/index.json`
2. Regenerate embeddings with `python database/utils.py`
3. Customize the agent prompt in `workflows/workflow.py`
4. Explore the API at http://localhost:8000/docs

---

**Need help?** Open an [issue](https://github.com/your-username/temporal-qna-agent/issues)
