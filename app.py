import streamlit as st
import folium
from streamlit_folium import st_folium
from supabase import create_client, Client

# 1. Page Configuration
st.set_page_config(page_title="Labeled Map with Supabase", layout="wide")
st.title("Database-Driven Map with Custom Labels")
st.write("Click anywhere on the map, give it a label, and save it to the cloud.")

# 2. Connect to Supabase
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# 3. Database Functions
def fetch_points():
    try:
        response = supabase.table("locations").select("latitude, longitude, label").execute()
        return [{"lat": row["latitude"], "lng": row["longitude"], "label": row["label"]} for row in response.data]
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

def save_point(lat, lng, label_text, description, user_input, stars, review):
    try:
        supabase.table("locations").insert({
            "latitude": lat, 
            "longitude": lng, 
            "label": label_text,
            "description": description_input,
            "user_input": user_input,
            "stars": star_input,
            "review": review_input
        }).execute()
    except Exception as e:
        st.error(f"Error saving data: {e}")

def clear_db():
    try:
        supabase.table("locations").delete().gt("id", 0).execute()
    except Exception as e:
        st.error(f"Error clearing data: {e}")

# Load initial data from cloud
if 'saved_points' not in st.session_state:
    st.session_state.saved_points = fetch_points()

# Keep track of a click that is waiting for a label
if 'pending_click' not in st.session_state:
    st.session_state.pending_click = None

# 4. Base Map Setup
m = folium.Map(location=[38.0293, -78.4767], zoom_start=13)

# 5. Drop pins with custom popups showing their labels
for point in st.session_state.saved_points:
    stars = "⭐" * point['stars']
    popup_html = f"""
    <div style='font-family: sans-serif; min-width: 150px;'>
        <h4 style='margin: 0 0 5px 0;'>{point['label']}</h4>
        <div style='color: #FFD700; font-size: 16px; margin-bottom: 5px;'>{stars}</div>
        <small style='color: #666;'>Lat: {point['lat']:.4f}<br>Lng: {point['lng']:.4f}</small>
    </div>
    """
    
    folium.Marker(
        location=[point['lat'], point['lng']],
        popup=folium.Popup(popup_html, max_width=250),
        icon=folium.Icon(color="amber" if point['stars'] >= 4 else "blue", icon="star")
    ).add_to(m)

# 6. Layout: Map on the left, input controls/data on the right
col1, col2 = st.columns([3, 1])

with col1:
    output = st_folium(m, width=900, height=600, key="labeled_map")

# Capture map click and hold it as pending
if output and output.get('last_clicked'):
    clicked_coords = output['last_clicked']
    # If it's a completely new click location, capture it
    if st.session_state.pending_click != clicked_coords:
        # Check against existing to prevent infinite rerun loops
        if not st.session_state.saved_points or (st.session_state.saved_points[-1]['lat'] != clicked_coords['lat']):
            st.session_state.pending_click = clicked_coords
            st.rerun()

with col2:
    # 7. Dynamic Input Field section
    if st.session_state.pending_click:
        st.subheader("📍 Label Your Selection")
        lat = st.session_state.pending_click['lat']
        lng = st.session_state.pending_click['lng']
        st.caption(f"Coords: {lat:.4f}, {lng:.4f}")
        
        # The user input field requested
        user_label = st.text_input("Enter a name or description for this pin:", key="pin_label_input")
        user_name = st.text_input("Who is entering this pin?", key = "pin_user_input")

        description_input = st.text_input("Enter the description of the restroom:", key = "pin_desc_input")
        
        # Streamlit Native Star Component
        st.write("Your Rating:")
        star_index = st.feedback("stars", key="pin_stars")
        # st.feedback returns 0 to 4 for stars, so we add 1 to get a 1-5 score
        rating = (star_index + 1) if star_index is not None else 0

        review_input = st.text_input("Enter the review or reason for the stars:", key = "pin_review_input")
        
        if st.button("Save Pin to Supabase", type="primary"):
            if user_label.strip() == "":
                user_label = "Unnamed Location"
                
            # Save to cloud
            save_point(lat, lng, user_label, description_input, user_name, rating, review_input)
            # Clear pending state
            st.session_state.pending_click = None
            # Refresh lists
            st.session_state.saved_points = fetch_points()
            st.success("Saved successfully!")
            st.rerun()
            
        if st.button("Cancel"):
            st.session_state.pending_click = None
            st.rerun()
    else:
        st.subheader("System Status")
        st.info("Click a spot on the map to label and save a new pin.")

    # 8. Data Overview Summary
    st.divider()
    st.subheader("Saved Cloud Places")
    if st.session_state.saved_points:
        for pt in st.session_state.saved_points:
            st.markdown(f"**{pt['label']}**<br><small>{pt['lat']:.3f}, {pt['lng']:.3f}</small>", unsafe_allow_html=True)
        
        if st.button("Clear All Data"):
            clear_db()
            st.session_state.saved_points = []
            st.session_state.pending_click = None
            st.rerun()
