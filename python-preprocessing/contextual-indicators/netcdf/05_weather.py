
"""
Weather station data:
     Requests /locations to retrieve metadata for available weather stations, 
     selects station identifiers and descriptive fields, 
     and converts longitude/latitude coordinates to point WKT.
     Selected fields:
     - name
     - wmoId
     - station_type
     - geometry_type
     - coordinates_wkt
     - id
"""

"""Weather observations (e.g., temperature): 
     Requests /position for the configured longitude, latitude, UTC timestamp, and weather parameters, 
     extracts the returned measurements, 
     and converts the observation coordinates to point WKT.
     Selected observations:
     - ta: air temperature measured at 1.5 m above ground level
     - Sav1H: wind speed past hour
     - pg: precipitation intensity past 10min
     - rh: relative humidity measured at 1.5 m above ground level   
"""

import os
import time
import sys
import pandas as pd
from shapely.geometry import Point
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from common_functions import get_json, save_csv
from config import OUTPUT_DIR


WEATHER_BASE = (
    "https://api.dataplatform.knmi.nl/edr/v1/collections/"
    "10-minute-in-situ-meteorological-observations"
)

# Example query settings. Change these values if another location/time is needed.
LONGITUDE = 2.9358
LATITUDE = 54.3256
DATETIME_UTC = "2026-07-26T10:30:00Z"
""" The names of air temperature, wind speed past hour, precipitation intensity past 10 min, and relative humidity past 10 min in the data source"""
PARAMETER_NAMES = "ta,Sav1H,pg,rh"


def main():
    """KNMI API token: Register at https://dataplatform.knmi.nl/ to obtain your own API token."""

    token = os.getenv("API_TOKEN")
    if not token:
        raise RuntimeError(
            "KNMI_API_TOKEN is not set. Register at https://dataplatform.knmi.nl/ "
            "and set your own token as an environment variable before running this script."
        )

    headers = {"Authorization": token}

    start = time.time()
    ###----------------------------------------------------------
    ### Weather stations
    ###----------------------------------------------------------
    """Selecting data in acquiring the data, before downloading"""
    """acquire the data"""
    stations_json = get_json(WEATHER_BASE, "locations", headers=headers)
    stations = pd.json_normalize(stations_json["features"])
    """Convert separate latitude and longitude values to WKT."""
    stations["coordinates_wkt"] = stations["geometry.coordinates"].apply(
        lambda point: Point(point[0], point[1]).wkt
    )
    """Change the names of columns of weather stations"""
    stations = stations.rename(
        columns={
            "properties.name": "name",
            "properties.wmoId": "wmoId",
            "properties.type": "station_type",
            "geometry.type": "geometry_type",
        }
    )[
        [
            "name",
            "wmoId",
            "station_type",
            "geometry_type",
            "coordinates_wkt",
            "id",
        ]
    ]
    station_output = save_csv(stations, OUTPUT_DIR, "weather_station.csv")
    print("Saved:", station_output)
    print(f"Weather-station processing time: {time.time() - start:.2f} s")
    ###----------------------------------------------------------
    ### Weather observations
    ###----------------------------------------------------------
    start = time.time()
    params = {
        "coords": Point(LONGITUDE, LATITUDE).wkt,
        "input": f"Platform({LATITUDE} {LONGITUDE})",
        "datetime": DATETIME_UTC,
        "parameter-name": PARAMETER_NAMES,
    }
    data = get_json(WEATHER_BASE, "position", headers=headers, **params)

    coverage = data["coverages"][0]
    axes = coverage["domain"]["axes"]
    ranges = coverage["ranges"]

    weather = pd.DataFrame(
        [
            {
                "coordinates_wkt": Point(
                    axes["x"]["values"][0], axes["y"]["values"][0]
                ).wkt,
                "time": axes["t"]["values"][0],
                "air_temperature_1_5m": ranges["ta"]["values"][0],
                "wind_speed_past_hour": ranges["Sav1H"]["values"][0],
                "precipitation_intensity_past_10min": ranges["pg"]["values"][0],
                "relative_humidity_1_5m": ranges["rh"]["values"][0],
            }
        ]
    )
    weather_output = save_csv(weather, OUTPUT_DIR, "weather.csv")
    print("Saved:", weather_output)
    print(f"Weather-observation processing time: {time.time() - start:.2f} s")


if __name__ == "__main__":
    main()
