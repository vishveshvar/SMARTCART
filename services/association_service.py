"""
SmartCart - Purchase Association & Frequently Bought Together Service
Calculates product co-occurrence patterns from historical orders to suggest
complimentary product bundles with 1-click bundle checkout.
"""

import os
from collections import defaultdict
import pandas as pd

class AssociationEngine:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AssociationEngine, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, data_dir=None):
        if self.initialized:
            return
            
        self.data_dir = data_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        self.products_df = None
        self.co_occurrences = defaultdict(lambda: defaultdict(int))
        self.load_data()
        self.initialized = True

    def load_data(self):
        prod_path = os.path.join(self.data_dir, "products.csv")
        pur_path = os.path.join(self.data_dir, "purchases.csv")
        
        if not os.path.exists(prod_path) or not os.path.exists(pur_path):
            return
            
        self.products_df = pd.read_csv(prod_path)
        pur_df = pd.read_csv(pur_path)
        
        # Group products by Order_ID
        orders = pur_df.groupby("Order_ID")["Product_ID"].unique()
        for p_list in orders:
            if len(p_list) > 1:
                for p1 in p_list:
                    for p2 in p_list:
                        if p1 != p2:
                            self.co_occurrences[p1][p2] += 1
                            
        print(f"AssociationEngine: Analyzed {len(orders)} orders for co-occurrence associations.")

    def get_frequently_bought_together(self, product_id, top_n=3):
        """
        Returns top_n frequently co-purchased products along with the primary product,
        calculating bundle total price and savings.
        """
        if self.products_df is None:
            return None
            
        base_match = self.products_df[self.products_df["Product_ID"] == product_id]
        if base_match.empty:
            return None
            
        primary_product = base_match.iloc[0].to_dict()
        
        # Check co-occurrences
        co_counts = self.co_occurrences.get(product_id, {})
        sorted_pairs = sorted(co_counts.items(), key=lambda x: x[1], reverse=True)
        top_product_ids = [pid for pid, count in sorted_pairs[:top_n]]
        
        # Fallback if insufficient co-occurrences
        if len(top_product_ids) < top_n:
            cat = primary_product.get("Category")
            # Complementary category mappings
            comp_map = {
                "Laptops": ["Accessories", "Gaming"],
                "Mobiles": ["Accessories", "Electronics"],
                "Electronics": ["Accessories", "Home"],
                "Fashion": ["Footwear", "Accessories"],
                "Footwear": ["Fashion", "Sports"],
                "Kitchen": ["Home", "Grocery"],
                "Gaming": ["Accessories", "Electronics"]
            }
            target_cats = comp_map.get(cat, ["Accessories", "Electronics"])
            candidates = self.products_df[
                (self.products_df["Category"].isin(target_cats)) &
                (self.products_df["Product_ID"] != product_id) &
                (~self.products_df["Product_ID"].isin(top_product_ids))
            ]
            needed = top_n - len(top_product_ids)
            if not candidates.empty:
                extra_pids = candidates.head(needed)["Product_ID"].tolist()
                top_product_ids.extend(extra_pids)
                
        bundle_items = []
        for pid in top_product_ids:
            item_row = self.products_df[self.products_df["Product_ID"] == pid]
            if not item_row.empty:
                bundle_items.append(item_row.iloc[0].to_dict())
                
        # Calculate bundle economics
        all_items = [primary_product] + bundle_items
        original_bundle_price = sum(item["Price"] for item in all_items)
        bundle_final_price = sum(item["Final_Price"] for item in all_items)
        
        # Extra 10% bundle discount for buying the complete bundle
        extra_bundle_discount = round(bundle_final_price * 0.10, 2)
        total_bundle_price = round(bundle_final_price - extra_bundle_discount, 2)
        total_savings = round(original_bundle_price - total_bundle_price, 2)
        
        return {
            "primary_product": primary_product,
            "bundle_items": bundle_items,
            "all_items": all_items,
            "original_bundle_price": round(original_bundle_price, 2),
            "bundle_final_price": round(bundle_final_price, 2),
            "extra_bundle_discount": extra_bundle_discount,
            "total_bundle_price": total_bundle_price,
            "total_savings": total_savings
        }

association_engine = AssociationEngine()
