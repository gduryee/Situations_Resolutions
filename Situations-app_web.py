import streamlit as st
import pandas as pd
from streamlit_js_eval import streamlit_js_eval

# Set Page Config
st.set_page_config(page_title="USA Swimming Officials - Situations & Resolutions", layout="centered")

image = 'USA_Swimming_Logo.svg'
css = f'''
<style>
    /* 1. Remove padding from the main content area */
    .block-container {{
        padding-top: 0rem;
        padding-bottom: 0rem;
        margin-top: -2rem; /* Forces content higher */
    }}

    /* 2. Hide the header/decoration bar at the top 
    header {{
        visibility: hidden;
        height: 0px;
    }}*/

    /* 3. Keep your background image logic 
    .stApp {{
        background-image: url({image});
        background-size: cover;
    }}
    .stApp > header {{
        background-color: transparent;
    }}*/
</style>
'''
st.markdown(css, unsafe_allow_html=True)

# Get dimensions to determine Orientation. This is used to control formating where needed.
def get_orientation_mode():
    # Use a static key. streamlit_js_eval will still update the values 
    # if the user rotates their phone.
    width = streamlit_js_eval(js_expressions='screen.width', key='WIDTH_STATIC')
    height = streamlit_js_eval(js_expressions='screen.height', key='HEIGHT_STATIC')

    if width is not None and height is not None:
        if width < height:
            return "Portrait"
        else:
            return "Landscape"
    # Default to Portrait if JS hasn't loaded yet
    return "Portrait"

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
# always_show = st.sidebar.checkbox("Always show resolution", value=False)
# Change to 'Hide' - default is False (so it shows by default)
hide_resolution = st.sidebar.checkbox("Hide resolution", value=False)

# Font Size Slider
font_size = st.sidebar.slider("Adjust Font Size", min_value=14, max_value=36, value=18)

orientation_mode = get_orientation_mode()
#st.write(f"Orientation Mode: {orientation_mode}")

# --- SESSION STATE MANAGEMENT ---
if 'current_index' not in st.session_state:
    st.session_state.current_index = None
if 'show_resolution_clicked' not in st.session_state:
    st.session_state.show_resolution_clicked = False

# def get_new_situation(filtered_df):
#     st.session_state.current_index = filtered_df.sample(n=1).index[0]
#     st.session_state.show_resolution_clicked = False

def get_new_situation(filtered_df):
    # Check if the dataframe actually has data
    if filtered_df is not None and len(filtered_df) > 0:
        st.session_state.current_index = filtered_df.sample(n=1).index[0]
        st.session_state.show_resolution_clicked = False
    else:
        # If empty, reset the index so no card is shown
        st.session_state.current_index = None

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
        st.markdown("<h2 style='text-align: center; margin-top: -20px;'>USA Swimming Officials</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; margin-top: -10px;'>Situations & Resolutions</h4>", unsafe_allow_html=True)
        st.markdown("<h5 style='text-align: center; margin-top: -10px;'>Stroke & Turn</h5>", unsafe_allow_html=True)
    with header_col3:
        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
        st.image("pns_logo.png", width=100)
        st.markdown('</div>', unsafe_allow_html=True)

def portrait_title_mode():
     with st.container(horizontal_alignment="center"):
        st.image("USA_Swimming_Logo.svg", width=100)
        # Reduced margin-top on the first title
        st.markdown("<h3 style='text-align: center; margin-top: -20px;'>USA Swimming Officials</h3>", unsafe_allow_html=True)
        st.markdown("<h5 style='text-align: center; margin-top: -10px;'>Situations & Resolutions</h5>", unsafe_allow_html=True)
        st.markdown("<h5 style='text-align: center; margin-top: -10px;'>Stroke & Turn</h5>", unsafe_allow_html=True)

# --- APP UI (Mobile Friendly) ---
if orientation_mode == "Portrait":
    portrait_title_mode()
else:
    landscape_title_mode()

# --- HELPER FOR MODE 2 WRAPPING ---
def handle_seq_change():
    # This runs the second the user clicks +/-
    val = st.session_state.seq_num_input
    total = st.session_state.max_items_in_section
    
    if val > total:
        st.session_state.seq_num_input = 1
    elif val < 1:
        st.session_state.seq_num_input = total

# --- MODE 1: Review BY STROKE/TOPIC ---
if mode == "Review by Stroke/Topic":
    stroke_topic_list = sorted(df['Stroke'].dropna().unique())
    
    # Selection
    selected_stroke_topic = st.segmented_control("Select Stroke/Topic:", stroke_topic_list)
    
    if selected_stroke_topic:
        section_df = df[df['Stroke'] == selected_stroke_topic]
        
        # Double check that we actually found rows for this stroke
        if not section_df.empty:
            # Load new situation if none is selected OR if the stroke changed
            if st.session_state.current_index is None or \
               st.session_state.current_index not in section_df.index:
                get_new_situation(section_df)

            if st.button("Get Another Random Situation"):
                get_new_situation(section_df)
        else:
            st.warning(f"No situations found for {selected_stroke_topic}")
    else:
        # User hasn't clicked a segment yet
        st.info("Tap a Stroke/Topic above to start.")
        st.session_state.current_index = None

# --- MODE 2: SEQUENTIAL REVIEW ---
elif mode == "Sequential Review":
    stroke_topic_list = sorted(df['Stroke'].dropna().unique())
    selected_stroke_topic = st.segmented_control("Select Stroke/Topic:", stroke_topic_list, key="seq_seg")
    
    if selected_stroke_topic:
        section_df = df[df['Stroke'] == selected_stroke_topic].sort_values(by='Number')
        total_items = len(section_df)
        
        # Store the max items in session state so the callback can see it
        st.session_state.max_items_in_section = total_items

        # --- RESET LOGIC ---
        # If the stroke changed, force the number input back to 1
        if "last_selected_stroke" not in st.session_state:
            st.session_state.last_selected_stroke = selected_stroke_topic
            
        if st.session_state.last_selected_stroke != selected_stroke_topic:
            st.session_state.seq_num_input = 1
            st.session_state.last_selected_stroke = selected_stroke_topic

        # --- THE WRAPPING WIDGET ---
        # We use the 'on_change' callback to trigger the wrap-around math
        current_val = st.number_input(
            f"Item (1 of {total_items})", 
            min_value=0, 
            max_value=total_items + 1, 
            step=1, 
            key="seq_num_input",
            on_change=handle_seq_change
        )

        # Map the widget value to the actual dataframe index
        # (Using max/min as a safety net if the callback is mid-process)
        safe_val = max(1, min(current_val, total_items))
        new_index = section_df.index[safe_val - 1]
        
        if st.session_state.current_index != new_index:
            st.session_state.current_index = new_index
            st.session_state.show_resolution_clicked = False
    else:
        st.info("Please select a Stroke/Topic.")
        st.session_state.current_index = None

# --- MODE 3: Search by Number ---
elif mode == "Search by Number":
    # We explicitly set this to None if they haven't searched yet 
    # so the old card from the previous mode disappears.
    # find the min and max numbers in the dataset to guide the user on valid inputs
    min_num = int(df['Number'].min())
    max_num = int(df['Number'].max())
    
    st.write(f"Available Situations: **{min_num} to {max_num}**")
    num_search = st.text_input("Enter Situation Number:", placeholder=f"e.g. {min_num}")

    #num_search = st.text_input("Enter Situation Number:")
    
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
    
    # The resolution should show if NOT hidden OR if the manual button was clicked
    should_show = (not hide_resolution) or st.session_state.show_resolution_clicked

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
def landscape_footer_mode():
    st.markdown("---") # Adds a horizontal line to separate the content from the footer
    st.markdown(
            """
            <div style="text-align: center; color: grey; font-size: 14px;">
                © 2025 USA Swimming <br>
                National Officials Committee, Version 03/07/2025<br>
            </div>
            """, 
            unsafe_allow_html=True
    )

def portrait_footer_mode():
    with st.container(horizontal_alignment="center"):
        st.markdown("---") # Adds a horizontal line to separate the content from the footer
        st.image("pns_logo.png", width=100)
        st.markdown(
            """
            <div style="text-align: center; color: grey; font-size: 14px;">
                © 2025 USA Swimming <br>
                National Officials Committee, Version 03/07/2025<br>
            </div>
            """, 
            unsafe_allow_html=True
        )

# --- Footer - Check Orientationa and set footer ---
# orientation_mode = get_orientation_mode()
#st.write(f"Orientation Mode: {orientation_mode}")
if orientation_mode == "Portrait":
    portrait_footer_mode()
else:
    landscape_footer_mode()