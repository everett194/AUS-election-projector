import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np

# Load NT electorates geometry from MapInfo .TAB
gdf = gpd.read_file("NT-march-2025-mapinfo/Lingiari_Solomon.TAB")

st.title("Northern Territory Election Projection")
st.write("Exploring Ranked Choice Voting (RCV) projections for Lingiari and Solomon.")

st.subheader("Preview of Electorate Boundaries")
st.write(gdf.head())

# Example: sliders for first preference votes
st.subheader("First Preference Votes")
labor = st.slider("Labor (%)", 0, 100, 35)
clp = st.slider("CLP (%)", 0, 100, 35)
greens = st.slider("Greens (%)", 0, 100, 10)
one_nation = st.slider("One Nation (%)", 0, 100, 5)
uap = st.slider("UAP (%)", 0, 100, 5)
lib_dems = st.slider("Liberal Democrats (%)", 0, 100, 3)
independent = st.slider("Independents (%)", 0, 100, 5)
citizens = st.slider("Citizens (%)", 0, 100, 2)

# Collect first preferences
votes = {
    "Labor": labor,
    "CLP": clp,
    "Greens": greens,
    "One Nation": one_nation,
    "UAP": uap,
    "Lib Dems": lib_dems,
    "Independent": independent,
    "Citizens": citizens,
}

st.write("### First Preference Votes (input)")
st.write(votes)

# Normalization
total = sum(votes.values())
if total == 0:
    st.warning("Please assign some votes to run a projection.")
else:
    normalized = {k: v / total for k, v in votes.items()}
    st.write("### Normalized first preference shares")
    st.write(normalized)

    # TODO: add RCV simulation logic here once preference flows are finalized
    st.info("RCV simulation will project the winner after preferences are distributed.")
