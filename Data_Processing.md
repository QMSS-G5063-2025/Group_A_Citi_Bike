## Reading in Neighborhoods GeoJSON
Please use the following lines of code to read in the neighborhoods GeoJSON file and filter down to the Manhattan neighborhoods.
```python
neighborhoodsGeometryFilepath = "./input/nyc_neighborhoods.geojson"
boroughCol = "borough"
dfNeighborhoods = gpd.read_file(neighborhoodsGeometryFilepath)
manhattanFilter = dfNeighborhoods[boroughCol] == "Manhattan"
dfManhattan = dfNeighborhoods[manhattanFilter]
```