import streamlit as st
import requests
import re
import pandas as pd

# Metadata
st.title("Sleeper Draft Tracker")

# User Inputs
draft_id = st.text_input("Sleeper Draft ID")
tier_txt = st.text_area("Tier String")

# Get Sleeper Players
@st.cache_data
def get_players():
    return requests.get("https://api.sleeper.app/v1/players/nfl").json()

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

def tiers():
    names_first = {player.get("search_full_name", None): ply_id for ply_id, player in sleeper_players.items()}

    ## Process Tier Input
    tier_split = "\s+Tier [0-9]*:\s+"
    split_tiers = re.split(tier_split, tier_txt)
    split_tiers.pop(0) # Drop first empty entry

    tier_labels = []
    tier_players = []
    for i, tierlist in enumerate(split_tiers, start=1):
        tier_labels.append(f"tier{i}")
        tier_players.append([int(names_first.get(clean_player_name(player))) for player in re.split(',', tierlist) if names_first.get(clean_player_name(player)) is not None])

    return dict(zip(tier_labels, tier_players))

sleeper_players = get_players()
tier_players = tiers()

# Update drafted players
draft_data = requests.get(f"https://api.sleeper.app/v1/draft/{draft_id}/picks").json()
drafted_players = [player["player_id"] for player in draft_data]

# Print Tiers
for tier, players in tier_players.items():
    tier_players = {}
    for player in players:
        tier_players[sleeper_players.get(str(player))["full_name"]] = sleeper_players.get(str(player))
    print(tier_players)
    cur_dataframe = pd.DataFrame.from_dict(tier_players, orient='index')
    st.subheader(tier)
    st.dataframe(cur_dataframe[["position", "team", "injury_status"]])
    



