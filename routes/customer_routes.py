"""
SmartCart - Customer Facing Routes
Handles Homepage, Dashboard, Profile, Wishlist, and Shopping Insights.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from database import db
from models import Customer, Product, Order, OrderItem, Wishlist, Interaction, RecommendationLog
from services.recommendation_service import recommendation_service
from services.association_service import association_engine
from routes.auth_routes import login_required

customer_bp = Blueprint("customer", __name__)

@customer_bp.route("/")
def home():
    customer_id = session.get("customer_id")
    customer_data = None
    customer_history = {}
    
    if customer_id:
        cust = Customer.query.filter_by(customer_id=customer_id).first()
        if cust:
            customer_data = cust.to_dict()
            
            # Fetch customer behavioral history for high-fidelity ML recommendation
            orders = Order.query.filter_by(customer_id=customer_id).all()
            purchased_pids = []
            purchased_cats = []
            for o in orders:
                for item in o.items:
                    purchased_pids.append(item.product_id)
                    p = Product.query.filter_by(product_id=item.product_id).first()
                    if p:
                        purchased_cats.append(p.category)
                        
            # Viewed items from session
            recent_views = session.get("recently_viewed", [])
            wishlist_items = [w.product_id for w in Wishlist.query.filter_by(customer_id=customer_id).all()]
            
            customer_history = {
                "viewed_product_ids": recent_views,
                "purchased_product_ids": purchased_pids,
                "purchased_categories": list(set(purchased_cats)),
                "wishlist_product_ids": wishlist_items,
                "recent_searches": session.get("recent_searches", [])
            }
            
    # Get Personalized AI Recommendations
    recommended_products = recommendation_service.get_personalized_recommendations(
        customer_data=customer_data,
        customer_history=customer_history,
        top_n=8
    )
    
    # Log recommendation impressions for analytics
    for rec in recommended_products[:6]:
        log_entry = RecommendationLog(
            customer_id=customer_id or "ANONYMOUS",
            product_id=rec["Product_ID"],
            recommendation_type="Personalized",
            score=float(rec.get("match_percentage", 80))
        )
        db.session.add(log_entry)
    db.session.commit()
    
    trending = recommendation_service.get_trending_products(top_n=8)
    bestsellers = recommendation_service.get_bestsellers(top_n=8)
    new_arrivals = recommendation_service.get_new_arrivals(top_n=8)
    
    # Recently Viewed products
    recent_view_pids = session.get("recently_viewed", [])
    recently_viewed = []
    if recent_view_pids:
        recently_viewed = Product.query.filter(Product.product_id.isin(recent_view_pids[:6])).all()
        
    return render_template(
        "home.html",
        recommended_products=recommended_products,
        trending_products=trending,
        bestsellers=bestsellers,
        new_arrivals=new_arrivals,
        recently_viewed=recently_viewed
    )

@customer_bp.route("/dashboard")
@login_required
def dashboard():
    customer_id = session.get("customer_id")
    cust = Customer.query.filter_by(customer_id=customer_id).first()
    if not cust:
        flash("Customer profile not found.", "warning")
        return redirect(url_for("customer.home"))
        
    orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.order_date.desc()).all()
    wishlist_records = Wishlist.query.filter_by(customer_id=customer_id).all()
    wishlist_pids = [w.product_id for w in wishlist_records]
    wishlist_prods = Product.query.filter(Product.product_id.isin(wishlist_pids)).all() if wishlist_pids else []
    
    # Analytics & Shopping Insights
    total_spent = sum(o.total_amount for o in orders)
    aov = round(total_spent / len(orders), 2) if orders else 0.0
    
    # Shopping Insights statements
    insights = [
        f"You shop mostly in {cust.preferred_category}.",
        f"Your average order value is ₹{aov:,.2f}.",
        f"You have placed {len(orders)} successful orders with SmartCart.",
        "Based on your profile, you receive optimized discounts and early access deals."
    ]
    
    # Get Personalized Recommendations
    customer_history = {
        "viewed_product_ids": session.get("recently_viewed", []),
        "purchased_product_ids": [item.product_id for o in orders for item in o.items],
        "purchased_categories": [cust.preferred_category],
        "wishlist_product_ids": wishlist_pids,
        "recent_searches": session.get("recent_searches", [])
    }
    
    recommendations = recommendation_service.get_personalized_recommendations(
        customer_data=cust.to_dict(),
        customer_history=customer_history,
        top_n=6
    )
    
    return render_template(
        "profile.html",
        customer=cust,
        orders=orders,
        wishlist_products=wishlist_prods,
        total_spent=round(total_spent, 2),
        aov=aov,
        insights=insights,
        recommendations=recommendations,
        is_dashboard=True
    )

@customer_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    customer_id = session.get("customer_id")
    cust = Customer.query.filter_by(customer_id=customer_id).first()
    
    if request.method == "POST":
        cust.name = request.form.get("name", cust.name)
        cust.age = int(request.form.get("age", cust.age or 30))
        cust.gender = request.form.get("gender", cust.gender)
        cust.city = request.form.get("city", cust.city)
        cust.state = request.form.get("state", cust.state)
        cust.preferred_category = request.form.get("preferred_category", cust.preferred_category)
        db.session.commit()
        session["customer_name"] = cust.name
        flash("Profile updated successfully!", "success")
        return redirect(url_for("customer.profile"))
        
    orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.order_date.desc()).all()
    total_spent = sum(o.total_amount for o in orders)
    aov = round(total_spent / len(orders), 2) if orders else 0.0
    
    return render_template(
        "profile.html",
        customer=cust,
        orders=orders,
        total_spent=round(total_spent, 2),
        aov=aov,
        is_dashboard=False
    )

@customer_bp.route("/wishlist")
def wishlist():
    customer_id = session.get("customer_id")
    if not customer_id:
        flash("Please log in to view your wishlist.", "info")
        return redirect(url_for("auth.login"))
        
    wishlist_records = Wishlist.query.filter_by(customer_id=customer_id).all()
    product_ids = [w.product_id for w in wishlist_records]
    products = Product.query.filter(Product.product_id.isin(product_ids)).all() if product_ids else []
    
    return render_template("wishlist.html", products=products)

@customer_bp.route("/api/wishlist/toggle", methods=["POST"])
def api_toggle_wishlist():
    customer_id = session.get("customer_id")
    if not customer_id:
        return jsonify({"success": False, "message": "Login required"}), 401
        
    data = request.get_json() or {}
    product_id = data.get("product_id")
    if not product_id:
        return jsonify({"success": False, "message": "Product ID required"}), 400
        
    existing = Wishlist.query.filter_by(customer_id=customer_id, product_id=product_id).first()
    if existing:
        db.session.delete(existing)
        in_wishlist = False
        message = "Removed from Wishlist"
    else:
        item = Wishlist(customer_id=customer_id, product_id=product_id)
        db.session.add(item)
        in_wishlist = True
        message = "Added to Wishlist"
        
    db.session.commit()
    count = Wishlist.query.filter_by(customer_id=customer_id).count()
    return jsonify({"success": True, "in_wishlist": in_wishlist, "message": message, "count": count})
