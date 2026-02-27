import streamlit as st
import pandas as pd
from streamlit_js_eval import streamlit_js_eval
import base64
import os
import re

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
    }}
    */
</style>
'''
st.markdown(css, unsafe_allow_html=True)

def highlight_text(text, query):
    if not query or not isinstance(text, str):
        return text
    
    # We use a span with a background color to make it look like a highlighter pen
    # Yellow background with black text for maximum contrast
    highlight_style = (
        'background-color: #ffff00; '  # Bright Yellow
        'color: #000000; '            # Black text
        'font-weight: bold; '          # Bold
        'padding: 2px 4px; '           # Slight padding for "pill" look
        'border-radius: 3px;'          # Rounded corners
    )
    
    # re.IGNORECASE ensures we find "Foot" even if user typed "foot"
    # re.escape ensures we don't crash if user types special characters like "("
    compiled = re.compile(re.escape(query), re.IGNORECASE)
    
    # This replaces the match while preserving the original casing of the text
    return compiled.sub(lambda m: f'<span style="{highlight_style}">{m.group()}</span>', text)

def get_img_with_href(local_img_path, target_url, width=None):
    """Encodes a local image file to Base64 and wraps it in an HTML hyperlink tag.

    Args:
        local_img_path: path to the image on disk.
        target_url: href for the anchor tag.
        width: optional pixel width to apply to the <img> element. If provided,
            the image tag will include a width attribute.
    """
    # Determine the image format from the file extension
    img_format = os.path.splitext(local_img_path)[-1].replace(".", "")
    if img_format.lower() == 'svg':
        mime_type = 'image/svg+xml'
    else:
        mime_type = f'image/{img_format}'
        
    # Read and encode the file
    with open(local_img_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")

    # Build width attribute if requested
    width_attr = f' width="{width}"' if width else ''

    # Construct the HTML markdown string
    html_string = f"""
    <a href="{target_url}" target="_blank">
        <img src="data:{mime_type};base64,{b64}" alt="Linked Image"{width_attr}/>
    </a>
    """
    return html_string

# Helper function to display the USA Swimming logo with a hyperlink
def usa_swimming_logo_w_hyperlink(desired_width=100):
    width = desired_width  # Desired width of the image in pixels
    image_path = "USA_Swimming_Logo.svg"  # Local path to your image
    target_url = "https://www.usaswimming.org/"  # URL you want to link to

    # pass width through to helper, which will set the width attribute
    inner_html = get_img_with_href(image_path, target_url, width=width)

    # wrap in a centered container so the logo appears centered in the sidebar
    html_string = f'<div style="text-align: center;">{inner_html}</div>'
    st.markdown(html_string, unsafe_allow_html=True)

# Helper function to display the USA Swimming logo with a hyperlink
def pns_logo_w_hyperlink(desired_width=100):
    width = desired_width  # Desired width of the image in pixels
    image_path = "pns_logo.png"  # Local path to your image
    target_url = "https://www.pns.org/page/home"  # URL you want to link to

    # pass width through to helper, which will set the width attribute
    inner_html = get_img_with_href(image_path, target_url, width=width)

    # wrap in a centered container so the logo appears centered in the sidebar
    html_string = f'<div style="text-align: center;">{inner_html}</div>'
    st.markdown(html_string, unsafe_allow_html=True)

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

with st.sidebar:
    with st.container(horizontal_alignment="center"):
        usa_swimming_logo_w_hyperlink()
    st.markdown("---")
    st.title("Navigation")
    mode = st.sidebar.radio(
        "Choose a Study Mode:",
        ["Sequential Review", 
        "Keyword Search",
        "Search by Number", 
        "Review by Stroke/Topic", 
        "Total Random Shuffle"]
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

with st.sidebar:
    usaswimming_rulebook_url = "https://websiteprodcoresa.blob.core.windows.net/sitefinity/docs/default-source/governance/governance-lsc-website/rules_policies/rulebooks/2026-rulebook.pdf"
    st.markdown(f"[2026 USA Swimming Rulebook]({usaswimming_rulebook_url})")
    usaswimming_st_sit_resol_url = "https://www.usaswimming.org/docs/default-source/officialsdocuments/officials-training-resources/situations-and-resolutions/situations-and-resolutions-stroke-and-turn.pdf"
    st.markdown(f"[Mar. 2025 USA Swimming Situations & Resolutions - Stroke & Turn]({usaswimming_st_sit_resol_url})")

    st.markdown("---")
    pns_logo_w_hyperlink()

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

def perform_keyword_search(df, query, search_field, selected_stroke):
    if not query:
        return pd.DataFrame()
    
    # 1. Filter by Stroke/Topic if not "All"
    if selected_stroke != "All":
        filtered_df = df[df['Stroke'] == selected_stroke]
    else:
        filtered_df = df.copy()
        
    # 2. Perform text search (case-insensitive)
    q = query.lower()
    
    if search_field == "Situations":
        results = filtered_df[filtered_df["Situation"].str.lower().str.contains(q, na=False)]
    elif search_field == "Resolutions":
        results = filtered_df[filtered_df["Recommended resolution"].str.lower().str.contains(q, na=False)]
    else:  # "All" option
        # Search across both "Situations" and "Resolutions" columns
        mask = (
            filtered_df["Situation"].str.lower().str.contains(q, na=False) | 
            filtered_df["Recommended resolution"].str.lower().str.contains(q, na=False)
        )
        results = filtered_df[mask]
        
    return results

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
        usa_swimming_logo_w_hyperlink()
    with header_col2:
        st.markdown("<h2 style='text-align: center; margin-top: -20px;'><a href='https://www.usaswimming.org' target='_blank' style='color: inherit; text-decoration: none;'>USA Swimming</a> Officials</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; margin-top: -10px;'>Situations & Resolutions</h4>", unsafe_allow_html=True)
        st.markdown("<h5 style='text-align: center; margin-top: -10px;'>Stroke & Turn</h5>", unsafe_allow_html=True)
    with header_col3:
        pns_logo_w_hyperlink()

def portrait_title_mode():
     with st.container(horizontal_alignment="center"):
        usa_swimming_logo_w_hyperlink()
        # Reduced margin-top on the first title
        st.markdown("<h3 style='text-align: center; margin-top: -20px;'><a href='https://www.usaswimming.org' target='_blank' style='color: inherit; text-decoration: none;'>USA Swimming</a> Officials</h3>", unsafe_allow_html=True)
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

# --- MODE 1: SEQUENTIAL REVIEW ---
if mode == "Sequential Review":
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

# --- MODE 2: KEYWORD SEARCH ---
elif mode == "Keyword Search":
    st.markdown("### 🔍 Keyword Search")
    
    # Field Selection - Added "Both"
    search_field = st.segmented_control(
        "Search within:", 
        ["All", "Situations", "Resolutions"], 
        default="All"
    )
    
    # Breadth Selection
    stroke_list = ["All"] + sorted(df['Stroke'].dropna().unique().tolist())
    selected_stroke = st.segmented_control(
        "Limit to Stroke/Topic:", 
        stroke_list, 
        default="All"
    )
    
    search_query = st.text_input("Enter keyword or phrase:", placeholder="Search...")
    
    if search_query:
        search_results = perform_keyword_search(df, search_query, search_field, selected_stroke)
        
        if not search_results.empty:
            st.success(f"Found {len(search_results)} matches.")
            
            # Create a dictionary for the dropdown: "Display Name": Index
            result_options = {
                f"#{row['Number']} [{row['Stroke']}] - {row['Situation'][:50]}...": idx 
                for idx, row in search_results.iterrows()
            }
            
            selected_label = st.selectbox("Select a result to view details:", options=list(result_options.keys()))
            
            # Update the global index
            new_index = result_options[selected_label]
            if st.session_state.current_index != new_index:
                st.session_state.current_index = new_index
                st.session_state.show_resolution_clicked = False
        else:
            st.warning("No matches found. Try broadening your search.")
            st.session_state.current_index = None
    else:
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

# --- MODE 4: Review BY STROKE/TOPIC ---
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

# --- MODE 5: Total Random Shuffle ---
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
    # Check if we are in Keyword Search mode to apply highlighting
    display_sit = row["Situation"]
    display_res = row["Recommended resolution"]

    # Apply highlighting if in Search Mode
    if mode == "Keyword Search" and 'search_query' in locals() and search_query:
        display_sit = highlight_text(display_sit, search_query)
        display_res = highlight_text(display_res, search_query)

    st.markdown(f'<div style="font-size: {font_size}px;"><b>Situation:</b><br>{display_sit}</div>', unsafe_allow_html=True)
    
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
        st.markdown(f'<div style="font-size: {font_size}px;">{display_res}</div>', unsafe_allow_html=True)
        st.warning(f"**Applicable Rule:**")
        st.markdown(f'<div style="font-size: {font_size}px;">{row["Applicable Rule"]}</div>', unsafe_allow_html=True)

# --- FOOTER ---
def landscape_footer_mode():
    st.markdown("---") # Adds a horizontal line to separate the content from the footer
    st.markdown(
            """
            <div style="text-align: center; color: grey; font-size: 14px;">
                © 2025 <a href="https://www.usaswimming.org" target="_blank">USA Swimming</a> <br>
                National Officials Committee, Version 03/07/2025<br>
            </div>
            """, 
            unsafe_allow_html=True
    )

def portrait_footer_mode():
    with st.container(horizontal_alignment="center"):
        pns_logo_w_hyperlink()
        st.markdown(
            """
            <div style="text-align: center; color: grey; font-size: 14px;">
                © 2025 <a href="https://www.usaswimming.org" target="_blank">USA Swimming</a> <br>
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