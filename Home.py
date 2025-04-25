import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
from streamlit import markdown
import geopandas as gpd
import folium
import pandas as pd
from branca.colormap import linear
import plotly.express as px
#Read in Manhattan GeoJSON
neighborhoodsGeometryFilepath = "./input/nyc_neighborhoods.geojson"
boroughCol = "borough"
dfNeighborhoods = gpd.read_file(neighborhoodsGeometryFilepath)
manhattanFilter = dfNeighborhoods[boroughCol] == "Manhattan"
dfManhattan = dfNeighborhoods[manhattanFilter]
#Read pickle files
df_0714_nyc = pd.read_pickle('./input/df_0714_nyc.pkl')
df_0719_nyc = pd.read_pickle('./input/df_0719_nyc.pkl')
df_0724_nyc = pd.read_pickle('./input/df_0724_nyc.pkl')

#Read counts for classic and electric bike rides from Pickle file
bikeTypeFilepath = "./input/plot_2_yl.pkl"
manhattan_counts = pd.read_pickle(bikeTypeFilepath)
manhattan_counts = manhattan_counts[['neighborhood', 'boroughCode', 'borough', '@id',
       'geometry', 'classic_bike', 'electric_bike', 'gap', 'percentage']]
manhattan_counts[['classic_bike', 'electric_bike']] = manhattan_counts[['classic_bike', 'electric_bike']].fillna(0)
manhattan_counts['gap'] = manhattan_counts['electric_bike'] - manhattan_counts['classic_bike']
manhattan_counts['percentage'] = manhattan_counts['electric_bike'] / (manhattan_counts['electric_bike'] + manhattan_counts['classic_bike'])
# This will drop Ellis Island and Liberty Island
manhattan_counts = manhattan_counts[~manhattan_counts['percentage'].isna()]

#Read in user type counts Pickle file
userCountsFilepath = "./input/plot_3_yl.pkl"
user_type_counts = pd.read_pickle(userCountsFilepath)
user_type_counts['neighborhood'] = user_type_counts['neighborhood'].astype(str)
user_type_counts = user_type_counts.sort_values(by='member')

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

            #overlap-of-casual-and-member-bike-rides-by-precinct {
                color: #ffffff;
            }

            h1 {
                color: #ffffff;
            }

            .st-emotion-cache-ah6jdd {
                color: #ffffff;
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
        zoom_start=12,
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
    #Add to streamlit app
    st.components.v1.html(folium.Figure().add_child(m).render(), height = 500)
    
def create_electric_vs_regular_map():
    # Create the base map
    m = folium.Map(
        location=[40.7738, -73.9660],
        zoom_start=12,
        tiles='CartoDB positron',
    )

    # Create FeatureGroups for the two layers
    fg_classic = folium.FeatureGroup(name='Classic Bike Rides')
    fg_electric = folium.FeatureGroup(name='Electric Bike Rides')
    fg_percentage_normalized = folium.FeatureGroup(name='Electric Bike Percentage Normalized')

    # Define colormap for Classic Bike Rides
    colormap_classic = linear.YlGn_09.scale(
        int(manhattan_counts['classic_bike'].min()), int(manhattan_counts['electric_bike'].max())
    )

    # Define colormap for Electric Bike Rides
    colormap_electric = linear.Blues_04.scale(
        int(manhattan_counts['classic_bike'].min()), int(manhattan_counts['electric_bike'].max())
    )

    # Define colormap for Electric Bike Rides
    colormap_percentage_normalized = linear.Purples_04.scale(
        manhattan_counts['percentage'].sort_values().to_list()[1], manhattan_counts['percentage'].max()
    )

    # Adding GeoJsonTooltip to display both classic and electric bike data when both layers are shown
    tooltip_combined_c = folium.GeoJsonTooltip(
        fields=['neighborhood', 'classic_bike'],  # Include both fields
        aliases=['Neighborhood:', 'Classic Bike Rides:'],  # Add appropriate aliases
        localize=True,
        sticky=True
    )

    # Adding GeoJsonTooltip to display both classic and electric bike data when both layers are shown
    tooltip_combined_e = folium.GeoJsonTooltip(
        fields=['neighborhood', 'electric_bike'],  # Include both fields
        aliases=['Neighborhood:', 'Electric Bike Rides:'],  # Add appropriate aliases
        localize=True,
        sticky=True
    )

    # Adding GeoJsonTooltip to display both classic and electric bike data when both layers are shown
    tooltip_combined_percentage_normalized = folium.GeoJsonTooltip(
        fields=['neighborhood', 'percentage', 'electric_bike', 'classic_bike'],  # Include both fields
        aliases=['Neighborhood:', 'Electric Bike % out of all rides in neighborhood:', 'Electric Bike Rides:', 'Classic Bike Rides:'],  # Add appropriate aliases
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
            "fillColor": colormap_percentage_normalized(feature["properties"]["percentage"]),
            "color": "transparent",  # Set border color to transparent
            "weight": 0,  # No visible border
            "fillOpacity": 0.7,  # Set fill opacity for the polygons
        },
        tooltip=tooltip_combined_percentage_normalized,
        popup=False
    ).add_to(fg_percentage_normalized)

    # Add FeatureGroups to the map
    fg_electric.add_to(m)
    fg_classic.add_to(m)
    fg_percentage_normalized.add_to(m)

    # Add Layer Control for toggling between layers
    folium.LayerControl(collapsed=False).add_to(m)
    #Add to Streamlit app
    st.components.v1.html(folium.Figure().add_child(m).render(), height = 500)

def create_user_type_plot():
    max_y_value = user_type_counts[['casual', 'member']].max().max()
    # Create a Plotly bar chart with overlapping bars
    fig = px.bar(
        user_type_counts,
        ##x='neighborhood',  # Now 'Precinct' is a regular column
        ##y=['casual', 'member'],  # Assuming your columns are 'casual' and 'member'
        x = ['casual', 'member'],
        y = 'neighborhood',
        labels={'neighborhood': 'Neighborhood', 'value': 'Count', 'member_casual': 'User Type'},
        ##title="Overlap of Casual and Member Bike Rides by Precinct",
        width = 500, height = 800
    )

    # Update the layout to set the bar mode to overlay and adjust the layout for better display
    fig.update_layout(
        barmode='overlay',  # Overlay the bars
        ##xaxis_title='',
        ##yaxis_title='Count',
        xaxis_title = "Count",
        yaxis_title = "Neighborhood",
        legend_title='User Type',
        ##xaxis=dict(
        yaxis=dict(
            fixedrange=True,  # Fix x-axis range
            tickmode='array',  # Set ticks to be explicitly defined
            tickvals=user_type_counts['neighborhood'],  # Show all precincts on the x-axis
            ticktext=user_type_counts['neighborhood'],  # Display all precinct values explicitly
            ###tickangle=45,  # Rotate the x-axis labels for better readability
        ),
        ##yaxis=dict(
        xaxis=dict(
            fixedrange=True,  # Fix y-axis range
            range=[0, max_y_value + 5],  # Set y-axis range based on maximum value
        )
    )

    # Update the traces to make the bars semi-transparent
    fig.update_traces(opacity=0.6)  # Set opacity to 60% (semi-transparent)

    # Show the plot
    st.plotly_chart(fig)


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
    create_electric_vs_regular_map()
    st.header("Overlap of Casual and Member Bike Rides by Precinct")
    create_user_type_plot()

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