# AI-Driven Legal Research & Prediction Engine

An advanced legal tech platform that combines **Retrieval-Augmented Generation (RAG)** for legal research with **State-of-the-Art Machine Learning** for case outcome prediction.

![Dashboard Preview](frontend/src/assets/react.svg)

## 🚀 Key Features

### 1. Intelligent Legal Research (RAG)
- **Chat Interface**: Ask complex legal questions in natural language.
- **Source Citations**: Answers are grounded in your uploaded PDF documents (Acts, Case Laws).
- **Agentic Workflow**: Uses LangGraph to orchestrate research, summarization, and drafting.

### 2. Case Outcome Prediction (Advanced ML)
- **Stacking Ensemble**: Combines **XGBoost**, **LightGBM**, and **Random Forest** for robust predictions.
- **BERT Semantic Embeddings**: Uses `all-MiniLM-L6-v2` to understand the deep semantic context of case descriptions (not just keywords).
- **Dual Modes**: 
    - **Advanced**: Uses full AI stack (Embeddings + Ensemble).
    - **Legacy**: Uses metadata-only heuristic model.

### 3. Modern Web Interface
- **Frontend**: Faster, responsive UI built with **React**, **Vite**, and **Tailwind CSS v4**.
- **Backend**: High-performance REST API powered by **FastAPI**.
- **Visualizations**: Interactive charts for prediction confidence and probability distribution.

## 🛠️ Technology Stack

- **Frontend**: React, Tailwind CSS, Lucide Icons, Recharts, Axios.
- **Backend**: FastAPI, Uvicorn, LangChain, LangGraph.
- **ML/AI**: XGBoost, LightGBM, Scikit-Learn, Sentence-Transformers (BERT), Ollama (Local LLM).
- **Database**: Milvus Lite (Vector Store for RAG).

## 📦 Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js & npm
- API Keys: `INDIAN_KANOON_API_TOKEN` (optional, for fetching real usage data).

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/MayankJaideep/MajorProjectsSee.git
cd MajorProjectsSee

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_key_here" > .env
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

## 🏃‍♂️ Running the Application

### Start the Backend API
```bash
# From the project root
cd 1-Rag
uvicorn api:app --reload
```
The API will run at `http://localhost:8000`.

### Start the Frontend
```bash
# From the frontend directory
npm run dev
```
The UI will be accessible at `http://localhost:5173`.

## 🧠 ML Model Training

To retrain the outcome prediction models with your own data:

1. **Add Data**: Place CSV data in `1-Rag/data/` or use the fetcher script.
2. **Fetch Real Cases**:
    ```bash
    python scripts/fetch_real_cases.py
    ```
3. **Train Model**:
    ```bash
    python 1-Rag/train_improved_model.py
    ```

## 📂 Project Structure

```
├── 1-Rag/
│   ├── api.py                  # FastAPI Backend
│   ├── core_agent.py           # LangGraph Agent Logic
│   ├── outcome_predictor.py    # Prediction Inference Engine
│   ├── train_improved_model.py # ML Training Pipeline
│   ├── bert_feature_extractor.py # Semantic Embedding Logic
│   └── models/                 # Saved ML Models & Encoders
├── frontend/
│   ├── src/
│   │   ├── components/         # React Components (Chat, Dashboard, etc.)
│   │   └── App.jsx             # Main Frontend Logic
├── scripts/
│   └── fetch_real_cases.py     # Data Collection Utility
└── requirements.txt
```

## 📝 License
This project is open-source.
