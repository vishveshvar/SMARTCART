# Machine Learning Architecture & Evaluation

This document provides technical documentation for the Machine Learning component of **SmartCart**, detailing dataset preprocessing, feature engineering, model training, and performance metrics.

---

## 1. Problem Formulation

The primary machine learning task is formulated as a **supervised binary classification problem**:
Given a customer's demographic profile, past behavior, and a target product's attributes, predict the probability that the customer will purchase the product:

$$\hat{y} = P(\text{Purchased} = 1 \mid X)$$

Where:
- $\hat{y} \in [0, 1]$ represents the predicted purchase propensity score.
- $X$ is the engineered feature vector combining customer, product, and historical interaction signals.

---

## 2. Prevention of Data Leakage

In e-commerce prediction models, data leakage occurs when features contain information that would only be available *after* a purchase has taken place (e.g. `Order_ID`, `Payment_Method`, or post-order transaction timestamps). 

In SmartCart, strict leakage prevention is enforced:
1. **Excluded Identifiers**: `Purchase_ID`, `Order_ID`, and order timestamps are omitted from training vectors.
2. **Behavioral Aggregation**: Historical view counts, wishlist flags, and category purchase counts are computed on interaction history without utilizing current target labels.
3. **Stratified Split**: Train (80%) and Test (20%) sets are partitioned prior to fitting preprocessors using `train_test_split(..., stratify=y, random_state=42)`.

---

## 3. Feature Pipeline & Preprocessing

The preprocessing pipeline (`preprocessing.py`) uses Scikit-Learn's `ColumnTransformer`:

```
Input Features (14 Numerical + 4 Categorical)
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
  Numerical Branch    Categorical Branch
         │                   │
  StandardScaler()    OneHotEncoder(handle_unknown='ignore')
         │                   │
         └─────────┬─────────┘
                   ▼
       Concatenated Feature Matrix
```

### Feature Dictionary:

| Feature Name | Type | Pipeline Transformer | Description |
| :--- | :--- | :--- | :--- |
| `Age` | Numerical | `StandardScaler` | Age of customer |
| `Product_Price` | Numerical | `StandardScaler` | Discounted / final price of product |
| `Discount` | Numerical | `StandardScaler` | Percentage discount (0–50%) |
| `Product_Rating` | Numerical | `StandardScaler` | Average product star rating (1.0–5.0) |
| `Review_Count` | Numerical | `StandardScaler` | Total verified customer reviews |
| `Popularity_Score`| Numerical | `StandardScaler` | Composite catalog engagement score |
| `Previous_Purchases` | Numerical | `StandardScaler` | Lifetime total orders placed by customer |
| `Category_Purchase_Count` | Numerical | `StandardScaler` | Prior purchases in this specific category |
| `Product_View_Count` | Numerical | `StandardScaler` | Number of times customer viewed this item |
| `Wishlist_Count` | Numerical | `StandardScaler` | Binary flag (1 if saved to wishlist) |
| `Cart_Count` | Numerical | `StandardScaler` | Binary flag (1 if added to cart) |
| `Average_Order_Value` | Numerical | `StandardScaler` | Customer lifetime average order spend |
| `Search_Relevance` | Numerical | `StandardScaler` | Keyword/category semantic search relevance |
| `Historical_Product_Rating` | Numerical | `StandardScaler` | Baseline historical rating |
| `Gender` | Categorical | `OneHotEncoder` | Customer gender (Male, Female, Other) |
| `Preferred_Category` | Categorical | `OneHotEncoder` | Declared favorite retail category |
| `Category` | Categorical | `OneHotEncoder` | Product primary category (15 classes) |
| `Subcategory` | Categorical | `OneHotEncoder` | Product specific sub-department |

---

## 4. Model Specification: Random Forest Classifier

SmartCart employs `RandomForestClassifier` from Scikit-Learn.

### Why Random Forest for SmartCart?
1. **Handling Mixed Data Types**: Naturally handles combined scaled numerical variables and sparse one-hot encoded categorical indicators without assuming linearity.
2. **Ensemble Variance Reduction**: Averages the predictions of 150 independent decision trees, reducing overfitting on synthetic behavioral artifacts.
3. **Class Imbalance Resilience**: Incorporates `class_weight="balanced"`, penalizing false negatives proportionally to class frequencies.
4. **Native Feature Importance**: Enables exact extraction of MDI (Mean Decrease in Impurity) to understand feature contributions.

### Hyperparameters (from `train_model.py`):
```python
RandomForestClassifier(
    n_estimators=150,
    max_depth=12,
    min_samples_split=8,
    min_samples_leaf=4,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)
```

---

## 5. Measured Model Evaluation Metrics

Evaluated on an **80/20 Stratified Test Set** (25,602 training samples, 6,401 test samples) generated from `data/interactions.csv` (recorded in `models/model_metrics.json`):

| Metric | Measured Score | Technical Interpretation |
| :--- | :---: | :--- |
| **Accuracy** | **78.58%** | Ratio of correctly identified purchase & non-purchase actions |
| **Precision** | **38.92%** | Precision of purchase predictions under high sensitivity tuning |
| **Recall** | **99.54%** | Successfully captures nearly 100% of all actual purchase events |
| **F1 Score** | **55.96%** | Harmonic mean balancing recall and precision |
| **ROC-AUC** | **0.8696** | High separability between purchase and non-purchase intent |

### Measured Confusion Matrix:

$$\begin{pmatrix} \text{TN} = 4,159 & \text{FP} = 1,367 \\ \text{FN} = 4 & \text{TP} = 871 \end{pmatrix}$$

- **True Negatives (4,159)**: Correctly predicted instances where the customer browsed without buying.
- **False Positives (1,367)**: High-intent interactions (e.g. cart additions) that didn't conclude in an order.
- **False Negatives (4)**: Rare cases where an unpredicted purchase occurred (reflecting $99.54\%$ recall).
- **True Positives (871)**: Correctly identified customer purchases.

---

## 6. Feature Importance Ranking

Derived from Gini impurity reductions across the 150-tree ensemble:

| Rank | Feature | Relative Importance (%) |
| :---: | :--- | :---: |
| 1 | `Cart_Count` | **43.33%** |
| 2 | `Product_View_Count` | **42.16%** |
| 3 | `Category` | **3.49%** |
| 4 | `Preferred_Category` | **2.26%** |
| 5 | `Subcategory` | **1.76%** |
| 6 | `Wishlist_Count` | **1.71%** |
| 7 | `Category_Purchase_Count` | **0.90%** |
| 8 | `Product_Price` | **0.81%** |
| 9 | `Average_Order_Value` | **0.74%** |
| 10 | `Age` | **0.60%** |
| 11 | `Previous_Purchases` | **0.57%** |
| 12 | `Review_Count` | **0.57%** |
| 13 | `Popularity_Score` | **0.54%** |
| 14 | `Historical_Product_Rating` | **0.40%** |
| 15 | `Gender` | **0.36%** |
| 16 | `Product_Rating` | **0.36%** |
| 17 | `Discount` | **0.35%** |

---

## 7. Retraining Workflow

Administrators can trigger model retraining dynamically:
1. Via the Admin Dashboard (`POST /admin/retrain` or `POST /api/retrain`).
2. Programmatically executing:
   ```bash
   python train_model.py
   ```
3. The process re-loads the latest data from `data/`, fits the preprocessing pipeline and Random Forest model, calculates updated metrics, updates `models/model_metrics.json`, and invokes `recommendation_service.reload()` to update memory without server restarts.
