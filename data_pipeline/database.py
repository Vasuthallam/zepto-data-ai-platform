import sqlite3
import pandas as pd

CSV_FILE = "data_pipeline/cleaned_books.csv"
DATABASE_FILE = "data_pipeline/books.db"


# ============================================================
# 1. LOAD CLEANED DATA
# ============================================================

df = pd.read_csv(CSV_FILE)

print("Loaded rows:", len(df))


# ============================================================
# 2. CONNECT TO SQLITE
# ============================================================

connection = sqlite3.connect(DATABASE_FILE)

cursor = connection.cursor()


# ============================================================
# 3. CREATE CATEGORIES TABLE
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE
)
""")


# ============================================================
# 4. CREATE BOOKS TABLE
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price_gbp REAL NOT NULL,
    price_inr REAL NOT NULL,
    rating INTEGER NOT NULL,
    in_stock INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
)
""")


# ============================================================
# 5. INSERT CATEGORIES
# ============================================================

for category in df["category"].dropna().unique():

    cursor.execute(
        """
        INSERT OR IGNORE INTO categories (category_name)
        VALUES (?)
        """,
        (category,)
    )


# ============================================================
# 6. INSERT BOOKS
# ============================================================

for _, row in df.iterrows():

    cursor.execute(
        """
        SELECT category_id
        FROM categories
        WHERE category_name = ?
        """,
        (row["category"],)
    )

    category_result = cursor.fetchone()

    category_id = category_result[0]

    cursor.execute(
        """
        INSERT INTO books (
            title,
            price_gbp,
            price_inr,
            rating,
            in_stock,
            category_id
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            row["title"],
            row["price_gbp"],
            row["price_inr"],
            row["rating"],
            int(row["in_stock"]),
            category_id
        )
    )


# ============================================================
# 7. SAVE DATABASE
# ============================================================

connection.commit()


# ============================================================
# 8. VERIFY DATABASE
# ============================================================

print()
print("========================================")
print("DATABASE CREATED")
print("========================================")

cursor.execute("SELECT COUNT(*) FROM categories")
category_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM books")
book_count = cursor.fetchone()[0]

print("Number of categories:", category_count)
print("Number of books:", book_count)


# ============================================================
# 9. SHOW SAMPLE JOIN
# ============================================================

print()
print("Sample JOIN result:")

cursor.execute("""
SELECT
    b.book_id,
    b.title,
    b.price_gbp,
    b.price_inr,
    b.rating,
    b.in_stock,
    c.category_name
FROM books b
JOIN categories c
    ON b.category_id = c.category_id
LIMIT 10
""")

rows = cursor.fetchall()

for row in rows:
    print(row)


# ============================================================
# 10. CLOSE DATABASE
# ============================================================

connection.close()

print()
print("Database saved to:")
print(DATABASE_FILE)