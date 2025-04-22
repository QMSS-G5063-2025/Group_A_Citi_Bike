import streamlit as st
from streamlit_option_menu import option_menu
import geopandas as gpd
import folium
import pandas as pd

def plot_manhattan():
    #fig = plt.figure()
    neighborhoodsGeometryFilepath = "./input/nyc_neighborhoods.geojson"
    dfNeighborhoods = gpd.read_file(neighborhoodsGeometryFilepath)
    boroughCol = "borough"
    dfManhattan = dfNeighborhoods[dfNeighborhoods[boroughCol] == "Manhattan"]
    map = folium.Map(location = [40.7685, -73.9822], zoom_start = 11)
    folium.GeoJson(dfManhattan).add_to(map)
    st.components.v1.html(folium.Figure().add_child(map).render(), height = 500)
    

with st.sidebar:
    selected = option_menu(
    menu_title = "Main Menu",
    options = ["Home", "Location Plots", "Network and Time Analysis", "External Data"],
    menu_icon = "cast",
    default_index = 0,
    #orientation = "horizontal",
)
    
if selected == "Home":
    st.header("The Citi of Bikes")
    plot_manhattan()

elif selected == "Location Plots":
    st.header("Location-Based Plots")

elif selected == "Network and Time Analysis":
    st.header("Network and Time Analysis")

elif selected == "External Data":
    st.header("Incorporating External Data Sources")
    neighborhoodStatsFilepath = "./output/neighborhood_stats.csv"
    dfInput = pd.read_csv(neighborhoodStatsFilepath)
    st.dataframe(dfInput, hide_index = True)