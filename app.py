import streamlit as st

st.set_page_config(page_title="NT Election RCV Simulator", layout="centered")

st.title("Northern Territory Election RCV Projection")
st.write("Adjust first-preference votes for each party. The app simulates "
         "ranked-choice voting (preferential voting) and projects the final winner.")

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

# --- Preference flow rules ---
def transfer(eliminated, active):
    """Return how eliminated candidate’s votes transfer to remaining parties."""
    flows = {}
    if eliminated == "Greens":
        flows["Labor"] = 0.85; flows["CLP"] = 0.15
    elif eliminated == "One Nation":
        flows["CLP"] = 0.75; flows["Labor"] = 0.25
    elif eliminated == "UAP":
        flows["CLP"] = 0.64; flows["Labor"] = 0.36
    elif eliminated == "Lib Dems":
        flows["CLP"] = 0.73; flows["Labor"] = 0.27
    elif eliminated == "Independent":
        flows["Labor"] = 0.67; flows["CLP"] = 0.33
    elif eliminated == "Citizens":
        flows["Labor"] = 0.56; flows["CLP"] = 0.44
    else:
        # Even distribution if no specific rule
        flows = {a: 1 / len(active) for a in active}
    # Keep only active parties
    flows = {a: flows.get(a, 0) for a in active}
    total_flow = sum(flows.values())
    if total_flow > 0:
        flows = {k: v / total_flow for k, v in flows.items()}
    return flows

# --- RCV elimination rounds ---
active = set(votes.keys())
rounds = []
while True:
    remaining_total = sum(votes[c] for c in active)
    leader = max(active, key=lambda c: votes[c])
    if votes[leader] > 50:
        winner = leader
        break
    # Eliminate lowest
    loser = min(active, key=lambda c: votes[c])
    eliminated_votes = votes[loser]
    active.remove(loser)
    # Transfer eliminated votes
    flows = transfer(loser, active)
    for cand, frac in flows.items():
        votes[cand] += eliminated_votes * frac
    rounds.append((loser, eliminated_votes, flows.copy()))

# --- Display results ---
st.subheader("Elimination Rounds")
for i, (loser, eliminated_votes, flows) in enumerate(rounds, start=1):
    st.write(f"**Round {i}**: Eliminated {loser} "
             f"({eliminated_votes:.1f}% of vote).")
    st.write(f"Transferred: " + ", ".join([f"{cand} +{eliminated_votes*frac:.1f}%" 
                                          for cand, frac in flows.items()]))

st.success(f"🏆 Final Winner: **{winner}** with {votes[winner]:.1f}% of the vote")
