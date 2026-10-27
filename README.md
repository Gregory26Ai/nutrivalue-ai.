# NutriValue AI — Version 5 development starter

**Status:** functional development starter, **not** a populated 500-product verified catalogue. It intentionally ships with **zero verified products** rather than inventing retailer prices, images, Health Star Ratings or ingredients.

## Preserve the working Version 4

1. On GitHub `Gregory26Ai/nutrivalue-ai`, create a tag `v4.0-backup` on the currently working commit (or download the existing repository ZIP).
2. Create a new branch named `v5-development` **from `main`**.
3. Upload the files in this package **to `v5-development` only**, preserving directory paths. `app.py` and `requirements.txt` in the new branch will replace those files on that branch only.
4. Leave `main` and the existing Streamlit deployment unchanged. Do **not** change the production app branch until v5 is validated.
5. For preview, deploy a **separate** Streamlit Community Cloud app using repo `Gregory26Ai/nutrivalue-ai`, branch `v5-development`, entrypoint `app.py`.
6. Run `python -m pytest -q` and `python scripts/validate_import.py` before merging.
7. When the new catalogue is populated and quality-tested, merge into `main` and check production logs.

**Important:** The existing Version 4 source was not provided in this conversation. This is a standalone v5 starter, not an in-place patch to the current `app.py`. Do not upload to `main` directly.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Importing data

- `data/categories.csv`: 50 category taxonomy.
- `data/products.csv`: unique product records with source URL, checked date and status.
- `data/offers.csv`: retailer-specific prices and observation dates.
- Import new rows only from sources you have verified and have permission to use.
- Set `verification_status=verified` **only after checking the original source**. A URL alone does not prove accuracy.
- Use HTTPS retailer product URLs and dates in ISO `YYYY-MM-DD` format.
- A product without a verified price can still appear once its product record is verified.
- Images are not automatically copied from retailer sites; obtain licensed assets or authorised feeds first.
- The app intentionally does not implement scraping, automated retailer extraction, or automatic claims of verification.

## Initial 500-product sourcing targets

- Everyday groceries: 100
- Powders: 80
- Superfoods: 80
- Supplements: 65
- Sports nutrition: 60
- Functional foods: 55
- Specialist diets: 60

Retailers: Coles, Woolworths, ALDI, Chemist Warehouse, Costco. A product may have zero or multiple offers. Prices vary by store, location, date, and membership eligibility.

## Expansion milestones

| Stage | Unique verified products | Release gate |
|---|---:|---|
| Starter | 0 | App, schema and validators run |
| Pilot | 100 | Source and nutrition review |
| Launch | 500 | Retailer coverage and mobile QA |
| Growth | 1,000 | Import monitoring and provenance |
| Expansion | 2,500 | Database migration and performance testing |
| Scale | 5,000 | Broader category and price coverage |

## International preparation

Offers already include `country_code`. Future migrations should add currency code, tax basis, language, market-specific labelling and country-specific retailer identifiers. Do not compare AUD prices with foreign-currency offers without explicit conversion and timestamp.

## Future production work

- Move CSV records to managed PostgreSQL when automated updates and price history justify it.
- Add image rights and provenance, change tracking, import review queue, data-quality scoring and audit logs.
- Add per-category ranking algorithms and tests; food Health Star Ratings must not be used to infer supplement efficacy.
- Add store-specific pricing, Costco membership flags, accessibility and mobile barcode search.
- Secure database credentials in Streamlit secrets, not GitHub.
