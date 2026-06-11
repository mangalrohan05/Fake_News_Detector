import os
import argparse
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split as tts
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC

from backend.app import config
from backend.app.predictor import preprocessing, get_embeddings, compute_rag_features

def run_training(num_samples=0, model_name=None):
    if model_name:
        config.MODEL_NAME = model_name
        
    print(f"Starting model training with embedding model: {config.MODEL_NAME}")
    
    # 1. Load dataset
    if not os.path.exists(config.CSV_DATA_PATH):
        raise FileNotFoundError(f"Dataset CSV not found at: {config.CSV_DATA_PATH}. Please make sure 'fake_or_real_news.csv' is in the workspace root.")
        
    print(f"Loading dataset from: {config.CSV_DATA_PATH}...")
    df = pd.read_csv(config.CSV_DATA_PATH, engine='python', on_bad_lines='skip')
    print(f"Loaded {len(df)} rows.")
    
    # 2. Encode labels
    le = LabelEncoder()
    df['label'] = le.fit_transform(df['label']) # FAKE -> 0, REAL -> 1 (usually)
    
    # 3. Preprocess news content
    print("Preprocessing text data...")
    df['content'] = (df['title'].fillna('') + ' ' + df['text'].fillna('')).apply(preprocessing)
    df = df[df['content'].str.len() > 100].reset_index(drop=True)
    print(f"Rows remaining after length filtering (>100 chars): {len(df)}")
    
    # 4. Handle subset sampling if specified
    if num_samples > 0 and num_samples < len(df):
        print(f"Sampling a stratified subset of {num_samples} rows for training...")
        # Stratified sampling
        df = df.groupby('label', group_keys=False).apply(lambda x: x.sample(int(num_samples * len(x) / len(df)), random_state=0)).reset_index(drop=True)
        print(f"Subset size: {len(df)} rows (Class distribution: {df['label'].value_counts().to_dict()})")
        
    # 5. Extract sentence embeddings (BERT)
    print("Computing sentence embeddings for news articles (this might take a few minutes on CPU)...")
    X_bert = get_embeddings(df['content'].tolist(), show_progress=True)
    print(f"Article embeddings shape: {X_bert.shape}")
    
    # 6. Extract RAG features against trusted facts database
    trusted_facts = config.DEFAULT_TRUSTED_FACTS
    print(f"Computing embeddings for {len(trusted_facts)} trusted reference facts...")
    fact_embeddings = get_embeddings(trusted_facts, show_progress=True)
    
    print("Computing RAG features (max, mean, top-3 similarity)...")
    X_rag = compute_rag_features(X_bert, fact_embeddings)
    print(f"RAG features shape: {X_rag.shape}")
    
    # 7. Combine features
    X_combined = np.hstack([X_bert, X_rag])
    y = df['label'].values
    print(f"Combined feature space shape: {X_combined.shape}")
    
    # 8. Train-test split
    X_train, X_test, y_train, y_test = tts(X_combined, y, test_size=0.2, random_state=0, stratify=y)
    
    # 9. Train SVC classifier
    print("Fitting Support Vector Machine (SVC) classifier...")
    model = SVC(kernel='rbf', C=10, probability=True, random_state=0)
    model.fit(X_train, y_train)
    
    # 10. Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nTraining complete!")
    print(f"Accuracy : {acc * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    
    # 11. Serialize outputs
    print(f"Saving serialized pickle files to workspace root...")
    with open(config.MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    with open(config.LABEL_ENCODER_PATH, 'wb') as f:
        pickle.dump(le, f)
    with open(config.FACT_EMBEDDINGS_PATH, 'wb') as f:
        pickle.dump(fact_embeddings, f)
    with open(config.TRUSTED_FACTS_PATH, 'wb') as f:
        pickle.dump(trusted_facts, f)
        
    print(f"Files saved:\n- {config.MODEL_PATH}\n- {config.LABEL_ENCODER_PATH}\n- {config.FACT_EMBEDDINGS_PATH}\n- {config.TRUSTED_FACTS_PATH}")
    return model, le, fact_embeddings, trusted_facts

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train SVC Fake News Detector model with BERT & RAG features.")
    parser.add_argument("--samples", type=int, default=0, help="Number of rows to sample. 0 runs on full dataset.")
    parser.add_argument("--model", type=str, default=None, help="Name of sentence transformer embedding model to use.")
    args = parser.parse_args()
    
    run_training(num_samples=args.samples, model_name=args.model)
