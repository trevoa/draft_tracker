import streamlit as st
import requests
import re
import pandas as pd

# Metadata
st.title(":football: Sleeper Draft Tracker")

# User Inputs
with st.sidebar:
    draft_id = st.text_input("Sleeper Draft ID")
    tier_txt = st.text_area("Tier String")

draft_status = requests.get(f"https://api.sleeper.app/v1/draft/{draft_id}/picks").json()
col1, col2 = st.columns(2)
with col1:
    st.metric(label=":clock1: Round", value=draft_status[-1]["round"])
with col2:
    st.metric(label=":hourglass: Pick", value=int(draft_status[-1]["pick_no"])+1)

st.button("Update", on_click=st.experimental_rerun)

# Utility functions
def clean_player_name(name):
    pass1 = name.strip().lower()
    splitname = pass1.split()
    fullname = splitname[0] + splitname[1]
    pass2 = ''.join(letter for letter in fullname if letter.isalnum())
    return pass2

def find_player_id(name: str, data: dict):
    name_split = re.split("\s", name)
    firstname = name_split[0]; lastname = name_split[1]
    fullname = firstname.lower() + lastname.lower()
    player_id = data.get(fullname)
    try:
        return(int(player_id))
    except:
        return None

# Update data
@st.cache_data
def get_players():
    return requests.get("https://api.sleeper.app/v1/players/nfl").json()

sleeper_players = get_players()

positions = ["QB", "RB", "WR", "K", "TE", ]
def tiers():
    names_first = {player.get("search_full_name", None): ply_id for ply_id, player in sleeper_players.items() if player.get("team") is not None and player.get("position") in positions}

    ## Process Tier Input
    tier_split = "\s+Tier [0-9]*:\s+"
    split_tiers = re.split(tier_split, tier_txt)
    split_tiers.pop(0) # Drop first empty entry

    tier_labels = []
    tier_players = []
    for i, tierlist in enumerate(split_tiers, start=1):
        tier_labels.append(f"Tier {i}")
        tier_players.append([int(names_first.get(clean_player_name(player))) for player in re.split(',', tierlist) if names_first.get(clean_player_name(player)) is not None])
        
        # Update drafted players
        draft_data = requests.get(f"https://api.sleeper.app/v1/draft/{draft_id}/picks").json()
        drafted_players = [player["player_id"] for player in draft_data]

        # strip drafted players
        for tier in tier_players:
            for player in tier:
                # print(player)
                # print(drafted_players)
                if str(player) in drafted_players:
                    tier.remove(player)

    return dict(zip(tier_labels, tier_players))

tier_data = tiers()

# Print Tiers
for tier, players in tier_data.items():
    tier_data2 = {}
    for player in players:
        tier_data2[sleeper_players.get(str(player))["full_name"]] = sleeper_players.get(str(player))
    cur_dataframe = pd.DataFrame.from_dict(tier_data2, orient='index')
    if not cur_dataframe.empty:
        st.divider()
        st.subheader(tier)
        st.dataframe(cur_dataframe[["position", "team", "age", "injury_status"]], use_container_width=True)
