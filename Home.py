import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
from streamlit import markdown
import geopandas as gpd
import folium
import pandas as pd
from branca.colormap import linear

def set_styling():
    markdown(
        """
        <style>
            .stApp {
                background-image: url("https://nycdotbikeshare.info/sites/default/files/inline-images/Citi%20Bike%20E%20Bike_0.jpg");
                background-size: cover;
            }
            .stApp::before {
                content: "";
                position: absolute;
                top: 0px;
                right: 0px;
                bottom: 0px;
                left: 0px;
                background-color: rgba(0,0,0,0.75)
            }
            .stAppHeader {
                opacity: 0.75;
                background-color: #1560bd;
            }

            .stSidebar {
                opacity: 0.95;
                background-color: #1560bd;
            }

            .st-emotion-cache-a6qe2i {
                opacity: 1.0;
            }

            reportview-container {
            margin-top: -2em;
            }
            #MainMenu {visibility: hidden;}
            .stDeployButton {display:none;}
            footer {visibility: hidden;}
            #stDecoration {display:none;}
        </style>
        """,
        unsafe_allow_html = True
    )

def plot_manhattan():
    #fig = plt.figure()
    neighborhoodsGeometryFilepath = "./input/nyc_neighborhoods.geojson"
    dfNeighborhoods = gpd.read_file(neighborhoodsGeometryFilepath)
    boroughCol = "borough"
    dfManhattan = dfNeighborhoods[dfNeighborhoods[boroughCol] == "Manhattan"]
    map = folium.Map(location = [40.7685, -73.9822], zoom_start = 11)
    folium.GeoJson(dfManhattan).add_to(map)
    st.components.v1.html(folium.Figure().add_child(map).render(), height = 500)


def create_station_map():
    # Create a map centered on Upper East Side
    m = folium.Map(
        location=[40.7738, -73.9660],
        zoom_start=14,
        tiles='CartoDB positron',
        # FIXME: if you comment out tiles, you can get openstreetmap as the base map
    )

    # Create feature groups for each year
    fg_2014 = folium.FeatureGroup(name='2014 (Red)', show=True)
    fg_2019 = folium.FeatureGroup(name='2019 (Green)', show=False)
    fg_2024 = folium.FeatureGroup(name='2024 (Blue)', show=False)

    # Function to add circle markers
    def add_markers(df, feature_group, color, year):
        for idx, row in df.iterrows():
            popup_content = f"""
            <b>Station ID:</b> {row['station id']}<br>
            <b>Station name:</b> {row['station name']}<br>
            <b>Year:</b> {year}<br>
            """
            folium.CircleMarker(
                location=[row['station latitude'], row['station longitude']],
                radius=4,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"Station name: {row['station name']}"
            ).add_to(feature_group)

    #Read pickle file data
    df_0714_nyc = pd.read_pickle('./input/df_0714_nyc.pkl')
    df_0719_nyc = pd.read_pickle('./input/df_0719_nyc.pkl')
    df_0724_nyc = pd.read_pickle('./input/df_0724_nyc.pkl')
    # Add markers to respective layers
    add_markers(df_0714_nyc, fg_2014, 'red', 2014)
    add_markers(df_0719_nyc, fg_2019, 'green', 2019)
    add_markers(df_0724_nyc, fg_2024, 'blue', 2024)

    # Add all layers to map
    fg_2014.add_to(m)
    fg_2019.add_to(m)
    fg_2024.add_to(m)

    # Add layer control
    folium.LayerControl(collapsed=False).add_to(m)
    st.components.v1.html(folium.Figure().add_child(m).render(), height = 500)
    
def create_electric_vs_regular_map():
    precinct_counts = (
        df_all_24_nyc
        .groupby(['Precinct', 'rideable_type'])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    manhattan_counts = manhattan.merge(precinct_counts, on='Precinct', how='left')
    manhattan_counts[['classic_bike', 'electric_bike']] = manhattan_counts[['classic_bike', 'electric_bike']].fillna(0)
    manhattan_counts['gap'] = manhattan_counts['electric_bike'] - manhattan_counts['classic_bike']
    # Create the base map
    m = folium.Map(
        location=[40.7738, -73.9660],
        zoom_start=14,
        tiles='CartoDB positron',
    )

    # Create FeatureGroups for the two layers
    fg_gap = folium.FeatureGroup(name='Electric Bike Rides - Classic Bike Rides')
    fg_classic = folium.FeatureGroup(name='Classic Bike Rides')
    fg_electric = folium.FeatureGroup(name='Electric Bike Rides')

    # Define colormap for Classic Bike Rides
    colormap_classic = linear.YlGn_09.scale(
        manhattan_counts['classic_bike'].min(), manhattan_counts['classic_bike'].max()
    )

    # Define colormap for Electric Bike Rides
    colormap_electric = linear.YlGn_09.scale(
        manhattan_counts['electric_bike'].min(), manhattan_counts['electric_bike'].max()
    )

    # Define colormap for Electric Bike Rides
    colormap_gap = linear.Purples_05.scale(
        manhattan_counts['gap'].min(), manhattan_counts['gap'].max()
    )

    # Adding GeoJsonTooltip to display both classic and electric bike data when both layers are shown
    tooltip_combined_c = folium.GeoJsonTooltip(
        fields=['Precinct', 'classic_bike', 'electric_bike'],  # Include both fields
        aliases=['Precinct:', 'Classic Bike Rides:', 'Electric Bike Rides:'],  # Add appropriate aliases
        localize=True,
        sticky=True
    )

    # Adding GeoJsonTooltip to display both classic and electric bike data when both layers are shown
    tooltip_combined_e = folium.GeoJsonTooltip(
        fields=['Precinct', 'classic_bike', 'electric_bike'],  # Include both fields
        aliases=['Precinct:', 'Classic Bike Rides:', 'Electric Bike Rides:'],  # Add appropriate aliases
        localize=True,
        sticky=True
    )

    # Adding GeoJsonTooltip to display both classic and electric bike data when both layers are shown
    tooltip_combined_gap = folium.GeoJsonTooltip(
        fields=['Precinct', 'gap'],  # Include both fields
        aliases=['Precinct:', 'Electric Bike Rides - Classic Bike Rides:'],  # Add appropriate aliases
        localize=True,
        sticky=True
    )

    # Adding GeoJson for Classic Bike Rides with dynamic styling
    folium.GeoJson(
        manhattan_counts,  # This is your GeoDataFrame or GeoJSON data
        style_function=lambda feature: {
            "fillColor": colormap_classic(feature["properties"]["classic_bike"]),
            "color": "transparent",  # Set border color to transparent
            "weight": 0,  # No visible border
            "fillOpacity": 0.7,  # Set fill opacity for the polygons
        },
        tooltip=tooltip_combined_c
    ).add_to(fg_classic)

    # Adding GeoJson for Electric Bike Rides with dynamic styling
    folium.GeoJson(
        manhattan_counts,  # This is your GeoDataFrame or GeoJSON data
        style_function=lambda feature: {
            "fillColor": colormap_electric(feature["properties"]["electric_bike"]),
            "color": "transparent",  # Set border color to transparent
            "weight": 0,  # No visible border
            "fillOpacity": 0.7,  # Set fill opacity for the polygons
        },
        tooltip=tooltip_combined_e,
        popup=False
    ).add_to(fg_electric)

    # Adding GeoJson for Electric Bike Rides with dynamic styling
    folium.GeoJson(
        manhattan_counts,  # This is your GeoDataFrame or GeoJSON data
        style_function=lambda feature: {
            "fillColor": colormap_gap(feature["properties"]["gap"]),
            "color": "transparent",  # Set border color to transparent
            "weight": 0,  # No visible border
            "fillOpacity": 0.7,  # Set fill opacity for the polygons
        },
        tooltip=tooltip_combined_gap,
        popup=False
    ).add_to(fg_gap)

    # Add FeatureGroups to the map
    fg_gap.add_to(m)
    fg_classic.add_to(m)
    fg_electric.add_to(m)

    # Add Layer Control for toggling between layers
    folium.LayerControl(collapsed=False).add_to(m)

    # Show the map
    m

with st.sidebar:
    selected = option_menu(
    menu_title = "Main Menu",
    options = ["Home", "Location Plots", "Network and Time Analysis", "External Data"],
    menu_icon = "cast",
    default_index = 0,
    #orientation = "horizontal",
)
    
if selected == "Home":
    set_styling()
    st.title("The Citi of Bikes")
    st.text("The Citi Bike program allows people to travel across New York City with reasonably-priced bike fares and an abundance of bike stations. There is an abundance of historical and real-time bike data available for NYC, so we aim to visualize and identify trends in this data.")

elif selected == "Location Plots":
    set_styling()
    st.title("Location-Based Plots")
    create_station_map()

elif selected == "Network and Time Analysis":
    set_styling()
    st.title("Network and Time Analysis")

elif selected == "External Data":
    set_styling()
    st.title("Incorporating External Data Sources")
    st.header("Neighborhood Train Stop and Bike Station Statistics")
    #Create table for neighborhood statistics
    neighborhoodStatsFilepath = "./output/neighborhood_stats.csv"
    dfInput = pd.read_csv(neighborhoodStatsFilepath)
    st.dataframe(dfInput, hide_index = True)