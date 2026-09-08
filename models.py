"""
SmartCart - Database Models
Defines SQLAlchemy schemas matching the system requirements.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer") # 'customer' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to customer profile
    customer = db.relationship("Customer", backref="user", uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }

class Customer(db.Model):
    __tablename__ = "customers"
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    age = db.Column(db.Integer, default=30)
    gender = db.Column(db.String(20), default="Other")
    city = db.Column(db.String(100), default="Mumbai")
    state = db.Column(db.String(100), default="Maharashtra")
    preferred_category = db.Column(db.String(100), default="Electronics")
    average_order_value = db.Column(db.Float, default=0.0)
    total_purchases = db.Column(db.Integer, default=0)
    purchase_frequency = db.Column(db.Float, default=0.0)
    average_rating_given = db.Column(db.Float, default=0.0)
    last_purchase_date = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
            "age": self.age,
            "gender": self.gender,
            "city": self.city,
            "state": self.state,
            "preferred_category": self.preferred_category,
            "average_order_value": self.average_order_value,
            "total_purchases": self.total_purchases,
            "purchase_frequency": self.purchase_frequency,
            "average_rating_given": self.average_rating_given,
            "last_purchase_date": self.last_purchase_date
        }

class Category(db.Model):
    __tablename__ = "categories"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

class Product(db.Model):
    __tablename__ = "products"
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False, index=True)
    subcategory = db.Column(db.String(100), nullable=True)
    brand = db.Column(db.String(100), nullable=True, index=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    final_price = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, default=4.0)
    review_count = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, default=50)
    popularity_score = db.Column(db.Float, default=50.0)
    tags = db.Column(db.Text, nullable=True)
    age_group = db.Column(db.String(50), default="All Ages")
    gender_target = db.Column(db.String(50), default="All")
    color = db.Column(db.String(50), default="Standard")
    size = db.Column(db.String(50), default="Standard")
    image_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default="Active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "subcategory": self.subcategory,
            "brand": self.brand,
            "description": self.description,
            "price": self.price,
            "discount": self.discount,
            "final_price": self.final_price,
            "rating": self.rating,
            "review_count": self.review_count,
            "stock": self.stock,
            "popularity_score": self.popularity_score,
            "tags": self.tags,
            "color": self.color,
            "size": self.size,
            "image_url": self.image_url,
            "status": self.status
        }

class Interaction(db.Model):
    __tablename__ = "interactions"
    
    id = db.Column(db.Integer, primary_key=True)
    interaction_id = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.String(50), nullable=False, index=True)
    product_id = db.Column(db.String(50), nullable=False, index=True)
    interaction_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(100), nullable=True)
    search_keyword = db.Column(db.String(150), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    device = db.Column(db.String(50), nullable=True)
    time_spent = db.Column(db.Integer, default=30)
    product_viewed = db.Column(db.Integer, default=0)
    added_to_wishlist = db.Column(db.Integer, default=0)
    added_to_cart = db.Column(db.Integer, default=0)
    purchased = db.Column(db.Integer, default=0)
    rating_given = db.Column(db.Integer, default=0)

class SearchHistory(db.Model):
    __tablename__ = "search_history"
    
    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.String(50), nullable=True)
    customer_id = db.Column(db.String(50), nullable=False, index=True)
    search_keyword = db.Column(db.String(200), nullable=False)
    search_category = db.Column(db.String(100), nullable=True)
    search_date = db.Column(db.DateTime, default=datetime.utcnow)
    result_clicked = db.Column(db.Integer, default=0)
    product_clicked = db.Column(db.String(200), nullable=True)

class Rating(db.Model):
    __tablename__ = "ratings"
    
    id = db.Column(db.Integer, primary_key=True)
    rating_id = db.Column(db.String(50), nullable=True)
    customer_id = db.Column(db.String(50), nullable=False, index=True)
    product_id = db.Column(db.String(50), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=True)
    rating_date = db.Column(db.DateTime, default=datetime.utcnow)

class Wishlist(db.Model):
    __tablename__ = "wishlists"
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), nullable=False, index=True)
    product_id = db.Column(db.String(50), nullable=False, index=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

class Cart(db.Model):
    __tablename__ = "cart"
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), nullable=True, index=True)
    session_id = db.Column(db.String(100), nullable=True, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = db.relationship("CartItem", backref="cart", lazy=True, cascade="all, delete-orphan")

class CartItem(db.Model):
    __tablename__ = "cart_items"
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("cart.id"), nullable=False)
    product_id = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    __tablename__ = "orders"
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.String(50), nullable=False, index=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default="UPI")
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(50), default="Placed") # Placed, Confirmed, Packed, Shipped, Delivered, Cancelled
    
    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "order_date": self.order_date.strftime("%Y-%m-%d %H:%M:%S") if self.order_date else "",
            "total_amount": self.total_amount,
            "payment_method": self.payment_method,
            "full_name": self.full_name,
            "address": f"{self.address}, {self.city}, {self.state} - {self.pincode}",
            "status": self.status,
            "items_count": len(self.items)
        }

class OrderItem(db.Model):
    __tablename__ = "order_items"
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), db.ForeignKey("orders.order_id"), nullable=False)
    product_id = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    total_price = db.Column(db.Float, nullable=False)

class RecommendationLog(db.Model):
    __tablename__ = "recommendations"
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), nullable=True, index=True)
    product_id = db.Column(db.String(50), nullable=False, index=True)
    recommendation_type = db.Column(db.String(50), default="Personalized") # Personalized, Similar, Frequently Bought Together, Trending
    score = db.Column(db.Float, default=0.0)
    shown_at = db.Column(db.DateTime, default=datetime.utcnow)
    clicked = db.Column(db.Integer, default=0) # 0 or 1
    purchased = db.Column(db.Integer, default=0) # 0 or 1

class Notification(db.Model):
    __tablename__ = "notifications"
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
