"""
SmartCart - Data Preprocessing & Feature Engineering Pipeline
Handles data cleaning, feature engineering, categorical encoding,
and numerical scaling using Scikit-Learn Pipeline and ColumnTransformer.
"""

import os
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline

NUMERICAL_FEATURES = [
    "Age",
    "Product_Price",
    "Discount",
    "Product_Rating",
    "Review_Count",
    "Popularity_Score",
    "Previous_Purchases",
    "Category_Purchase_Count",
    "Product_View_Count",
    "Wishlist_Count",
    "Cart_Count",
    "Average_Order_Value",
    "Search_Relevance",
    "Historical_Product_Rating"
]

CATEGORICAL_FEATURES = [
    "Gender",
    "Preferred_Category",
    "Category",
    "Subcategory"
]

def build_preprocessing_pipeline():
    """
    Creates and returns a ColumnTransformer for numerical and categorical features.
    """
    numeric_transformer = Pipeline(steps=[
        ("scaler", StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERICAL_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES)
        ]
    )
    return preprocessor

def load_and_merge_data(data_dir=None):
    """
    Loads raw CSV datasets and creates an enriched feature matrix for ML training.
    Prevents data leakage by computing behavioral aggregations without using
    the current record's target label or order IDs.
    """
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        
    cust_df = pd.read_csv(os.path.join(data_dir, "customers.csv"))
    prod_df = pd.read_csv(os.path.join(data_dir, "products.csv"))
    int_df = pd.read_csv(os.path.join(data_dir, "interactions.csv"))
    search_df = pd.read_csv(os.path.join(data_dir, "search_history.csv"))
    
    # Clean duplicates & validate
    cust_df = cust_df.drop_duplicates(subset=["Customer_ID"])
    prod_df = prod_df.drop_duplicates(subset=["Product_ID"])
    int_df = int_df.drop_duplicates(subset=["Interaction_ID"])
    
    # Calculate customer search interests (categories searched)
    cust_search_cats = search_df.groupby(["Customer_ID", "Search_Category"]).size().unstack(fill_value=0)
    
    # Calculate interaction summaries per customer-product pair
    pair_views = int_df.groupby(["Customer_ID", "Product_ID"])["Product_Viewed"].sum().rename("Product_View_Count")
    pair_wishlist = int_df.groupby(["Customer_ID", "Product_ID"])["Added_To_Wishlist"].max().rename("Wishlist_Count")
    pair_cart = int_df.groupby(["Customer_ID", "Product_ID"])["Added_To_Cart"].max().rename("Cart_Count")
    
    # Merge interaction records with product and customer data
    merged = int_df.merge(
        cust_df,
        on="Customer_ID",
        how="inner",
        suffixes=("", "_cust")
    )
    
    merged = merged.merge(
        prod_df,
        on="Product_ID",
        how="inner",
        suffixes=("", "_prod")
    )
    
    # Target variable: Purchased (1 if Purchased == 1, else 0)
    merged["Purchased"] = (merged["Purchased"] == 1).astype(int)
    
    # Feature engineering
    merged["Product_Price"] = merged["Final_Price"].fillna(merged["Price"]).fillna(500.0)
    merged["Product_Rating"] = merged["Rating"].fillna(4.0)
    merged["Historical_Product_Rating"] = merged["Rating"].fillna(4.0)
    merged["Review_Count"] = merged["Review_Count"].fillna(10)
    merged["Popularity_Score"] = merged["Popularity_Score"].fillna(50.0)
    merged["Previous_Purchases"] = merged["Total_Purchases"].fillna(0)
    merged["Average_Order_Value"] = merged["Average_Order_Value"].fillna(0.0)
    
    # Category purchase count estimation from total purchases & preferred category
    merged["Category_Purchase_Count"] = np.where(
        merged["Preferred_Category"] == merged["Category"],
        (merged["Total_Purchases"] * 0.6).astype(int),
        (merged["Total_Purchases"] * 0.1).astype(int)
    )
    
    # Map pair view/wishlist/cart counts
    merged = merged.join(pair_views, on=["Customer_ID", "Product_ID"])
    merged = merged.join(pair_wishlist, on=["Customer_ID", "Product_ID"])
    merged = merged.join(pair_cart, on=["Customer_ID", "Product_ID"])
    
    merged["Product_View_Count"] = merged["Product_View_Count"].fillna(1)
    merged["Wishlist_Count"] = merged["Wishlist_Count"].fillna(0)
    merged["Cart_Count"] = merged["Cart_Count"].fillna(0)
    
    # Search Relevance: 1 if customer searched for this category or matches keyword, else 0
    merged["Search_Relevance"] = np.where(
        (merged["Preferred_Category"] == merged["Category"]) | (merged["Search_Keyword"] != ""),
        1.0,
        0.2
    )
    
    # Fill any remaining NaNs in numerical features
    for col in NUMERICAL_FEATURES:
        if col in merged.columns:
            merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(0)
            
    for col in CATEGORICAL_FEATURES:
        if col in merged.columns:
            merged[col] = merged[col].fillna("Unknown").astype(str)
            
    feature_df = merged[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
    target_series = merged["Purchased"]
    
    return feature_df, target_series, merged

def build_single_inference_features(customer_dict, product_dict, context=None):
    """
    Constructs a 1-row DataFrame formatted for pipeline transformation during live recommendation scoring.
    """
    context = context or {}
    
    pref_cat = customer_dict.get("Preferred_Category", "Electronics")
    prod_cat = product_dict.get("Category", "Electronics")
    total_purchases = customer_dict.get("Total_Purchases", 0)
    
    cat_purchases = int(total_purchases * 0.6) if pref_cat == prod_cat else int(total_purchases * 0.1)
    search_relevance = 1.0 if (pref_cat == prod_cat or context.get("searched_category") == prod_cat) else 0.2
    
    row = {
        "Age": customer_dict.get("Age", 30),
        "Gender": customer_dict.get("Gender", "Male"),
        "Preferred_Category": pref_cat,
        "Category": prod_cat,
        "Subcategory": product_dict.get("Subcategory", "General"),
        "Product_Price": float(product_dict.get("Final_Price", product_dict.get("Price", 1000))),
        "Discount": float(product_dict.get("Discount", 10)),
        "Product_Rating": float(product_dict.get("Rating", 4.0)),
        "Review_Count": int(product_dict.get("Review_Count", 50)),
        "Popularity_Score": float(product_dict.get("Popularity_Score", 60.0)),
        "Previous_Purchases": total_purchases,
        "Category_Purchase_Count": cat_purchases,
        "Product_View_Count": context.get("view_count", 1),
        "Wishlist_Count": 1 if context.get("in_wishlist") else 0,
        "Cart_Count": 1 if context.get("in_cart") else 0,
        "Average_Order_Value": float(customer_dict.get("Average_Order_Value", 1500.0)),
        "Search_Relevance": search_relevance,
        "Historical_Product_Rating": float(product_dict.get("Rating", 4.0))
    }
    
    return pd.DataFrame([row])
