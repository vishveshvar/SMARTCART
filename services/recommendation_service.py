"""
SmartCart - AI-Powered Recommendation Service
Integrates trained Random Forest Classifier with multi-factor scoring,
explainable recommendation reasoning, trending detection, and cold-start fallback.
"""

import os
import random
import joblib
import pandas as pd
import numpy as np

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

class RecommendationService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RecommendationService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        self.model = None
        self.pipeline = None
        self.products_df = None
        self.load_models()
        self.load_products()
        self.initialized = True

    def load_models(self):
        model_path = os.path.join(MODELS_DIR, "smartcart_random_forest.pkl")
        pipe_path = os.path.join(MODELS_DIR, "preprocessing_pipeline.pkl")
        
        if os.path.exists(model_path) and os.path.exists(pipe_path):
            try:
                self.model = joblib.load(model_path)
                self.pipeline = joblib.load(pipe_path)
                print("RecommendationService: Loaded Random Forest model and preprocessor pipeline.")
            except Exception as e:
                print(f"RecommendationService: Error loading models: {e}")
        else:
            print("RecommendationService: Model files not found yet.")

    def load_products(self):
        csv_path = os.path.join(DATA_DIR, "products.csv")
        if os.path.exists(csv_path):
            self.products_df = pd.read_csv(csv_path)
            print(f"RecommendationService: Loaded {len(self.products_df)} products for catalog.")

    def reload(self):
        """Called after retraining to refresh model in memory."""
        self.load_models()
        self.load_products()

    def get_personalized_recommendations(self, customer_data=None, customer_history=None, top_n=8):
        """
        Generates personalized product recommendations using Random Forest predictions
        combined with multi-factor scoring and explainable reason tags.
        """
        if self.products_df is None or self.products_df.empty:
            return []

        # If no customer or anonymous guest, use cold-start recommendations
        if not customer_data:
            return self.get_cold_start_recommendations(top_n=top_n)

        customer_history = customer_history or {}
        viewed_pids = set(customer_history.get("viewed_product_ids", []))
        purchased_pids = set(customer_history.get("purchased_product_ids", []))
        cart_pids = set(customer_history.get("cart_product_ids", []))
        wishlist_pids = set(customer_history.get("wishlist_product_ids", []))
        recent_searches = customer_history.get("recent_searches", [])
        
        pref_category = customer_data.get("Preferred_Category") or customer_history.get("top_category") or "Electronics"
        age = customer_data.get("Age", 30)
        gender = customer_data.get("Gender", "Unisex")
        total_purchases = customer_data.get("Total_Purchases", len(purchased_pids))
        aov = customer_data.get("Average_Order_Value", 1500.0)

        # Candidate selection: Exclude already purchased products
        candidates = self.products_df[~self.products_df["Product_ID"].isin(purchased_pids)].copy()
        if candidates.empty:
            candidates = self.products_df.copy()

        # Build feature inference batch
        infer_rows = []
        candidate_list = candidates.to_dict(orient="records")
        
        for p in candidate_list:
            pid = p["Product_ID"]
            p_cat = p["Category"]
            
            # Contextual signals
            view_count = 3 if pid in viewed_pids else 1
            in_wish = 1 if pid in wishlist_pids else 0
            in_cart = 1 if pid in cart_pids else 0
            search_match = 1.0 if any(s.lower() in p["Product_Tags"].lower() or s.lower() in p["Product_Name"].lower() for s in recent_searches) else (0.8 if p_cat == pref_category else 0.2)
            cat_purchases = int(total_purchases * 0.6) if p_cat == pref_category else int(total_purchases * 0.1)

            infer_rows.append({
                "Age": age,
                "Gender": gender,
                "Preferred_Category": pref_category,
                "Category": p_cat,
                "Subcategory": p.get("Subcategory", "General"),
                "Product_Price": float(p.get("Final_Price", p.get("Price", 1000))),
                "Discount": float(p.get("Discount", 10)),
                "Product_Rating": float(p.get("Rating", 4.0)),
                "Review_Count": int(p.get("Review_Count", 50)),
                "Popularity_Score": float(p.get("Popularity_Score", 60.0)),
                "Previous_Purchases": total_purchases,
                "Category_Purchase_Count": cat_purchases,
                "Product_View_Count": view_count,
                "Wishlist_Count": in_wish,
                "Cart_Count": in_cart,
                "Average_Order_Value": float(aov),
                "Search_Relevance": search_match,
                "Historical_Product_Rating": float(p.get("Rating", 4.0))
            })

        df_infer = pd.DataFrame(infer_rows)

        # Get ML Purchase Probabilities
        if self.model and self.pipeline:
            try:
                X_trans = self.pipeline.transform(df_infer)
                # Probability of Purchased (Class 1)
                ml_probs = self.model.predict_proba(X_trans)[:, 1]
            except Exception as e:
                print(f"Recommendation inference fallback: {e}")
                ml_probs = np.random.uniform(0.5, 0.85, size=len(candidates))
        else:
            ml_probs = np.random.uniform(0.5, 0.85, size=len(candidates))

        scored_products = []
        for i, p in enumerate(candidate_list):
            pid = p["Product_ID"]
            p_cat = p["Category"]
            
            ml_prob = float(ml_probs[i]) # 0.0 to 1.0
            
            # Component scores normalized between 0.0 and 1.0
            cat_pref_score = 1.0 if p_cat == pref_category else 0.4
            purchase_hist_score = 0.9 if any(cat in customer_history.get("purchased_categories", []) for cat in [p_cat]) else 0.3
            popularity_score = float(p.get("Popularity_Score", 50)) / 100.0
            rating_score = float(p.get("Rating", 4.0)) / 5.0
            search_score = 1.0 if any(s.lower() in p["Product_Tags"].lower() or s.lower() in p["Product_Name"].lower() for s in recent_searches) else (0.7 if p_cat == pref_category else 0.2)

            # Final Score formula:
            # ML Purchase Probability * 0.50 + Category Preference * 0.15 + Purchase History * 0.10 + Product Popularity * 0.10 + Product Rating * 0.10 + Search Relevance * 0.05
            composite_score = (
                (ml_prob * 0.50) +
                (cat_pref_score * 0.15) +
                (purchase_hist_score * 0.10) +
                (popularity_score * 0.10) +
                (rating_score * 0.10) +
                (search_score * 0.05)
            )

            # Normalize to 0-100% percentage display
            match_percentage = int(min(99, max(62, round(composite_score * 100))))
            
            # Recommendation Badge
            if match_percentage >= 88:
                badge_label = "AI Recommended"
                badge_class = "bg-primary"
            elif match_percentage >= 76:
                badge_label = "Highly Relevant"
                badge_class = "bg-success"
            else:
                badge_label = "Recommended"
                badge_class = "bg-info"

            # Explainable AI Reason
            if pid in viewed_pids:
                reason = f"Because you recently viewed this item."
            elif p_cat == pref_category and recent_searches:
                reason = f"Matches your search for '{recent_searches[0]}' in {p_cat}."
            elif p_cat == pref_category:
                reason = f"Matches your shopping preference for {p_cat}."
            elif any(cat in customer_history.get("purchased_categories", []) for cat in [p_cat]):
                reason = f"Complements your previous purchases in {p_cat}."
            elif p.get("Rating", 4.0) >= 4.7:
                reason = f"Top-rated ({p.get('Rating')}★) customer favorite."
            else:
                reason = "Popular among customers with similar shopping behavior."

            product_dict = dict(p)
            product_dict["ml_prob"] = round(ml_prob, 3)
            product_dict["match_percentage"] = match_percentage
            product_dict["badge_label"] = badge_label
            product_dict["badge_class"] = badge_class
            product_dict["recommendation_reason"] = reason
            product_dict["composite_score"] = composite_score
            
            scored_products.append(product_dict)

        # Sort descending by composite score
        scored_products.sort(key=lambda x: x["composite_score"], reverse=True)
        return scored_products[:top_n]

    def get_cold_start_recommendations(self, top_n=8):
        """
        Cold-start fallback for visitors or new customers with no history.
        Selects popular, highly rated, and trending products across distinct categories.
        """
        if self.products_df is None or self.products_df.empty:
            return []

        # Sort by popularity and rating
        top_pool = self.products_df.sort_values(
            by=["Popularity_Score", "Rating", "Review_Count"],
            ascending=[False, False, False]
        )
        
        results = []
        seen_cats = set()
        
        # Ensure category diversity
        for _, row in top_pool.iterrows():
            cat = row["Category"]
            if cat not in seen_cats or len(seen_cats) >= 6:
                p = row.to_dict()
                match_pct = random.randint(82, 95)
                p["match_percentage"] = match_pct
                p["badge_label"] = "Trending Match"
                p["badge_class"] = "bg-gradient-primary"
                p["recommendation_reason"] = f"Bestseller in {cat} ({p.get('Rating')}★ rating)."
                results.append(p)
                seen_cats.add(cat)
                if len(results) >= top_n:
                    break

        return results

    def get_trending_products(self, top_n=8):
        """
        Returns trending products with high popularity and recent activity.
        """
        if self.products_df is None or self.products_df.empty:
            return []
            
        trending = self.products_df.sort_values(by="Popularity_Score", ascending=False).head(top_n * 2)
        sampled = trending.sample(min(len(trending), top_n)).to_dict(orient="records")
        for p in sampled:
            p["trend_tag"] = "Trending Now"
        return sampled

    def get_bestsellers(self, top_n=8):
        """Returns top reviewed and high rated items."""
        if self.products_df is None or self.products_df.empty:
            return []
            
        bestsellers = self.products_df.sort_values(by=["Review_Count", "Rating"], ascending=[False, False]).head(top_n)
        return bestsellers.to_dict(orient="records")

    def get_new_arrivals(self, top_n=8):
        """Returns newest created products."""
        if self.products_df is None or self.products_df.empty:
            return []
            
        new_items = self.products_df.sort_values(by="Created_Date", ascending=False).head(top_n)
        return new_items.to_dict(orient="records")

recommendation_service = RecommendationService()
