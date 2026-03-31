import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Page configuration
st.set_page_config(
    page_title="IT Job Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("IT Job Analysis Dashboard")
st.markdown("**Powered by PostgreSQL & Python** 🐘")
st.markdown("---")

# Connect and load data from PostgreSQL
@st.cache_data(ttl=600) # Refresh every 10 minutes
def load_data_from_db():
    DB_USER = 'postgres'
    DB_PASSWORD = 'postgres' 
    DB_HOST = 'postgres'
    DB_PORT = '5432'
    DB_NAME = 'IT_job_data'
    
    try:
        # Create connection
        engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
        
        # SQL Query to fetch all data from the it_jobs table
        query = "SELECT * FROM it_jobs;"
        df = pd.read_sql(query, engine)
        
        return df
    except Exception as e:
        st.error(f"❌ Database connection error: {e}")
        return pd.DataFrame()

# Load data
df = load_data_from_db()

if df.empty:
    st.warning("No data available in the database. Please run the ETL pipeline first!")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("🔍 Filters")
    positions = ["All"] + sorted(df["position_search"].unique().tolist())
    selected_position = st.selectbox("Select Job Position:", positions)

# Filter data based on selection
if selected_position != "All":
    filtered_df = df[df["position_search"] == selected_position]
else:
    filtered_df = df

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Number of Jobs", len(filtered_df))
col2.metric("Selected Position", selected_position)

st.markdown("---")

# Display job list
st.subheader(f"List of jobs: ({len(filtered_df)} jobs)")

for index, row in filtered_df.iterrows():
    with st.container():
        st.markdown(f"### [{row['job_name']}]({row['job_link']})")

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"🏢 **Company:** {row['company']}")
        c2.markdown(f"📍 **Location:** {row['location']}")
        c3.markdown(f"💰 **Salary:** {row['salary']}")
        c4.markdown(f"🧠 **Experience:** {row['experience']}")

        with st.expander("View Job Description Details"):
            if pd.notna(row['job_description']) and row['job_description'] != "N/A":
                st.markdown(row['job_description'])
            else:
                st.warning("No information available.")
        
        st.divider()