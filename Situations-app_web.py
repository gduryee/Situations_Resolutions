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
         "Random Shuffle",
        "Keyword Search",
        "Search by Number"]  # Renamed and consolidated
    )

# --- MODE SWITCH DETECTION ---
if 'last_mode' not in st.session_state:
    st.session_state.last_mode = mode
if 'seq_num_input' not in st.session_state:
    st.session_state.seq_num_input = 1

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

# --- HELPER FOR MODE 1 (Sequential) Number Wrapping ---
def handle_seq_change():
    val = st.session_state.seq_num_input
    total = st.session_state.max_items_in_section
    
    if val > total:
        st.session_state.seq_num_input = 1
    elif val <= 0: # Catch 0 or negative immediately
        st.session_state.seq_num_input = total

# --- MODE 1: SEQUENTIAL REVIEW ---
if mode == "Sequential Review":
    stroke_topic_list = sorted(df['Stroke'].dropna().unique())
    default_stroke = "Backstroke" if "Backstroke" in stroke_topic_list else stroke_topic_list[0]
    
    selected_stroke_topic = st.segmented_control(
        "Select Stroke/Topic:", 
        stroke_topic_list, 
        key="seq_seg", 
        default=default_stroke
    )
    
    if selected_stroke_topic:
        section_df = df[df['Stroke'] == selected_stroke_topic].sort_values(by='Number')
        total_items = len(section_df)
        st.session_state.max_items_in_section = total_items

        # --- RESET & SYNC LOGIC ---
        if "last_selected_stroke" not in st.session_state:
            st.session_state.last_selected_stroke = selected_stroke_topic
            
        if st.session_state.last_selected_stroke != selected_stroke_topic:
            st.session_state.seq_num_input = 1
            st.session_state.last_selected_stroke = selected_stroke_topic

        # Force value to 1 if it somehow became 0
        if st.session_state.seq_num_input == 0:
            st.session_state.seq_num_input = 1

        # --- STYLING ---
        st.markdown(f"""
            <style>
                /* 1. Ensure the box is wide enough for +/- buttons */
                div[data-testid="stNumberInput"] {{
                    width: 150px !important;
                    text-align: right; 
                }}
                div[data-testid="stNumberInput"] input {{
                    font-size: 18px !important;
                    text-align: center;
                }}
                /* 2. Vertically align the text with the box */
                .seq-count-text {{
                    font-size: 18px;
                    white-space: nowrap;
                    line-height: 42px; /* Matches the height of the input box */
                }}
            </style>
        """, unsafe_allow_html=True)

        # --- THE SANDWICHED ROW ---
        # We put an empty element at the start and end to push content to the middle
        with st.container(horizontal=True, 
                        vertical_alignment="center",
                        horizontal_alignment="center",
                        gap="small", 
                        width="content"):
            current_val = st.number_input(
                "Select Item", 
                min_value=0, 
                max_value=total_items + 1, 
                step=1, 
                key="seq_num_input",
                on_change=handle_seq_change,
                label_visibility="collapsed"
            )
            
            st.markdown(f'<span style="font-size: 18px; white-space: nowrap; margin-left: 10px;">of {total_items} items</span>', unsafe_allow_html=True)
            

        # st.markdown(f'<span style="font-size: 20px; white-space: 
                # nowrap; margin-left: 10px;">of {total_items} items</span>', unsafe_allow_html=True)

        # Map to index
        safe_val = max(1, min(current_val, total_items))
        new_index = section_df.index[safe_val - 1]
        
        if st.session_state.current_index != new_index:
            st.session_state.current_index = new_index
            st.session_state.show_resolution_clicked = False
    else:
        st.info("Please select a Stroke/Topic.")
        st.session_state.current_index = None

# --- MODE 2: RANDOM SHUFFLE  ---
elif mode == "Random Shuffle":
    # 1. Create the list with "ALL" at the front
    stroke_topic_list = ["ALL"] + sorted(df['Stroke'].dropna().unique().tolist())
    
    # 2. Selection
    selected_stroke_topic = st.segmented_control(
        "Select Stroke/Topic (or ALL for total random):", 
        stroke_topic_list,
        default="ALL" # Default to total shuffle
    )
    
    if selected_stroke_topic:
        # 3. Filter Logic
        if selected_stroke_topic == "ALL":
            active_df = df
        else:
            active_df = df[df['Stroke'] == selected_stroke_topic]
        
        # 4. Situation Selection Logic
        if not active_df.empty:
            # Load new situation if none is selected OR if the stroke changed
            # We track the stroke in session state to detect changes
            if 'last_random_stroke' not in st.session_state:
                st.session_state.last_random_stroke = selected_stroke_topic

            if st.session_state.current_index is None or \
               st.session_state.current_index not in active_df.index or \
               st.session_state.last_random_stroke != selected_stroke_topic:
                
                get_new_situation(active_df)
                st.session_state.last_random_stroke = selected_stroke_topic

            # 5. Shuffle Button
            if st.button("Shuffle Next Situation", width="content", icon=":material/refresh:", type="secondary"):
                get_new_situation(active_df)
        else:
            st.warning(f"No situations found for {selected_stroke_topic}")
    else:
        st.info("Tap a Stroke/Topic or 'ALL' to start.")
        st.session_state.current_index = None

# --- MODE 3: KEYWORD SEARCH ---
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

# --- MODE 4: Search by Number ---
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



# --- DISPLAY CARD ---
if st.session_state.current_index is not None:
    row = df.loc[st.session_state.current_index]
    
    st.markdown("---")
    st.info(f"**Stroke/Topic: {row['Stroke']}  #{row['Number']}** \n\n **Situation:**")
    
    # Prepare text for display
    display_sit = row["Situation"]
    display_res = row["Recommended resolution"]

    # Apply highlighting if in Search Mode
    if mode == "Keyword Search" and 'search_query' in locals() and search_query:
        display_sit = highlight_text(display_sit, search_query)
        display_res = highlight_text(display_res, search_query)

    # Situation Display
    st.markdown(f'<div style="font-size: {font_size}px;"><br>{display_sit}</div>', unsafe_allow_html=True)
    
    # Logic to show/hide resolution
    should_show = (not hide_resolution) or st.session_state.show_resolution_clicked

    if not should_show:
        if st.button("Show Resolution", key=f"btn_{st.session_state.current_index}"):
            st.session_state.show_resolution_clicked = True
    
    if should_show:
        st.write("") 
        st.success("**Recommended Resolution:**")
        # Display the highlighted resolution
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