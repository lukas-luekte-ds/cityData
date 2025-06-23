import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import os
import osmnx as ox
import pandas as pd

st.set_page_config(page_title="Spielplätze Dortmund", layout="centered")

@st.cache_data(ttl=3600)
def lade_spielplaetze():
    pfad = "spielplaetze.geojson"
    if os.path.exists(pfad):
        return gpd.read_file(pfad)
    else:
        gdf = ox.features_from_place("Dortmund, Germany", tags={"leisure": "playground"})
        gdf.to_file(pfad, driver="GeoJSON")
        return gdf

spielplaetze = lade_spielplaetze()

# Erstellt Kartenobjekt nur beim ersten Laden oder nach Reset
if "map_center" not in st.session_state:
    center = spielplaetze.geometry.union_all().centroid
    st.session_state.map_center = [center.y, center.x]
    st.session_state.zoom = 12

# Karte erzeugen
karte = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.zoom)

# Spielplätze einzeichnen
for _, row in spielplaetze.iterrows():
    geom = row.geometry
    name = row.get("name")
    tooltip = name if pd.notnull(name) else "Spielplatz"

    if geom.geom_type in ['Polygon', 'MultiPolygon']:
        folium.GeoJson(
            geom,
            style_function=lambda x: {"fillColor": "green", "color": "green", "weight": 1, "fillOpacity": 0.4},
            tooltip=tooltip
        ).add_to(karte)
    elif geom.geom_type == 'Point':
        folium.CircleMarker(
            location=[geom.y, geom.x],
            radius=5,
            color="green",
            fill=True,
            fill_opacity=0.7,
            tooltip=tooltip
        ).add_to(karte)

st.title("🧸 Spielplätze in Dortmund")

# Interaktive Karte anzeigen
view = st_folium(karte, width=700, returned_objects=["last_view"])

# Zoom & Position merken
if view and view.get("last_view"):
    st.session_state.map_center = view["last_view"]["center"]
    st.session_state.zoom = view["last_view"]["zoom"]

