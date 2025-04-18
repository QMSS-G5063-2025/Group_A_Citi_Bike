## Reading in Neighborhoods GeoJSON
Please use the following lines of code to read in the neighborhoods GeoJSON file and filter down to the Manhattan neighborhoods.
```python
import geopandas as gpd
neighborhoodsGeometryFilepath = "./input/nyc_neighborhoods.geojson"
boroughCol = "borough"
dfNeighborhoods = gpd.read_file(neighborhoodsGeometryFilepath)
manhattanFilter = dfNeighborhoods[boroughCol] == "Manhattan"
dfManhattan = dfNeighborhoods[manhattanFilter]
```

## Reading in CITI Bike Station
Please use the following code to extract an array of JSON objects. Each JSON object contains information (including but not limited to latitude, longitude, station name) about a unique bike station.
```python
import json
bikeStationsFilepath = "./input/citi_bike_station_information.json"
fp = open(bikeStationsFilepath, "r")
stationInformation = json.load(fp)
bikeStations = stationInformation["data"]["stations"]
``` 