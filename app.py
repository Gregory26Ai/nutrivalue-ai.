import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title='NutriValue AI | Version 4', page_icon='🥗', layout='wide', initial_sidebar_state='collapsed')
st.markdown('''<style>
.block-container{padding-top:1.1rem;max-width:1100px}h1,h2,h3{letter-spacing:-.035em}div[data-testid="stMetric"]{background:#f3f7f5;padding:14px;border-radius:14px} .stButton button{border-radius:12px} @media(max-width:640px){h1{font-size:2rem!important}.block-container{padding-left:1rem;padding-right:1rem}div[data-testid="stHorizontalBlock"]{gap:.4rem}}
</style>''', unsafe_allow_html=True)

@st.cache_data
def load_data():
    path=Path(__file__).with_name('products.csv')
    df=pd.read_csv(path)
    required={'product','supermarket','package_g','price_aud','protein_g_100g','fibre_g_100g'}
    missing=required-set(df.columns)
    if missing: raise ValueError('Missing CSV columns: '+', '.join(sorted(missing)))
    for col in ['package_g','price_aud','protein_g_100g','fibre_g_100g']:
        df[col]=pd.to_numeric(df[col],errors='coerce')
    df=df.dropna(subset=list(required))
    df=df[(df.package_g>0)&(df.price_aud>0)]
    if 'category' not in df: df['category']='Other'
    if 'data_status' not in df: df['data_status']='demo'
    if 'source_url' not in df: df['source_url']=''
    if 'checked_date' not in df: df['checked_date']=''
    df['price_100g']=df.price_aud/df.package_g*100
    df['protein_per_dollar']=df.protein_g_100g/df.price_100g
    df['fibre_per_dollar']=df.fibre_g_100g/df.price_100g
    df['balanced_value']=df.protein_per_dollar+df.fibre_per_dollar
    return df

st.title('🥗 NutriValue AI')
st.caption('Version 4 · Better nutrition. Better value.')
st.warning('DEMONSTRATION DATA — prices and nutrition values are illustrative and not verified retailer listings. Do not rely on these figures for purchasing or medical decisions.',icon='⚠️')
try: df=load_data()
except Exception as exc:
    st.error(f'Unable to load products.csv: {exc}')
    st.stop()

with st.expander('🔎 Find and filter foods',expanded=True):
    search=st.text_input('Search foods',placeholder='e.g. oats, lentils, almonds')
    supermarkets=st.multiselect('Supermarkets',sorted(df.supermarket.unique()),default=sorted(df.supermarket.unique()))
    categories=st.multiselect('Food categories',sorted(df.category.unique()),default=sorted(df.category.unique()))
    metric=st.selectbox('Rank by', ['Balanced nutrition value','Protein per dollar','Fibre per dollar','Lowest price per 100 g'])
filtered=df[df.supermarket.isin(supermarkets)&df.category.isin(categories)]
if search: filtered=filtered[filtered['product'].str.contains(search,case=False,regex=False,na=False)]

c1,c2,c3=st.columns(3)
c1.metric('Foods',filtered['product'].nunique())
c2.metric('Listings',len(filtered))
c3.metric('Retailers',filtered['supermarket'].nunique())
if filtered.empty:
    st.info('No matches. Try clearing the search or changing the filters.')
    st.stop()

metric_map={'Balanced nutrition value':'balanced_value','Protein per dollar':'protein_per_dollar','Fibre per dollar':'fibre_per_dollar','Lowest price per 100 g':'price_100g'}
metric_col=metric_map[metric]
ascending=metric=='Lowest price per 100 g'
ranked=filtered.sort_values(metric_col,ascending=ascending)
st.subheader('🏆 Best nutrition value')
show=ranked[['product','supermarket','package_g','price_aud','price_100g','protein_g_100g','fibre_g_100g',metric_col]].copy()
show=show.loc[:,~show.columns.duplicated()]
st.dataframe(show.rename(columns={'product':'Food','supermarket':'Store','package_g':'Pack (g)','price_aud':'Price (AUD)','price_100g':'AUD / 100g','protein_g_100g':'Protein / 100g','fibre_g_100g':'Fibre / 100g','balanced_value':'Balanced score','protein_per_dollar':'Protein g / AUD','fibre_per_dollar':'Fibre g / AUD'}),hide_index=True,use_container_width=True)
st.download_button('⬇️ Download filtered CSV',filtered.to_csv(index=False).encode('utf-8'),'nutrivalue_v4_filtered.csv','text/csv')
chart=ranked.head(12).copy()
chart['label']=chart['product']+' · '+chart['supermarket']
fig=px.bar(chart.sort_values(metric_col,ascending=not ascending),x=metric_col,y='label',orientation='h',labels={'label':'','balanced_value':'Balanced score','protein_per_dollar':'Protein g / AUD','fibre_per_dollar':'Fibre g / AUD','price_100g':'AUD / 100g'},title='Top matching products')
fig.update_layout(height=max(340,45*len(chart)),margin=dict(l=0,r=10,t=50,b=10))
st.plotly_chart(fig,use_container_width=True)
st.subheader('🛒 Compare the same food')
food=st.selectbox('Select a food',sorted(filtered['product'].unique()))
comparison=filtered[filtered['product']==food].sort_values('price_100g')
st.dataframe(comparison[['supermarket','package_g','price_aud','price_100g','protein_g_100g','fibre_g_100g']].rename(columns={'supermarket':'Store','package_g':'Pack (g)','price_aud':'Price (AUD)','price_100g':'AUD / 100g','protein_g_100g':'Protein / 100g','fibre_g_100g':'Fibre / 100g'}),hide_index=True,use_container_width=True)
with st.expander('Methodology and limitations'):
    st.write('Prices are normalised to AUD per 100 g. Protein and fibre per dollar are the respective grams per 100 g divided by the price per 100 g. The balanced score is their unweighted sum, an illustrative heuristic rather than a validated nutrition rating. Compare equivalent dry/cooked forms only. Source URLs and checked dates are metadata, not independently validated by this app.')
    st.write('This build uses local CSV data. It does not retrieve live supermarket prices or verify product availability.')
