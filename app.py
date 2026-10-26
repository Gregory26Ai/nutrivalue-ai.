import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

st.set_page_config(page_title='NutriValue AI | Australian Grocery Value', page_icon='🥗', layout='wide')
st.title('🥗 NutriValue AI')
st.subheader('Better Nutrition. Better Value.')
st.info('DEMONSTRATION DATA — all prices and nutrition figures are illustrative, not verified retailer prices or nutrition labels. Do not use for purchasing or medical decisions.')

@st.cache_data
def load_data():
    return pd.read_csv(Path(__file__).with_name('products.csv'))

try:
    data = load_data()
except Exception as exc:
    st.error(f'Unable to load products.csv: {exc}')
    st.stop()

with st.sidebar:
    st.header('Find better value')
    supermarkets = st.multiselect('Supermarkets', sorted(data.supermarket.unique()), default=sorted(data.supermarket.unique()))
    goal = st.selectbox('Nutrition goal', ['Balanced value', 'High protein', 'High fibre', 'GLP-1 nutrition support', 'Lowest price per 100 g'])
    max_price = st.slider('Maximum package price (AUD)', 1.0, float(max(5, data.price_aud.max())), float(data.price_aud.max()), 0.5)
    query = st.text_input('Search foods', placeholder='e.g. lentils')
    chart_count = st.slider('Products shown in chart', 5, 25, 12)

filtered = data[data.supermarket.isin(supermarkets) & (data.price_aud <= max_price)].copy()
if query.strip():
    filtered = filtered[filtered['product'].str.contains(query.strip(), case=False, regex=False)]
if filtered.empty:
    st.warning('No products match your filters. Try expanding your selection.')
    st.stop()

filtered['price_100g'] = filtered.price_aud * 100 / filtered.package_g
filtered['protein_per_dollar'] = filtered.protein_g_100g / filtered.price_100g
filtered['fibre_per_dollar'] = filtered.fibre_g_100g / filtered.price_100g
filtered['combined_per_dollar'] = (filtered.protein_g_100g + filtered.fibre_g_100g) / filtered.price_100g
filtered['protein_fibre_score'] = (filtered.protein_g_100g + 2 * filtered.fibre_g_100g) / filtered.price_100g

if goal == 'High protein':
    filtered = filtered.sort_values('protein_per_dollar', ascending=False)
    metric = 'protein_per_dollar'
elif goal == 'High fibre':
    filtered = filtered.sort_values('fibre_per_dollar', ascending=False)
    metric = 'fibre_per_dollar'
elif goal == 'GLP-1 nutrition support':
    filtered = filtered.sort_values('protein_fibre_score', ascending=False)
    metric = 'protein_fibre_score'
elif goal == 'Lowest price per 100 g':
    filtered = filtered.sort_values('price_100g')
    metric = 'price_100g'
else:
    filtered = filtered.sort_values('combined_per_dollar', ascending=False)
    metric = 'combined_per_dollar'

m1,m2,m3,m4 = st.columns(4)
m1.metric('Food categories', filtered['product'].nunique())
m2.metric('Sample listings', len(filtered))
m3.metric('Lowest package price', f'${filtered.price_aud.min():.2f}')
m4.metric('Supermarkets', filtered.supermarket.nunique())

st.header('Best nutrition value products')
st.write("Available columns:", filtered.columns.tolist())
view = filtered[['product','supermarket','package_g','price_aud','price_100g','protein_g_100g','fibre_g_100g','sugar_g_100g','energy_kcal_100g','protein_per_dollar','fibre_per_dollar']].rename(columns={
'product':'Product','supermarket':'Supermarket','package_g':'Pack (g)','price_aud':'Price (AUD)','price_100g':'Price / 100g (AUD)','protein_g_100g':'Protein / 100g','fibre_g_100g':'Fibre / 100g','sugar_g_100g':'Sugar / 100g','energy_kcal_100g':'kcal / 100g','protein_per_dollar':'Protein g / $','fibre_per_dollar':'Fibre g / $'})
st.dataframe(view, hide_index=True, use_container_width=True)
st.download_button('Download filtered sample CSV', filtered.to_csv(index=False).encode('utf-8'), 'nutrivalue_filtered_sample.csv', 'text/csv')

st.header('Value rankings')
top = filtered.head(chart_count).copy()
top['label'] = top['product'] + ' · ' + top['supermarket']
fig = px.bar(top.sort_values(metric), x=metric, y='label', orientation='h', labels={metric: goal, 'label':'Product / store'}, title=f'{goal} — illustrative comparison')
fig.update_layout(height=max(420, chart_count * 34), margin=dict(l=10,r=10,t=55,b=20))
st.plotly_chart(fig, use_container_width=True)

st.header('Compare the same food across supermarkets')
selected = st.selectbox('Select a food', sorted(data['product'].unique()))
comparison = data[data['product'] == selected].copy()
comparison['price_100g'] = comparison.price_aud * 100 / comparison.package_g
st.dataframe(comparison[['supermarket','package_g','price_aud','price_100g']], hide_index=True, use_container_width=True)
st.caption('Prices are fabricated demonstration figures. This comparison is not evidence of retailer pricing or product availability.')

with st.expander('Methodology and limitations'):
    st.markdown('''**Basis:** Nutrition is shown per 100 g. Package prices are converted to AUD per 100 g before calculating protein and fibre per dollar. Rankings are simple heuristics, not clinical or dietary recommendations. The GLP-1 support option prioritises protein and fibre value only; it does not account for individual tolerability, clinical needs, or total dietary adequacy. All data is illustrative and generic. Before public use, replace the CSV with dated, sourced, SKU-specific supermarket pricing and verified nutrition labels.''')
