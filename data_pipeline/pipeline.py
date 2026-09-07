import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

BASE_URL = "https://books.toscrape.com/"
GBP_TO_INR = 105.50


def scrape_books():
    books = []

    # Scrape first 5 catalogue pages
    for page_number in range(1, 6):

        if page_number == 1:
            url = BASE_URL
        else:
            url = f"{BASE_URL}catalogue/page-{page_number}.html"

        print(f"Scraping page {page_number}...")

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        book_items = soup.select("article.product_pod")

        for book in book_items:

            # Title
            title = book.h3.a["title"]

            # Price as listed
            price_text = book.select_one(
                ".price_color"
            ).get_text(strip=True)

            # Star rating as text
            rating_element = book.select_one("p.star-rating")
            star_rating = rating_element.get("class")[1]

            # Availability
            availability = book.select_one(
                ".availability"
            ).get_text(" ", strip=True)

            # Book details URL
            book_url = urljoin(url, book.h3.a["href"])

            # Open details page
            detail_response = requests.get(
                book_url,
                timeout=10
            )
            detail_response.raise_for_status()

            detail_soup = BeautifulSoup(
                detail_response.text,
                "html.parser"
            )

            # Category
            breadcrumb = detail_soup.select(
                "ul.breadcrumb li"
            )

            if len(breadcrumb) >= 3:
                category = breadcrumb[2].get_text(strip=True)
            else:
                category = "Unknown"

            books.append({
                "title": title,
                "price": price_text,
                "star_rating": star_rating,
                "availability": availability,
                "category": category
            })

    return books


# ============================================================
# 1. SCRAPE
# ============================================================

books = scrape_books()

df = pd.DataFrame(books)

print()
print("========================================")
print("SCRAPING COMPLETED")
print("========================================")
print("Total books scraped:", len(df))


# ============================================================
# 2. CLEAN PRICE
# ============================================================

df["price_gbp"] = (
    df["price"]
    .astype(str)
    .str.replace(r"[^\d.]", "", regex=True)
)

df["price_gbp"] = pd.to_numeric(
    df["price_gbp"],
    errors="coerce"
)

# Median imputation for invalid numeric values
df["price_gbp"] = df["price_gbp"].fillna(
    df["price_gbp"].median()
)


# ============================================================
# 3. CLEAN STAR RATING
# ============================================================

rating_mapping = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

df["rating"] = df["star_rating"].map(
    rating_mapping
)

# Median imputation for invalid ratings
df["rating"] = df["rating"].fillna(
    df["rating"].median()
).astype(int)


# ============================================================
# 4. CLEAN AVAILABILITY
# ============================================================

df["in_stock"] = (
    df["availability"]
    .astype(str)
    .str.lower()
    .str.contains("in stock", na=False)
)


# ============================================================
# 5. GBP TO INR
# ============================================================

df["price_inr"] = (
    df["price_gbp"] * GBP_TO_INR
)


# ============================================================
# 6. FINAL DATASET
# ============================================================

df = df[
    [
        "title",
        "price_gbp",
        "price_inr",
        "rating",
        "in_stock",
        "category"
    ]
]


# ============================================================
# 7. VALIDATION
# ============================================================

print()
print("========================================")
print("CLEANED DATA")
print("========================================")

print()
print("First 10 rows:")
print(df.head(10))

print()
print("Data types:")
print(df.dtypes)

print()
print("Number of rows:", len(df))

print()
print("Number of categories:",
      df["category"].nunique())

print()
print("Categories:")
print(df["category"].value_counts())

print()
print("Missing values:")
print(df.isnull().sum())


# ============================================================
# 8. SAVE CLEANED DATA
# ============================================================

df.to_csv(
    "data_pipeline/cleaned_books.csv",
    index=False
)

print()
print("========================================")
print("FILE SAVED")
print("========================================")
print("data_pipeline/cleaned_books.csv")