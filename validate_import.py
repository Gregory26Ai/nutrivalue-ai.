"""Validate incoming product/offer CSV before merging into public data."""
import argparse
from pathlib import Path
from urllib.parse import urlparse
import pandas as pd

RETAILERS = {"Coles", "Woolworths", "ALDI", "Chemist Warehouse", "Costco"}
STATUSES = {"verified", "partially_verified", "unverified", "demo"}

def check_url(url):
    parsed = urlparse(str(url))
    return parsed.scheme == "https" and bool(parsed.netloc)

def validate_products(df, valid_categories):
    required = {"product_id", "brand", "product_name", "category_id", "source_url", "source_checked_at", "verification_status"}
    errors = []
    missing = required - set(df.columns)
    if missing:
        return [f"Missing product columns: {sorted(missing)}"]
    if df["product_id"].isna().any() or df["product_id"].duplicated().any():
        errors.append("Product IDs must be present and unique")
    if not df["category_id"].isin(valid_categories).all():
        errors.append("Unknown category ID")
    if not df["verification_status"].isin(STATUSES).all():
        errors.append("Unknown verification status")
    verified = df[df["verification_status"] == "verified"]
    for _, row in verified.iterrows():
        if not check_url(row["source_url"]) or pd.isna(row["source_checked_at"]):
            errors.append(f"Verified product {row['product_id']} needs HTTPS source and checked date")
    if "health_star_rating" in df:
        ratings = pd.to_numeric(df["health_star_rating"], errors="coerce").dropna()
        if not ratings.between(0.5, 5).all() or not ((ratings * 2) % 1 == 0).all():
            errors.append("Health Star Ratings must be 0.5 to 5 in half-star increments")
    return errors

def validate_offers(df, product_ids):
    required = {"offer_id", "product_id", "retailer", "country_code", "price_aud", "product_url", "price_checked_at", "verification_status"}
    missing = required - set(df.columns)
    if missing:
        return [f"Missing offer columns: {sorted(missing)}"]
    errors = []
    if df["offer_id"].isna().any() or df["offer_id"].duplicated().any():
        errors.append("Offer IDs must be present and unique")
    if not df["product_id"].isin(product_ids).all():
        errors.append("Offer references unknown product")
    if not df["retailer"].isin(RETAILERS).all():
        errors.append("Unknown retailer")
    if not df["verification_status"].isin(STATUSES).all():
        errors.append("Unknown offer verification status")
    verified = df[df["verification_status"] == "verified"]
    for _, row in verified.iterrows():
        price = pd.to_numeric(pd.Series([row["price_aud"]]), errors="coerce").iloc[0]
        if pd.isna(price) or price <= 0 or row["country_code"] != "AU":
            errors.append(f"Verified offer {row['offer_id']} needs positive AUD price and AU country")
        if not check_url(row["product_url"]) or pd.isna(row["price_checked_at"]):
            errors.append(f"Verified offer {row['offer_id']} needs HTTPS source and checked date")
    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--products", default="products.csv")
    parser.add_argument("--offers", default="offers.csv")
    parser.add_argument("--categories", default="categories.csv")
    args = parser.parse_args()
    products, offers, categories = (pd.read_csv(Path(path)) for path in (args.products, args.offers, args.categories))
    errors = validate_products(products, set(categories["category_id"])) + validate_offers(offers, set(products["product_id"]))
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit(1)
    print(f"Validation passed: {len(products)} products, {len(offers)} offers, {len(categories)} categories")

if __name__ == "__main__":
    main()
