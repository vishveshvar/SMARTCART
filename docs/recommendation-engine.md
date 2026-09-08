# Recommendation Engine Architecture & Algorithms

This document describes the algorithms, mathematical formulations, and engineering architecture behind the recommendation modules in **SmartCart**.

---

## 1. Engine Taxonomy

SmartCart implements a hybrid recommendation system comprising four complementary strategies:

```mermaid
graph TD
    User["Customer / Session Context"] --> EngineRouter{"Recommendation Router"}
    
    EngineRouter -->|Personalized Context| Hybrid["1. Multi-Factor Hybrid Engine<br/>Random Forest ML + Business Signals"]
    EngineRouter -->|Product View Context| ContentSim["2. Content-Based Similarity Engine<br/>TF-IDF + Cosine Similarity"]
    EngineRouter -->|Product Detail / Cart| BasketAssoc["3. Market Basket Association Engine<br/>Co-occurrence Matrix + Bundle Pricing"]
    EngineRouter -->|New Visitor (Cold-Start)| Fallback["4. Popularity & Diversity Fallback<br/>Bestsellers & Trending Scores"]
```

---

## 2. Personalized Multi-Factor Hybrid Scoring

The personalized recommendation engine (`services/recommendation_service.py`) ranks catalog candidates by combining the statistical predictions of the **Random Forest Classifier** with weighted heuristic signals.

### Mathematical Formulation:

For a given customer $u$ and candidate product $i$, the composite recommendation score $S(u, i)$ is computed as:

$$S(u, i) = w_1 \cdot P_{\text{ML}}(u, i) + w_2 \cdot C_{\text{pref}}(u, i) + w_3 \cdot H_{\text{hist}}(u, i) + w_4 \cdot P_{\text{pop}}(i) + w_5 \cdot R_{\text{rate}}(i) + w_6 \cdot Q_{\text{search}}(u, i)$$

Where the weights $w_k$ sum to $1.0$:

| Weight | Parameter | Formula / Definition | Range |
| :---: | :--- | :--- | :---: |
| **0.50** | $P_{\text{ML}}(u, i)$ | Random Forest purchase propensity `predict_proba(X)[:, 1]` | $[0.0, 1.0]$ |
| **0.15** | $C_{\text{pref}}(u, i)$ | $1.0$ if $\text{Category}(i) = \text{PreferredCategory}(u)$, else $0.4$ | $[0.4, 1.0]$ |
| **0.10** | $H_{\text{hist}}(u, i)$ | $0.9$ if category was previously purchased by customer, else $0.3$ | $[0.3, 0.9]$ |
| **0.10** | $P_{\text{pop}}(i)$ | $\text{PopularityScore}(i) / 100.0$ | $[0.0, 1.0]$ |
| **0.10** | $R_{\text{rate}}(i)$ | $\text{Rating}(i) / 5.0$ | $[0.0, 1.0]$ |
| **0.05** | $Q_{\text{search}}(u, i)$ | $1.0$ if product matches recent session queries, else $0.2$ | $[0.2, 1.0]$ |

### Score Normalization & Match Badging:
The composite score $S(u, i)$ is scaled to a visible percentage:
$$\text{Match Percentage} = \min(99, \max(62, \text{round}(S(u, i) \times 100)))$$

Visual badges are assigned based on score thresholds:
- $\ge 88\%$: **AI Recommended** (`badge bg-primary`)
- $76\% - 87\%$: **Highly Relevant** (`badge bg-success`)
- $< 76\%$: **Recommended** (`badge bg-info`)

### Explainable AI (XAI) Reason Generator:
To maintain user trust, every recommended product card carries a dynamically generated reason:
- If recently viewed: *"Because you recently viewed this item."*
- If matching recent search: *"Matches your search for '{query}' in {category}."*
- If matching preferred category: *"Matches your shopping preference for {category}."*
- If matching past purchase: *"Complements your previous purchases in {category}."*
- If top rated: *"Top-rated ({rating}★) customer favorite."*
- Default: *"Popular among customers with similar shopping behavior."*

---

## 3. Content-Based Product Similarity

The similarity engine (`services/similarity_service.py`) powers the **"Similar Products"** carousel on product detail pages.

### Vectorization & Cosine Similarity:
1. **Feature Concatenation**: For each product, a combined text document is formed:
   $$\text{Doc}_i = \text{Category} \oplus \text{Subcategory} \oplus \text{Brand} \oplus \text{Tags} \oplus \text{Description}$$
2. **TF-IDF Matrix**: Scikit-Learn's `TfidfVectorizer(stop_words='english', max_features=1500)` constructs a normalized document-term matrix $V$.
3. **Pairwise Cosine Similarity**:
   $$\text{Sim}(i, j) = \cos(\theta) = \frac{\mathbf{v}_i \cdot \mathbf{v}_j}{\|\mathbf{v}_i\| \|\mathbf{v}_j\|}$$
4. **Ranking**: The top $N=6$ items with highest cosine similarity (excluding product $i$) are returned.

---

## 4. Market Basket Association & Frequently Bought Together

The association engine (`services/association_service.py`) analyzes historical order groupings from `data/purchases.csv` and the database `order_items` table.

### Co-Occurrence Matrix:
For any pair of products $(i, j)$ appearing in the same `Order_ID`:
$$C(i, j) = \sum_{o \in \text{Orders}} \mathbb{I}(i \in o \land j \in o)$$

When viewing product $i$, the engine selects candidates $j$ maximizing $C(i, j)$.

### Fallback Complementary Rules:
If historical co-occurrences are sparse for a new product, category-level accessory rules fill the bundle:
- `Laptops` $\rightarrow$ `Accessories` (Laptop Backpack, Wireless Mouse)
- `Mobiles` $\rightarrow$ `Accessories` (Shockproof Case, Tempered Glass)
- `Footwear` $\rightarrow$ `Fashion` (Crew Socks, Athletic Shorts)

### Bundle Economics:
When rendered on the product page:
- Bundle Total: Sum of individual items.
- Bundle Discount: Automatic additional **10% discount** applied to the combined total.
- 1-Click Action: **"Add All to Cart"** dispatches an array of product IDs to `POST /api/cart/add`.

---

## 5. Cold-Start Fallback Strategy

For anonymous visitors or newly registered accounts with zero prior interactions:
1. **Candidate Pool**: Sorts catalog by `Popularity_Score` descending, filtered by verified ratings $\ge 4.0$.
2. **Category Diversity Constraint**: Enforces that no single retail category dominates more than 1 slot in the first 6 recommendations.
3. **Assigned Badge**: Designated as **"Trending Match"** with reasons such as *"Bestseller in Electronics (4.8★ rating)"*.

---

## 6. Feedback Telemetry & Analytics Loop

Every recommendation is instrumented for end-to-end telemetry:

```
[ Recommendation Shown ] ──> RecommendationLog (shown_at, clicked=0, purchased=0)
          │
          ├──> [ Customer Clicks Card ] ──> POST /api/recommendations/track (clicked=1)
          │
          └──> [ Customer Buys Product ] ──> OrderService (purchased=1)
```

This telemetry enables real-time reporting on the Admin Portal (`/admin/recommendations`):
$$\text{Click-Through Rate (CTR)} = \frac{\sum \text{Clicks}}{\sum \text{Impressions}} \times 100$$
$$\text{Conversion Rate (CVR)} = \frac{\sum \text{Purchases}}{\max(1, \sum \text{Clicks})} \times 100$$
