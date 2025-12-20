import json
import streamlit as st
from github import Github
from .config import JSON_FILE, REPO_NAME

def load_data():
    """Loads the JSON data from local file."""
    try:
        with open(JSON_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json_to_github(new_data):
    """Saves the updated JSON to GitHub."""
    token = st.secrets.get("GITHUB_TOKEN")
    if not token:
        st.error("GITHUB_TOKEN not found.")
        return False
    try:
        g = Github(token)
        user = g.get_user()
        repo = user.get_repo(REPO_NAME)
        # Note: We need to be careful with the path in the repo. 
        # If the repo structure matches local, it should be data/ticker_data.json
        # But previously it was likely in root. 
        # For now, let's assume we want to update it where it was or where it should be.
        # If we moved it locally, we should probably update it in the same relative path in repo if we want to mirror.
        # However, the previous code used JSON_FILE which was just "ticker_data.json".
        # Now JSON_FILE is absolute path. We need the relative path for GitHub.
        
        repo_path = "data/ticker_data.json" # Assuming we want to enforce this structure in repo too.
        
        try:
            contents = repo.get_contents(repo_path)
        except:
            # If not in data/, try root
            try:
                contents = repo.get_contents("ticker_data.json")
            except:
                st.error("Could not find ticker_data.json in repo.")
                return False

        new_content = json.dumps(new_data, indent=2)
        repo.update_file(contents.path, "Update ticker_data.json via Streamlit", new_content, contents.sha)
        return True
    except Exception as e:
        st.error(f"Error saving to GitHub: {e}")
        return False

def save_local_data(data):
    """Saves data to local JSON file."""
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=2)
