"""
SmartCart - Content-Based Similarity Service
Computes cosine similarity between products using product metadata
(Category, Subcategory, Brand, Tags, Description, Price, Rating).
"""

import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SimilarityEngine:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SimilarityEngine, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, data_dir=None):
        if self.initialized:
            return
            
        self.data_dir = data_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        self.products_df = None
        self.similarity_matrix = None
        self.prod_to_idx = {}
        self.idx_to_prod = {}
        self.load_and_compute()
        self.initialized = True

    def load_and_compute(self):
        csv_path = os.path.join(self.data_dir, "products.csv")
        if not os.path.exists(csv_path):
            return
            
        df = pd.read_csv(csv_path)
        self.products_df = df
        
        # Build text feature representation
        df["combined_features"] = (
            df["Category"].fillna("") + " " +
            df["Subcategory"].fillna("") + " " +
            df["Brand"].fillna("") + " " +
            df["Product_Tags"].fillna("").str.replace(",", " ") + " " +
            df["Product_Description"].fillna("")
        )
        
        tfidf = TfidfVectorizer(stop_words="english", max_features=1500)
        tfidf_matrix = tfidf.fit_transform(df["combined_features"])
        
        # Calculate Cosine Similarity
        self.similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        self.prod_to_idx = {pid: idx for idx, pid in enumerate(df["Product_ID"])}
        self.idx_to_prod = {idx: pid for idx, pid in enumerate(df["Product_ID"])}
        print(f"SimilarityEngine: Fitted cosine similarity on {len(df)} products.")

    def get_similar_products(self, product_id, top_n=6):
        """
        Returns top_n similar product dictionaries for a given product_id.
        """
        if self.products_df is None or product_id not in self.prod_to_idx:
            # Fallback to same category products
            if self.products_df is not None:
                matches = self.products_df[self.products_df["Product_ID"] != product_id]
                return matches.head(top_n).to_dict(orient="records")
            return []
            
        idx = self.prod_to_idx[product_id]
        sim_scores = list(enumerate(self.similarity_matrix[idx]))
        # Sort by similarity descending, excluding the product itself
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        top_indices = [i for i, score in sim_scores if i != idx][:top_n]
        
        results = []
        for i in top_indices:
            row = self.products_df.iloc[i].to_dict()
            row["similarity_score"] = round(float(self.similarity_matrix[idx][i]) * 100, 1)
            results.append(row)
            
        return results

similarity_engine = SimilarityEngine()
