# NutriValue AI — Version 4
Mobile-friendly Streamlit demo. All prices and nutrition values are fabricated demonstration data.

## Deploy to existing Streamlit app
1. Back up the current GitHub `app.py`, `products.csv`, and `requirements.txt` (for example, create a backup branch).
2. Replace those three files on the `main` branch with the files in this folder. The entrypoint is `app.py`.
3. Commit changes. The existing Streamlit deployment should redeploy from the connected branch.
4. Refresh your existing Streamlit URL. If it fails, inspect **Manage app → Logs**.

Keep just one lowercase `requirements.txt` and one `app.py` to avoid confusion. This demo does not provide live pricing.
