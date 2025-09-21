# AUS-election-projector

import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="AU Election Modeller", page_icon="🗳️")

st.title("Australia election modeller")
st.caption("Primary vote sliders feed two party preferred, then a toy seat projection")

# -----------------------------
# Defaults and constants
# -----------------------------

# AEC 2022 national preference flows to Labor in percent
# Sources:
# Greens -> Labor about 85.66 percent
# One Nation -> Labor about 35.70 percent
# UAP -> Labor about 38.14 percent
# Independents in 2022 flowed to Labor about 63.77 percent, but Others is a mix
FLOWS_TO_LABOR_DEFAULT = {
    "Greens": 85.66,
    "One Nation": 35.70,
    "UAP": 38.14,
    "Others": 55.00,  # heuristic midpoint for a mixed Others bucket
}

# 2022 anchor for seat projection
TPP_ANCHOR = 52.13   # Labor national two party preferred in 2022
SEATS_ANCHOR_LAB = 77
TOTAL_SEATS = 151

# Elasticity in seats for each one point of two party preferred movement
# Roughly tuned so that a three point swing moves seats by about twenty three
SEATS_PER_TPP_POINT = 7.5

# -----------------------------
# Helper functions
# -----------------------------

def normalize_primary(votes):
    """Return dict that sums to one hundred by simple rescale if needed."""
    total = sum(votes.values())
    if total <= 0:
        return {k: 0.0 for k in votes}
    return {k: v * 100.0 / total for k, v in votes.items()}

def compute_two_party_preferred(primary, flows_to_labor):
    """
    primary values are in percent for Labor, Coalition, Greens, One Nation, UAP, Others.
    We allocate minor party votes to the majors using flow shares.
    The Labor two party share equals Labor primary
    plus Greens primary times Greens to Labor share
    plus One Nation primary times One Nation to Labor share
    plus UAP primary times UAP to Labor share
    plus Others primary times Others to Labor share.
    Coalition two party is one hundred minus that.
    """
    lab = primary["Labor"]
    coal = primary["Coalition"]
    greens = primary["Greens"]
    phon = primary["One Nation"]
    uap = primary["UAP"]
    other = primary["Others"]

    lab_from_greens = greens * (flows_to_labor["Greens"] / 100.0)
    lab_from_phon = phon * (flows_to_labor["One Nation"] / 100.0)
    lab_from_uap = uap * (flows_to_labor["UAP"] / 100.0)
    lab_from_other = other * (flows_to_labor["Others"] / 100.0)

    labor_tpp = lab + lab_from_greens + lab_from_phon + lab_from_uap + lab_from_other
    labor_tpp = max(0.0, min(100.0, labor_tpp))
    coal_tpp = 100.0 - labor_tpp
    return labor_tpp, coal_tpp

def project_seats(labor_tpp, anchor_tpp=TPP_ANCHOR, anchor_seats=SEATS_ANCHOR_LAB, seats_per_point=SEATS_PER_TPP_POINT):
    """
    Very simple national swing curve. Take the anchor point then move seats by a fixed
    amount for each one point of national two party preferred movement.
    Constrain to valid bounds.
    Coalition seats are computed as the remainder after crossbench is inferred.
    For this toy we let the crossbench float implicitly if the formula pushes majors above totals.
    """
    delta = labor_tpp - anchor_tpp
    seats_lab = round(anchor_seats + seats_per_point * delta)
    seats_lab = int(max(0, min(TOTAL_SEATS, seats_lab)))

    # For a quick display, split the remainder proportionally using the two party ratio,
    # but never let Coalition seats fall below zero.
    seats_coal = TOTAL_SEATS - seats_lab
    seats_coal = int(max(0, seats_coal))

    return seats_lab, seats_coal

# -----------------------------
# Inputs
# -----------------------------

st.subheader("Primary vote inputs")

col1, col2, col3 = st.columns(3)
with col1:
    pv_lab = st.slider("Labor percent", 0.0, 60.0, 33.0, 0.1)
    pv_grn = st.slider("Greens percent", 0.0, 30.0, 12.0, 0.1)
with col2:
    pv_coal = st.slider("Coalition percent", 0.0, 60.0, 36.0, 0.1)
    pv_phon = st.slider("One Nation percent", 0.0, 20.0, 5.0, 0.1)
with col3:
    pv_uap = st.slider("UAP percent", 0.0, 20.0, 4.0, 0.1)
    pv_oth = st.slider("Others percent", 0.0, 40.0, 10.0, 0.1)

raw_primary = {
    "Labor": pv_lab,
    "Coalition": pv_coal,
    "Greens": pv_grn,
    "One Nation": pv_phon,
    "UAP": pv_uap,
    "Others": pv_oth,
}

norm_primary = normalize_primary(raw_primary)

st.write("Primary votes after rescale so they sum to one hundred")
st.dataframe(pd.DataFrame([norm_primary]).round(2))

with st.expander("Advanced preference flow settings"):
    st.write("Flows to Labor in percent. Defaults based on AEC 2022. Tweak if you want to explore.")
    f_g = st.slider("Greens to Labor", 0.0, 100.0, FLOWS_TO_LABOR_DEFAULT["Greens"], 0.1)
    f_p = st.slider("One Nation to Labor", 0.0, 100.0, FLOWS_TO_LABOR_DEFAULT["One Nation"], 0.1)
    f_u = st.slider("UAP to Labor", 0.0, 100.0, FLOWS_TO_LABOR_DEFAULT["UAP"], 0.1)
    f_o = st.slider("Others to Labor", 0.0, 100.0, FLOWS_TO_LABOR_DEFAULT["Others"], 0.1)
    flows_to_labor = {"Greens": f_g, "One Nation": f_p, "UAP": f_u, "Others": f_o}
else:
    flows_to_labor = FLOWS_TO_LABOR_DEFAULT.copy()

# -----------------------------
# Compute TPP and seats
# -----------------------------

lab_tpp, coal_tpp = compute_two_party_preferred(norm_primary, flows_to_labor)

st.subheader("Two party preferred")
st.metric(label="Labor two party preferred", value=f"{lab_tpp:.2f} percent")
st.metric(label="Coalition two party preferred", value=f"{coal_tpp:.2f} percent")

st.subheader("Seat projection")
seats_lab, seats_coal = project_seats(lab_tpp)
seats_cross = max(0, TOTAL_SEATS - seats_lab - seats_coal)

c1, c2, c3 = st.columns(3)
c1.metric("Labor seats", seats_lab)
c2.metric("Coalition seats", seats_coal)
c3.metric("Crossbench seats", seats_cross)

# Show a small summary table
summary = pd.DataFrame(
    {
        "Labor TPP percent": [round(lab_tpp, 2)],
        "Coalition TPP percent": [round(coal_tpp, 2)],
        "Labor seats": [seats_lab],
        "Coalition seats": [seats_coal],
        "Crossbench seats": [seats_cross],
    }
)
st.dataframe(summary)

st.caption(
    "Flows taken from AEC national tables for 2022. "
    "This is a teaching demo not a forecast. Seat curve anchored at 2022 and uses a simple elasticity."
)
