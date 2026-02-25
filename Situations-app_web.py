import streamlit as st
import pandas as pd
import random

# Set Page Config for Mobile
st.set_page_config(page_title="USA Swimming Study Tool", layout="centered")

# --- DATA LOADING ---
@st.cache_data # This keeps the app fast by loading data only once
def load_data():
    # Note: When you deploy this, the Excel file must be in the same folder as the script
    file_path = "Situations-n-Resolutions-with-sections.xlsx"
    df = pd.read_excel(file_path)
    df.columns = [c.strip() for c in df.columns]
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load Excel file. Please ensure it is in the app folder. Error: {e}")
    st.stop()

# --- APP UI ---
st.title("🏊 USA Swimming Officials")
st.subheader("Stroke & Turn Study Tool")

# Sidebar for Mode Selection
mode = st.sidebar.radio(
    "Choose a Study Mode:",
    ["Review by Section", "Sequential Review", "Search by Number", "Total Random Shuffle"]
)

# Initialize Session State (to keep track of the current situation across button clicks)
if 'current_index' not in st.session_state:
    st.session_state.current_index = None
if 'show_resolution' not in st.session_state:
    st.session_state.show_resolution = False

def get_new_situation(filtered_df):
    st.session_state.current_index = filtered_df.sample(n=1).index[0]
    st.session_state.show_resolution = False

# --- MODE 1: REVIEW BY SECTION ---
if mode == "Review by Section":
    sections = sorted(df['Section'].dropna().unique())
    selected_section = st.selectbox("Select Section:", sections)
    
    section_df = df[df['Section'] == selected_section]
    
    if st.button("Get Random Situation") or st.session_state.current_index is None:
        get_new_situation(section_df)

# --- MODE 2: SEQUENTIAL REVIEW ---
elif mode == "Sequential Review":
    sections = sorted(df['Section'].dropna().unique())
    selected_section = st.selectbox("Select Section:", sections)
    
    section_df = df[df['Section'] == selected_section].sort_values(by='Number')
    
    # Simple slider or number input to move through the section
    idx_in_list = st.number_input("Item Number in List", min_value=1, max_value=len(section_df), step=1)
    st.session_state.current_index = section_df.index[idx_in_list - 1]

# --- MODE 3: SEARCH BY NUMBER ---
elif mode == "Search by Number":
    num_search = st.text_input("Enter Situation Number (e.g., 12):")
    if num_search:
        results = df[df['Number'].astype(str).str.strip() == num_search.strip()]
        if not results.empty:
            st.session_state.current_index = results.index[0]
        else:
            st.warning("Situation number not found.")

# --- MODE 4: TOTAL RANDOM ---
elif mode == "Total Random Shuffle":
    if st.button("Shuffle Next") or st.session_state.current_index is None:
        get_new_situation(df)

# --- DISPLAY THE CARD ---
if st.session_state.current_index is not None:
    row = df.loc[st.session_state.current_index]
    
    st.markdown("---")
    st.info(f"**SECTION: {row['Section']}  #{row['Number']}**")
    st.write(f"### Situation:")
    st.write(row['Situation'])
    
    if st.button("Show Resolution"):
        st.session_state.show_resolution = True
        
    if st.session_state.show_resolution:
        st.success(f"**Recommended Resolution:**\n\n{row['Recommended resolution']}")
        st.warning(f"**Applicable Rule:** {row['Applicable Rule']}")