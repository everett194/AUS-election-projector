import streamlit as st
import numpy as np

st.set_page_config(page_title="NT Election Monte Carlo RCV", layout="centered")

st.title("NT Election RCV Projection (Monte Carlo Simulation)")
st.write("Adjust first-preference votes for each party. The app simulates "
         "ranked-choice voting (preferential voting) 10,000 times with random "
         "preference flows and shows the probability of each party winning.")

# --- First preference sliders ---
labor = st.slider("Labor (%)", 0, 100, 35)
clp = st.slider("CLP (%)", 0, 100, 35)
greens = st.slider("Greens (%)", 0, 100, 10)
one_nation = st.slider("One Nation (%)", 0, 100, 5)
uap = st.slider("UAP (%)", 0, 100, 5)
lib_dems = st.slider("Liberal Democrats (%)", 0, 100, 3)
independent = st.slider("Independents (%)", 0, 100, 5)
citizens = st.slider("Citizens (%)", 0, 100, 2)

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

# --- Normalize to 100 ---
total = sum(votes.values())
if total == 0:
    st.warning("Please assign some votes to start the simulation.")
    st.stop()

votes = {k: (v / total) * 100 for k, v in votes.items()}

st.subheader("Normalized First Preferences")
st.write({k: f"{v:.1f}%" for k, v in votes.items()})

# --- Base preference flows (means, from history/assumptions) ---
base_flows = {
    "Greens": {"Labor": 0.85, "CLP": 0.15},
    "One Nation": {"CLP": 0.75, "Labor": 0.25},
    "UAP": {"CLP": 0.64, "Labor": 0.36},
    "Lib Dems": {"CLP": 0.73, "Labor": 0.27},
    "Independent": {"Labor": 0.67, "CLP": 0.33},
    "Citizens": {"Labor": 0.56, "CLP": 0.44},
}

def sample_flows(eliminated, active):
    """Sample a random flow distribution for eliminated candidate."""
    if eliminated not in base_flows:
        # Even split if no rule
        return {a: 1/len(active) for a in active}
    flows = {}
    remaining = [a for a in base_flows[eliminated] if a in active]
    if not remaining:
        return {a: 1/len(active) for a in active}
    probs = [base_flows[eliminated][a] for a in remaining]
    probs = np.array(probs) / np.sum(probs)
    # Add randomness with Dirichlet distribution (like noisy proportions)
    noisy = np.random.dirichlet(probs*20)  # larger factor = less random
    for cand, p in zip(remaining, noisy):
        flows[cand] = p
    return flows

def run_rcv_sim(votes):
    """Run one RCV simulation with random flows. Return the winner."""
    votes = votes.copy()
    active = set(votes.keys())
    while True:
        # Check majority
        remaining_total = sum(votes[c] for c in active)
        leader = max(active, key=lambda c: votes[c])
        if votes[leader] > 50:
            return leader
        # Eliminate lowest
        loser = min(active, key=lambda c: votes[c])
        eliminated_votes = votes[loser]
        active.remove(loser)
        # Transfer with random noise
        flows = sample_flows(loser, active)
        for cand, frac in flows.items():
            votes[cand] += eliminated_votes * frac

# --- Monte Carlo simulation ---
N = 10000
winners = [run_rcv_sim(votes) for _ in range(N)]
unique, counts = np.unique(winners, return_counts=True)
probs = {u: c/N*100 for u, c in zip(unique, counts)}

st.subheader("Win Probabilities")
for party in sorted(probs, key=probs.get, reverse=True):
    st.write(f"{party}: {probs[party]:.1f}%")

# Highlight most likely winner
likely = max(probs, key=probs.get)
st.success(f"🏆 Most likely winner: {likely}")
