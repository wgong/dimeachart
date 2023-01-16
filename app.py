# streamlit_app.py

import streamlit as st
from supabase import create_client  # , Client
from streamlit_supabase_auth import login_form, logout_button

@st.experimental_memo(ttl=600)
def get_config(is_local=True, toml_file=".streamlit/secrets.toml"):
    cfg = {}
    try:
        if is_local:
            import toml
            cfg = toml.load(toml_file)
        else:
            cfg = {
                "supabase_url": st.secrets["supabase_url"],
                "supabase_key": st.secrets["supabase_key"],
                "table_user": st.secrets["table_user"],
            }
    except Exception as e:
        st.error(f"{str(e)}")
    return cfg

cfg = get_config(is_local=True)
if not cfg:
    st.error("Failed to get_config()")
    st.stop()

session = login_form(
    url=cfg.get("supabase_url",""),
    apiKey=cfg.get("supabase_key",""),
    providers=["apple", "facebook", "github", "google"],
)
if not session:
    st.warning("Not signed in!")
    st.stop()

# Update query param to reset url fragments
st.experimental_set_query_params(page=["success"])
with st.sidebar:
    st.write(f"Welcome {session['user']['email']}")
    logout_button()

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def get_supabase_client():
    url = cfg.get("supabase_url","")
    key = cfg.get("supabase_key","")
    return create_client(url, key)

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
# @st.experimental_memo(ttl=600)
def run_query():
    supabase = get_supabase_client()
    return supabase.table(cfg.get("table_user","")).select("*").execute()

# disable RLS on Supabase table, otherwise, rows is empty
rows = run_query()
# Print results.
st.json(rows.data)