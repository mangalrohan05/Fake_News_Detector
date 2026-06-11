import os
import re
import pickle
import numpy as np
from gnews import GNews
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from backend.app import config

# Lazy loading of sentence transformer
_embedder = None
_gnews_client = None

def get_embedder():
    global _embedder
    if _embedder is None:
        print(f"Loading SentenceTransformer: {config.MODEL_NAME}...")
        _embedder = SentenceTransformer(config.MODEL_NAME)
    return _embedder

def get_gnews_client():
    global _gnews_client
    if _gnews_client is None:
        _gnews_client = GNews(
            language='en',
            country='us',
            period='30d',
            max_results=6,
        )
    return _gnews_client

# Text preprocessing
def preprocessing(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Get embeddings
def get_embeddings(texts, batch_size=64, show_progress=False):
    if isinstance(texts, str):
        texts = [texts]
    embedder = get_embedder()
    return embedder.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        convert_to_numpy=True,
    )

# Claim extraction
def extract_claims(text, n=5):
    # Split text into sentences by period, exclamation, or question mark
    raw_sentences = re.split(r'[.!?]+', text)
    sentences = []
    for s in raw_sentences:
        cleaned = s.strip()
        # Clean double spaces/newlines
        cleaned = re.sub(r'\s+', ' ', cleaned)
        # Filters out short/irrelevant snippets, matching notebook criteria (> 40 chars)
        if len(cleaned) > 40:
            sentences.append(cleaned)
    return sentences[:n]

# Search news snippets on GNews
def search_gnews(query):
    gnews_client = get_gnews_client()
    try:
        results = gnews_client.get_news(query)
        snippets = []
        for article in results:
            title = article.get('title', '')
            description = article.get('desc', '')
            combined = f"{title} {description}"
            # Clean HTML tags and weird whitespace if any
            combined = re.sub(r'\s+', ' ', combined).strip()
            if combined and len(combined) > 20:
                snippets.append({
                    "text": combined,
                    "title": title,
                    "desc": description,
                    "url": article.get('link', ''),
                    "published": article.get('published date', ''),
                    "publisher": article.get('publisher', {}).get('title', 'Google News')
                })
        return snippets
    except Exception as e:
        print(f"  GNews search failed for '{query[:40]}': {e}")
        return []

# Live evidence retrieval
def fetch_live_evidence(article_text, n_claims=5):
    claims = extract_claims(article_text, n=n_claims)
    evidence = []
    seen_texts = set()
    
    for claim in claims:
        # Notebook cuts to first 60 chars for query
        query = claim[:60]
        results = search_gnews(query)
        for res in results:
            snippet_text = res["text"]
            if snippet_text not in seen_texts:
                seen_texts.add(snippet_text)
                evidence.append(res)
                
    return evidence, claims

# RAG feature calculation
def compute_rag_features(article_embeddings, reference_embeddings):
    # sims size is: (num_articles, num_references)
    sims = cosine_similarity(article_embeddings, reference_embeddings)
    max_sim = sims.max(axis=1, keepdims=True)
    mean_sim = sims.mean(axis=1, keepdims=True)
    # Get mean of top 3 similarities
    # Sort and take last 3 columns
    sorted_sims = np.sort(sims, axis=1)
    if sorted_sims.shape[1] >= 3:
        top3_sim = sorted_sims[:, -3:].mean(axis=1, keepdims=True)
    else:
        # Fallback if there are fewer than 3 references
        top3_sim = sorted_sims.mean(axis=1, keepdims=True)
        
    return np.hstack([max_sim, mean_sim.reshape(-1, 1), top3_sim.reshape(-1, 1)])

# Model State Manager
class ModelManager:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.fact_embeddings = None
        self.trusted_facts = []
        self.is_loaded = False
        
    def load_model(self):
        if self.is_loaded:
            return True
            
        if not (os.path.exists(config.MODEL_PATH) and 
                os.path.exists(config.LABEL_ENCODER_PATH) and 
                os.path.exists(config.FACT_EMBEDDINGS_PATH) and 
                os.path.exists(config.TRUSTED_FACTS_PATH)):
            print("Model files missing. Please train the model first.")
            self.is_loaded = False
            return False
            
        try:
            with open(config.MODEL_PATH, 'rb') as f:
                self.model = pickle.load(f)
            with open(config.LABEL_ENCODER_PATH, 'rb') as f:
                self.label_encoder = pickle.load(f)
            with open(config.FACT_EMBEDDINGS_PATH, 'rb') as f:
                self.fact_embeddings = pickle.load(f)
            with open(config.TRUSTED_FACTS_PATH, 'rb') as f:
                self.trusted_facts = pickle.load(f)
                
            self.is_loaded = True
            print("Model files loaded successfully.")
            return True
        except Exception as e:
            print(f"Error loading model files: {e}")
            self.is_loaded = False
            return False

    def add_trusted_fact(self, fact_text):
        """Adds a trusted fact, computes its embedding, updates memory and disk."""
        if not self.is_loaded:
            loaded = self.load_model()
            if not loaded:
                # Initialize empty state if files don't exist
                self.trusted_facts = config.DEFAULT_TRUSTED_FACTS.copy()
                self.fact_embeddings = get_embeddings(self.trusted_facts)
                self.is_loaded = True
        
        preprocessed = preprocessing(fact_text)
        if preprocessed in self.trusted_facts:
            return False, "Fact already exists in database"
            
        # 1. Compute embedding
        emb = get_embeddings(preprocessed) # shape (1, 768)
        
        # 2. Update memory list and numpy array
        self.trusted_facts.append(preprocessed)
        self.fact_embeddings = np.vstack([self.fact_embeddings, emb])
        
        # 3. Save to disk
        try:
            with open(config.TRUSTED_FACTS_PATH, 'wb') as f:
                pickle.dump(self.trusted_facts, f)
            with open(config.FACT_EMBEDDINGS_PATH, 'wb') as f:
                pickle.dump(self.fact_embeddings, f)
            return True, "Fact added successfully"
        except Exception as e:
            return False, f"Failed to save updated database: {e}"

    def analyze_news(self, text, use_live_rag=True, n_claims=5):
        if not self.is_loaded:
            success = self.load_model()
            if not success:
                return {"error": "Classifier model is not trained/loaded. Please run the training first."}
                
        # Preprocess text
        cleaned_text = preprocessing(text)
        if len(cleaned_text) < 20:
            return {"error": "Article content is too short for meaningful analysis."}
            
        # Get BERT embedding for article
        emb_article = get_embeddings(cleaned_text) # shape: (1, 768)
        
        evidence_list = []
        claims = []
        
        if use_live_rag:
            # 1. Fetch live news evidence based on claims
            live_snippets_info, claims = fetch_live_evidence(text, n_claims=n_claims)
            
            if live_snippets_info:
                # Extract snippet strings for embedding calculations
                live_snippets = [item["text"] for item in live_snippets_info]
                
                # Preprocess snippets
                processed_snippets = [preprocessing(s) for s in live_snippets]
                
                # Compute embeddings of evidence snippets
                evidence_embs = get_embeddings(processed_snippets)
                
                # Compute similarity with current article
                rag_features = compute_rag_features(emb_article, evidence_embs)
                
                # Format evidence details to return to frontend
                # Calculate similarity score for each snippet separately
                sims = cosine_similarity(emb_article, evidence_embs)[0]
                for idx, val in enumerate(sims):
                    item = live_snippets_info[idx].copy()
                    item["similarity"] = float(val)
                    # Support vs Contradict criteria: if similarity > 0.5 we check content similarity
                    # Let's label it as 'support', 'refute' or 'neutral' based on cosine score
                    if val > 0.55:
                        item["verdict"] = "Supports"
                    elif val > 0.35:
                        item["verdict"] = "Related"
                    else:
                        item["verdict"] = "Neutral"
                    evidence_list.append(item)
            else:
                # Fallback to static facts if no live news found
                rag_features = compute_rag_features(emb_article, self.fact_embeddings)
                evidence_list = self._get_static_evidence_matches(emb_article, top_k=3)
        else:
            # Use static facts
            claims = extract_claims(text, n=n_claims)
            rag_features = compute_rag_features(emb_article, self.fact_embeddings)
            evidence_list = self._get_static_evidence_matches(emb_article, top_k=3)
            
        # Combine BERT and RAG features
        X_combined = np.hstack([emb_article, rag_features])
        
        # SVC predictions
        verdict_idx = self.model.predict(X_combined)[0]
        probs = self.model.predict_proba(X_combined)[0] # [p_fake, p_real] or vice versa depending on label encoder
        
        # Get human readable classes
        classes = self.label_encoder.classes_ # e.g. ['FAKE', 'REAL']
        verdict_label = classes[verdict_idx]
        
        # Create map of probabilities
        prob_dict = {classes[i]: float(probs[i]) for i in range(len(classes))}
        
        # Calculate overall credibility score (0 - 100) based on REAL probability
        credibility_score = int(prob_dict.get("REAL", 0.0) * 100)
        
        # Ensure we return clean types
        return {
            "verdict": verdict_label,
            "credibility_score": credibility_score,
            "probabilities": prob_dict,
            "claims": claims,
            "evidence": evidence_list,
            "rag_mode": "live" if (use_live_rag and evidence_list) else "static"
        }
        
    def _get_static_evidence_matches(self, article_emb, top_k=3):
        # Calculate cosine similarity with all static facts
        sims = cosine_similarity(article_emb, self.fact_embeddings)[0]
        top_indices = np.argsort(sims)[-top_k:][::-1]
        
        matches = []
        for idx in top_indices:
            score = float(sims[idx])
            fact_text = self.trusted_facts[idx]
            
            if score > 0.55:
                verdict = "Supports"
            elif score > 0.35:
                verdict = "Related"
            else:
                verdict = "Neutral"
                
            matches.append({
                "text": fact_text,
                "title": "Trusted Fact Database",
                "desc": fact_text,
                "url": "",
                "publisher": "Veritas Fact DB",
                "published": "Verified Static Record",
                "similarity": score,
                "verdict": verdict
            })
        return matches

# Create global manager instance
model_manager = ModelManager()
