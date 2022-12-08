import geopandas as gpd


def main():
    filename = "labels.geojson"
    output_path = "scaled_labels.geojson"
    xfactor = 0.7
    yfactor = 0.7

    gdf_fp = gpd.read_file(filename)
    gdf_fp['geometry'] = [gpd.GeoSeries(x).scale(xfact=xfactor, yfact=yfactor)[0] for x in gdf_fp['geometry']]
    gdf_fp.to_file(driver = 'GeoJSON', filename= output_path)


if __name__ == '__main__':
    main()
