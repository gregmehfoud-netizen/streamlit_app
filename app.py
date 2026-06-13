import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Page Configuration
st.set_page_config(page_title="Charlottesville Map Selector", layout="wide")
st.title("Interactive Map Point Selector")
st.write("Click on the map to drop a permanent pin. Click 'Clear All Pins' to start over.")

# 2. Initialize Session State for saving points
if 'saved_points' not in st.session_state:
    st.session_state.saved_points = []

# 3. Create the Base Map (Centered on Charlottesville, VA)
m = folium.Map(location=[38.0293, -78.4767], zoom_start=13)

# Add the click popup helper
folium.LatLngPopup().add_to(m)

# 4. Draw existing pins from our saved session state onto the map
for i, point in enumerate(st.session_state.saved_points):
    folium.Marker(
        location=[point['lat'], point['lng']],
        popup=f"Pin #{i+1}: {point['lat']:.4f}, {point['lng']:.4f}",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

# 5. Render the map in Streamlit
output = st_folium(m, width=900, height=600, key="cville_map")

# 6. Capture new clicks and update session state
if output and output.get('last_clicked'):
    new_click = output['last_clicked']
    
    # Check to make sure we don't accidentally double-add the exact same click
    if not st.session_state.saved_points or st.session_state.saved_points[-1] != new_click:
        st.session_state.saved_points.append(new_click)
        # Rerun the app immediately to draw the newly added pin
        st.rerun()

# 7. Sidebar Sidebar UI to show data and add utility
with st.sidebar:
    st.subheader("Saved Locations")
    if st.session_state.saved_points:
        for i, pt in enumerate(st.session_state.saved_points):
            st.text(f"#{i+1}: {pt['lat']:.4f}, {pt['lng']:.4f}")
        
        # Button to clear the memory
        if st.button("Clear All Pins"):
            st.session_state.saved_points = []
            st.rerun()
    else:
        st.info("No points saved yet. Click the map to add one!")
