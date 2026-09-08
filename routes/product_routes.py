"""
SmartCart - Product Browsing, Search, Filtering & Product Details
"""

import datetime
from flask import Blueprint, render_template, request, session, jsonify
from sqlalchemy import or_, desc, asc
from database import db
from models import Product, Category, Rating, Interaction, SearchHistory, Wishlist
from services.similarity_service import similarity_engine
from services.association_service import association_engine
from services.recommendation_service import recommendation_service

product_bp = Blueprint("product", __name__)

@product_bp.route("/products")
@product_bp.route("/search")
def search():
    query_str = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    subcategory = request.args.get("subcategory", "").strip()
    brand = request.args.get("brand", "").strip()
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    min_rating = request.args.get("rating", type=float)
    in_stock_only = request.args.get("in_stock") == "1"
    sort_by = request.args.get("sort", "relevance")
    page = request.args.get("page", 1, type=int)
    per_page = 16

    # Track search query in session and SearchHistory table
    customer_id = session.get("customer_id")
    if query_str:
        recent_searches = session.get("recent_searches", [])
        if query_str not in recent_searches:
            recent_searches.insert(0, query_str)
            session["recent_searches"] = recent_searches[:5]
            
        if customer_id:
            sh = SearchHistory(
                customer_id=customer_id,
                search_keyword=query_str,
                search_category=category or "General",
                result_clicked=0
            )
            db.session.add(sh)
            db.session.commit()

    # Query builder
    query = Product.query.filter(Product.status == "Active")

    # Text Search across name, brand, category, tags, description
    if query_str:
        search_pattern = f"%{query_str}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_pattern),
                Product.brand.ilike(search_pattern),
                Product.category.ilike(search_pattern),
                Product.subcategory.ilike(search_pattern),
                Product.tags.ilike(search_pattern),
                Product.description.ilike(search_pattern)
            )
        )

    # Facet Filters
    if category and category != "All":
        query = query.filter(Product.category == category)
    if subcategory:
        query = query.filter(Product.subcategory == subcategory)
    if brand:
        query = query.filter(Product.brand == brand)
    if min_price is not None:
        query = query.filter(Product.final_price >= min_price)
    if max_price is not None:
        query = query.filter(Product.final_price <= max_price)
    if min_rating is not None:
        query = query.filter(Product.rating >= min_rating)
    if in_stock_only:
        query = query.filter(Product.stock > 0)

    # Sorting
    if sort_by == "price_asc":
        query = query.order_by(asc(Product.final_price))
    elif sort_by == "price_desc":
        query = query.order_by(desc(Product.final_price))
    elif sort_by == "rating":
        query = query.order_by(desc(Product.rating))
    elif sort_by == "popularity":
        query = query.order_by(desc(Product.popularity_score))
    elif sort_by == "newest":
        query = query.order_by(desc(Product.created_at))
    else: # relevance
        if query_str:
            query = query.order_by(desc(Product.popularity_score))
        else:
            query = query.order_by(desc(Product.popularity_score))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    # Available filter metadata for sidebar
    categories = [c[0] for c in db.session.query(Product.category).distinct().all()]
    brands = [b[0] for b in db.session.query(Product.brand).filter(Product.brand != "").distinct().limit(25).all()]

    return render_template(
        "search.html",
        products=products,
        pagination=pagination,
        categories=categories,
        brands=brands,
        selected_category=category,
        selected_subcategory=subcategory,
        selected_brand=brand,
        min_price=min_price,
        max_price=max_price,
        selected_rating=min_rating,
        in_stock_only=in_stock_only,
        sort_by=sort_by,
        query_str=query_str,
        total_results=pagination.total
    )

@product_bp.route("/product/<product_id>")
def product_details(product_id):
    product = Product.query.filter_by(product_id=product_id).first_or_404()
    
    # Track recent view in session
    recent_views = session.get("recently_viewed", [])
    if product_id in recent_views:
        recent_views.remove(product_id)
    recent_views.insert(0, product_id)
    session["recently_viewed"] = recent_views[:10]

    # Log interaction to database
    customer_id = session.get("customer_id")
    if customer_id:
        interaction = Interaction(
            interaction_id=f"INT_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:18]}",
            customer_id=customer_id,
            product_id=product_id,
            interaction_type="View",
            category=product.category,
            time_spent=45,
            product_viewed=1
        )
        db.session.add(interaction)
        db.session.commit()

    # 1. Similar Products (TF-IDF & Cosine Similarity)
    similar_products = similarity_engine.get_similar_products(product_id, top_n=6)

    # 2. Frequently Bought Together (Purchase Co-occurrence bundle)
    fbt_bundle = association_engine.get_frequently_bought_together(product_id, top_n=3)

    # 3. AI Recommendations for customer context
    customer_data = None
    if customer_id:
        from models import Customer
        cust = Customer.query.filter_by(customer_id=customer_id).first()
        if cust:
            customer_data = cust.to_dict()
            
    recommended_items = recommendation_service.get_personalized_recommendations(
        customer_data=customer_data,
        customer_history={"viewed_product_ids": session.get("recently_viewed", [])},
        top_n=6
    )

    # Check if wishlisted
    is_wishlisted = False
    if customer_id:
        is_wishlisted = Wishlist.query.filter_by(customer_id=customer_id, product_id=product_id).first() is not None

    # Reviews
    reviews = Rating.query.filter_by(product_id=product_id).order_by(Rating.rating_date.desc()).limit(6).all()

    return render_template(
        "product.html",
        product=product,
        similar_products=similar_products,
        fbt_bundle=fbt_bundle,
        recommended_items=recommended_items,
        is_wishlisted=is_wishlisted,
        reviews=reviews
    )

@product_bp.route("/api/search/suggestions")
def api_search_suggestions():
    q = request.args.get("q", "").strip()
    if not q or len(q) < 2:
        return jsonify([])
        
    matches = Product.query.filter(
        or_(
            Product.name.ilike(f"%{q}%"),
            Product.category.ilike(f"%{q}%"),
            Product.brand.ilike(f"%{q}%")
        )
    ).limit(8).all()
    
    results = [
        {
            "id": p.product_id,
            "name": p.name,
            "category": p.category,
            "brand": p.brand,
            "price": p.final_price,
            "image_url": p.image_url
        }
        for p in matches
    ]
    return jsonify(results)

@product_bp.route("/api/products")
def api_get_products():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    cat = request.args.get("category")
    
    query = Product.query
    if cat:
        query = query.filter_by(category=cat)
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    
    return jsonify({
        "total": pagination.total,
        "page": page,
        "products": [p.to_dict() for p in pagination.items]
    })

@product_bp.route("/api/products/<product_id>")
def api_get_product_by_id(product_id):
    product = Product.query.filter_by(product_id=product_id).first()
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product.to_dict())
