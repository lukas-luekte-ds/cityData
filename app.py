import streamlit as st
import folium
from streamlit_folium import st_folium
import osmnx as ox
import pandas as pd

@st.cache_data(ttl=300)
def lade_spielplaetze():
    return ox.features_from_place("Dortmund, Germany", tags={"leisure": "playground"})

spielplaetze = lade_spielplaetze()
center = spielplaetze.geometry.union_all().centroid
karte = folium.Map(location=[center.y, center.x], zoom_start=12)

for _, row in spielplaetze.iterrows():
    geom = row.geometry
    name = row.get("name")
    tooltip = name if pd.notnull(name) else "Spielplatz ohne Namen"

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

