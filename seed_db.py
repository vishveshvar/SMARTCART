"""
SmartCart - Database Seeder
Imports generated datasets into SQLite/MySQL database and sets up
the demo admin and demo customer credentials.
"""

import os
import random
import datetime
import pandas as pd
from flask import Flask
from werkzeug.security import generate_password_hash

from config import Config
from database import db, init_db
from models import (
    User, Customer, Product, Category,
    Interaction, SearchHistory, Rating,
    Order, OrderItem, RecommendationLog, Notification
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_db(app)
    return app

def seed_database():
    app = create_app()
    with app.app_context():
        print("=== Seeding SmartCart Database ===")
        db.create_all()
        
        # 1. Create Demo Admin if not exists
        admin_user = User.query.filter_by(email="admin@smartcart.com").first()
        if not admin_user:
            admin_user = User(
                email="admin@smartcart.com",
                role="admin"
            )
            admin_user.set_password("Admin@123")
            db.session.add(admin_user)
            print("Demo Admin created: admin@smartcart.com / Admin@123")
            
        # 2. Create Demo Customer if not exists
        cust_user = User.query.filter_by(email="customer@smartcart.com").first()
        if not cust_user:
            cust_user = User(
                email="customer@smartcart.com",
                role="customer"
            )
            cust_user.set_password("Customer@123")
            db.session.add(cust_user)
            db.session.flush()
            
            # Link demo customer profile
            demo_profile = Customer(
                customer_id="CUST_00001",
                user_id=cust_user.id,
                name="Aarav Sharma",
                email="customer@smartcart.com",
                age=28,
                gender="Male",
                city="Bengaluru",
                state="Karnataka",
                preferred_category="Electronics",
                average_order_value=4500.0,
                total_purchases=8,
                purchase_frequency=1.2,
                average_rating_given=4.8,
                last_purchase_date="2026-08-25"
            )
            db.session.add(demo_profile)
            print("Demo Customer created: customer@smartcart.com / Customer@123")
            
        db.session.commit()
        
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        
        # 3. Import Categories & Products
        prod_csv = os.path.join(data_dir, "products.csv")
        if os.path.exists(prod_csv) and Product.query.count() == 0:
            print("Importing products...")
            df_prod = pd.read_csv(prod_csv)
            
            # Categories
            unique_cats = df_prod["Category"].unique()
            for c_name in unique_cats:
                cat_obj = Category(name=c_name, description=f"Premium collection of {c_name} products.")
                db.session.add(cat_obj)
            db.session.flush()
            
            # Products
            prod_objects = []
            for _, r in df_prod.iterrows():
                p = Product(
                    product_id=str(r["Product_ID"]),
                    name=str(r["Product_Name"]),
                    category=str(r["Category"]),
                    subcategory=str(r["Subcategory"]) if pd.notna(r["Subcategory"]) else "",
                    brand=str(r["Brand"]) if pd.notna(r["Brand"]) else "",
                    description=str(r["Product_Description"]) if pd.notna(r["Product_Description"]) else "",
                    price=float(r["Price"]),
                    discount=float(r["Discount"]) if pd.notna(r["Discount"]) else 0.0,
                    final_price=float(r["Final_Price"]),
                    rating=float(r["Rating"]) if pd.notna(r["Rating"]) else 4.0,
                    review_count=int(r["Review_Count"]) if pd.notna(r["Review_Count"]) else 0,
                    stock=int(r["Stock"]) if pd.notna(r["Stock"]) else 50,
                    popularity_score=float(r["Popularity_Score"]) if pd.notna(r["Popularity_Score"]) else 50.0,
                    tags=str(r["Product_Tags"]) if pd.notna(r["Product_Tags"]) else "",
                    age_group=str(r["Age_Group"]) if pd.notna(r["Age_Group"]) else "All Ages",
                    gender_target=str(r["Gender_Target"]) if pd.notna(r["Gender_Target"]) else "All",
                    color=str(r["Color"]) if pd.notna(r["Color"]) else "Standard",
                    size=str(r["Size"]) if pd.notna(r["Size"]) else "Standard",
                    image_url=str(r["Image_URL"]) if pd.notna(r["Image_URL"]) else "",
                    status=str(r["Status"]) if pd.notna(r["Status"]) else "Active"
                )
                prod_objects.append(p)
            db.session.bulk_save_objects(prod_objects)
            db.session.commit()
            print(f"Imported {len(prod_objects)} products.")
            
        # 4. Import Customers
        cust_csv = os.path.join(data_dir, "customers.csv")
        if os.path.exists(cust_csv) and Customer.query.count() <= 1:
            print("Importing customers...")
            df_cust = pd.read_csv(cust_csv)
            cust_objects = []
            for _, r in df_cust.iterrows():
                cid = str(r["Customer_ID"])
                if cid == "CUST_00001":
                    continue
                c = Customer(
                    customer_id=cid,
                    name=str(r["Customer_Name"]),
                    email=f"{cid.lower()}@example.com",
                    age=int(r["Age"]),
                    gender=str(r["Gender"]),
                    city=str(r["City"]),
                    state=str(r["State"]),
                    preferred_category=str(r["Preferred_Category"]),
                    average_order_value=float(r["Average_Order_Value"]) if pd.notna(r["Average_Order_Value"]) else 0.0,
                    total_purchases=int(r["Total_Purchases"]) if pd.notna(r["Total_Purchases"]) else 0,
                    purchase_frequency=float(r["Purchase_Frequency"]) if pd.notna(r["Purchase_Frequency"]) else 0.0,
                    average_rating_given=float(r["Average_Rating_Given"]) if pd.notna(r["Average_Rating_Given"]) else 0.0,
                    last_purchase_date=str(r["Last_Purchase_Date"]) if pd.notna(r["Last_Purchase_Date"]) else None
                )
                cust_objects.append(c)
                if len(cust_objects) >= 1000:
                    db.session.bulk_save_objects(cust_objects)
                    cust_objects = []
            if cust_objects:
                db.session.bulk_save_objects(cust_objects)
            db.session.commit()
            print(f"Imported customer records.")

        # 5. Import Orders & Order Items from purchases.csv
        pur_csv = os.path.join(data_dir, "purchases.csv")
        if os.path.exists(pur_csv) and Order.query.count() == 0:
            print("Importing historical orders and items...")
            df_pur = pd.read_csv(pur_csv)
            
            # Group by Order_ID
            grouped = df_pur.groupby("Order_ID")
            order_objects = []
            item_objects = []
            
            for oid, group in list(grouped)[:600]: # Seed 600 orders with full items
                first_row = group.iloc[0]
                total = float(group["Total_Amount"].sum())
                order_date = datetime.datetime.strptime(first_row["Purchase_Date"], "%Y-%m-%d %H:%M:%S") if " " in str(first_row["Purchase_Date"]) else datetime.datetime.utcnow()
                
                status_choices = ["Delivered", "Delivered", "Delivered", "Shipped", "Confirmed", "Packed"]
                order_status = status_choices[hash(oid) % len(status_choices)]
                
                order_obj = Order(
                    order_id=oid,
                    customer_id=str(first_row["Customer_ID"]),
                    order_date=order_date,
                    total_amount=round(total, 2),
                    payment_method=str(first_row["Payment_Method"]),
                    full_name="Verified Customer",
                    email=f"{str(first_row['Customer_ID']).lower()}@example.com",
                    phone="+91 9876543210",
                    address="123 Tech Park Residency",
                    city="Bengaluru",
                    state="Karnataka",
                    pincode="560001",
                    status=order_status
                )
                order_objects.append(order_obj)
                
                for _, item_row in group.iterrows():
                    item_obj = OrderItem(
                        order_id=oid,
                        product_id=str(item_row["Product_ID"]),
                        quantity=int(item_row["Quantity"]),
                        unit_price=float(item_row["Unit_Price"]),
                        discount=float(item_row["Discount"]),
                        total_price=float(item_row["Total_Amount"])
                    )
                    item_objects.append(item_obj)
                    
            db.session.bulk_save_objects(order_objects)
            db.session.commit()
            db.session.bulk_save_objects(item_objects)
            db.session.commit()
            print(f"Imported {len(order_objects)} orders and {len(item_objects)} order items.")

        # 6. Seed Recommendation Logs for Analytics
        if RecommendationLog.query.count() == 0:
            print("Seeding recommendation feedback logs...")
            rec_logs = []
            rec_types = ["Personalized", "Similar", "Frequently Bought Together", "Trending"]
            prod_ids = [p.product_id for p in Product.query.limit(40).all()]
            
            for i in range(1500):
                pid = prod_ids[i % len(prod_ids)]
                rtype = rec_types[i % len(rec_types)]
                clicked = 1 if (i % 3 == 0) else 0
                purchased = 1 if (clicked and i % 6 == 0) else 0
                score = round(random.uniform(70.0, 98.0), 1)
                
                rec = RecommendationLog(
                    customer_id=f"CUST_{(i % 100) + 1:05d}",
                    product_id=pid,
                    recommendation_type=rtype,
                    score=score,
                    shown_at=datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(0, 30)),
                    clicked=clicked,
                    purchased=purchased
                )
                rec_logs.append(rec)
            db.session.bulk_save_objects(rec_logs)
            db.session.commit()
            print(f"Imported {len(rec_logs)} recommendation analytics logs.")

        print("=== SmartCart Database Seeding Complete! ===")

if __name__ == "__main__":
    seed_database()
