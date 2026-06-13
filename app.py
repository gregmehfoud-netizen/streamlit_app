### this is an app

import streamlit as st
import folium
from streamlit_folium import st_folium

# Set up the page configuration
st.set_page_config(page_title="Map Point Selector", layout="wide")

st.title("📍 Interactive Map Point Selector")
st.write("Click anywhere on the map to select a point and capture its coordinates.")

# 1. Initialize a Folium map centered on a specific location (e.g., San Francisco)
m = folium.Map(location=[38.0293, -78.4767], zoom_start=13)

# Add a click event marker or just let the user click
# st_folium renders the map and returns data about user interactions (like clicks)
map_data = st_folium(m, width=1000, height=600)

# 2. Check if the user clicked on the map
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lng = map_data["last_clicked"]["lng"]
    
    # Display the captured coordinates
    st.success(f"Selected Coordinates: **Latitude**: {lat} | **Longitude**: {lng}")
    
    # Optional: store it in session state if you want to build a list of multiple points
    if 'selected_points' not in st.session_state:
        st.session_state.selected_points = []
        
    # Button to save the point to a list
    if st.button("Save this point"):
        st.session_state.selected_points.append({"lat": lat, "lon": lng})
        st.toast("Point saved!", icon="✅")

# 3. Display saved points if any exist
if 'selected_points' in st.session_state and st.session_state.selected_points:
    st.write("### Saved Points")
    st.json(st.session_state.selected_points)
    
    if st.button("Clear saved points"):
        st.session_state.selected_points = []
        st.rerun()
