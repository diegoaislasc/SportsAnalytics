import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from datetime import date
import os

# Page Config
st.set_page_config(page_title="EPL Predictor", layout="wide")

# Initialize BigQuery Client
@st.cache_resource
def get_bq_client():
    # Load credentials explicitly to avoid environment issues
    creds_path = ".dbt/dbt-user-creds.json"
    if os.path.exists(creds_path):
        credentials = service_account.Credentials.from_service_account_file(creds_path)
        return bigquery.Client(credentials=credentials, project="sportsanalytics-mlops")
    else:
        # Fallback if running elsewhere, though likely to fail if env vars aren't set
        return bigquery.Client(project="sportsanalytics-mlops")

client = get_bq_client()

# --- Helper Functions ---
@st.cache_data(ttl=3600)
def get_teams():
    query = """
        SELECT distinct team_name 
        FROM `sportsanalytics-mlops.intermediate.int_team_history_spine`
        ORDER BY 1
    """
    return client.query(query).to_dataframe()['team_name'].tolist()

def get_latest_stats(team_name, match_date):
    """Fetches the latest rolling stats for a team prior to the given date."""
    query = f"""
        WITH team_id_lookup AS (
            SELECT DISTINCT team_id 
            FROM `sportsanalytics-mlops.intermediate.int_team_history_spine`
            WHERE team_name = '{team_name}'
        )
        SELECT 
            rolling_5_goals_for,
            rolling_5_xg_for,
            rolling_5_points,
            season_avg_xg_for,
            season_total_points
        FROM `sportsanalytics-mlops.intermediate.int_team_rolling_stats` stats
        JOIN team_id_lookup t ON stats.team_id = t.team_id
        WHERE match_date < '{match_date}'
        ORDER BY match_date DESC
        LIMIT 1
    """
    df = client.query(query).to_dataframe()
    if df.empty:
        return None
    return df.iloc[0]

def predict_match(home_team, away_team, match_date):
    home_stats = get_latest_stats(home_team, match_date)
    away_stats = get_latest_stats(away_team, match_date)
    
    if home_stats is None or away_stats is None:
        return None, "Insufficient historical data for one or both teams."
        
    # Prepare Input for BQML Model
    # We need to construct a SQL query that selects the features and calls ML.PREDICT
    
    points_diff = home_stats['season_total_points'] - away_stats['season_total_points']
    
    predict_query = f"""
        SELECT * FROM ML.PREDICT(MODEL `sportsanalytics-mlops.marts.match_winner_model`, (
            SELECT 
                {home_stats['rolling_5_goals_for']} as home_form_goals,
                {home_stats['rolling_5_xg_for']} as home_form_xg,
                {home_stats['rolling_5_points']} as home_form_points,
                {home_stats['season_avg_xg_for']} as home_season_xg,
                CAST({home_stats['season_total_points']} as INT64) as home_season_points,
                
                {away_stats['rolling_5_goals_for']} as away_form_goals,
                {away_stats['rolling_5_xg_for']} as away_form_xg,
                {away_stats['rolling_5_points']} as away_form_points,
                {away_stats['season_avg_xg_for']} as away_season_xg,
                CAST({away_stats['season_total_points']} as INT64) as away_season_points,
                
                CAST({points_diff} as INT64) as points_diff
        ))
    """
    
    results = client.query(predict_query).to_dataframe()
    return results, None

# --- UI Layout ---
st.title("Sports Analytics Platform")

# Sidebar for Navigation
st.sidebar.title("Leagues")
league = st.sidebar.radio("Select League", ["EPL (English Premier League)", "NBA (Coming Soon)", "NFL (Coming Soon)", "MLB (Coming Soon)"])

if league == "EPL (English Premier League)":
    # League Logo
    st.image("images/epl-logo.png", width=300)
        
    # Sub-navigation for EPL
    page = st.sidebar.selectbox("EPL Modules", ["The Oracle (Predictor)", "Analytics Dashboards"])

    if page == "The Oracle (Predictor)":
        st.header("EPL Predictor")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            match_date = st.date_input("Match Date", min_value=date(2020, 1, 1), value=date.today())
        
        with col2:
            home_team = st.selectbox("Home Team", get_teams(), index=0)
            
        with col3:
            away_team = st.selectbox("Away Team", get_teams(), index=1)
            
        if st.button("Generate Prediction", type="primary"):
            if home_team == away_team:
                st.error("Home and Away teams must be different.")
            else:
                with st.spinner("Consulting the Oracle..."):
                    prediction_df, error = predict_match(home_team, away_team, match_date)
                    
                    if error:
                        st.error(error)
                    else:
                        # Parse Results
                        predicted_label = prediction_df['predicted_label'][0]
                        probs = prediction_df['predicted_label_probs'][0]
                        
                        # Find probabilities for each outcome
                        prob_home = next((item['prob'] for item in probs if str(item['label']) == '1'), 0)
                        prob_draw = next((item['prob'] for item in probs if str(item['label']) == '3'), 0)
                        prob_away = next((item['prob'] for item in probs if str(item['label']) == '2'), 0)
                        
                        # Display Metrics
                        st.success("Prediction Generated!")
                        
                        m_col1, m_col2, m_col3 = st.columns(3)
                        m_col1.metric("Home Win", f"{prob_home:.1%}")
                        m_col2.metric("Draw", f"{prob_draw:.1%}")
                        m_col3.metric("Away Win", f"{prob_away:.1%}")
                        
                        # Winner Highlight
                        winner_map = {'1': home_team, '2': away_team, '3': 'Draw'}
                        st.subheader(f"Predicted Winner: {winner_map.get(str(predicted_label))}")
                        
                        # Progress Bars
                        st.write(f"**{home_team}**")
                        st.progress(float(prob_home))
                        
                        st.write(f"**Draw**")
                        st.progress(float(prob_draw))
                        
                        st.write(f"**{away_team}**")
                        st.progress(float(prob_away))

    elif page == "Analytics Dashboards":
        st.header("📊 EPL Analytics Suite")
        
        # Embed Looker Studio Report
        st.markdown("### Interactive Dashboard")
        
        iframe_code = """
        <iframe width="100%" height="900" 
        src="https://lookerstudio.google.com/embed/reporting/894ccc07-6497-4bcd-a9ad-336bc61257d2/page/p_d3lxuaqdzd" 
        frameborder="0" style="border:0" allowfullscreen 
        sandbox="allow-storage-access-by-user-activation allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox"></iframe>
        """
        st.components.v1.html(iframe_code, height=900, scrolling=True)

else:
    st.info(f"🚧 The {league.split(' ')[0]} module is currently under development. Check back soon!")


