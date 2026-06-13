import streamlit as st
import folium
from streamlit_folium import st_folium
from supabase import create_client, Client

# 1. Page Configuration
st.set_page_config(page_title="C-Ville Map with Supabase", layout="wide")
st.title("Supabase Cloud Map Selector")
st.write("Click on the map to save a pin directly to your cloud Supabase database.")

# 2. Connect to Supabase (Cached to run only once)
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# 3. Database Functions
def fetch_points():
    """Fetch all coordinates from the Supabase table."""
    try:
        response = supabase.table("locations").select("latitude, longitude").execute()
        # Transform response into list of dicts to match our map loop
        return [{"lat": row["latitude"], "lng": row["longitude"]} for row in response.data]
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

def save_point(lat, lng):
    """Insert a new coordinate row into Supabase."""
    try:
        supabase.table("locations").insert({"latitude": lat, "longitude": lng}).execute()
    except Exception as e:
        st.error(f"Error saving data: {e}")

def clear_db():
    """Clear all records from the table (Deletes rows where ID is greater than 0)."""
    try:
        supabase.table("locations").delete().gt("id", 0).execute()
    except Exception as e:
        st.error(f"Error clearing data: {e}")

# 4. Load points into Session State from cloud
if 'saved_points' not in st.session_state:
    st.session_state.saved_points = fetch_points()

# 5. Create Map UI (Charlottesville center)
m = folium.Map(location=[38.0293, -78.4767], zoom_start=13)
folium.LatLngPopup().add_to(m)

# 6. Overlay pins from Supabase
for i, point in enumerate(st.session_state.saved_points):
    folium.Marker(
        location=[point['lat'], point['lng']],
        popup=f"Supabase Pin #{i+1}: {point['lat']:.4f}, {point['lng']:.4f}",
        icon=folium.Icon(color="green", icon="cloud")
    ).add_to(m)

# 7. Render map component
output = st_folium(m, width=900, height=600, key="cville_supabase_map")

# 8. Handle Map Clicks
if output and output.get('last_clicked'):
    new_click = output['last_clicked']
    
    # Avoid duplicate additions from the same interaction loop
    if not st.session_state.saved_points or st.session_state.saved_points[-1] != new_click:
        # Write to cloud database
        save_point(new_click['lat'], new_click['lng'])
        # Re-fetch fresh data from cloud
        st.session_state.saved_points = fetch_points()
        st.rerun()

# 9. Sidebar panel to show current data status
with st.sidebar:
    st.subheader("Cloud Records")
    if st.session_state.saved_points:
        for i, pt in enumerate(st.session_state.saved_points):
            st.text(f"Cloud ID {i+1}: {pt['lat']:.4f}, {pt['lng']:.4f}")
        
        if st.button("Clear Supabase Database"):
            clear_db()
            st.session_state.saved_points = []
            st.rerun()
    else:
        st.info("No cloud points found. Click the map to populate Supabase!")
