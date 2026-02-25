import streamlit as st
import pandas as pd
from streamlit_js_eval import streamlit_js_eval

# Set Page Config
st.set_page_config(page_title="USA Swimming Officials", layout="centered")

image = 'USA_Swimming_Logo.svg'

css = f'''
<style>
    .stApp {{
        background-image: url({image});
        background-size: cover;

    }}
    .stApp > header {{
        background-color: transparent;
    }}
</style>
'''
st.markdown(css, unsafe_allow_html=True)


# st.markdown("""
#     <style>
#     /* Force images to center on mobile */
#     [data-testid="stImage"] {
#         display: flex;
#         justify-content: center;
#     }
#     </style>
#     """, unsafe_allow_html=True)

# Get viewport dimensions
def get_orientation_mode():
    #size = get_window_size()
    #if size:
    # Get width and height via JavaScript
    width = streamlit_js_eval(js_expressions='screen.width', key='WIDTH')
    height = streamlit_js_eval(js_expressions='screen.height', key='HEIGHT')

    if width is not None and height is not None:
        # Determine orientation
        if width < height:
            orientation = "Portrait"
        else:
            orientation = "Landscape"
        #st.write(f"Device Orientation: {orientation}")

        # Force rerun to update if orientation changes (optional)
    # if 'last_orient' not in st.session_state:
    #     st.session_state['last_orient'] = orientation
        
    # if st.session_state['last_orient'] != orientation:
    #     st.session_state['last_orient'] = orientation
    #     st.rerun()
    return orientation

@st.cache_data
def load_data():
    file_path = "Situations-n-Resolutions-with-sections.xlsx"
    df = pd.read_excel(file_path)
    df.columns = [c.strip() for c in df.columns]
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading Excel: {e}")
    st.stop()

def landscape_title_mode():
    # Use columns for desktop. On mobile, Streamlit will stack these 
    # if the screen is narrow enough, but we'll optimize the content.
    header_col1, header_col2, header_col3 = st.columns([1, 2, 1])

    with header_col1:
        # On mobile, we center the image using a div
        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
        st.image("USA_Swimming_Logo.svg", width=100) # Slightly smaller for mobile
        st.markdown('</div>', unsafe_allow_html=True)

    with header_col2:
        st.markdown("<h2 style='text-align: center; margin-bottom: 0px;'>USA Swimming Officials</h2>", unsafe_allow_html=True)
        # Adding a sub-header that stays close to the main title
        st.markdown("<h5 style='text-align: center; '\
                >Situations & Resolutions</h5>", unsafe_allow_html=True)
        st.markdown("<h5 style='text-align: center; '\
                >Stroke & Turn</h5>", unsafe_allow_html=True)
    with header_col3:
        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
        st.image("pns_logo.png", width=100)
        st.markdown('</div>', unsafe_allow_html=True)


def mobile_title_mode():
    # Use columns for desktop. On mobile, Streamlit will stack these 
    # if the screen is narrow enough, but we'll optimize the content.
    # On mobile, we center the image using a div
    header_col1, header_col2 = st.columns(2)

    with header_col1:
        # On mobile, we center the image using a div
        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
        st.image("USA_Swimming_Logo.svg", width=50) # Slightly smaller for mobile
        st.markdown('</div>', unsafe_allow_html=True)
    with header_col2:
        # On mobile, we center the image using a div
        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
        st.image("pns_logo.png", width=50)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>USA Swimming Officials</h3>", unsafe_allow_html=True)
    # Adding a sub-header that stays close to the main title

    st.markdown("<h5 style='text-align: center; margin-bottom: 0px;'\
                >Situations & Resolutions</h5>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center; margin-bottom: 0px;'\
                >Stroke & Turn</h5>", unsafe_allow_html=True)

# --- APP UI (Mobile Friendly) ---
orientation_mode = get_orientation_mode()
#st.write(f"Orientation Mode: {orientation_mode}")
if orientation_mode == "Portrait":
    mobile_title_mode()
else:
    landscape_title_mode()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
mode = st.sidebar.radio(
    "Choose a Study Mode:",
    ["Review by Stroke/Topic", "Sequential Review", "Search by Number", "Total Random Shuffle"]
)

# --- MODE SWITCH DETECTION ---
if 'last_mode' not in st.session_state:
    st.session_state.last_mode = mode

# If the mode changed, clear the current card so the new mode can generate its own
if st.session_state.last_mode != mode:
    st.session_state.current_index = None
    st.session_state.show_resolution_clicked = False
    st.session_state.last_mode = mode

# --- SIDEBAR OPTIONS ---
st.sidebar.markdown("---")
st.sidebar.subheader("Options")
always_show = st.sidebar.checkbox("Always show resolution", value=False)

# Font Size Slider
font_size = st.sidebar.slider("Adjust Font Size", min_value=14, max_value=36, value=18)

# --- SESSION STATE MANAGEMENT ---
if 'current_index' not in st.session_state:
    st.session_state.current_index = None
if 'show_resolution_clicked' not in st.session_state:
    st.session_state.show_resolution_clicked = False

def get_new_situation(filtered_df):
    st.session_state.current_index = filtered_df.sample(n=1).index[0]
    st.session_state.show_resolution_clicked = False

# --- MODE 1: Review BY STROKE/TOPIC ---
if mode == "Review by Stroke/Topic":
    stroke_topic_list = sorted(df['Stroke'].dropna().unique())
    selected_stroke_topic = st.selectbox("Select Stroke/Topic:", stroke_topic_list)
    
    # Filter the dataframe for the selection
    section_df = df[df['Stroke'] == selected_stroke_topic]
    
    # Check if we need to load a situation for the first time 
    # OR if the user just switched strokes in the dropdown
    if st.session_state.current_index is None or df.loc[st.session_state.current_index]['Stroke'] != selected_stroke_topic:
        get_new_situation(section_df)

    # We keep the button so the user can "reroll" a new random item 
    # within the same stroke without changing the dropdown.
    if st.button("Get Another Random Situation"):
        get_new_situation(section_df)

# --- MODE 2: SEQUENTIAL REVIEW ---
elif mode == "Sequential Review":
    stroke_topic = sorted(df['Stroke'].dropna().unique())
    selected_stroke_topic = st.selectbox("Select Stroke/Topic:", stroke_topic)
    
    section_df = df[df['Stroke'] == selected_stroke_topic].sort_values(by='Number')
    
    # Use a key for the number input so Streamlit tracks it better
    idx_in_list = st.number_input("Item Number", min_value=1, max_value=len(section_df), step=1, key="seq_num")
    
    new_index = section_df.index[idx_in_list - 1]
    
    # If the user moves to a new item, reset the "Show Resolution" button state
    if st.session_state.current_index != new_index:
        st.session_state.current_index = new_index
        st.session_state.show_resolution_clicked = False

# # --- MODE 3: Search by Number ---
# elif mode == "Search by Number":
#     num_search = st.text_input("Enter Situation Number:")
#     if num_search:
#         results = df[df['Number'].astype(str).str.strip() == num_search.strip()]
#         if not results.empty:
#             st.session_state.current_index = results.index[0]
#         else:
#             st.warning("Number not found.")

# --- MODE 3: Search by Number ---
elif mode == "Search by Number":
    # We explicitly set this to None if they haven't searched yet 
    # so the old card from the previous mode disappears.
    num_search = st.text_input("Enter Situation Number:")
    
    if not num_search:
        st.session_state.current_index = None
    else:
        results = df[df['Number'].astype(str).str.strip() == num_search.strip()]
        if not results.empty:
            st.session_state.current_index = results.index[0]
        else:
            st.warning("Number not found.")
            st.session_state.current_index = None


# --- MODE 4: Total Random Shuffle ---
elif mode == "Total Random Shuffle":
    # If we just switched to this mode and don't have a situation yet, 
    # or if the previous situation was locked into a specific stroke, grab a new random one.
    if st.session_state.current_index is None:
        get_new_situation(df)
    
    # Optional: If you want a fresh shuffle every time you click the sidebar 'Total Random Shuffle' 
    # even if you were already in it, we can trigger it here.
    
    if st.button("Shuffle Next", key="shuffle_btn"):
        get_new_situation(df)

# --- DISPLAY CARD ---
if st.session_state.current_index is not None:
    row = df.loc[st.session_state.current_index]
    
    st.markdown("---")
    st.info(f"**Stroke/Topic: {row['Stroke']}  #{row['Number']}**")
    
    # Situation Display
    st.markdown(f'<div style="font-size: {font_size}px;"><b>Situation:</b><br>{row["Situation"]}</div>', unsafe_allow_html=True)
    
    should_show = always_show or st.session_state.show_resolution_clicked

    if not should_show:
        # We add a unique key to the button based on the index 
        # so Streamlit doesn't get confused between different situations
        if st.button("Show Resolution", key=f"btn_{st.session_state.current_index}"):
            st.session_state.show_resolution_clicked = True
            st.rerun()
    
    if should_show:
        st.write("") 
        st.success("Recommended Resolution:")
        st.markdown(f'<div style="font-size: {font_size}px;">{row["Recommended resolution"]}</div>', unsafe_allow_html=True)
        
        st.warning(f"**Applicable Rule:**")
        st.markdown(f'<div style="font-size: {font_size}px;">{row["Applicable Rule"]}</div>', unsafe_allow_html=True)


# --- FOOTER ---
st.markdown("---") # Adds a horizontal line to separate the content from the footer
st.markdown(
    """
    <div style="text-align: center; color: grey; font-size: 14px;">
        © USA Swimming, National Officials Committee, Version 03/07/2025<br>
    </div>
    """, 
    unsafe_allow_html=True
)