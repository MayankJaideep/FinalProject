# Lumina Copilot — AI Legal Research Engine

**Lumina Copilot** is an AI-driven research and prediction engine for Indian commercial courts. It combines a hybrid retrieval pipeline (FAISS + BM25 + CrossEncoder reranking) with a stacking ML model (XGBoost + LightGBM + Random Forest) to retrieve semantically similar case law and predict litigation outcomes. A LangGraph multi-tool agent orchestrates all reasoning and exposes a clean FastAPI backend to a React/Vite/Tailwind frontend.

---

## Architecture Overview

Lumina operates on two parallel tracks:

```
User Query
    │
    ├─► Track 1: RAG Pipeline
    │       1. InLegalBERT Dense Retrieval (FAISS / Milvus Lite)
    │       2. BM25 Sparse Retrieval
    │       3. Reciprocal Rank Fusion (RRF) merge
    │       4. CrossEncoder Reranking
    │       └─► Top-k chunks → LangGraph Agent → LLM (Gemini → OpenAI → Ollama)
    │
    └─► Track 2: ML Prediction
            1. Enhanced Feature Extractor (20 features)
            2. Stacking Model (XGBoost + LightGBM + Random Forest → Meta LR)
            └─► Outcome probability + confidence score
```

**Vector Store**: Milvus Lite (default, zero-dependency, file-based). FAISS is the automatic fallback if Milvus is unavailable. The Docker Compose Milvus stack (`infrastructure/docker-compose.yml`) is for production-scale deployments only.

**LLM Fallback Chain**: Gemini 1.5 Flash (`GEMINI_API_KEY`) → GPT-4o-mini (`OPENAI_API_KEY`) → Ollama `llama3.2` (local, no key required).

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.9+ |
| Node.js | 18+ |
| Ollama | latest |

Install Ollama and pull the default model:
```bash
# Install from https://ollama.com
ollama pull llama3.2
```

---

## Setup

### 1. Environment Configuration

Copy the template and fill in your keys:
```bash
cp .env.example .env
```

Edit `.env`:
```dotenv
GEMINI_API_KEY="your_gemini_key"           # Primary LLM – get from aistudio.google.com
OPENAI_API_KEY="your_openai_key"           # Fallback LLM (optional)
LUMINA_API_KEY="secret-lumina-key-2026"    # Backend API key for frontend
ALLOWED_ORIGINS="http://localhost:5173"    # Comma-separated frontend URLs
INDIAN_KANOON_API_TOKEN="your_token"       # Optional: live case law search
```

### 2. Backend

```bash
cd "1-Rag"
python -m venv .venv && source .venv/bin/activate
pip install -r ../requirements.txt
uvicorn api:app --reload --port 8000
```

> **Important**: The backend must be started from within the `1-Rag/` directory. Starting from the project root will cause import failures.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Running

| Service | Command | URL |
|---|---|---|
| Backend | `cd 1-Rag && uvicorn api:app --reload` | http://localhost:8000 |
| Frontend | `cd frontend && npm run dev` | http://localhost:5173 |

---

## API Endpoints

| Method | Path | Description | Body / Response |
|---|---|---|---|
| `GET` | `/health` | System health check | `{status, vector_db, bm25_loaded, ml_model_loaded, docs_indexed, llm}` |
| `POST` | `/chat` | Main agent chat | `{message: str (max 4000 chars), history, language, jurisdiction}` |
| `POST` | `/upload` | Ingest PDF documents | `multipart/form-data` with `files[]` (PDF only, ≤20 MB each, magic bytes verified) |
| `POST` | `/similar_cases` | Find similar cases by description | `{description, jurisdiction?}` |
| `POST` | `/predict` | Predict case outcome | `{description, court?, sections?}` |
| `GET` | `/llm-status` | Active LLM provider info | `{provider, model}` |
| `POST` | `/visualize/timeline` | Extract chronological timeline from text | `{text}` |
| `GET` | `/performance-metrics` | Request latency and cache stats | JSON metrics object |

All endpoints with model loading are wrapped with a **60-second asyncio timeout** and return `504` with a user-friendly message on timeout.

---

## Data & Training

### Fetching Training Data

Case law data is collected using `generate_training_data.py` and `enhanced_training_data.py` from the Indian Kanoon API (requires `INDIAN_KANOON_API_TOKEN`):

```bash
cd 1-Rag
python generate_training_data.py    # Basic case set
python enhanced_training_data.py    # Expanded, augmented set
```

Data is saved to `1-Rag/dataset/`.

### Retraining the Stacking Model

```bash
cd 1-Rag
python train_hybrid_model.py        # Base stacking model
python train_improved_model.py      # Improved variant (run after base)
```

Trained models are saved to `1-Rag/models/stacking_model.pkl` and related files.

---

## Model Notes

The stacking ensemble uses three base learners:
- **XGBoost** — captures non-linear feature interactions
- **LightGBM** — high-speed gradient boosting for large datasets
- **Random Forest** — variance reduction via bagging

A **Logistic Regression** meta-learner is trained on the out-of-fold predictions of the base learners.

Feature engineering is handled by `enhanced_feature_extractor.py` (20 features, production) and `feature_extractor.py` (6 features, legacy fallback, `__version__ = "legacy"`).

**Improvement levers**:
- Add more jurisdiction-specific training data (High Court vs. Supreme Court)
- Fine-tune InLegalBERT on your ingested corpus using the FAISS store
- Increase `chunk_size` and `chunk_overlap` in the document ingestion pipeline for better semantic chunking

---

## Vector Store Notes

| Mode | When Used |
|---|---|
| **Milvus Lite** | Default. Zero infra, file-based (`milvus_demo.db`). Works out of the box. |
| **FAISS** | Automatic fallback if Milvus Lite fails. Index saved to `1-Rag/faiss_store/`. |
| **Docker Milvus** | Production only. Run `docker-compose -f infrastructure/docker-compose.yml up`. |

---

## Running Tests

```bash
# From project root
pip install pytest
pytest
```

| Test File | Coverage |
|---|---|
| `tests/test_api.py` | Core API endpoint smoke tests |
| `tests/test_predictor.py` | OutcomePredictor (valid, empty, long input) |
| `tests/test_feature_extractor.py` | Enhanced (20 features) + Fallback (6 features) |
| `tests/test_rag_pipeline.py` | LegalNER entity extraction |
| `tests/test_translations.py` | Multi-language translation pipeline |

---

## License

MIT
