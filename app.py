
import streamlit as st

import pandas as pd

st.set_page_config(

    page_title="NutriValue AI",

    page_icon="🥗",

    layout="wide"

)

st.title("🥗 NutriValue AI")

st.subheader("Better Nutrition. Better Value.")

st.write(

    "Compare affordable foods for protein, fibre "

    "and GLP-1 nutrition support."

)

products = [

    ["Rolled Oats", 2.50, 13, 10],

    ["Chickpeas", 1.20, 7, 6],

    ["Lentils", 1.50, 9, 8],

    ["Greek Yoghurt", 5.00, 10, 0],

    ["Eggs", 5.50, 13, 0],

    ["Cottage Cheese", 4.50, 12, 0],

    ["High Protein Bar", 3.50, 20, 5],

    ["Protein Shake", 4.50, 25, 2]

]

df = pd.DataFrame(

    products,

    columns=["Product", "Price AUD", "Protein g", "Fibre g"]

)

st.sidebar.header("Your Nutrition Goals")

goal = st.sidebar.selectbox(

    "Choose your priority",

    ["Best Value", "High Protein", "High Fibre", "GLP-1 Support"]

)

budget = st.sidebar.slider(

    "Maximum product price ($)",

    1.0, 10.0, 5.0

)

df = df[df["Price AUD"] <= budget].copy()

df["Protein per $"] = df["Protein g"] / df["Price AUD"]

df["Fibre per $"] = df["Fibre g"] / df["Price AUD"]

if goal == "High Protein":

    df = df.sort_values("Protein per $", ascending=False)

elif goal == "High Fibre":

    df = df.sort_values("Fibre per $", ascending=False)

elif goal == "GLP-1 Support":

    df["Score"] = df["Protein per $"] + df["Fibre per $"]

    df = df.sort_values("Score", ascending=False)

else:

    df["Score"] = df["Protein per $"] + df["Fibre per $"]

    df = df.sort_values("Score", ascending=False)

st.header("Best Nutrition Value Products")

st.dataframe(df, use_container_width=True)

if not df.empty:

    st.success("Top ranked product: " + df.iloc[0]["Product"])

st.caption(
    "Prototype only. Prices and nutrition values are "
    "illustrative, with no standardised serving sizes. "
    "Not medical advice or verified retailer data."
)
