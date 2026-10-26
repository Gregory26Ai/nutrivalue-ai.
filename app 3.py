import io
from datetime import date
import pandas as pd
import streamlit as st

st.set_page_config(page_title='NutriValue AI | Version 3', page_icon='🥗', layout='wide')
st.markdown('''<style>
.block-container {padding-top:1.1rem;max-width:1100px}
[data-testid="stMetric"] {background:#f3f7f6;padding:14px;border-radius:12px}
h1 {font-size:2.1rem!important}
@media(max-width:650px){h1{font-size:1.75rem!important}.block-container{padding-left:1rem;padding-right:1rem}}
</style>''', unsafe_allow_html=True)

REQUIRED = ['product','supermarket','package_g','price_aud','protein_g_100g','fibre_g_100g','data_status','source_url','checked_date']
STORES = ['Coles','Woolworths','ALDI']

def read_data(upload=None):
    if upload is not None:
        return pd.read_csv(upload)
    return pd.read_csv('products.csv')

def clean_data(df):
    df.columns = [str(c).strip().lower() for c in df.columns]
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError('Missing columns: ' + ', '.join(missing))
    df = df.copy()
    for c in ['package_g','price_aud','protein_g_100g','fibre_g_100g']:
        df[c] = pd.to_numeric(df[c],errors='coerce')
    df['data_status'] = df['data_status'].fillna('demo').astype(str).str.strip().str.lower()
    df['source_url'] = df['source_url'].fillna('').astype(str).str.strip()
    df['checked_date'] = df['checked_date'].fillna('').astype(str).str.strip()
    df['product'] = df['product'].fillna('').astype(str).str.strip()
    df['supermarket'] = df['supermarket'].fillna('').astype(str).str.strip()
    df = df.dropna(subset=['package_g','price_aud','protein_g_100g','fibre_g_100g'])
    df = df[(df.package_g>0)&(df.price_aud>0)&(df.protein_g_100g>=0)&(df.fibre_g_100g>=0)]
    df['verified'] = (df.data_status=='verified') & df.source_url.str.startswith('https://') & pd.to_datetime(df.checked_date,errors='coerce').notna()
    df['price_100g'] = df.price_aud/df.package_g*100
    # Nutrition values are per 100g. Protein/fibre per dollar uses the whole package.
    df['protein_per_aud'] = (df.protein_g_100g*df.package_g/100)/df.price_aud
    df['fibre_per_aud'] = (df.fibre_g_100g*df.package_g/100)/df.price_aud
    df['balanced_score'] = df.protein_per_aud + df.fibre_per_aud
    return df

st.title('🥗 NutriValue AI')
st.caption('Version 3 • Better nutrition. Better value. Australian grocery comparisons.')
st.info('Prices and nutrition figures in the bundled dataset are **demonstration values**, not retailer-verified information. Do not use demo results to make purchasing or medical decisions.')

with st.sidebar:
    st.header('Data & filters')
    upload = st.file_uploader('Upload updated product CSV',type=['csv'],help='Use the provided products.csv column structure. Uploads apply only to this session.')
    st.caption('Upload is session-only. To make updates permanent, replace products.csv in GitHub.')
try:
    data = clean_data(read_data(upload))
except Exception as exc:
    st.error(f'Could not load the product data: {exc}')
    st.stop()
if data.empty:
    st.warning('No valid product rows found. Check prices, package weights and nutrition columns.')
    st.stop()

with st.sidebar:
    stores = st.multiselect('Supermarkets',sorted(data.supermarket.unique()),default=sorted(data.supermarket.unique()))
    query = st.text_input('Search products',placeholder='e.g. lentils')
    verified_only = st.toggle('Verified listings only',value=False)
    goal = st.selectbox('Rank by',['Balanced protein + fibre per $','Protein per $','Fibre per $','Lowest price per 100g'])
    st.caption('Verified status requires data_status=verified, an HTTPS source URL and a valid checked date. This is a metadata check, not independent verification.')

filtered = data[data.supermarket.isin(stores)].copy()
if query.strip():
    filtered = filtered[filtered['product'].str.contains(query.strip(),case=False,regex=False,na=False)]
if verified_only:
    filtered = filtered[filtered.verified]

m1,m2,m3 = st.columns(3)
m1.metric('Product listings',len(filtered))
m2.metric('Food categories',filtered['product'].nunique())
m3.metric('Verified-labelled listings',int(filtered.verified.sum()))
if filtered.empty:
    st.warning('No products match these filters. Turn off “Verified listings only” to view demonstration data, or upload sourced products.')
    st.stop()

sort_map = {'Balanced protein + fibre per $':('balanced_score',False),'Protein per $':('protein_per_aud',False),'Fibre per $':('fibre_per_aud',False),'Lowest price per 100g':('price_100g',True)}
key,ascending = sort_map[goal]
ranked = filtered.sort_values(key,ascending=ascending).reset_index(drop=True)
ranked['data_label'] = ranked.verified.map({True:'Verified-labelled',False:'Demo / unverified'})

st.subheader('Best nutrition value products')
show = ranked[['product','supermarket','package_g','price_aud','price_100g','protein_g_100g','fibre_g_100g','protein_per_aud','fibre_per_aud','data_label']].copy()
show.columns=['Product','Supermarket','Pack (g)','Price (AUD)','$/100g','Protein (g/100g)','Fibre (g/100g)','Protein (g/$)','Fibre (g/$)','Data status']
st.dataframe(show,hide_index=True,use_container_width=True,column_config={'Price (AUD)':st.column_config.NumberColumn(format='$%.2f'),'$/100g':st.column_config.NumberColumn(format='$%.2f'),'Protein (g/$)':st.column_config.NumberColumn(format='%.1f'),'Fibre (g/$)':st.column_config.NumberColumn(format='%.1f')})
st.download_button('Download filtered CSV',ranked.to_csv(index=False).encode('utf-8'),'nutrivalue_filtered_v3.csv','text/csv')

st.subheader('Top value rankings')
chart = ranked.head(12).copy()
chart['label'] = chart['product'] + ' · ' + chart['supermarket']
chart = chart.set_index('label')
st.bar_chart(chart[[key]],horizontal=True)
st.caption('Scores compare nutritional grams per Australian dollar, based on supplied values. They do not account for protein quality, individual dietary needs, or GLP-1 medication suitability.')

st.subheader('Compare the same food across supermarkets')
foods = sorted(filtered['product'].unique())
selected = st.selectbox('Select a food',foods)
compare = filtered[filtered['product']==selected].sort_values('price_100g')
for _,item in compare.iterrows():
    with st.container(border=True):
        a,b = st.columns([3,2])
        with a:
            st.markdown(f"**{item['supermarket']}** · {item['package_g']:g} g")
            st.caption('Verified-labelled' if item['verified'] else 'Demo / unverified')
        with b:
            st.markdown(f"**${item['price_aud']:.2f}**")
            st.caption(f"${item['price_100g']:.2f} per 100g")
        if item['verified']:
            st.markdown(f"[Retailer source]({item['source_url']}) · Checked {item['checked_date']}")

with st.expander('Methodology, data sources and limitations'):
    st.markdown('''**Calculation basis**: price per 100g = package price ÷ package grams × 100. Protein (or fibre) per dollar = grams per 100g × package grams ÷ 100 ÷ package price. Balanced score = protein grams per dollar + fibre grams per dollar, equally weighted. Rankings are illustrative, not medical advice.\n\n**Data integrity**: The bundled CSV is entirely synthetic and marked `demo`. No live supermarket connection is included. A row labelled `verified` requires a retailer source URL and checked date; this app checks those fields exist but cannot independently confirm their truth, current price, stock, or nutrition accuracy. Nutrition must use a consistent per-100g basis (dry versus cooked products can differ substantially).\n\n**Updates**: Upload a CSV during a session, or commit an updated `products.csv` to the GitHub repository for persistent changes. Only use data collected with appropriate permissions.\n\n**GLP-1 note**: This is a general food-comparison tool, not guidance for GLP-1 prescriptions or individual nutritional requirements.''')
