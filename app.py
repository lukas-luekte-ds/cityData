import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import os
import osmnx as ox
import pandas as pd

@st.cache_data(ttl=3600)  # Cache für 1 Stunde
def lade_spielplaetze():
    pfad = "spielplaetze.geojson"
    if os.path.exists(pfad):
        return gpd.read_file(pfad)
    else:
        gdf = ox.features_from_place("Dortmund, Germany", tags={"leisure": "playground"})
        gdf.to_file(pfad, driver="GeoJSON")
        return gdf

spielplaetze = lade_spielplaetze()

# Mittelpunkt der Karte berechnen
dortmund_center = spielplaetze.geometry.union_all().centroid
karte = folium.Map(location=[dortmund_center.y, dortmund_center.x], zoom_start=12)

# Darstellung der Spielplätze
for _, row in spielplaetze.iterrows():
    geom = row.geometry
    name = row.get("name")
    tooltip = name if pd.notnull(name) else "Spielplatz (ohne Namen)"

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
st_folium(karte, width=700)

