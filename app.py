"""
SmartCart - AI-Based Product Recommendation System
Main Flask Application Entry Point
"""

import os
from flask import Flask, render_template, session
from config import Config
from database import db, init_db
from models import Product, Wishlist, Cart, CartItem
from services.recommendation_service import recommendation_service
from services.similarity_service import similarity_engine
from services.association_service import association_engine

# Import blueprints
from routes.auth_routes import auth_bp
from routes.customer_routes import customer_bp
from routes.product_routes import product_bp
from routes.cart_routes import cart_bp
from routes.order_routes import order_bp
from routes.recommendation_routes import recommendation_bp
from routes.admin_routes import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(admin_bp)
    
    # Context Processor for Navbar badges and global data
    @app.context_processor
    def inject_global_data():
        cart_count = 0
        wishlist_count = 0
        
        customer_id = session.get("customer_id")
        cart_session_id = session.get("cart_session_id")
        
        # Calculate cart items
        cart = None
        if customer_id:
            cart = Cart.query.filter_by(customer_id=customer_id).first()
        elif cart_session_id:
            cart = Cart.query.filter_by(session_id=cart_session_id).first()
            
        if cart:
            cart_count = sum(item.quantity for item in cart.items)
            
        # Wishlist count
        if customer_id:
            wishlist_count = Wishlist.query.filter_by(customer_id=customer_id).count()
            
        # Top categories for navbar
        nav_categories = [
            "Electronics", "Mobiles", "Laptops", "Fashion",
            "Footwear", "Beauty", "Home", "Kitchen", "Gaming"
        ]
        
        return {
            "nav_cart_count": cart_count,
            "nav_wishlist_count": wishlist_count,
            "nav_categories": nav_categories
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("base.html", error_title="404 - Page Not Found", error_message="The product or page you are looking for does not exist or has been moved."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("base.html", error_title="500 - Internal Server Error", error_message="An unexpected error occurred. Our engineering team has been notified."), 500

    return app

app = create_app()

if __name__ == "__main__":
    # Preload services
    with app.app_context():
        recommendation_service.load_models()
        recommendation_service.load_products()
        similarity_engine.load_and_compute()
        association_engine.load_data()
        
    print("=== SmartCart Server Starting on http://127.0.0.1:5000 ===")
    app.run(host="0.0.0.0", port=5000, debug=True)
