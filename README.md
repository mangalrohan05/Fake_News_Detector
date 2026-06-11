# 📰 FaN-De : Fake News Detector

FaN-De (Fake News Detector) is a premium, full-stack machine learning web application that evaluates the credibility of news articles. 

Unlike simple keyword matching or frequency-based models, FaN-De uses **deep semantic embeddings (Sentence-BERT)** to understand news content, extracts key statements, and validates them in real-time using a **Retrieval-Augmented Generation (RAG) pipeline** against both a database of trusted facts and live Google News articles.

---

## 🚀 Key Features

* **🧠 Semantic Modeling**: Uses `all-mpnet-base-v2` SentenceTransformer embeddings to capture context, rather than simple keyword frequencies.
* **🛡️ SVC Classification**: Classified via a Support Vector Machine (SVC) trained on textual patterns.
* **🔍 Claim-by-Claim Check**: Automatically separates the text into core factual assertions.
* **📡 Live RAG Verification**: Searches live news reports (via GNews) to gather supporting or contradicting evidence for each claim.
* **📁 Database Manager**: Includes an interactive panel to review baseline facts and dynamically add new verified statements (which are immediately embedded in vector space and saved to disk).
* **📰 News Explorer**: Browse active stories on Google News and verify them with a single click.
* **📜 Verification Logs**: Saves history locally so you can recall past checks instantly.
* **🎨 Human-Designed UI**: Responsive dark/light theme designed with a clean slate SaaS look.

---

## 🛠️ Tech Stack

### 🔹 Machine Learning & NLP
* **Sentence-Transformers**: `all-mpnet-base-v2` (for semantic text vectorization)
* **Scikit-learn**: Support Vector Classifier (RBF kernel, probability estimation)
* **Pandas & NumPy**: Feature mapping and dataset operations

### 🔹 Backend
* **FastAPI**: Modern, async ASGI framework serving endpoints
* **Uvicorn**: High-performance web server
* **GNews**: Google News client API
* **BeautifulSoup**: Article scrubbing and HTML cleaning

### 🔹 Frontend
* **HTML5, CSS3, ES6 JavaScript**: Sleek Single Page Application served statically from the backend
* **SVG Gauge Rendering**: Custom animated gauge charts

---

## 📂 Project Structure

```
Fake_News_Detector/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py         # Paths, model names, and default parameters
│   │   ├── main.py           # FastAPI routes and static files mounting
│   │   ├── predictor.py      # Claims isolation, similarity checking, and inference
│   │   └── train.py          # Standalone training CLI
│   │
│   ├── static/               # Frontend Client SPA
│   │   ├── index.html        # App layout and modals
│   │   ├── style.css         # Minimalist slate design styles
│   │   └── app.js            # API fetch calls, storage logging, and rendering
│   │
│   └── requirements.txt      # Python dependencies
│
├── fake_or_real_news.csv     # Model training dataset
├── model.pkl                 # Pre-trained SVC classifier model
├── label_encoder.pkl         # Target classes label encoder
├── fact_embeddings.pkl       # Vectorized baseline fact embeddings
├── trusted_facts.pkl         # Baseline text facts list
├── .gitignore
└── README.md
```

---

## ⚙️ Installation & Local Setup

### 1️⃣ Install Dependencies
Ensure you have **Python 3.10+** installed. Install the backend requirements:
```bash
pip install -r backend/requirements.txt
```

### 2️⃣ Initialize Pre-trained Models
Ensure the following files are present in the workspace root directory:
* `model.pkl`
* `label_encoder.pkl`
* `fact_embeddings.pkl`
* `trusted_facts.pkl`

*(If you ever need to train or retrain the classifier on the CSV dataset, run the training script:)*
```bash
# Trains model (runs on a 1000-sample subset by default to save time on CPU)
python -m backend.app.train --samples 1000
```

### 3️⃣ Launch the Server
Start the FastAPI server:
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

### 4️⃣ Open Dashboard
Open your web browser and navigate to:
```
http://127.0.0.1:8000/
```

---

## 🧪 API Endpoints

### `GET /api/status`
Returns model loading details, facts count, and config parameters.

### `POST /api/analyze`
Submits text for credibility checking.
* **Payload**:
  ```json
  {
    "text": "The article content...",
    "use_live_rag": true,
    "n_claims": 5
  }
  ```
* **Response**:
  ```json
  {
    "verdict": "REAL",
    "credibility_score": 87,
    "probabilities": { "FAKE": 0.13, "REAL": 0.87 },
    "claims": ["Statement 1", "Statement 2"],
    "evidence": [
      {
        "title": "Evidence Article Title",
        "publisher": "BBC News",
        "desc": "Summary details...",
        "url": "https://bbc.com/news/...",
        "similarity": 0.72,
        "verdict": "Supports"
      }
    ],
    "rag_mode": "live"
  }
  ```

### `GET /api/trusted-facts`
Returns the current database fact list.

### `POST /api/trusted-facts`
Dynamically adds a fact, embeds it, and saves it.
* **Payload**: `{"fact": "Factual statement here..."}`

---

## 👨‍💻 Author

**Rohan Mangal**
MBM University, Jodhpur
*(Educational Research Project)*
