"""NutriValue AI v5 starter: only verified records are publicly displayed."""
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
RETAILERS = ["Coles", "Woolworths", "ALDI", "Chemist Warehouse", "Costco"]

st.set_page_config(page_title="NutriValue AI v5", page_icon="🥗", layout="wide")
st.title("🥗 NutriValue AI")
st.caption("Version 5 development preview · Australia · Verified data only")
st.info("Product catalogue is being built. Missing retailer prices are never estimated or fabricated.")

@st.cache_data(ttl=3600)
def load_data():
    products = pd.read_csv(ROOT / "data/products.csv", dtype={"barcode": "string", "artg_id": "string"})
    offers = pd.read_csv(ROOT / "data/offers.csv")
    categories = pd.read_csv(ROOT / "data/categories.csv")
    return products, offers, categories

products, offers, categories = load_data()
valid_products = products.loc[products["verification_status"].eq("verified")].copy()
valid_offers = offers.loc[offers["verification_status"].eq("verified")].copy()
valid_offers = valid_offers[valid_offers["product_id"].isin(valid_products["product_id"])]

col1, col2, col3 = st.columns(3)
col1.metric("Verified products", len(valid_products))
col2.metric("Verified retailer offers", len(valid_offers))
col3.metric("Launch target", "500")

query = st.text_input("Search products", placeholder="e.g. creatine, oats, protein isolate")
group = st.selectbox("Product range", ["All ranges"] + sorted(categories["group"].unique().tolist()))
retailer = st.selectbox("Retailer", ["All retailers"] + RETAILERS)

catalogue = valid_products.merge(categories, on="category_id", how="left")
if query:
    catalogue = catalogue[catalogue["product_name"].str.contains(query, case=False, na=False, regex=False) |
                          catalogue["brand"].str.contains(query, case=False, na=False, regex=False)]
if group != "All ranges":
    catalogue = catalogue[catalogue["group"] == group]

if retailer != "All retailers":
    allowed_ids = valid_offers.loc[valid_offers["retailer"] == retailer, "product_id"]
    catalogue = catalogue[catalogue["product_id"].isin(allowed_ids)]

if catalogue.empty:
    st.warning("No verified products match yet. Import and validate source records to populate this catalogue.")
else:
    st.subheader("Verified products")
    for _, product in catalogue.head(100).iterrows():
        with st.container(border=True):
            st.markdown(f"**{product['brand']} — {product['product_name']}**")
            st.caption(f"{product['group']} / {product['category']} · {product['package_size']}")
            matching = valid_offers[valid_offers["product_id"] == product["product_id"]]
            if retailer != "All retailers":
                matching = matching[matching["retailer"] == retailer]
            if matching.empty:
                st.write("No verified retailer price")
            else:
                st.dataframe(matching[["retailer", "price_aud", "price_checked_at", "product_url"]].rename(
                    columns={"price_aud": "Price (AUD)", "price_checked_at": "Checked", "product_url": "Source"}),
                    hide_index=True, use_container_width=True)
            with st.expander("Ingredients, nutrition and verification"):
                st.write("Ingredients:", product.get("ingredients") if pd.notna(product.get("ingredients")) else "Not available")
                st.write("Allergens:", product.get("allergens") if pd.notna(product.get("allergens")) else "Not available")
                for key, label in [("protein_g_100g", "Protein (g/100g)"), ("fibre_g_100g", "Fibre (g/100g)"),
                                   ("sugar_g_100g", "Sugar (g/100g)"), ("sodium_mg_100g", "Sodium (mg/100g)"),
                                   ("health_star_rating", "Published Health Star Rating")]:
                    value = product.get(key)
                    st.write(label + ":", value if pd.notna(value) else "Not available")
                st.write("Source:", product.get("source_url", ""))
                st.write("Checked:", product.get("source_checked_at", ""))
    st.download_button("Download visible products (CSV)", catalogue.to_csv(index=False).encode("utf-8"),
                       file_name="nutrivalue_verified_products.csv", mime="text/csv")

st.divider()
st.caption("Health Star Ratings apply only where published for eligible foods. Supplement efficacy is not inferred from food nutrition scores. Product images require permission or suitable licensing.")
