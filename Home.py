import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
from streamlit import markdown
import geopandas as gpd
import folium
import pandas as pd
from branca.colormap import linear
import plotly.express as px
from folium.plugins import MarkerCluster
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

#Load in and process geometry data to map to standard neighborhoods
stationsFilepath = "./input/bike_stations_augmented.csv"
mappingsFilepath = "./input/neighborhood_mappings.csv"
incomeFilepath = "./input/nyc_neighborhood_incomes.csv"
dfBikeStationsAugmented = pd.read_csv(stationsFilepath)
dfMappings = pd.read_csv(mappingsFilepath)
dfManhattanNormalized = dfManhattan.merge(dfMappings, left_on = "neighborhood", right_on = "source_neighborhood", how = "inner")
dfManhattanNormalized = dfManhattanNormalized[["geometry", "source_neighborhood", "standardized_neighborhood"]]
# Drop the 'source_neighborhood' column
dfManhattanNormalized = dfManhattanNormalized.drop(columns=["source_neighborhood"])
# Merge polygons by 'standardized_neighborhood'
merged = dfManhattanNormalized.dissolve(by="standardized_neighborhood")
#Read in income data
dfIncomes = pd.read_csv(incomeFilepath)
dfIncomes = dfIncomes.rename(columns = {"Location":"standardized_neighborhood", "Data":"Annual Income"})
dfIncomes = dfIncomes[["standardized_neighborhood", "Annual Income"]]
#Join income and neighborhood data by 'standardized_neighborhood' field
dfManhattanIncomes = merged.merge(dfIncomes, left_on = "standardized_neighborhood", right_on = "standardized_neighborhood", how = "inner")
manhattanFilter = dfBikeStationsAugmented[boroughCol] == "Manhattan"
dfManhattanStations = dfBikeStationsAugmented[manhattanFilter]
#Set page title
st.set_page_config(page_title = "Citi Where Nobody Sleeps")

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
                background-color: rgba(36,36,36,0.75)
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
        x = ['casual', 'member'],
        y = 'neighborhood',
        labels={'neighborhood': 'Neighborhood', 'value': 'Count', 'member_casual': 'User Type'},
        width = 500, height = 800
    )

    # Update the layout to set the bar mode to overlay and adjust the layout for better display
    fig.update_layout(
        barmode='overlay',  # Overlay the bars
        xaxis_title = "Count",
        yaxis_title = "Neighborhood",
        legend_title='User Type',
        yaxis=dict(
            fixedrange=True,  # Fix y-axis range
            tickmode='array',  # Set ticks to be explicitly defined
            tickvals=user_type_counts['neighborhood'],  # Show all precincts on the y-axis
            ticktext=user_type_counts['neighborhood'],  # Display all precinct values explicitly
            ###tickangle=45,  # Rotate the y-axis labels for better readability
        ),
        xaxis=dict(
            fixedrange=True,  # Fix x-axis range
            range=[0, max_y_value + 5],  # Set x-axis range based on maximum value
        )
    )

    # Update the traces to make the bars semi-transparent
    fig.update_traces(opacity=0.6)  # Set opacity to 60% (semi-transparent)

    # Show the plot
    st.plotly_chart(fig)

def income_plot_and_stations():
    bikeStationNameCol = "name"
    # Create the base map
    m = folium.Map(
        location=[40.7738, -73.9660],
        zoom_start=14,
        tiles='CartoDB positron',
    )

    # Define colormap for Classic Bike Rides
    colormap = linear.YlGn_09.scale(
        int(dfManhattanIncomes['Annual Income'].min()), int(dfManhattanIncomes['Annual Income'].max())
    )

    # Adding GeoJsonTooltip to display both classic and electric bike data when both layers are shown
    tooltip_combined = folium.GeoJsonTooltip(
        fields=['standardized_neighborhood', 'Annual Income'],  # Include both fields
        aliases=['Neighborhood:', 'Annual Income:'],  # Add appropriate aliases
        localize=True,
        sticky=True
    )

    folium.GeoJson(
        dfManhattanIncomes,  # This is your GeoDataFrame or GeoJSON data
        style_function=lambda feature: {
            "fillColor": colormap(feature["properties"]["Annual Income"]),
            "color": "transparent",  # Set border color to transparent
            "weight": 0,  # No visible border
            "fillOpacity": 0.7,  # Set fill opacity for the polygons
        },
        tooltip=tooltip_combined,
        popup=False
    ).add_to(m)

    markerCluster = MarkerCluster().add_to(m)

    for index, row in dfManhattanStations.iterrows():
        stationText = folium.IFrame(f"<p style = 'font-size:14px;'><b>Station Name</b>: {row[bikeStationNameCol]}</p>", width = 200, height = 40)
        popup = folium.Popup(stationText, max_width = 400)
        folium.Marker(
            location = [row["lat"], row["lon"]],
            popup = popup
        ).add_to(markerCluster)

    markerCluster.add_to(m)
    #Add to Streamlit app
    st.components.v1.html(folium.Figure().add_child(m).render(), height = 500)


with st.sidebar:
    selected = option_menu(
    menu_title = "Main Menu",
    options = ["Home", "Location Plots", "Network and Time Analysis", "External Data"],
    menu_icon = "cast",
    default_index = 0,
)
    
if selected == "Home":
    set_styling()
    st.markdown(f'<h1 style="color:#6CACE4;font-size:48px;">{"The Citi of Bikes"}</h1>', unsafe_allow_html = True)
    st.markdown(f'<h2 style = "color:#FFFFFF;font-size:36px;">{"Group Members"}</h2>', unsafe_allow_html = True)
    st.markdown(f'<ul style = "color:#FFFFFF;font-size:24px;"><li>{"Adit Anand"}</li><li>{"Vivian Li"}</li><li>{"Varsha Varkhedi"}</li></ul>', unsafe_allow_html = True)
    st.markdown(f'<h2 style = "color:#FFFFFF;font-size:36px;">{"Description"}</h2>', unsafe_allow_html = True)
    st.markdown(f'<p style="color:#FFFFFF;font-size:18px;">{"In this project, we used a mix of interactive and static visualizations to explore trends in Citi Bike usage and deployment across Manhattan. An interactive time-layered map highlighted how station coverage has expanded from 2014 to 2024. To compare rider behavior, we used a heatmap for electric vs. classic bike usage and a bar plot to contrast member vs. casual rider patterns by neighborhood.<br><br>A circular network graph visualized trip flows between neighborhoods, while a hexbin plot examined the relationship between ride duration and distance during peak summer months. Seasonal usage trends were captured with a line chart, showing how ridership fluctuates over the year.<br><br>We also included a comparative table to examine infrastructure alignment, showing the number of bike and subway stations per neighborhood and their proximity. Lastly, an interactive map overlaying average income and station count helped us assess the equity of station distribution.<br><br>Each visualization was designed to reveal a different dimension of the data—from spatial growth and rider demographics to network flow and social context."}</p>', unsafe_allow_html = True)

elif selected == "Location Plots":
    set_styling()
    st.markdown(f'<h1 style="color:#6CACE4;font-size:48px;">{"Location-Based Plots"}</h1>', unsafe_allow_html = True)
    st.markdown(f'<h2 style = "color:#FFFFFF;font-size:36px;">{"Evolution of Manhattan Bike Stations (2014–2024)"}</h2>', unsafe_allow_html = True)
    st.markdown(f'<p style = "color:#FFFFFF;font-size:18px;">{"This interactive map shows the dramatic growth of the bike station network in Manhattan over time. Users can explore snapshots from July of 2014, 2019, and 2024 to see how stations have expanded across the city. In 2014, the system was limited to areas below Central Park. By 2019, it extended past Harlem. And by 2024, it reached deep into upper Manhattan, with coverage even below 231st Street — highlighting the ongoing investment in accessible, sustainable transit across more neighborhoods in NYC."}</p>', unsafe_allow_html = True)
    create_station_map()
    st.markdown(f'<h2 style = "color:#FFFFFF;font-size:36px;">{"Electric vs. Classic Bike Usage by Neighborhood in 2024"}</h2>', unsafe_allow_html = True)
    st.markdown(f'<p style = "color:#FFFFFF;font-size:18px;">{"This interactive map explores the spatial dynamics of bike usage in NYC, based on ride starting locations. Users can toggle between three heatmap layers: one for electric bike rides, one for classic bike rides, and a third showing the percentage of electric bike rides relative to all rides in each neighborhood."}</p>', unsafe_allow_html = True)
    st.markdown(f'<p style = "color:#FFFFFF;font-size:18px;">{"Across all bike types, the distribution is similar for all neighborhoods. Ride density is highest in Midtown, Chelsea, and the East Village. However, a notable trend emerges in the northern neighborhoods: areas like Washington Heights show a higher proportion of electric bike usage compared to classic bikes. This may reflect rider preferences for longer or hillier routes — or possibly differences in bike availability, as many of the northern stations are newer and may have launched with more electric bikes in their fleets."}</p>', unsafe_allow_html = True)
    create_electric_vs_regular_map()
    st.markdown(f'<h2 style = "color:#FFFFFF;font-size:36px;">{"Member vs. Casual Bike Usage by Neighborhood in 2024"}</h2>', unsafe_allow_html = True)
    st.markdown(f'<p style = "color:#FFFFFF;font-size:18px;">{"This overlapping bar chart compares the number of bike rides taken by members versus casual users across NYC neighborhoods. Neighborhoods are sorted in descending order by total member ride counts. Across the board, members consistently account for more rides than casual users — often by a large margin."}</p>', unsafe_allow_html = True)
    st.markdown(f'<p style = "color:#FFFFFF;font-size:18px;">{"The top three neighborhoods for overall bike activity are Midtown, Chelsea, and the East Village. This aligns with earlier visualizations, reinforcing these areas as major biking hubs, regardless of bike type or user status."}</p>', unsafe_allow_html = True)
    create_user_type_plot()

elif selected == "Network and Time Analysis":
    set_styling()
    st.markdown(f'<h1 style="color:#6CACE4;font-size:48px;">{"Network and Time Analysis"}</h1>', unsafe_allow_html = True)
    st.markdown(f'<h2 style = "color:#FFFFFF;font-size:36px;">{"Seasonal Trends of CITI Bike Ride Counts in 2024"}</h2>', unsafe_allow_html = True)
    st.markdown(f'<p style = "color:#FFFFFF;font-size:18px;">{"This line plot shows the change in ride counts by month in 2024. It clearly indicates a seasonal trend, with the highest counts occurring in the summer and fall. Usage increases with warmer temperatures and drops significantly during the cold winter months. This information can be used to inform seasonal patterns of maintaining Citi bike stations."}</p>', unsafe_allow_html = True)
    st.image("./input/images/citi_seasonal_ungrided.png")
    st.markdown(f'<h2 style = "color:#FFFFFF;font-size:36px;">{"Grouped Bar Plot: July CITI Bike Ride Duration Density (Normalized by User Type)"}</h2>', unsafe_allow_html = True)
    st.markdown(f'<p style = "color:#FFFFFF;font-size:18px;">{"This grouped bar plot shows the density of specific ride durations in July, normalized by user type. It reveals a clear trend toward shorter ride durations overall. Interestingly, casual users tend to have shorter ride durations, whereas members typically have longer ones. This information could inform potential route suggestions for members with the Citi bike app if descriptive statistics about ride duration are known."}</p>', unsafe_allow_html = True)
    st.image("./input/images/citi_duration_dark.png")
    st.markdown(f'<h2 style = "color:#FFFFFF;font-size:36px;">{"Hexbin Plot: July CITI Bike Ride Duration vs Distance"}</h2>', unsafe_allow_html = True)
    st.markdown(f'<p style = "color:#FFFFFF;font-size:18px;">{"This Hexbin plot shows the relationship between ride distance and duration. It was created by randomly sampling 200,000 rides from the month of July. The plot reveals a clear correlation between distance and duration, indicating that, aside from outliers, most users are using their bikes to travel from one place to another. Alternatively, the high frequency of rides with low distance and high duration suggests that some people take joy rides for extended periods without covering much ground."}</p>', unsafe_allow_html = True)
    st.image("./input/images/citi_hexbin_dark.png")
    st.markdown(f'<h2 style = "color:#FFFFFF; font-size:36px;">{"Bike Trip Network Across Manhattan Neighborhoods"}</h2>', unsafe_allow_html = True)
    st.markdown(f'<p style = "color:#FFFFFF;font-size:18px;">{"This circular network analysis illustrates the connections and most frequently used pathways between Manhattan neighborhoods. Node colors represent degree centrality, with red indicating highly trafficked hubs and blue indicating less trafficked ones. Node size reflects the number of rides entering and exiting each hub. The graph was created by randomly sampling ~80,000 rides from the 2024 Citi Bike data. It highlights Chelsea, Midtown, and the Upper and Lower East Sides as major hubs that users frequently travel to and from. This plot can be used to inform where future Citi bike stations can be built; for example, neighborhoods with more total rides can be prioritized for future station placement."}</p>', unsafe_allow_html = True)
    st.image("./input/images/Citi_Network_round.png")

elif selected == "External Data":
    set_styling()
    st.markdown(f'<h1 style="color:#6CACE4;font-size:48px;">{"Incorporating External Data Sources"}</h1>', unsafe_allow_html = True)
    st.markdown(f'<h2 style="color:#FFFFFF; font-size:36px;">{"Neighborhood Train Stop and Bike Station Statistics"}</h2>', unsafe_allow_html = True)
    st.markdown(f'<p style = "color:#FFFFFF; font-size:18px;">{"These tables provide descriptive statistics for both train stations and bike stations, offering a detailed overview of key metrics such as the number of stations and average closest distance from train stations to a bike station. The first table focused on Manhattan neighborhoods, and the second table focused on the level of boroughs."}</p>', unsafe_allow_html = True)
    #Create table for neighborhood statistics
    neighborhoodStatsFilepath = "./output/manhattan_neighborhood_stats.csv"
    boroughStatsFilepath = "./output/borough_stats.csv"
    dfNeighborhood = pd.read_csv(neighborhoodStatsFilepath)
    dfBorough = pd.read_csv(boroughStatsFilepath)
    st.markdown(f'<h3 style="color:#FFFFFF; font-size:30px;">{"Neighborhood Statistics (Manhattan Only)"}</h3>', unsafe_allow_html = True)
    st.dataframe(dfNeighborhood, hide_index = True)
    st.markdown(f'<h3 style="color:#FFFFFF; font-size:30px;">{"Borough Statistics"}</h3>', unsafe_allow_html = True)
    st.dataframe(dfBorough, hide_index = True)
    st.markdown(f'<h2 style="color:#FFFFFF; font-size:36px;">{"Median Income of Neighborhood by Number of Bike Stations"}</h2>', unsafe_allow_html = True)
    st.markdown(f'<p style="color:#FFFFFF;font-size:18px">{"This map shows the median income of neighborhoods in Manhattan and overlays it with clustered markers for the bike stations in Manhattan. The median income of a neighborhood has no clear association with the number of Citi bike stations in the neighborhood."}</p>', unsafe_allow_html = True)
    income_plot_and_stations()