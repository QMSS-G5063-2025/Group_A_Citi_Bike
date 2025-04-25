# Group_A_Citi_Bike
Group Project Repo

### Group title: The Citi of Bikes

### Brief description:
In this project, we used a mix of interactive and static visualizations to explore trends in Citi Bike usage and deployment across Manhattan. An **interactive time-layered map** highlighted how station coverage has expanded from 2014 to 2024. To compare rider behavior, we used a **heatmap** for electric vs. classic bike usage and a **bar plot** to contrast member vs. casual rider patterns by neighborhood.

A **circular network** graph visualized trip flows between neighborhoods, while a **hexbin plot** examined the relationship between ride duration and distance during peak summer months. Seasonal usage trends were captured with a **line chart**, showing how ridership fluctuates over the year.

We also included a **comparative table** to examine infrastructure alignment, showing the number of bike and subway stations per neighborhood and their proximity. Lastly, an **interactive map overlaying average income and station count** helped us assess the equity of station distribution.

Each visualization was designed to reveal a different dimension of the data—from spatial growth and rider demographics to network flow and social context.


### Team members
- Varsha Varkhedi (vv2392@cumc.columbia.edu)
- Yanwei Li (yl5403@cumc.columbia.edu)
- Adit Anand (adit.anand@columbia.edu)

### Data
#### df_07xx_nyc.pkl
It stores the station information for July data of the years 2014, 2019, and 2024, and filtered the data based on the precincts that only falls within **Manhattan**. 

Every row is unique, and every station ID will only be matched with a single station name, lat, and lng.

- 'station id': all station IDs that exist within the data.
- 'station name': the corresponding station name of that station ID.
- 'station latitude': the corresponding station latitude of that station ID.
- 'station longitude': the corresponding station longitude of that station ID.
- 'geometry': the geospatial data of the **start station**.
- 'index_right': the index from the precinct dataframe, which I merged. Not very useful.
- 'Precinct': the precinct matched to the start station lat and lng.
- 'Shape_Leng': the shape length of the precinct.
- 'Shape_Area': the area of the precinct.


#### df_all_24_nyc.pkl
This file in in [Google Drive](https://drive.google.com/drive/folders/1ZopAQfZGVEy3_q5dNR8q6IhZxdkayQ2E). Github does not allow files greater than 100MB.

It merged all the CSV files for 2024, and filtered the data based on the precincts that only falls within **Manhattan**.
You may notice the same station ID may have different station names, and the same station name may have different station latitude and station longitude. 

Note: If you need to filter by station ID or station name (like my first plot), you can first group by station IDs, station names, station latitudes, station longitudes. Then sort by station ID and count. Next use the most frequent appearing combination of the 4 columns as ground truth. (Vivian can share you the code to do this if you need the code.)

Note: It usually takes 3 - 6 minutes to load the pickle file. If the loading pickle file tells you the file is corupted, it might be due to the pickle package version you are using. We can corrdinate on the python and package version if this is an issue.


- 'ride_id': the unique identifier for the ride itself, not the rider.
- 'rideable_type': classic or electric.
- 'started_at': starting time of the ride.
- 'ended_at': ending time of the ride.
- 'start_station_name': the station name of the start station.
- 'start_station_id': the station id of the start station.
- 'end_station_name': the station name of the end station.
- 'end_station_id': the station id of the end station.
- 'start_lat': the start station latitude.
- 'start_lng': the start station longitude.
- 'end_lat': the end station latitude.
- 'end_lng': the end station longitude.
- 'member_casual': member or casual rider.
- 'rideable_type_duplicate_column_name_1': I think it is just a duplicate of column 'ridable_type'. I did not drop because it was in the original data. Most are NaNs as well.
- 'Unnamed: 0': Unsure what this is, but was in the original data, so I kept it in there. Most are NaNs.
- 'geometry': the geospatial data of the **start station**.
- 'index_right': the index from the precinct dataframe, which I merged. Not very useful.
- 'Precinct': the precinct matched to the start station lat and lng.
- 'Shape_Leng': the shape length of the precinct.
- 'Shape_Area': the area of the precinct.
