# FaN-De: Fake News Detector 📰

> Fake-news classifier with **Sentence-BERT** semantic embeddings and **live web retrieval** (gnews) — a lightweight RAG pipeline for real-time fact context.

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://python.org)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-yellow?logo=huggingface)](https://huggingface.co)

## How It Works

Unlike keyword-matching or frequency-based classifiers, FaN-De uses **Sentence-BERT** to understand the semantic meaning of a news article. It also fetches real-time related articles via gnews to provide live fact context — making it a lightweight RAG pipeline.

```
Article text
     │
     ▼
Sentence-BERT embedding (DistilBERT base)
     │
     ├── Cosine similarity vs. labeled training set
     │
     ▼
gnews live retrieval ── top real-time related articles
     │
     ▼
Hybrid credibility score -> Fake / Real verdict
```

## Features

- **Semantic Understanding** — Sentence-BERT captures meaning, not just keywords
- **Live Fact Context** — gnews fetches related real articles at inference time
- **Scikit-learn Pipeline** — trained on labeled CSV; Precision / Recall / F1 evaluation
- **Full-stack Web App** — React/Vite frontend + Python Flask backend
- **Pre-trained Models** — model.pkl, label_encoder.pkl, fact_embeddings.pkl included

## Tech Stack

| Component | Technology |
|---|---|
| Embeddings | sentence-transformers (DistilBERT) |
| Live Retrieval | gnews |
| ML Pipeline | scikit-learn |
| Backend | Python Flask |
| Frontend | React (Vite) |
| Data | fake_or_real_news.csv (Kaggle) |

## Setup

```bash
git clone https://github.com/mangalrohan05/Fake_News_Detector
cd Fake_News_Detector/backend
pip install -r requirements.txt
python app.py   # starts Flask on :5000

# Frontend (new terminal)
cd ../frontend
npm install && npm run dev
```

## Repository Structure

```
Fake_News_Detector/
├── Fake_News_Detection.ipynb  # Exploration & training notebook
├── backend/                   # Flask API
├── model.pkl                  # Trained classifier
├── label_encoder.pkl
├── fact_embeddings.pkl        # Pre-computed fact embeddings
└── fake_or_real_news.csv      # Training dataset
```