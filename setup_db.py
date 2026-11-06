"""
build_merged_database.py

Creates store.db with a single, unified `products` table that merges:
  1. The original hardcoded product list (honey, oils, nuts, grains, etc.)
  2. The rows from shopping_products_dataset.csv

Also creates commerce tables for customers, sales, suppliers, inventory
movements, product-supplier links, reviews, and orders.

Run:
    python setup_db.py
"""

import os
import sqlite3
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "store.db")
CSV_PATH = os.path.join(os.path.dirname(__file__), "shopping_products_dataset.csv")


def create_schema(conn):
    # Unified products table. Columns beyond the "core" set (name, category,
    # price, description, is_organic) come from the CSV and are nullable so
    # the hardcoded rows can still be inserted without them.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            source_id TEXT,              -- original CSV product_id (e.g. P100001), NULL for hardcoded rows
            name TEXT NOT NULL,
            brand TEXT,
            category TEXT,
            subcategory TEXT,
            price REAL,                  -- final/selling price
            mrp REAL,                    -- original CSV list price (NULL for hardcoded rows)
            discount_percent REAL,
            quantity TEXT,
            description TEXT,
            is_organic INTEGER DEFAULT 0,
            veg INTEGER,
            avg_rating REAL,
            stock_qty INTEGER,
            image_url TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            rating REAL,
            reviewer_name TEXT,
            review_text TEXT,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            ordered_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            city TEXT,
            state TEXT,
            country TEXT NOT NULL DEFAULT 'USA',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            contact_name TEXT,
            email TEXT,
            phone TEXT,
            city TEXT,
            country TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS product_suppliers (
            product_id INTEGER NOT NULL,
            supplier_id INTEGER NOT NULL,
            supplier_sku TEXT,
            cost_price REAL,
            PRIMARY KEY (product_id, supplier_id),
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            unit_price REAL NOT NULL CHECK (unit_price >= 0),
            total_amount REAL NOT NULL CHECK (total_amount >= 0),
            sold_at TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'completed',
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS inventory_movements (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            quantity_change INTEGER NOT NULL,
            movement_type TEXT NOT NULL CHECK (
                movement_type IN ('received', 'sold', 'adjustment')
            ),
            occurred_at TEXT NOT NULL,
            note TEXT,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)


def sample_customers():
    return [
        (1, "Ava", "Patel", "ava.patel@example.com", "555-0101", "Austin", "Texas", "USA"),
        (2, "Noah", "Kim", "noah.kim@example.com", "555-0102", "Seattle", "Washington", "USA"),
        (3, "Mia", "Garcia", "mia.garcia@example.com", "555-0103", "Denver", "Colorado", "USA"),
        (4, "Liam", "Brown", "liam.brown@example.com", "555-0104", "Boston", "Massachusetts", "USA"),
        (5, "Zoe", "Wilson", "zoe.wilson@example.com", "555-0105", "Portland", "Oregon", "USA"),
    ]


def sample_suppliers():
    return [
        (1, "Golden Fields Cooperative", "Elena Ruiz", "contact@goldenfields.example", "555-0201", "Sacramento", "USA"),
        (2, "Northstar Organics", "David Chen", "sales@northstar.example", "555-0202", "Seattle", "USA"),
        (3, "Mediterranean Harvest", "Sofia Costa", "hello@medharvest.example", "555-0203", "Lisbon", "Portugal"),
        (4, "Mountain Grain Works", "Ethan Miller", "orders@mountaingrain.example", "555-0204", "Denver", "USA"),
    ]


def sample_product_suppliers():
    return [
        (1, 1, "GF-HNY-001", 8.25),
        (3, 1, "GF-HNY-003", 17.50),
        (9, 3, "MH-OIL-009", 9.10),
        (13, 2, "NO-NUT-013", 6.25),
        (17, 4, "MG-GRN-017", 5.40),
        (21, 2, "NO-TEA-021", 7.80),
    ]


def sample_sales():
    # (id, customer_id, product_id, quantity, unit_price, total, sold_at, payment_method, status)
    return [
        (1, 1, 1, 2, 14.99, 29.98, "2026-09-01 10:15:00", "card", "completed"),
        (2, 2, 9, 1, 16.99, 16.99, "2026-09-02 14:20:00", "wallet", "completed"),
        (3, 3, 17, 3, 10.99, 32.97, "2026-09-03 09:05:00", "card", "completed"),
        (4, 4, 13, 1, 11.99, 11.99, "2026-09-04 16:45:00", "cash", "completed"),
        (5, 5, 21, 2, 12.99, 25.98, "2026-09-05 11:30:00", "card", "completed"),
        (6, 1, 3, 1, 29.99, 29.99, "2026-09-06 13:10:00", "wallet", "completed"),
        (7, 2, 18, 4, 5.49, 21.96, "2026-09-07 08:40:00", "card", "completed"),
        (8, 3, 25, 2, 9.99, 19.98, "2026-09-08 17:25:00", "card", "completed"),
        (9, 4, 29, 3, 4.99, 14.97, "2026-09-09 12:00:00", "wallet", "completed"),
        (10, 5, 23, 1, 16.99, 16.99, "2026-09-10 07:55:00", "card", "completed"),
    ]


def sample_inventory_movements():
    return [
        (1, 1, 20, "received", "2026-08-28 09:00:00", "Opening stock"),
        (2, 1, -2, "sold", "2026-09-01 10:15:00", "Sale 1"),
        (3, 9, 15, "received", "2026-08-29 09:00:00", "Supplier delivery"),
        (4, 9, -1, "sold", "2026-09-02 14:20:00", "Sale 2"),
        (5, 17, 12, "received", "2026-08-30 09:00:00", "Supplier delivery"),
        (6, 17, -3, "sold", "2026-09-03 09:05:00", "Sale 3"),
    ]


def hardcoded_products():
    # (id, name, category, price, description, is_organic)
    return [
        # --- Honey (8) ---
        (1,  "Organic Raw Honey",            "honey",        14.99, "Pure organic raw honey, unfiltered and cold-pressed",                1),
        (2,  "Wildflower Honey",             "honey",        12.99, "Natural wildflower honey from local beekeepers",                     0),
        (3,  "Organic Manuka Honey",         "honey",        29.99, "Premium organic Manuka honey from New Zealand",                      1),
        (4,  "Clover Honey",                 "honey",         8.99, "Classic clover honey, smooth and sweet",                             0),
        (5,  "Organic Buckwheat Honey",      "honey",        18.99, "Dark and robust organic buckwheat honey, antioxidant-rich",          1),
        (6,  "Orange Blossom Honey",         "honey",        15.99, "Light and floral orange blossom honey",                              0),
        (7,  "Organic Acacia Honey",         "honey",        17.99, "Light and mild organic acacia honey, low glycemic index",            1),
        (8,  "Creamed Honey",                "honey",        11.99, "Smooth creamed honey with spreadable texture",                       0),
        # --- Oils (4) ---
        (9,  "Organic Extra Virgin Olive Oil","oil",         16.99, "Cold-pressed organic EVOO from Mediterranean olives",               1),
        (10, "Coconut Oil",                  "oil",          12.49, "Refined coconut oil, great for high-heat cooking",                   0),
        (11, "Organic Flaxseed Oil",         "oil",          14.99, "Cold-pressed organic flaxseed oil, rich in omega-3",                 1),
        (12, "Avocado Oil",                  "oil",          18.99, "Cold-pressed avocado oil, high smoke point",                         0),
        # --- Nuts & Seeds (4) ---
        (13, "Organic Almonds",              "nuts",         11.99, "Raw organic almonds, unsalted, non-GMO certified",                   1),
        (14, "Roasted Cashews",              "nuts",          9.99, "Lightly salted dry-roasted cashews",                                 0),
        (15, "Organic Chia Seeds",           "seeds",         8.49, "Organic black chia seeds, high in fiber and omega-3",                1),
        (16, "Mixed Nuts",                   "nuts",         13.99, "Premium mix of walnuts, pecans, almonds and Brazil nuts",            0),
        # --- Grains & Cereals (4) ---
        (17, "Organic Quinoa",               "grains",       10.99, "Organic white quinoa, complete protein, gluten-free",                1),
        (18, "Rolled Oats",                  "grains",        5.49, "Whole grain rolled oats, great for porridge and baking",             0),
        (19, "Organic Brown Rice",           "grains",        7.99, "Long-grain organic brown rice, naturally gluten-free",               1),
        (20, "Steel-Cut Oats",               "grains",        6.99, "Traditional steel-cut oats, low GI, hearty texture",                 0),
        # --- Tea & Coffee (4) ---
        (21, "Organic Green Tea",            "tea",          12.99, "Japanese organic sencha green tea, 50 bags",                         1),
        (22, "Chamomile Tea",                "tea",           8.99, "Dried chamomile flowers, caffeine-free, soothing",                   0),
        (23, "Organic Ethiopian Coffee",     "coffee",       16.99, "Single-origin organic Arabica, medium roast whole bean",             1),
        (24, "Dark Roast Espresso Blend",    "coffee",       14.49, "Bold dark roast espresso blend, ground",                             0),
        # --- Snacks (4) ---
        (25, "Organic Granola",              "snacks",        9.99, "Organic oat granola with honey, almonds and dried cranberries",      1),
        (26, "Rice Cakes",                   "snacks",        4.49, "Lightly salted brown rice cakes, low calorie",                       0),
        (27, "Organic Dried Mango",          "snacks",        7.99, "Unsweetened organic dried mango slices, no preservatives",           1),
        (28, "Trail Mix",                    "snacks",        8.49, "Classic trail mix with raisins, M&Ms, peanuts and sunflower seeds",  0),
        # --- Dairy Alternatives (4) ---
        (29, "Organic Almond Milk",          "dairy-alt",     4.99, "Unsweetened organic almond milk, fortified with calcium",            1),
        (30, "Oat Milk",                     "dairy-alt",     4.49, "Barista-style oat milk, great for coffee",                           0),
        (31, "Organic Coconut Milk",         "dairy-alt",     3.99, "Full-fat organic coconut milk, great for curries",                   1),
        (32, "Soy Milk",                     "dairy-alt",     3.49, "Unsweetened soy milk, high protein",                                 0),
    ]


def hardcoded_reviews():
    return [
        (1, 5.0, "Alice",   "Amazing honey! Best I've ever tried."),
        (1, 4.0, "Bob",     "Good quality, will buy again."),
        (1, 5.0, "Carol",   "Excellent raw flavor, very pure."),
        (1, 4.5, "Dave",    "Very good, love that it's unfiltered."),
        (2, 4.0, "Eve",     "Decent honey for the price."),
        (2, 3.5, "Frank",   "Average, nothing special."),
        (2, 4.0, "Grace",   "Good everyday honey."),
        (3, 5.0, "Henry",   "Worth every penny, incredible quality."),
        (3, 4.5, "Iris",    "Excellent antibacterial properties."),
        (3, 5.0, "Jack",    "Best honey I have ever tasted."),
        (4, 3.5, "Kate",    "Okay for cooking, nothing fancy."),
        (4, 3.5, "Leo",     "Nothing special, pretty generic."),
        (4, 3.5, "Mia",     "Average clover honey."),
        (5, 5.0, "Noah",    "Rich bold flavor, great in tea."),
        (5, 4.0, "Olivia",  "Good strong honey, unique taste."),
        (5, 5.0, "Paul",    "Love the dark color and depth."),
        (5, 4.5, "Quinn",   "Great organic option at this price."),
        (6, 4.0, "Rachel",  "Nice floral flavor."),
        (6, 4.5, "Sam",     "Lovely and delicate."),
        (6, 4.0, "Tina",    "Good for baking."),
        (7, 5.0, "Uma",     "Perfect mild flavor, love it!"),
        (7, 4.5, "Victor",  "Excellent light honey."),
        (7, 4.5, "Wendy",   "Great product, very pure taste."),
        (7, 5.0, "Xavier",  "Wonderful, highly recommend."),
        (8, 4.0, "Yvonne",  "Nice spreadable texture."),
        (8, 4.0, "Zack",    "Good on toast."),
        (8, 4.0, "Amy",     "Decent creamed honey."),
        (9,  5.0, "Brian",  "Best olive oil I've used, very fresh."),
        (9,  4.5, "Clara",  "Great flavor, organic certified."),
        (9,  4.5, "Derek",  "Excellent quality, love it."),
        (10, 4.0, "Elena",  "Good for frying, neutral taste."),
        (10, 3.5, "Felix",  "Does the job, nothing exciting."),
        (10, 3.5, "Gina",   "Decent but slightly greasy."),
        (11, 5.0, "Harry",  "Great for smoothies, very fresh."),
        (11, 4.0, "Isla",   "Good omega-3 source, mild flavor."),
        (11, 4.5, "James",  "Love this for salad dressings."),
        (12, 4.5, "Karen",  "Excellent smoke point, tastes great."),
        (12, 4.0, "Liam",   "Good all-purpose oil."),
        (12, 4.5, "Maya",   "Great for cooking and salads."),
        (13, 5.0, "Nate",   "Crunchy and fresh, great snack."),
        (13, 4.5, "Olivia", "Love that they're organic and raw."),
        (13, 4.5, "Peter",  "Perfect size, very fresh."),
        (13, 5.0, "Rita",   "Best almonds I've bought online."),
        (14, 4.0, "Steve",  "Good cashews, nice crunch."),
        (14, 4.0, "Tara",   "Tasty but slightly over-salted."),
        (14, 4.0, "Ursula", "Good value for the quantity."),
        (15, 4.5, "Vince",  "Easy to add to smoothies, love it."),
        (15, 4.5, "Wanda",  "Great fiber source, very fresh."),
        (15, 4.5, "Xena",   "Good quality organic chia seeds."),
        (16, 4.0, "Yuri",   "Good mix, well-balanced variety."),
        (16, 3.5, "Zara",   "A bit too many peanuts for my taste."),
        (16, 4.0, "Alex",   "Nice mix for snacking."),
        (16, 3.5, "Blake",  "Would prefer fewer raisins."),
        (17, 5.0, "Chloe",  "Cooks perfectly, great nutty flavor."),
        (17, 4.5, "Dylan",  "Excellent protein content, love it."),
        (17, 4.5, "Ella",   "Best quinoa I've tried."),
        (18, 4.5, "Finn",   "Great oats, cook quickly and evenly."),
        (18, 4.0, "Gabi",   "Good quality, nice texture."),
        (18, 4.5, "Hugo",   "Reliable everyday oats."),
        (19, 4.5, "Irene",  "Nice chewy texture, great organic choice."),
        (19, 4.5, "Jake",   "Good quality, cooks evenly."),
        (19, 4.5, "Kara",   "Love the organic certification."),
        (20, 4.0, "Lars",   "Great texture, a bit longer to cook."),
        (20, 3.5, "Mona",   "Takes forever to cook but tastes good."),
        (20, 4.0, "Ned",    "Hearty and filling."),
        (21, 5.0, "Opal",   "Delicate flavor, very smooth."),
        (21, 4.5, "Phil",   "Best green tea I've had, very fresh."),
        (21, 4.5, "Quinn",  "Great quality, calming and tasty."),
        (22, 4.0, "Rose",   "Very soothing before bed."),
        (22, 4.5, "Seth",   "Lovely floral notes, very relaxing."),
        (22, 4.0, "Tess",   "Good chamomile, nice and mild."),
        (23, 5.0, "Uri",    "Best coffee I've ever brewed at home."),
        (23, 4.5, "Vera",   "Amazing single-origin flavor."),
        (23, 4.5, "Will",   "Very smooth with great aroma."),
        (23, 5.0, "Xara",   "Exceptional quality, worth every penny."),
        (24, 4.0, "Yael",   "Strong and bold, perfect espresso."),
        (24, 4.0, "Zion",   "Good dark roast, consistent grind."),
        (24, 4.0, "Abe",    "Solid everyday espresso blend."),
        (25, 4.5, "Beth",   "Delicious and not too sweet."),
        (25, 4.5, "Cole",   "Great texture, love the almonds."),
        (25, 4.5, "Dana",   "My go-to breakfast granola."),
        (26, 4.0, "Earl",   "Light and crispy, good for dieting."),
        (26, 3.5, "Faye",   "A bit bland but does the job."),
        (26, 4.0, "Glen",   "Good value, decent snack."),
        (27, 5.0, "Hope",   "So sweet and chewy, love these!"),
        (27, 4.5, "Ivan",   "Great that there's no added sugar."),
        (27, 4.5, "Jade",   "Perfect snack, very natural taste."),
        (28, 4.0, "Kent",   "Good mix, great for hiking."),
        (28, 3.5, "Luna",   "Too many M&Ms, prefer less candy."),
        (28, 3.5, "Marc",   "Decent but not my favorite mix."),
        (29, 4.5, "Nina",   "Great in coffee, smooth texture."),
        (29, 4.5, "Omar",   "Love the organic certification."),
        (29, 4.5, "Pam",    "Tastes great and not too thin."),
        (30, 4.5, "Rex",    "Perfect for lattes, froths well."),
        (30, 4.0, "Sara",   "Good oat milk, slightly sweet."),
        (30, 4.5, "Tom",    "Best barista oat milk I've tried."),
        (31, 4.5, "Una",    "Creamy and rich, great for curries."),
        (31, 4.5, "Vito",   "Full fat and delicious."),
        (31, 4.5, "Wren",   "Perfect coconut milk, great quality."),
        (32, 4.0, "Xio",    "Good protein content, mild flavor."),
        (32, 3.5, "Yosef",  "Slightly thin but good for cereal."),
        (32, 3.5, "Zola",   "Decent soy milk, nothing special."),
    ]


def load_csv_products(csv_path, start_id):
    """Read the CSV and map its columns onto the unified products schema."""
    df = pd.read_csv(csv_path)

    # Normalize "True"/"False" text -> 1/0
    for col in ["is_organic", "veg"]:
        if col in df.columns:
            df[col] = (
                df[col].astype(str).str.strip().str.lower()
                .map({"true": 1, "false": 0})
            )

    rows = []
    next_id = start_id
    for _, r in df.iterrows():
        rows.append((
            next_id,                          # id
            r.get("product_id"),              # source_id
            r.get("product_name"),            # name
            r.get("brand"),                    # brand
            r.get("category"),                 # category
            r.get("subcategory"),               # subcategory
            r.get("final_price"),               # price
            r.get("mrp"),                       # mrp
            r.get("discount_percent"),          # discount_percent
            r.get("quantity"),                  # quantity
            r.get("description"),               # description
            int(r.get("is_organic")) if pd.notna(r.get("is_organic")) else 0,  # is_organic
            int(r.get("veg")) if pd.notna(r.get("veg")) else None,             # veg
            r.get("avg_rating"),                 # avg_rating
            r.get("stock_qty"),                  # stock_qty
            r.get("image_url"),                  # image_url
        ))
        next_id += 1
    return rows


def build_database():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    create_schema(conn)

    # Clear tables so this script can be re-run cleanly
    cur.execute("DELETE FROM orders")
    cur.execute("DELETE FROM reviews")
    cur.execute("DELETE FROM sales")
    cur.execute("DELETE FROM inventory_movements")
    cur.execute("DELETE FROM product_suppliers")
    cur.execute("DELETE FROM products")
    cur.execute("DELETE FROM customers")
    cur.execute("DELETE FROM suppliers")

    # 1. Insert hardcoded products (ids 1-32), core columns only
    hc_products = hardcoded_products()
    cur.executemany(
        """INSERT INTO products
           (id, name, category, price, description, is_organic)
           VALUES (?, ?, ?, ?, ?, ?)""",
        hc_products,
    )

    # 2. Insert CSV products, continuing ids after the hardcoded ones
    next_id = max(p[0] for p in hc_products) + 1
    csv_products = load_csv_products(CSV_PATH, next_id)
    cur.executemany(
        """INSERT INTO products
           (id, source_id, name, brand, category, subcategory, price, mrp,
            discount_percent, quantity, description, is_organic, veg,
            avg_rating, stock_qty, image_url)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        csv_products,
    )

    # 3. Insert original reviews (for products 1-32)
    cur.executemany(
        "INSERT INTO reviews (product_id, rating, reviewer_name, review_text) VALUES (?, ?, ?, ?)",
        hardcoded_reviews(),
    )

    cur.executemany(
        """INSERT INTO customers
           (id, first_name, last_name, email, phone, city, state, country)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        sample_customers(),
    )
    cur.executemany(
        """INSERT INTO suppliers
           (id, name, contact_name, email, phone, city, country)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        sample_suppliers(),
    )
    cur.executemany(
        """INSERT INTO product_suppliers
           (product_id, supplier_id, supplier_sku, cost_price)
           VALUES (?, ?, ?, ?)""",
        sample_product_suppliers(),
    )
    cur.executemany(
        """INSERT INTO sales
           (id, customer_id, product_id, quantity, unit_price, total_amount,
            sold_at, payment_method, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        sample_sales(),
    )
    cur.executemany(
        """INSERT INTO inventory_movements
           (id, product_id, quantity_change, movement_type, occurred_at, note)
           VALUES (?, ?, ?, ?, ?, ?)""",
        sample_inventory_movements(),
    )

    conn.commit()

    total = cur.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    print(f"Database created at: {DB_PATH}")
    print(f"Total products merged: {total} "
          f"({len(hc_products)} hardcoded + {len(csv_products)} from CSV)")
    print(f"Customers: {len(sample_customers())}; sales: {len(sample_sales())}; "
          f"suppliers: {len(sample_suppliers())}")

    conn.close()


if __name__ == "__main__":
    build_database()
