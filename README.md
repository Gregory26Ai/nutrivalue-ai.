# NutriValue AI — Version 3

Mobile-friendly Streamlit prototype for Australian supermarket nutrition value comparisons.

## Deploy
1. Back up the existing GitHub `app.py`, `products.csv`, and `requirements.txt` (or create a `version-2-backup` branch).
2. Replace `app.py`, `products.csv`, and the **lowercase** `requirements.txt` in the `main` branch with these files. GitHub is case-sensitive: remove the older `Requirements.txt` if present.
3. Commit changes. Streamlit Community Cloud normally redeploys when `main` changes.
4. Open your existing app from the Streamlit dashboard; do not create a new deployment unless necessary.

## Data schema
`product,supermarket,package_g,price_aud,protein_g_100g,fibre_g_100g,data_status,source_url,checked_date`

- Every included price and nutrition figure is fabricated for demonstration.
- `data_status=demo` by default.
- For sourced records, use `data_status=verified`, an HTTPS URL to the source and an ISO checked date (`YYYY-MM-DD`). The application checks metadata, not the source itself.
- Use nutrition per 100 g, and ensure that dry/cooked forms are comparable.
- Do not scrape retailers without permission or claim real-time pricing without a legitimate data feed.

## Local run
`pip install -r requirements.txt`
`streamlit run app.py`
