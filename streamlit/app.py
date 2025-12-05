import streamlit as st
import pandas as pd

st.set_page_config(page_title="Airbnb Insights", layout="wide")


@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/cleaned_listings.csv")
    return df


# Load full dataset once
df = load_data()

if "df" not in st.session_state:
    st.session_state.df = df.copy()

MAX_POINTS = 5000

if "df_sampled" not in st.session_state:
    if len(df) > MAX_POINTS:
        st.session_state.df_sampled = df.sample(MAX_POINTS, random_state=42)
    else:
        st.session_state.df_sampled = df.copy()


st.title("Airbnb Investment Insights")
st.markdown("""
Welcome everyone! This page is here to just give a brief introduction about my streamlit page!
            Truthfully, this page is here, so my other pages buffer properly. 
            This is because I had more than 80,000 data points and some scaling and caching was needed to ensure a smoother experience.

### **Pages**
1. General Dasboard Overview  
2. Pricing Competitiveness Insights
3. Occupancy Potential insights
""")

st.dataframe(df.iloc[23:27])
