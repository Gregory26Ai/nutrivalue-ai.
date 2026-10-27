import pandas as pd
from scripts.validate_import import validate_products, validate_offers

def test_empty_imports():
    products = pd.DataFrame(columns=["product_id", "brand", "product_name", "category_id", "source_url", "source_checked_at", "verification_status"])
    offers = pd.DataFrame(columns=["offer_id", "product_id", "retailer", "country_code", "price_aud", "product_url", "price_checked_at", "verification_status"])
    assert validate_products(products, {1}) == []
    assert validate_offers(offers, set()) == []

def test_reject_fake_verified_offer():
    offers = pd.DataFrame([dict(offer_id="o1", product_id="p1", retailer="Coles", country_code="AU", price_aud=-1, product_url="bad", price_checked_at=None, verification_status="verified")])
    assert validate_offers(offers, {"p1"})
