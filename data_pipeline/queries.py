import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# 1. FILE PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_FILE = BASE_DIR / "books.db"
OUTPUT_FILE = BASE_DIR / "query_results.txt"


# ============================================================
# 2. CONNECT TO DATABASE
# ============================================================

connection = sqlite3.connect(DATABASE_FILE)

cursor = connection.cursor()

print("=" * 70)
print("BOOKS DATABASE QUERY ANALYSIS")
print("=" * 70)
print()

print("Database:")
print(DATABASE_FILE)
print()


# ============================================================
# 3. LOAD DATA INTO PANDAS
# ============================================================

books_df = pd.read_sql_query(
    """
    SELECT
        book_id,
        title,
        price_gbp,
        price_inr,
        rating,
        in_stock,
        category_id
    FROM books
    """,
    connection
)

categories_df = pd.read_sql_query(
    """
    SELECT
        category_id,
        category_name
    FROM categories
    """,
    connection
)


# ============================================================
# 4. OUTPUT STORAGE
# ============================================================

all_output = []


def print_and_save(text=""):
    """Print text and also save it for query_results.txt."""
    print(text)
    all_output.append(str(text))


def print_dataframe(df):
    """Print a dataframe and save its string representation."""
    text = df.to_string(index=False)
    print(text)
    all_output.append(text)


# ============================================================
# 5. DATABASE INFORMATION
# ============================================================

print_and_save("DATABASE INFORMATION")
print_and_save("=" * 70)

cursor.execute("SELECT COUNT(*) FROM books")
book_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM categories")
category_count = cursor.fetchone()[0]

print_and_save(f"Total books: {book_count}")
print_and_save(f"Total categories: {category_count}")


# ============================================================
# 6. QUERY 1 - FIRST 10 BOOKS
# ============================================================

print_and_save("")
print_and_save("=" * 70)
print_and_save("QUERY 1 - FIRST 10 BOOKS")
print_and_save("=" * 70)

sql_result = pd.read_sql_query(
    """
    SELECT
        book_id,
        title,
        price_gbp,
        price_inr,
        rating,
        in_stock,
        category_id
    FROM books
    ORDER BY book_id
    LIMIT 10
    """,
    connection
)

print_dataframe(sql_result)


# ============================================================
# 7. QUERY 2 - BOOKS WITH RATING 5
# ============================================================

print_and_save("")
print_and_save("=" * 70)
print_and_save("QUERY 2 - FIVE STAR BOOKS")
print_and_save("=" * 70)

five_star_books = pd.read_sql_query(
    """
    SELECT
        title,
        price_gbp,
        price_inr,
        rating,
        in_stock
    FROM books
    WHERE rating = 5
    ORDER BY title
    """,
    connection
)

print_dataframe(five_star_books)


# ============================================================
# 8. QUERY 3 - BOOKS ABOVE AVERAGE PRICE
# ============================================================

print_and_save("")
print_and_save("=" * 70)
print_and_save("QUERY 3 - BOOKS ABOVE AVERAGE GBP PRICE")
print_and_save("=" * 70)

above_average = pd.read_sql_query(
    """
    SELECT
        title,
        price_gbp,
        rating
    FROM books
    WHERE price_gbp > (
        SELECT AVG(price_gbp)
        FROM books
    )
    ORDER BY price_gbp DESC
    """,
    connection
)

print_dataframe(above_average)


# ============================================================
# 9. QUERY 4 - TOP 10 MOST EXPENSIVE BOOKS
# ============================================================

print_and_save("")
print_and_save("=" * 70)
print_and_save("QUERY 4 - TOP 10 MOST EXPENSIVE BOOKS")
print_and_save("=" * 70)

expensive_books = pd.read_sql_query(
    """
    SELECT
        title,
        price_gbp,
        price_inr,
        rating
    FROM books
    ORDER BY price_gbp DESC
    LIMIT 10
    """,
    connection
)

print_dataframe(expensive_books)


# ============================================================
# 10. QUERY 5 - CATEGORY SUMMARY
# ============================================================

print_and_save("")
print_and_save("=" * 70)
print_and_save("QUERY 5 - CATEGORY SUMMARY")
print_and_save("=" * 70)

category_summary = pd.read_sql_query(
    """
    SELECT
        c.category_name,
        COUNT(b.book_id) AS book_count,
        ROUND(AVG(b.price_gbp), 2) AS average_price_gbp,
        ROUND(AVG(b.rating), 2) AS average_rating
    FROM books b
    JOIN categories c
        ON b.category_id = c.category_id
    GROUP BY c.category_id, c.category_name
    ORDER BY book_count DESC, c.category_name
    """,
    connection
)

print_dataframe(category_summary)


# ============================================================
# 11. QUERY 6 - IN-STOCK BOOKS
# ============================================================

print_and_save("")
print_and_save("=" * 70)
print_and_save("QUERY 6 - IN-STOCK BOOKS")
print_and_save("=" * 70)

stock_summary = pd.read_sql_query(
    """
    SELECT
        in_stock,
        COUNT(*) AS book_count
    FROM books
    GROUP BY in_stock
    ORDER BY in_stock DESC
    """,
    connection
)

print_dataframe(stock_summary)


# ============================================================
# 12. QUERY 7 - CATEGORY WITH HIGHEST AVERAGE PRICE
# ============================================================

print_and_save("")
print_and_save("=" * 70)
print_and_save("QUERY 7 - CATEGORY WITH HIGHEST AVERAGE PRICE")
print_and_save("=" * 70)

highest_category = pd.read_sql_query(
    """
    SELECT
        c.category_name,
        ROUND(AVG(b.price_gbp), 2) AS average_price_gbp
    FROM books b
    JOIN categories c
        ON b.category_id = c.category_id
    GROUP BY c.category_id, c.category_name
    ORDER BY average_price_gbp DESC
    LIMIT 1
    """,
    connection
)

print_dataframe(highest_category)


# ============================================================
# 13. QUERY 8 - TOP RATED BOOKS
# ============================================================

print_and_save("")
print_and_save("=" * 70)
print_and_save("QUERY 8 - TOP RATED BOOKS")
print_and_save("=" * 70)

top_rated = pd.read_sql_query(
    """
    SELECT
        title,
        price_gbp,
        rating,
        in_stock
    FROM books
    WHERE rating = 5
    ORDER BY price_gbp DESC
    LIMIT 10
    """,
    connection
)

print_dataframe(top_rated)


# ============================================================
# 14. QUERY 9 - SQL JOIN
# ============================================================

print_and_save("")
print_and_save("=" * 70)
print_and_save("QUERY 9 - SQL JOIN")
print_and_save("=" * 70)

sql_join = pd.read_sql_query(
    """
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
    ORDER BY b.book_id
    """,
    connection
)

print_and_save(f"SQL JOIN rows: {len(sql_join)}")
print_and_save("")
print_dataframe(sql_join.head(10))


# ============================================================
# 15. QUERY 10 - PANDAS MERGE
# ============================================================

print_and_save("")
print_and_save("=" * 70)
print_and_save("QUERY 10 - PANDAS MERGE")
print_and_save("=" * 70)

pandas_merge = books_df.merge(
    categories_df,
    on="category_id",
    how="inner"
)

pandas_merge = pandas_merge[
    [
        "book_id",
        "title",
        "price_gbp",
        "price_inr",
        "rating",
        "in_stock",
        "category_name"
    ]
].sort_values("book_id").reset_index(drop=True)

print_and_save(f"pd.merge() rows: {len(pandas_merge)}")
print_and_save("")
print_dataframe(pandas_merge.head(10))


# ============================================================
# 16. QUERY 11 - VALIDATE SQL JOIN VS PANDAS MERGE
# ============================================================

print_and_save("")
print_and_save("=" * 70)
print_and_save("QUERY 11 - SQL JOIN VS PANDAS MERGE")
print_and_save("=" * 70)


def normalize_join_dataframe(df):
    """
    Normalize values before comparison.

    Floating-point values from SQLite and pandas can have tiny
    precision differences. Rounding to 2 decimal places makes
    the comparison reliable.
    """

    result = df.copy()

    result["price_gbp"] = pd.to_numeric(
        result["price_gbp"],
        errors="coerce"
    ).round(2)

    result["price_inr"] = pd.to_numeric(
        result["price_inr"],
        errors="coerce"
    ).round(2)

    result["rating"] = pd.to_numeric(
        result["rating"],
        errors="coerce"
    )

    result["in_stock"] = result["in_stock"].astype(bool)

    result["category_name"] = result["category_name"].astype(str)

    result = result.sort_values(
        by=["book_id"]
    ).reset_index(drop=True)

    return result


sql_normalized = normalize_join_dataframe(sql_join)

pandas_normalized = normalize_join_dataframe(pandas_merge)


same_join = sql_normalized.equals(pandas_normalized)


print_and_save(
    f"Do SQL JOIN and pd.merge() produce equivalent results?"
)

print_and_save(same_join)


# ============================================================
# 17. QUERY 12 - SQL AND PANDAS PRICE COMPARISON
# ============================================================

print_and_save("")
print_and_save("=" * 70)
print_and_save("QUERY 12 - SQL VS PANDAS PRICE VALIDATION")
print_and_save("=" * 70)


# SQL values
sql_prices = pd.read_sql_query(
    """
    SELECT
        book_id,
        price_gbp,
        price_inr,
        rating,
        in_stock
    FROM books
    ORDER BY book_id
    """,
    connection
)


# Pandas values
pandas_prices = books_df[
    [
        "book_id",
        "price_gbp",
        "price_inr",
        "rating",
        "in_stock"
    ]
].copy()

pandas_prices = pandas_prices.sort_values(
    "book_id"
).reset_index(drop=True)


# Normalize floating point values
sql_prices["price_gbp"] = pd.to_numeric(
    sql_prices["price_gbp"],
    errors="coerce"
).round(2)

sql_prices["price_inr"] = pd.to_numeric(
    sql_prices["price_inr"],
    errors="coerce"
).round(2)

pandas_prices["price_gbp"] = pd.to_numeric(
    pandas_prices["price_gbp"],
    errors="coerce"
).round(2)

pandas_prices["price_inr"] = pd.to_numeric(
    pandas_prices["price_inr"],
    errors="coerce"
).round(2)


same_ratings = (
    sql_prices["rating"].tolist()
    ==
    pandas_prices["rating"].tolist()
)

same_stock = (
    sql_prices["in_stock"].astype(bool).tolist()
    ==
    pandas_prices["in_stock"].astype(bool).tolist()
)

same_gbp = (
    sql_prices["price_gbp"].tolist()
    ==
    pandas_prices["price_gbp"].tolist()
)

same_inr = (
    sql_prices["price_inr"].tolist()
    ==
    pandas_prices["price_inr"].tolist()
)


print_and_save(f"Same ratings: {same_ratings}")
print_and_save(f"Same stock values: {same_stock}")
print_and_save(f"Same GBP prices: {same_gbp}")
print_and_save(f"Same INR prices: {same_inr}")


# ============================================================
# 18. QUERY 13 - MISSING VALUES
# ============================================================

print_and_save("")
print_and_save("=" * 70)
print_and_save("QUERY 13 - MISSING VALUES")
print_and_save("=" * 70)

missing_values = books_df.isnull().sum()

print_and_save(missing_values.to_string())


# ============================================================
# 19. QUERY 14 - PANDAS CATEGORY ANALYSIS
# ============================================================

print_and_save("")
print_and_save("=" * 70)
print_and_save("QUERY 14 - PANDAS CATEGORY ANALYSIS")
print_and_save("=" * 70)

pandas_category = (
    pandas_merge
    .groupby("category_name")
    .agg(
        book_count=("book_id", "count"),
        average_price_gbp=("price_gbp", "mean"),
        average_rating=("rating", "mean")
    )
    .reset_index()
)

pandas_category["average_price_gbp"] = (
    pandas_category["average_price_gbp"].round(2)
)

pandas_category["average_rating"] = (
    pandas_category["average_rating"].round(2)
)

pandas_category = pandas_category.sort_values(
    ["book_count", "category_name"],
    ascending=[False, True]
)

print_dataframe(pandas_category)


# ============================================================
# 20. QUERY 15 - VALIDATE SQL CATEGORY SUMMARY VS PANDAS
# ============================================================

print_and_save("")
print_and_save("=" * 70)
print_and_save("QUERY 15 - SQL VS PANDAS CATEGORY VALIDATION")
print_and_save("=" * 70)


sql_category_validation = category_summary.copy()

sql_category_validation["average_price_gbp"] = (
    sql_category_validation["average_price_gbp"].round(2)
)

sql_category_validation["average_rating"] = (
    sql_category_validation["average_rating"].round(2)
)

pandas_category_validation = pandas_category.copy()

sql_category_validation = sql_category_validation[
    [
        "category_name",
        "book_count",
        "average_price_gbp",
        "average_rating"
    ]
].sort_values(
    ["book_count", "category_name"],
    ascending=[False, True]
).reset_index(drop=True)

pandas_category_validation = pandas_category_validation[
    [
        "category_name",
        "book_count",
        "average_price_gbp",
        "average_rating"
    ]
].sort_values(
    ["book_count", "category_name"],
    ascending=[False, True]
).reset_index(drop=True)


same_category_results = (
    sql_category_validation.equals(
        pandas_category_validation
    )
)

print_and_save(
    f"Do SQL GROUP BY and pandas groupby() produce equivalent results?"
)

print_and_save(same_category_results)


# ============================================================
# 21. SAVE ALL QUERY OUTPUT
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "\n".join(all_output)
    )


# ============================================================
# 22. CLOSE DATABASE
# ============================================================

connection.close()


# ============================================================
# 23. COMPLETION MESSAGE
# ============================================================

print()
print("=" * 70)
print("QUERY WORK COMPLETED")
print("=" * 70)

print()
print("Query results saved to:")
print(OUTPUT_FILE)