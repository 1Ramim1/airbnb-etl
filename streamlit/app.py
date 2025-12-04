import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="London Airbnb Insights", layout="wide")


@st.cache_data
def load_data():
    return pd.read_csv("cleaned_listings.csv")


df = load_data()

st.title("London Airbnb Market Analysis")
st.write("Interactive insights generated from cleaned Airbnb listing data.")
