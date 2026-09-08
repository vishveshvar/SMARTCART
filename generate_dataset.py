"""
SmartCart - Synthetic Dataset Generator
Generates realistic customer, product, interaction, purchase, search history, and rating datasets
with realistic behavioral correlations and co-occurrence patterns.
"""

import os
import random
import datetime
import pandas as pd
import numpy as np

# Set seeds for reproducibility
random.seed(42)
np.random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. CATEGORY & PRODUCT DEFINITIONS
# -------------------------------------------------------------
CATEGORIES = {
    "Electronics": {
        "subcategories": ["Audio", "Television", "Cameras", "Smart Devices", "Wearables"],
        "brands": ["Sony", "Bose", "JBL", "Samsung", "LG", "Sennheiser", "Boat", "Noise"],
        "price_range": (1200, 45000),
        "items": [
            ("Wireless Bluetooth Headphones", "Audio", "Over-ear noise cancelling headphones with deep bass", "wireless,bluetooth,audio,headphones,anc"),
            ("Compact Bluetooth Speaker", "Audio", "Portable waterproof outdoor bluetooth speaker", "speaker,portable,waterproof,audio,bluetooth"),
            ("Smart Fitness Watch", "Wearables", "AMOLED fitness tracker with heart rate and SpO2 monitor", "smartwatch,fitness,heartrate,wearable,tracker"),
            ("4K Ultra HD Smart TV 55-inch", "Television", "Vibrant Dolby Vision smart display with voice assistant", "tv,smart tv,4k,ultra hd,television,display"),
            ("Noise Cancelling Wireless Earbuds", "Audio", "True wireless earbuds with active noise cancellation and low latency", "earbuds,tws,wireless,bluetooth,audio,anc"),
            ("Digital Mirrorless Camera", "Cameras", "4K video recording with 24MP sensor and interchangeable lens", "camera,photography,4k,video,lens"),
            ("Smart Home Voice Hub", "Smart Devices", "Voice-controlled assistant for automated home appliances", "smart home,voice assistant,hub,iot"),
            ("Bass Soundbar with Subwoofer", "Audio", "2.1 channel cinematic soundbar for home theatre experience", "soundbar,audio,speaker,home theatre,subwoofer"),
            ("Action Camera 4K Waterproof", "Cameras", "Rugged 4K 60fps action cam with dual screens", "action camera,waterproof,4k,sports,vlog"),
            ("Smart Wi-Fi Security Camera", "Smart Devices", "1080p full color night vision security camera with motion alert", "security camera,cctv,smart home,wifi"),
        ]
    },
    "Mobiles": {
        "subcategories": ["Flagship", "Budget", "Mid-Range", "Refurbished"],
        "brands": ["Apple", "Samsung", "OnePlus", "Xiaomi", "Google", "Realme", "Motorola"],
        "price_range": (8000, 125000),
        "items": [
            ("Smartphone Ultra 5G", "Flagship", "Snapdragon 8 Gen 3 flagship with 200MP camera system", "smartphone,mobile,5g,flagship,android"),
            ("NextGen Smartphone Pro Max", "Flagship", "Titanium frame with OLED Super Retina display and A17 Pro", "smartphone,ios,apple,flagship,premium"),
            ("Smooth Display Mid-Range 5G", "Mid-Range", "120Hz AMOLED 64MP OIS camera with 67W fast charging", "mobile,5g,smartphone,amoled,fastcharge"),
            ("Battery King Phone 6000mAh", "Budget", "Long-lasting dual SIM smartphone with expandable memory", "mobile,budget,long battery,smartphone"),
            ("Pure Android Experience 5G", "Mid-Range", "Clean software with best-in-class computational photography", "google,android,camera phone,5g"),
            ("Sleek Curve Screen 5G Phone", "Mid-Range", "Ultra slim 3D curved display with 50MP portrait selfie", "smartphone,curved display,selfie,5g"),
        ]
    },
    "Laptops": {
        "subcategories": ["Gaming Laptops", "Ultrabooks", "Business Laptops", "Student Laptops"],
        "brands": ["Apple", "Dell", "HP", "Lenovo", "Asus", "Acer", "MSI"],
        "price_range": (28000, 185000),
        "items": [
            ("Pro Gaming Laptop RTX 4070", "Gaming Laptops", "Intel i7 14th Gen 16GB RAM 1TB SSD with high refresh rate screen", "laptop,gaming,rtx,intel,high performance"),
            ("Ultra-Slim Metal Ultrabook", "Ultrabooks", "Lightweight 1.2kg carbon chassis with all-day battery life", "laptop,ultrabook,lightweight,slim,work"),
            ("Business Productivity Notebook", "Business Laptops", "Anti-glare screen with fingerprint reader and military-grade durability", "laptop,business,office,durability"),
            ("Student Essential Laptop", "Student Laptops", "Budget friendly 15.6-inch laptop with fast SSD storage", "laptop,student,budget,college,school"),
            ("Creator Studio Laptop 4K OLED", "Ultrabooks", "Color-calibrated 100% DCI-P3 display for video and graphic design", "laptop,creator,editing,oled,design"),
        ]
    },
    "Fashion": {
        "subcategories": ["Men's Clothing", "Women's Clothing", "Winterwear", "Ethnic Wear"],
        "brands": ["Zara", "H&M", "Levis", "Nike", "Adidas", "Puma", "Raymond", "FabIndia"],
        "price_range": (499, 6999),
        "items": [
            ("Classic Denim Slim Jeans", "Men's Clothing", "Durable stretch cotton denim jeans in deep indigo wash", "jeans,denim,men,fashion,clothing"),
            ("Solid Crew Neck Cotton T-Shirt", "Men's Clothing", "100% combed breathable cotton everyday tee", "tshirt,cotton,casual,men,fashion"),
            ("Floral Print Maxi Summer Dress", "Women's Clothing", "Lightweight chiffon breezy bohemian dress for outings", "dress,women,floral,summer,fashion"),
            ("Cozy Fleece Pullover Hoodie", "Winterwear", "Warm brushed fleece hoodie with kangaroo pocket", "hoodie,winter,sweater,casual,warm"),
            ("Tailored Formal Oxford Shirt", "Men's Clothing", "Crisp wrinkle-resistant 100% Egyptian cotton dress shirt", "shirt,formal,office,men,cotton"),
            ("Handcrafted Cotton Kurta", "Ethnic Wear", "Traditional artisan embroidered ethnic festive kurta", "ethnic,kurta,traditional,indian,festival"),
            ("Casual Stretch Chino Trousers", "Men's Clothing", "Versatile casual smart-fit flat-front chinos", "chinos,trousers,pants,men,casual"),
            ("Denim Trucker Jacket", "Winterwear", "Vintage rugged button-down denim outerwear jacket", "jacket,denim,outerwear,winter,fashion"),
        ]
    },
    "Footwear": {
        "subcategories": ["Running Shoes", "Sneakers", "Formal Shoes", "Sandals"],
        "brands": ["Nike", "Adidas", "Puma", "Reebok", "Clarks", "Bata", "Skechers"],
        "price_range": (999, 12999),
        "items": [
            ("Cushioned Running Shoes", "Running Shoes", "Breathable mesh lightweight running shoes with responsive foam", "shoes,running,sports,fitness,cushion"),
            ("Classic Low-Top Canvas Sneakers", "Sneakers", "Timeless casual streetwear sneakers with rubber sole", "sneakers,casual,streetwear,shoes,canvas"),
            ("Genuine Leather Oxford Shoes", "Formal Shoes", "Handcrafted premium full-grain leather formal dress shoes", "shoes,formal,leather,oxford,office"),
            ("Comfort Walking Slip-On Shoes", "Running Shoes", "Orthopedic memory foam slip-on shoes for daily walking", "shoes,walking,comfort,slip-on,foam"),
            ("Waterproof Outdoor Hiking Boots", "Running Shoes", "High-traction grip rugged all-terrain hiking shoes", "boots,hiking,outdoor,adventure,shoes"),
        ]
    },
    "Beauty": {
        "subcategories": ["Skincare", "Haircare", "Makeup", "Fragrances"],
        "brands": ["L'Oreal", "Maybelline", "Neutrogena", "The Ordinary", "Nivea", "Minimalist"],
        "price_range": (299, 4500),
        "items": [
            ("Hydrating Hyaluronic Acid Serum", "Skincare", "Deep moisture replenishing serum for glowing radiant skin", "serum,skincare,hyaluronic,hydration,glow"),
            ("Vitamin C Brightening Facial Cleanser", "Skincare", "Gentle foaming antioxidant face wash for clear complexion", "face wash,cleanser,vitamin c,brightening,skin"),
            ("Matte Liquid Longwear Foundation", "Makeup", "24-hour oil-free flawless coverage lightweight foundation", "makeup,foundation,matte,cosmetics,beauty"),
            ("Keratin Smoothing Hair Mask", "Haircare", "Intensive repair mask for dry frizzy and damaged hair", "haircare,mask,keratin,repair,smooth"),
            ("Luxury Eau De Parfum 100ml", "Fragrances", "Long-lasting woody aromatic fragrance with amber and citrus notes", "perfume,fragrance,scent,edp,luxury"),
            ("Matte Velvet Long-Stay Lipstick", "Makeup", "Non-drying smudge-proof intensely pigmented lipstick", "lipstick,makeup,matte,beauty,lips"),
        ]
    },
    "Home": {
        "subcategories": ["Bedding", "Decor", "Lighting", "Storage"],
        "brands": ["IKEA", "Spaces", "D'Decor", "Philips", "Home Centre", "Solimo"],
        "price_range": (399, 9999),
        "items": [
            ("100% Cotton 300TC Double Bed Sheet", "Bedding", "Super soft breathable bedsheet set with two matching pillow covers", "bedsheet,bedding,cotton,home,decor"),
            ("Smart LED Color Ambient Bulb", "Lighting", "App and voice controlled dimmable 16 million colors bulb", "lighting,smart bulb,led,home,philips"),
            ("Velvet Touch Blackout Window Curtains", "Decor", "Thermal insulated light blocking curtains for living room and bedroom", "curtains,decor,blackout,home,window"),
            ("Collapsible Fabric Storage Organizers", "Storage", "Multi-pack sturdy wardrobe closet organizers for clothes", "storage,organizer,wardrobe,home,box"),
            ("Handwoven Boho Area Rug", "Decor", "Intricate geometric pattern durable jute and cotton floor rug", "rug,carpet,decor,floor,boho"),
        ]
    },
    "Kitchen": {
        "subcategories": ["Cookware", "Small Appliances", "Storage & Containers", "Kitchen Tools"],
        "brands": ["Prestige", "Hawkins", "Wonderchef", "Philips", "Pigeon", "Milton"],
        "price_range": (499, 14999),
        "items": [
            ("Hard Anodized Non-Stick Cookware Set", "Cookware", "Durable scratch-resistant frying pan, kadai and sauce pan with glass lids", "cookware,kitchen,pan,non-stick,cooking"),
            ("Electric Rapid Air Fryer 4.5L", "Small Appliances", "Oil-free healthy frying, baking, grilling and roasting appliance", "air fryer,appliance,healthy,kitchen,cooking"),
            ("Heavy-Duty 750W Mixer Grinder", "Small Appliances", "High torque copper motor with 3 stainless steel multi-use jars", "mixer grinder,blender,kitchen,appliance,cook"),
            ("Airtight Glass Food Storage Jars", "Storage & Containers", "Leak-proof borosilicate glass food containers with bamboo lids", "glass jars,containers,kitchen,storage,airtight"),
            ("Stainless Steel Chef Knife Set", "Kitchen Tools", "Ultra-sharp precision forged Japanese stainless steel knife block", "knife,chef knife,kitchen,cutlery,tools"),
        ]
    },
    "Furniture": {
        "subcategories": ["Living Room", "Bedroom", "Office", "Dining"],
        "brands": ["IKEA", "Wakefit", "Urban Ladder", "Sleepyhead", "Godrej Interio"],
        "price_range": (2999, 39999),
        "items": [
            ("Ergonomic Mesh High-Back Office Chair", "Office", "Adjustable lumbar support and 3D armrests for long sitting hours", "office chair,ergonomic,furniture,desk chair,mesh"),
            ("Modern Engineered Wood Computer Desk", "Office", "Spacious study table with cable management grommet and side drawers", "desk,table,office,furniture,study"),
            ("Orthopedic Memory Foam Mattress 6-inch", "Bedroom", "Zero partner disturbance dual-comfort orthopedic sleeping mattress", "mattress,bed,bedroom,memory foam,sleep"),
            ("Contemporary 3-Seater Fabric Sofa", "Living Room", "High-density cushioned lounge sofa with solid wood frame", "sofa,living room,couch,furniture,home"),
            ("Minimalist Nesting Coffee Tables", "Living Room", "Set of 2 Scandinavian round metal and oak wood accent tables", "coffee table,living room,furniture,table,decor"),
        ]
    },
    "Sports": {
        "subcategories": ["Fitness Equipment", "Outdoor Sports", "Sportswear", "Yoga"],
        "brands": ["Decathlon", "Nivia", "Yonex", "Cosco", "Puma", "Boldfit"],
        "price_range": (349, 15999),
        "items": [
            ("Anti-Burst Gym Exercise Ball with Pump", "Fitness Equipment", "Core strengthening and pilates stability swiss ball", "fitness,gym,exercise,workout,ball"),
            ("Extra Thick Non-Slip Eco Yoga Mat", "Yoga", "6mm TPE high-density alignment yoga mat with carry strap", "yoga mat,fitness,exercise,wellness,yoga"),
            ("Adjustable Hex Dumbbells Pair", "Fitness Equipment", "Cast iron rubber-encased heavy weights for home gym workouts", "dumbbells,weights,gym,fitness,bodybuilding"),
            ("Carbon Fiber Badminton Racket", "Outdoor Sports", "High tension lightweight isometric tournament badminton racket", "badminton,racket,sports,outdoor,games"),
            ("Quick Dry Athletic Training Shorts", "Sportswear", "Moisture wicking running gym shorts with zippered pockets", "shorts,sportswear,gym,training,running"),
        ]
    },
    "Books": {
        "subcategories": ["Fiction", "Self-Help", "Technology", "Business & Finance"],
        "brands": ["Penguin", "HarperCollins", "O'Reilly", "Random House", "Bloomsbury"],
        "price_range": (199, 2999),
        "items": [
            ("Atomic Habits: Build Good Habits", "Self-Help", "Proven framework for improving every day by James Clear", "book,self-help,habits,bestseller,reading"),
            ("Designing Data-Intensive Applications", "Technology", "The definitive guide to distributed data systems and architecture", "book,tech,programming,data,engineering"),
            ("The Psychology of Money", "Business & Finance", "Timeless lessons on wealth, greed, and happiness by Morgan Housel", "book,finance,money,investing,reading"),
            ("Deep Work: Focused Success in a Distracted World", "Self-Help", "Rules for focused success in a distracted world by Cal Newport", "book,productivity,work,focus,career"),
            ("Python Machine Learning & AI Mastery", "Technology", "Comprehensive hands-on guide from algorithms to production deployment", "book,python,ai,machine learning,tech"),
        ]
    },
    "Gaming": {
        "subcategories": ["Consoles", "Controllers", "Accessories", "Gaming Mice & Keyboards"],
        "brands": ["PlayStation", "Xbox", "Razer", "Logitech G", "Corsair", "SteelSeries"],
        "price_range": (999, 54999),
        "items": [
            ("Wireless Haptic Feedback Gaming Controller", "Controllers", "Customizable triggers with ultra-low latency wireless dongle", "controller,gamepad,gaming,wireless,pc"),
            ("RGB Mechanical Gaming Keyboard", "Gaming Mice & Keyboards", "Hot-swappable tactile switches with per-key customizable RGB lighting", "keyboard,mechanical,gaming,rgb,pc"),
            ("Ultra-Lightweight 8KHz Optical Gaming Mouse", "Gaming Mice & Keyboards", "Sensor with 26000 DPI and optical switches for competitive esports", "mouse,gaming mouse,esports,rgb,pc"),
            ("Surround Sound Gaming Headset with Mic", "Accessories", "50mm drivers with detachable noise-cancelling boom mic", "headset,gaming,audio,mic,discord"),
            ("Next-Gen Home Gaming Console 1TB", "Consoles", "High-speed custom SSD 4K 120fps ray tracing next-generation console", "console,gaming,4k,playstation,xbox"),
        ]
    },
    "Accessories": {
        "subcategories": ["Bags & Backpacks", "Computer Accessories", "Mobile Accessories", "Travel"],
        "brands": ["American Tourister", "Logitech", "Anker", "Spigen", "Portronics"],
        "price_range": (299, 6999),
        "items": [
            ("Water-Resistant Laptop Backpack 15.6-inch", "Bags & Backpacks", "Ergonomic multi-compartment travel laptop bag with USB charging port", "bag,backpack,laptop bag,travel,office"),
            ("Ergonomic Silent Wireless Mouse", "Computer Accessories", "Comfortable contoured shape with whisper quiet clicks and long battery", "mouse,wireless mouse,office,computer,laptop"),
            ("Multi-Port 7-in-1 USB-C Hub Adapter", "Computer Accessories", "4K HDMI 100W Power Delivery USB 3.0 and SD card reader", "usb hub,adapter,usb-c,laptop,monitor"),
            ("Magnetic Qi Fast Wireless Charger Stand", "Mobile Accessories", "15W fast induction charging station for phones and wireless earbuds", "charger,wireless charger,mobile,charging"),
            ("Shockproof Clear Phone Case", "Mobile Accessories", "Military grade drop protection slim clear bumper case", "phone case,cover,protection,mobile"),
            ("9H Tempered Glass Screen Protector (2-Pack)", "Mobile Accessories", "Scratch-resistant ultra-clear tempered glass with alignment frame", "screen protector,tempered glass,mobile,screen"),
        ]
    },
    "Grocery": {
        "subcategories": ["Beverages", "Snacks", "Cooking Essentials", "Organic Foods"],
        "brands": ["Tata", "Nestle", "Organic India", "Saffola", "Dabur"],
        "price_range": (149, 1999),
        "items": [
            ("Organic Green Tea Herbal Infusion 100 Bags", "Beverages", "Antioxidant-rich whole leaf soothing detox green tea", "tea,green tea,organic,beverage,detox"),
            ("Roasted California Almonds 500g", "Snacks", "Crunchy vacuum-packed premium salted California almonds", "almonds,nuts,healthy,snack,dry fruits"),
            ("Cold-Pressed Extra Virgin Olive Oil 1L", "Cooking Essentials", "Unrefined cold-extracted Mediterranean olive oil for salads and cooking", "olive oil,cooking,healthy,organic,grocery"),
            ("Organic Raw Honey 500g", "Organic Foods", "100% pure unfiltered natural forest wildflower honey", "honey,organic,raw,sweetener,grocery"),
            ("Artisan Dark Roasted Arabica Coffee Beans 250g", "Beverages", "Single-origin aromatic medium dark roast whole coffee beans", "coffee,espresso,beverage,arabica,beans"),
        ]
    },
    "Personal Care": {
        "subcategories": ["Oral Care", "Bath & Body", "Shaving & Grooming", "Wellness"],
        "brands": ["Colgate", "Oral-B", "Philips", "Gillette", "Dettol", "Dove"],
        "price_range": (199, 5999),
        "items": [
            ("Sonic Electric Toothbrush with Timer", "Oral Care", "40000 vibrations/min with 3 cleaning modes and 4 brush heads", "toothbrush,electric,oral care,hygiene,sonic"),
            ("Cordless Rechargeable Beard Trimmer", "Shaving & Grooming", "Stainless steel self-sharpening blades with 20 length settings", "trimmer,beard,grooming,shaver,mens"),
            ("Deep Cleansing Charcoal Body Wash 500ml", "Bath & Body", "Refreshing activated charcoal body shower gel with invigorating mint", "body wash,shower gel,bath,hygiene,soap"),
            ("Gentle Sulfate-Free Moisturizing Body Lotion", "Bath & Body", "Enriched with shea butter and cocoa butter for 48h hydration", "lotion,moisturizer,skincare,body lotion,bath"),
        ]
    }
}

CITIES_STATES = [
    ("Mumbai", "Maharashtra"),
    ("Delhi", "Delhi"),
    ("Bengaluru", "Karnataka"),
    ("Hyderabad", "Telangana"),
    ("Chennai", "Tamil Nadu"),
    ("Kolkata", "West Bengal"),
    ("Pune", "Maharashtra"),
    ("Ahmedabad", "Gujarat"),
    ("Jaipur", "Rajasthan"),
    ("Lucknow", "Uttar Pradesh"),
    ("Chandigarh", "Punjab"),
    ("Kochi", "Kerala"),
    ("Indore", "Madhya Pradesh"),
    ("Bhopal", "Madhya Pradesh"),
    ("Coimbatore", "Tamil Nadu"),
    ("Visakhapatnam", "Andhra Pradesh"),
    ("Surat", "Gujarat"),
    ("Nagpur", "Maharashtra"),
    ("Patna", "Bihar"),
    ("Guwahati", "Assam")
]

FIRST_NAMES = [
    "Aarav", "Aditi", "Rohan", "Priya", "Vikram", "Neha", "Rahul", "Ananya", "Amit", "Pooja",
    "Karan", "Sneha", "Arjun", "Kavita", "Suresh", "Divya", "Manish", "Shweta", "Rajesh", "Deepika",
    "Gaurav", "Meera", "Abhishek", "Ritu", "Sanjay", "Tanvi", "Varun", "Swati", "Nikhil", "Isha",
    "Akash", "Simran", "Deepak", "Aakanksha", "Pranav", "Sunita", "Harsh", "Pallavi", "Vivek", "Preeti"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Gupta", "Singh", "Kumar", "Mehta", "Shah", "Reddy", "Nair",
    "Iyer", "Rao", "Joshi", "Bose", "Das", "Chopra", "Malhotra", "Kapoor", "Agarwal", "Bhatia",
    "Sen", "Deshmukh", "Kulkarni", "Choudhury", "Menon", "Pillai", "Mishra", "Pandey", "Saxena", "Trivedi"
]

PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash on Delivery", "Wallet"]
DEVICES = ["Mobile App", "Mobile Web", "Desktop", "Tablet"]
INTERACTION_TYPES = ["View", "Search", "Wishlist", "Cart", "Purchase", "Rating"]

# -------------------------------------------------------------
# 2. GENERATE PRODUCTS DATASET (600+ Products)
# -------------------------------------------------------------
def generate_products():
    print("Generating Products dataset...")
    products = []
    prod_id = 1
    
    # We will expand each base template with brand/color/spec variations to create 600+ diverse products
    for category_name, cat_data in CATEGORIES.items():
        base_items = cat_data["items"]
        brands = cat_data["brands"]
        price_min, price_max = cat_data["price_range"]
        
        # Determine number of product variations to reach >600 total products
        target_count_for_cat = 42 # 15 categories * ~42 = ~630 products
        
        count = 0
        while count < target_count_for_cat:
            item_tuple = random.choice(base_items)
            base_title, subcat, base_desc, tags = item_tuple
            brand = random.choice(brands)
            
            # Variations in title, color, price
            color = random.choice(["Midnight Black", "Space Gray", "Pearl White", "Navy Blue", "Crimson Red", "Silver", "Olive Green", "Charcoal", "Rose Gold", "Classic Beige"])
            size = random.choice(["Standard", "S", "M", "L", "XL", "Free Size", "Compact", "Pro", "Max"]) if category_name in ["Fashion", "Footwear"] else random.choice(["Default", "128GB", "256GB", "512GB", "16GB RAM", "Standard"])
            
            # Age group & Gender target
            if category_name in ["Beauty", "Fashion"]:
                gender_target = random.choice(["Unisex", "Men", "Women"])
            else:
                gender_target = "All"
                
            age_group = random.choice(["All Ages", "18-35", "25-50", "Teens & Youth", "Adults"])
            
            # Title creation
            name = f"{brand} {base_title}"
            if random.random() > 0.4:
                name += f" - {color}"
                
            price = round(random.uniform(price_min, price_max), -1)
            if price == 0:
                price = 499.0
            discount = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 50])
            final_price = round(price * (1 - discount / 100), 2)
            
            rating = round(random.uniform(3.5, 4.9), 1)
            review_count = int(np.random.exponential(scale=180)) + 15
            stock = random.randint(5, 250)
            
            # Popularity score (0 to 100)
            popularity = round(min(100.0, max(15.0, (rating / 5.0) * 50 + (min(review_count, 1000) / 1000) * 40 + random.uniform(0, 10))), 1)
            
            created_days_ago = random.randint(10, 730)
            created_date = (datetime.datetime.now() - datetime.timedelta(days=created_days_ago)).strftime("%Y-%m-%d")
            
            # Stock image placeholder with category theme keywords
            image_url = f"https://images.unsplash.com/photo-{1500000000000 + prod_id}?auto=format&fit=crop&w=600&q=80"
            
            products.append({
                "Product_ID": f"PROD_{prod_id:05d}",
                "Product_Name": name,
                "Category": category_name,
                "Subcategory": subcat,
                "Brand": brand,
                "Price": price,
                "Discount": discount,
                "Final_Price": final_price,
                "Rating": rating,
                "Review_Count": review_count,
                "Stock": stock,
                "Popularity_Score": popularity,
                "Product_Description": f"{base_desc}. Designed with premium quality materials by {brand}.",
                "Product_Tags": f"{tags},{brand.lower()},{category_name.lower()},{color.lower()}",
                "Age_Group": age_group,
                "Gender_Target": gender_target,
                "Color": color,
                "Size": size,
                "Created_Date": created_date,
                "Image_URL": image_url,
                "Status": "Active"
            })
            prod_id += 1
            count += 1
            
    df_products = pd.DataFrame(products)
    csv_path = os.path.join(DATA_DIR, "products.csv")
    df_products.to_csv(csv_path, index=False)
    print(f"Products dataset saved to {csv_path}: {len(df_products)} records.")
    return df_products

# -------------------------------------------------------------
# 3. GENERATE CUSTOMERS DATASET (3,000 Customers)
# -------------------------------------------------------------
def generate_customers(num_customers=3000):
    print(f"Generating {num_customers} Customers dataset...")
    customers = []
    
    cat_names = list(CATEGORIES.keys())
    
    for c_id in range(1, num_customers + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        
        # Gender
        gender = random.choice(["Male", "Female", "Other"])
        
        # Age distribution: 18 to 68, weighted towards 21-42
        age = int(np.random.normal(loc=32, scale=10))
        age = max(18, min(70, age))
        
        # Realistic category preference based on age and gender
        if age <= 28:
            cat_weights = [
                0.20 if c in ["Electronics", "Gaming", "Mobiles", "Fashion", "Footwear"]
                else 0.04 for c in cat_names
            ]
        elif age <= 45:
            cat_weights = [
                0.15 if c in ["Home", "Kitchen", "Laptops", "Books", "Personal Care", "Electronics"]
                else 0.05 for c in cat_names
            ]
        else:
            cat_weights = [
                0.22 if c in ["Home", "Kitchen", "Furniture", "Grocery", "Books"]
                else 0.03 for c in cat_names
            ]
            
        cat_weights = [w / sum(cat_weights) for w in cat_weights]
        pref_category = np.random.choice(cat_names, p=cat_weights)
        
        city, state = random.choice(CITIES_STATES)
        
        reg_days_ago = random.randint(20, 800)
        reg_date = (datetime.datetime.now() - datetime.timedelta(days=reg_days_ago)).strftime("%Y-%m-%d")
        
        total_purchases = int(np.random.poisson(lam=random.choice([2, 5, 9, 14])))
        if total_purchases > 0:
            last_p_days_ago = random.randint(1, min(reg_days_ago, 90))
            last_p_date = (datetime.datetime.now() - datetime.timedelta(days=last_p_days_ago)).strftime("%Y-%m-%d")
            avg_order_val = round(float(np.random.exponential(scale=2800) + 400), 2)
        else:
            last_p_date = None
            avg_order_val = 0.0
            
        purchase_freq = round(total_purchases / max(1, (reg_days_ago / 30.0)), 2)
        avg_rating = round(random.uniform(3.6, 5.0), 1) if total_purchases > 0 else 0.0
        
        # Customer ID
        cust_id = f"CUST_{c_id:05d}"
        
        customers.append({
            "Customer_ID": cust_id,
            "Customer_Name": name,
            "Age": age,
            "Gender": gender,
            "City": city,
            "State": state,
            "Registration_Date": reg_date,
            "Preferred_Category": pref_category,
            "Average_Order_Value": avg_order_val,
            "Total_Purchases": total_purchases,
            "Purchase_Frequency": purchase_freq,
            "Average_Rating_Given": avg_rating,
            "Last_Purchase_Date": last_p_date or ""
        })
        
    df_customers = pd.DataFrame(customers)
    csv_path = os.path.join(DATA_DIR, "customers.csv")
    df_customers.to_csv(csv_path, index=False)
    print(f"Customers dataset saved to {csv_path}: {len(df_customers)} records.")
    return df_customers

# -------------------------------------------------------------
# 4. GENERATE INTERACTIONS, PURCHASES, SEARCH, RATINGS (30,000+ interactions)
# -------------------------------------------------------------
def generate_behavioral_data(df_customers, df_products, min_interactions=30000):
    print(f"Generating behavioral data ({min_interactions}+ interactions, co-occurrences, searches)...")
    
    interactions = []
    purchases = []
    searches = []
    ratings = []
    
    customers_list = df_customers.to_dict(orient="records")
    products_by_cat = {}
    for cat in CATEGORIES.keys():
        products_by_cat[cat] = df_products[df_products["Category"] == cat].to_dict(orient="records")
        
    all_products = df_products.to_dict(orient="records")
    
    # Co-occurrence accessory rules for Frequently Bought Together:
    # Key = primary subcategory or item keyword -> target complementary category/subcategory
    co_occurrence_map = {
        "Laptops": ["Accessories", "Gaming"],
        "Mobiles": ["Accessories", "Electronics"],
        "Footwear": ["Fashion", "Sports"],
        "Cookware": ["Small Appliances", "Kitchen Tools"],
        "Gaming Laptops": ["Gaming Mice & Keyboards", "Controllers"],
        "Cameras": ["Accessories", "Audio"]
    }
    
    interaction_id = 1
    purchase_id = 1
    order_id_counter = 1000
    search_id = 1
    rating_id = 1
    
    # Generate sessions for customers
    while len(interactions) < min_interactions:
        cust = random.choice(customers_list)
        cust_id = cust["Customer_ID"]
        pref_cat = cust["Preferred_Category"]
        device = random.choice(DEVICES)
        session_id = f"SESS_{random.randint(100000, 999999)}"
        session_time = datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 180), minutes=random.randint(0, 1440))
        
        # In this session, user has high probability (70%) of browsing preferred category
        if random.random() < 0.70 and pref_cat in products_by_cat and len(products_by_cat[pref_cat]) > 0:
            target_cat = pref_cat
        else:
            target_cat = random.choice(list(CATEGORIES.keys()))
            
        cat_prods = products_by_cat[target_cat]
        if not cat_prods:
            continue
            
        # Session search action
        keyword = random.choice(target_cat.lower().split() + [target_cat.lower()] + [p["Subcategory"].lower() for p in cat_prods[:4]])
        clicked_prod = random.choice(cat_prods)
        
        searches.append({
            "Search_ID": f"SRCH_{search_id:06d}",
            "Customer_ID": cust_id,
            "Search_Keyword": keyword,
            "Search_Category": target_cat,
            "Search_Date": session_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Result_Clicked": 1,
            "Product_Clicked": clicked_prod["Product_Name"]
        })
        search_id += 1
        
        # Interaction: Search
        interactions.append({
            "Interaction_ID": f"INT_{interaction_id:07d}",
            "Customer_ID": cust_id,
            "Product_ID": clicked_prod["Product_ID"],
            "Interaction_Type": "Search",
            "Timestamp": session_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Session_ID": session_id,
            "Search_Keyword": keyword,
            "Category": target_cat,
            "Device": device,
            "Time_Spent": random.randint(15, 60),
            "Product_Viewed": 0,
            "Added_To_Wishlist": 0,
            "Added_To_Cart": 0,
            "Purchased": 0,
            "Rating_Given": 0
        })
        interaction_id += 1
        
        # Product browsing in session (1 to 4 items)
        session_prods = random.sample(cat_prods, min(len(cat_prods), random.randint(1, 4)))
        for p in session_prods:
            session_time += datetime.timedelta(seconds=random.randint(30, 180))
            time_spent = random.randint(20, 240)
            
            # View
            interactions.append({
                "Interaction_ID": f"INT_{interaction_id:07d}",
                "Customer_ID": cust_id,
                "Product_ID": p["Product_ID"],
                "Interaction_Type": "View",
                "Timestamp": session_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Session_ID": session_id,
                "Search_Keyword": "",
                "Category": p["Category"],
                "Device": device,
                "Time_Spent": time_spent,
                "Product_Viewed": 1,
                "Added_To_Wishlist": 0,
                "Added_To_Cart": 0,
                "Purchased": 0,
                "Rating_Given": 0
            })
            interaction_id += 1
            
            # Wishlist decision
            is_wishlist = 1 if (random.random() < 0.22) else 0
            if is_wishlist:
                interactions.append({
                    "Interaction_ID": f"INT_{interaction_id:07d}",
                    "Customer_ID": cust_id,
                    "Product_ID": p["Product_ID"],
                    "Interaction_Type": "Wishlist",
                    "Timestamp": session_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Session_ID": session_id,
                    "Search_Keyword": "",
                    "Category": p["Category"],
                    "Device": device,
                    "Time_Spent": random.randint(5, 30),
                    "Product_Viewed": 1,
                    "Added_To_Wishlist": 1,
                    "Added_To_Cart": 0,
                    "Purchased": 0,
                    "Rating_Given": 0
                })
                interaction_id += 1
                
            # Cart decision: Higher if time spent > 60 or in preferred category or high popularity
            cart_prob = 0.35 if (p["Category"] == pref_cat or time_spent > 80) else 0.15
            is_cart = 1 if (random.random() < cart_prob) else 0
            
            if is_cart:
                interactions.append({
                    "Interaction_ID": f"INT_{interaction_id:07d}",
                    "Customer_ID": cust_id,
                    "Product_ID": p["Product_ID"],
                    "Interaction_Type": "Cart",
                    "Timestamp": session_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Session_ID": session_id,
                    "Search_Keyword": "",
                    "Category": p["Category"],
                    "Device": device,
                    "Time_Spent": random.randint(20, 90),
                    "Product_Viewed": 1,
                    "Added_To_Wishlist": is_wishlist,
                    "Added_To_Cart": 1,
                    "Purchased": 0,
                    "Rating_Given": 0
                })
                interaction_id += 1
                
                # Purchase decision: cart leads to purchase with 50-60% probability
                purchase_prob = 0.58 if (p["Rating"] >= 4.2 or p["Category"] == pref_cat) else 0.38
                if random.random() < purchase_prob:
                    # An order is created!
                    order_id_counter += 1
                    curr_order_id = f"SC-2026-{order_id_counter:06d}"
                    pay_method = random.choice(PAYMENT_METHODS)
                    
                    # Target product purchase record
                    qty = 1 if p["Final_Price"] > 5000 else random.choice([1, 1, 1, 2])
                    tot_amt = round(p["Final_Price"] * qty, 2)
                    
                    purchases.append({
                        "Purchase_ID": f"PUR_{purchase_id:06d}",
                        "Customer_ID": cust_id,
                        "Product_ID": p["Product_ID"],
                        "Order_ID": curr_order_id,
                        "Purchase_Date": session_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "Quantity": qty,
                        "Unit_Price": p["Price"],
                        "Discount": p["Discount"],
                        "Total_Amount": tot_amt,
                        "Payment_Method": pay_method,
                        "Category": p["Category"],
                        "Device": device
                    })
                    purchase_id += 1
                    
                    interactions.append({
                        "Interaction_ID": f"INT_{interaction_id:07d}",
                        "Customer_ID": cust_id,
                        "Product_ID": p["Product_ID"],
                        "Interaction_Type": "Purchase",
                        "Timestamp": session_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "Session_ID": session_id,
                        "Search_Keyword": "",
                        "Category": p["Category"],
                        "Device": device,
                        "Time_Spent": random.randint(60, 300),
                        "Product_Viewed": 1,
                        "Added_To_Wishlist": is_wishlist,
                        "Added_To_Cart": 1,
                        "Purchased": 1,
                        "Rating_Given": 0
                    })
                    interaction_id += 1
                    
                    # Rating after purchase (50% give a rating)
                    if random.random() < 0.50:
                        rating_val = int(np.clip(np.random.normal(loc=p["Rating"], scale=0.6), 1, 5))
                        review_samples = {
                            5: ["Exceptional quality, surpassed expectations!", "Absolutely loved this! Highly recommended.", "Top notch performance and build."],
                            4: ["Good product, very satisfied with the purchase.", "Value for money. Delivery was fast.", "Works as described, pleased with quality."],
                            3: ["Decent purchase. Average experience.", "Meets basic expectations.", "Okay for the price point."],
                            2: ["Could have been better. Material feels average.", "Slightly disappointed with specs."],
                            1: ["Not as expected. Would not recommend.", "Poor quality experience."]
                        }
                        review_text = random.choice(review_samples.get(rating_val, ["Good."]))
                        
                        ratings.append({
                            "Rating_ID": f"RAT_{rating_id:06d}",
                            "Customer_ID": cust_id,
                            "Product_ID": p["Product_ID"],
                            "Rating": rating_val,
                            "Review_Text": review_text,
                            "Rating_Date": (session_time + datetime.timedelta(days=random.randint(2, 7))).strftime("%Y-%m-%d %H:%M:%S")
                        })
                        rating_id += 1
                        
                        # Add Rating interaction
                        interactions.append({
                            "Interaction_ID": f"INT_{interaction_id:07d}",
                            "Customer_ID": cust_id,
                            "Product_ID": p["Product_ID"],
                            "Interaction_Type": "Rating",
                            "Timestamp": (session_time + datetime.timedelta(days=random.randint(2, 7))).strftime("%Y-%m-%d %H:%M:%S"),
                            "Session_ID": session_id,
                            "Search_Keyword": "",
                            "Category": p["Category"],
                            "Device": device,
                            "Time_Spent": random.randint(30, 90),
                            "Product_Viewed": 1,
                            "Added_To_Wishlist": is_wishlist,
                            "Added_To_Cart": 1,
                            "Purchased": 1,
                            "Rating_Given": rating_val
                        })
                        interaction_id += 1
                        
                    # -------------------------------------------------------------
                    # FREQUENTLY BOUGHT TOGETHER (BASKET CO-OCCURRENCE)
                    # If user purchases a product with known complementary accessories,
                    # frequently bundle them in the same order!
                    # -------------------------------------------------------------
                    comp_cats = co_occurrence_map.get(p["Category"], [])
                    if comp_cats and random.random() < 0.65:
                        comp_cat = random.choice(comp_cats)
                        if comp_cat in products_by_cat and len(products_by_cat[comp_cat]) > 0:
                            comp_prod = random.choice(products_by_cat[comp_cat])
                            if comp_prod["Product_ID"] != p["Product_ID"]:
                                c_qty = 1
                                purchases.append({
                                    "Purchase_ID": f"PUR_{purchase_id:06d}",
                                    "Customer_ID": cust_id,
                                    "Product_ID": comp_prod["Product_ID"],
                                    "Order_ID": curr_order_id,
                                    "Purchase_Date": session_time.strftime("%Y-%m-%d %H:%M:%S"),
                                    "Quantity": c_qty,
                                    "Unit_Price": comp_prod["Price"],
                                    "Discount": comp_prod["Discount"],
                                    "Total_Amount": round(comp_prod["Final_Price"] * c_qty, 2),
                                    "Payment_Method": pay_method,
                                    "Category": comp_prod["Category"],
                                    "Device": device
                                })
                                purchase_id += 1
                                
                                # Add Purchase interaction for accessory
                                interactions.append({
                                    "Interaction_ID": f"INT_{interaction_id:07d}",
                                    "Customer_ID": cust_id,
                                    "Product_ID": comp_prod["Product_ID"],
                                    "Interaction_Type": "Purchase",
                                    "Timestamp": session_time.strftime("%Y-%m-%d %H:%M:%S"),
                                    "Session_ID": session_id,
                                    "Search_Keyword": "",
                                    "Category": comp_prod["Category"],
                                    "Device": device,
                                    "Time_Spent": random.randint(45, 120),
                                    "Product_Viewed": 1,
                                    "Added_To_Wishlist": 0,
                                    "Added_To_Cart": 1,
                                    "Purchased": 1,
                                    "Rating_Given": 0
                                })
                                interaction_id += 1

    df_interactions = pd.DataFrame(interactions)
    df_purchases = pd.DataFrame(purchases)
    df_searches = pd.DataFrame(searches)
    df_ratings = pd.DataFrame(ratings)
    
    int_path = os.path.join(DATA_DIR, "interactions.csv")
    pur_path = os.path.join(DATA_DIR, "purchases.csv")
    srch_path = os.path.join(DATA_DIR, "search_history.csv")
    rat_path = os.path.join(DATA_DIR, "ratings.csv")
    
    df_interactions.to_csv(int_path, index=False)
    df_purchases.to_csv(pur_path, index=False)
    df_searches.to_csv(srch_path, index=False)
    df_ratings.to_csv(rat_path, index=False)
    
    print(f"Interactions saved to {int_path}: {len(df_interactions)} records.")
    print(f"Purchases saved to {pur_path}: {len(df_purchases)} records.")
    print(f"Search history saved to {srch_path}: {len(df_searches)} records.")
    print(f"Ratings saved to {rat_path}: {len(df_ratings)} records.")
    
    return df_interactions, df_purchases, df_searches, df_ratings

def main():
    print("=== Starting SmartCart Synthetic Data Generation ===")
    df_products = generate_products()
    df_customers = generate_customers(3000)
    generate_behavioral_data(df_customers, df_products, min_interactions=32000)
    print("=== Synthetic Data Generation Complete! ===")

if __name__ == "__main__":
    main()
