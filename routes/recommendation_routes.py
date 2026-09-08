"""
SmartCart - AI Recommendation API Routes
Provides endpoints for personalized recommendations, product similarity,
frequently bought together bundles, and recommendation telemetry tracking.
"""

from flask import Blueprint, jsonify, request, session
from database import db
from models import Product, Customer, RecommendationLog
from services.recommendation_service import recommendation_service
from services.similarity_service import similarity_engine
from services.association_service import association_engine

recommendation_bp = Blueprint("recommendation", __name__)

@recommendation_bp.route("/api/recommendations")
def get_personalized_recommendations():
    customer_id = session.get("customer_id")
    customer_data = None
    customer_history = {}
    
    if customer_id:
        cust = Customer.query.filter_by(customer_id=customer_id).first()
        if cust:
            customer_data = cust.to_dict()
            customer_history = {
                "viewed_product_ids": session.get("recently_viewed", []),
                "recent_searches": session.get("recent_searches", [])
            }
            
    limit = request.args.get("limit", 8, type=int)
    recs = recommendation_service.get_personalized_recommendations(
        customer_data=customer_data,
        customer_history=customer_history,
        top_n=limit
    )
    return jsonify({"success": True, "count": len(recs), "recommendations": recs})

@recommendation_bp.route("/api/recommendations/similar/<product_id>")
def get_similar_products(product_id):
    limit = request.args.get("limit", 6, type=int)
    similar = similarity_engine.get_similar_products(product_id, top_n=limit)
    return jsonify({"success": True, "product_id": product_id, "similar_products": similar})

@recommendation_bp.route("/api/recommendations/frequently-bought/<product_id>")
def get_frequently_bought_together(product_id):
    bundle = association_engine.get_frequently_bought_together(product_id, top_n=3)
    if not bundle:
        return jsonify({"success": False, "message": "Product not found"}), 404
    return jsonify({"success": True, "bundle": bundle})

@recommendation_bp.route("/api/recommendations/track", methods=["POST"])
def track_recommendation():
    """
    Logs user interactions with recommendations (click or purchase) to feed Recommendation CTR & CVR.
    """
    data = request.get_json() or {}
    product_id = data.get("product_id")
    event_type = data.get("event_type", "click") # 'click' or 'purchase'
    rec_type = data.get("recommendation_type", "Personalized")
    customer_id = session.get("customer_id", "ANONYMOUS")
    
    if not product_id:
        return jsonify({"success": False, "message": "product_id required"}), 400
        
    rec_entry = RecommendationLog.query.filter_by(
        customer_id=customer_id,
        product_id=product_id
    ).order_by(RecommendationLog.shown_at.desc()).first()
    
    if rec_entry:
        if event_type == "click":
            rec_entry.clicked = 1
        elif event_type == "purchase":
            rec_entry.purchased = 1
    else:
        rec_entry = RecommendationLog(
            customer_id=customer_id,
            product_id=product_id,
            recommendation_type=rec_type,
            clicked=1 if event_type == "click" else 0,
            purchased=1 if event_type == "purchase" else 0
        )
        db.session.add(rec_entry)
        
    db.session.commit()
    return jsonify({"success": True, "message": f"Tracked {event_type}"})
