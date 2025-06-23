import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import os
import osmnx as ox
import pandas as pd

st.set_page_config(page_title="Sportplätze Dortmund", layout="centered")

@st.cache_data(ttl=3600)
def lade_sportplaetze():
    pfad = "sportplaetze.geojson"
    if os.path.exists(pfad):
        return gpd.read_file(pfad)
    else:
        gdf = ox.features_from_place("Dortmund, Germany", tags={"leisure": "pitch"})
        gdf.to_file(pfad, driver="GeoJSON")
        return gdf

sportplaetze = lade_sportplaetze()

# Karten-Zentrum und Zoom-Level in session_state merken
if "map_center_sport" not in st.session_state:
    center = sportplaetze.geometry.union_all().centroid
    st.session_state.map_center_sport = [center.y, center.x]
    st.session_state.zoom_sport = 12

karte = folium.Map(location=st.session_state.map_center_sport, zoom_start=st.session_state.zoom_sport)

# Einzeichnen auf Karte
for _, row in sportplaetze.iterrows():
    geom = row.geometry
    name = row.get("name")
    tooltip = name if pd.notnull(name) else "Sportplatz"

    if geom.geom_type in ['Polygon', 'MultiPolygon']:
        folium.GeoJson(
            geom,
            style_function=lambda x: {"fillColor": "blue", "color": "blue", "weight": 1, "fillOpacity": 0.4},
            tooltip=tooltip
        ).add_to(karte)
    elif geom.geom_type == 'Point':
        folium.CircleMarker(
            location=[geom.y, geom.x],
            radius=5,
            color="blue",
            fill=True,
            fill_opacity=0.7,
            tooltip=tooltip
        ).add_to(karte)

st.title("⚽ Sportplätze in Dortmund")
view = st_folium(karte, width=700, returned_objects=["last_view"])

# Position und Zoom-Level merken
if view and view.get("last_view"):
    st.session_state.map_center_sport = view["last_view"]["center"]
    st.session_state.zoom_sport = view["last_view"]["zoom"]

