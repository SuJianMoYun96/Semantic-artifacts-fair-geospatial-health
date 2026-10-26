

# Repository Structure

The Python scripts are organised by data category and original data format and numbered according to their processing order:

```text
Python_coding/
├── Geographic_areas/
│   └── GeoPackage/
│       ├── 01_postcode4.py
│       └── 02_cbs_administrative_areas.py
│
├── Contextual_indicators/
│   ├── GeoTIFF/
│   │   └── 03_rivm_rasters.py
│   ├── Plain_text/
│   │   └── 04_traffic_safety.py
│   ├── NetCDF/
│   │   └── 05_weather.py
│   ├── XLSX/
│   │   └── 06_taxi_stops.py
│   ├── XML/
│   │   ├── 07_public_transport_stops.py
│   │   └── 08_green_space_administrative.py
│   └── CSV/
│       └── 09_land_use_diversity.py
│
├── common_functions.py
├── config.py
├── FUNCTION_AUDIT.md
├── README.md
└── requirements.txt
```

`common_functions.py` contains functions reused across multiple scripts, including downloading files, saving CSV files, requesting JSON data, identifying the URL of the latest available file, extracting ZIP archives, recursively locating files of a specified format, exporting selected GeoPackage fields to CSV, and extracting local XML tag names without namespace prefixes.

`FUNCTION_AUDIT.md` provides an overview of which file formats use the shared functions and which data sources are handled by script-specific functions.

`config.py` specifies the directory in which the generated CSV files are stored.

`requirements.txt` lists the Python package dependencies required to run the scripts.

---
# List of abbreviations
The following table lists the abbreviations of the data platforms referred to throughout this repository.

| Abbreviation | Full name |
|---|---|
| CBS | Statistics Netherlands |
| Police | data.politie.nl (Dutch Police Open Data Platform) |
| PDOK | Publieke Dienstverlening Op de Kaart |
| RIVM | National Institute for Public Health and the Environment |
| NDW | National Road Traffic Data Portal |
| NDOV | Nationale Data Openbaar Vervoer |
| KNMI | Royal Netherlands Meteorological Institute |


These data platforms supply data in several different file formats. The following table summarises the main formal and geospatial file formats referred to in the data acquisition and preprocessing workflow. 

| Category | File format |
|---|---|
| File types | Comma-Separated Values (CSV) |
| File types | Plain Text (TXT) |
| File types | Extensible Markup Language (XML) |
| File types | Microsoft Excel Workbook (xlsx) |
| Geospatial data formats | GeoPackage (GPKG) |
| Geospatial data formats | GeoTIFF |
| Geospatial data formats | Network Common Data Form (NetCDF) |

---
# Setup and Running the Python Scripts

Before running `01_...py` to `09_...py`, configure the output directory, install the required Python packages, and provide any source-specific inputs required by individual scripts.

**1. Configure the output directory**

Open `config.py` and specify the directory in which the generated CSV files should be stored:

```python
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent

# Change this path to the folder where the CSV files should be stored
OUTPUT_DIR = Path(
    r"Your path to the folder containing the CSV files"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
```

Replace:

```text
Your path to the folder containing the CSV files
```

with the desired directory on your computer.

For example, on Windows:

```python
OUTPUT_DIR = Path(
    r"C:\Users\username\Documents\RDFization\CSVs"
)
```

On macOS or Linux:

```python
OUTPUT_DIR = Path(
    "/home/username/RDFization/CSVs"
)
```

All scripts from `01_...py` to `09_...py` use the `OUTPUT_DIR` defined in `config.py`. The same directory should therefore also be used as the CSV data location in the subsequent PostgreSQL data-loading steps.

---

**2. Install the required Python packages**

The required Python packages are listed in `requirements.txt`:

- `beautifulsoup4==4.15.0`
- `geopandas==1.1.4`
- `numpy==2.5.2`
- `openpyxl==3.1.5`
- `pandas==3.0.5`
- `pyogrio==0.13.0`
- `rasterio==1.5.1`
- `requests==2.34.2`
- `shapely==2.1.2`

`geopandas` is used to read, manipulate, and analyse vector geospatial data, such as GeoPackage files; `rasterio` is used to process raster data, such as GeoTIFF files; `shapely` is used for geometric operations, including creating geometries from coordinate information and converting geometries to WKT representations; and `pyogrio` is used for efficient reading and writing of vector geospatial files.

Open **PowerShell** or the **Terminal** in PyCharm and navigate to the `Python_coding` directory, where `requirements.txt` is located:

```powershell
cd "C:\path\to\RDFization-of-geographic-area-and-contextual-indicator-data\Semantic artifacts\Python_coding"
```

> Replace the path above with the location of the repository on your computer.

If a `.venv` virtual environment does not yet exist in the parent `Semantic artifacts` directory, create one:

```powershell
cd ..
py -m venv .venv
cd "Python_coding"
```

Install all required packages using the Python interpreter from the virtual environment:

```powershell
& "..\.venv\Scripts\python.exe" -m pip install -r requirements.txt
```

To verify the installation:

```powershell
& "..\.venv\Scripts\python.exe" -m pip list
```

If `.venv` already exists, the virtual-environment creation step can be skipped.

---

**3. Configure source-specific inputs**

Some scripts require additional user-provided inputs before they can be run.

**KNMI API token for `05_weather.py`**

`05_weather.py` requires a personal KNMI API token. Each user should register at:

```text
https://dataplatform.knmi.nl/
```

and obtain their own API token.

In Windows PowerShell, set the token as an environment variable before running the script:

```powershell
$env:KNMI_API_TOKEN="<your_api_token>"
```

The Python script retrieves the token from the `KNMI_API_TOKEN` environment variable. The token should not be stored directly in the source code or committed to Git.

**CBS input file for `09_land_use_diversity.py`**

The input file:

```text
CBS data no calculation.csv
```

is downloaded manually from the CBS Open Data portal and should be placed in the directory specified by `OUTPUT_DIR` before running `09_land_use_diversity.py`.

The script reads the file using:

```python
input_path = OUTPUT_DIR / "CBS data no calculation.csv"
```

Detailed instructions for selecting and downloading the required CBS variables are provided in the data-acquisition section below.

---

**4. Run the Python scripts**

The Python scripts should be run from the `Python_coding` directory.

If necessary, navigate to this directory first:

```powershell
cd "C:\path\to\RDFization-of-geographic-area-and-contextual-indicator-data\Semantic artifacts\Python_coding"
```

Run the scripts in numerical order using the Python interpreter from the `.venv` virtual environment:

```powershell
& "..\.venv\Scripts\python.exe" ".\Geographic_areas\GeoPackage\01_postcode4.py"

& "..\.venv\Scripts\python.exe" ".\Geographic_areas\GeoPackage\02_cbs_administrative_areas.py"

& "..\.venv\Scripts\python.exe" ".\Contextual_indicators\GeoTIFF\03_rivm_rasters.py"

& "..\.venv\Scripts\python.exe" ".\Contextual_indicators\Plain_text\04_traffic_safety.py"

& "..\.venv\Scripts\python.exe" ".\Contextual_indicators\NetCDF\05_weather.py"

& "..\.venv\Scripts\python.exe" ".\Contextual_indicators\XLSX\06_taxi_stops.py"

& "..\.venv\Scripts\python.exe" ".\Contextual_indicators\XML\07_public_transport_stops.py"

& "..\.venv\Scripts\python.exe" ".\Contextual_indicators\XML\08_green_space_administrative.py"

& "..\.venv\Scripts\python.exe" ".\Contextual_indicators\CSV\09_land_use_diversity.py"
```

Each script downloads or processes its corresponding source data and writes the generated CSV file(s) to the directory specified by `OUTPUT_DIR` in `config.py`.

The scripts contain the processing logic specific to each data source, keeping source-specific column names, API parameters, parsing rules, and transformations close to the relevant data.

---

# Overview of the Python Scripts
## Downloading CSV Data and Performing Calculations Where Applicable

> **Coordinate reference system (CRS):** Data from the following two data sources use **Amersfoort / RD New (EPSG:28992)**.

### CBS Data Processing for Land-Use Diversity and Area Proportion of Inland Water and Residential Area (CSV)

For **land-use diversity**, **area proportion of inland water**, and **area proportion of residential area**, use the [CBS Open Data table](https://opendata.cbs.nl/portal.html?_la=nl&_catalog=CBS&tableId=86211NED&_theme=313).

In **Onbewerkte datasets**, select the following variables under **Onderwerpen**:

| Variable | Description | Used for |
|---|---|---|
| `content.properties.Gemeentenaam_1` | Municipality name | Region identification |
| `content.properties.SoortRegio_2` | Region type | Region identification |
| `content.properties.Codering_3` | Region code | Region identification |
| `content.properties.TotaalLandEnWater_4` | Total land and water area | Denominator for area proportions |
| `content.properties.TotaalBinnenwater_42` | Total inland water area | Inland water proportion |
| `content.properties.TotaalRecreatiefTerrein_27` | Total recreational area | Land-use diversity |
| `content.properties.Bedrijfsterrein_19` | Business / industrial area | Land-use diversity |
| `content.properties.Sportterrein_29` | Sports area | Land-use diversity |
| `content.properties.Woonterrein_15` | Residential area | Residential area proportion; land-use diversity |
| `content.properties.SociaalCultureleVoorziening_18` | Social and cultural facilities | Land-use diversity |
| `content.properties.OpenbareVoorziening_17` | Public service area | Land-use diversity |

For **Alle regio-indelingen**, select **all available region classifications**.

Then download the CSV file.

##### Calculations

The area proportion of inland water and residential area are derived later in the PostgreSQL/Ontop workflow from the selected CBS variables and therefore require no calculation at this stage.

Land-use diversity is not provided directly by CBS and is calculated using the Shannon entropy method adopted by the [Geoscience and Health Cohort Consortium (GECCO)](https://www.gecco.nl/exposure-data-1/):

```text
H = - sum(p_i ln(p_i)) / ln(n)
```

where `p_i` is the proportion of land-use category `i`, and `n = 5`.

The five land-use categories are:
1. **Residential**: residential areas and leisure accommodation;
2. **Commercial**: retail and catering establishments;
3. **Social and cultural services;**
4. **Offices and public services;**
5. **Green and recreational space**: parks, forests, graveyards, sports fields, and day-recreation areas.

Ontop/PostgreSQL do not support the LN() function, and is calculated in Python using:

`09_land_use_diversity.py` 
1. Reads the downloaded CBS CSV file;
2. Converts the required land-use and total-area fields to numeric values;
3. Calculates the proportion of each selected land-use category relative to the total land and water area;
4. Calculates normalised Shannon entropy for each record;
5. Assigns a diversity value of `0` when only one valid land-use category is present; and
6. Exports a new CSV file with an additional `land_use_diversity` column.


### Police Data Download for Crime Safety (CSV)

For **crime safety**, use the [Police Open Data table](https://data.politie.nl/portal.html?_la=nl&_catalog=Politie&tableId=47022NED&_theme=141).

In **Onbewerkte datasets**:
- Under **Soort misdrijf**, select **Totaal misdrijven**;
- Under **Wijken en buurten**, select **Alles**; and
- Under **Perioden**, select the desired month.
Then download the CSV file.

---

## Preprocessing Non-CSV Data Sources into a Common CSV Format Using Python
>**Coordinate reference system (CRS):** Except for the KNMI weather station and observation data, which use **WGS84 (EPSG:4326)**, data from all other sources use **Amersfoort / RD New (EPSG:28992)**.

This repository contains **Python_coding** to download environmental data from several Dutch sources and convert selected data from **six non-CSV file formats** into CSV files for subsequent database, Ontop, and RDF workflows. Unless otherwise stated, the scripts **retain the source CRS**. Geometric information is exported as **WKT** and converted to **2D** to remove unnecessary Z coordinates.


### Description of Data Sources, Processing Scripts, and Outputs

The Python scripts retrieve and preprocess geographic-area and contextual-indicator data from multiple Dutch data providers. The table below provides a concise overview. Detailed information for each script is provided in the following sections.

| Script | Provider | Data source | Format | Main output |
|---|---|---|---|---|
| `01_postcode4.py` | PDOK | Postal code four areas | GeoPackage | `postcode4_data_not_WGS84.csv` |
| `02_cbs_administrative_areas.py` | CBS | Districts and neighbourhoods | GeoPackage | `wijken_2024.csv`, `buurten_2024.csv` `wijken_2026.csv`, `buurten_2026.csv` |
| `03_rivm_rasters.py` | RIVM | Green-space proportion and NDVI | GeoTIFF | `raster_green_space.csv`, `raster_ndvi.csv` |
| `04_traffic_safety.py` | NDW | BRON traffic accidents and locations | TXT | `traffic_safety_filter.csv`, `traffic_safety_location_filter.csv` |
| `05_weather.py` | KNMI | Weather stations and observations | NetCDF / API | `weather_station.csv`, `weather.csv` |
| `06_taxi_stops.py` | NDOV | Taxi stops | XLSX | `clean_taxi.csv` |
| `07_public_transport_stops.py` | NDOV | Public-transport stops and stations | XML | `public_transport_stops_not_WGS84.csv` |
| `08_green_space_administrative.py` | RIVM | Green-space proportion by administrative area | XML | `area_proportion_green_wijk.csv`, `area_proportion_green_buurt.csv` |


### **PDOK Data for Dutch 4-digit postal code areas (GeoPackage)**
#### Data source information

**1： Provider:**  PDOK

**2： Source / discovery URL:**  `https://service.pdok.nl/cbs/postcode4/atom/postcode4_numeriek_deel.xml`

**3： Source selection:**  Latest available

**4： Year:** 2024

**5： Original format:**  GeoPackage (`.gpkg`), discovered through an Atom XML feed

---
#### Python script information

**1： Processing:**  
- Discovers the latest available GeoPackage for Dutch 4-digit postal code areas from the PDOK Atom feed.
- Downloads the GeoPackage file.
- Selects the required fields.
- Replaces the source missing-value codes `-99995` and `-99997` with `NaN`.
- Converts the geometry to two-dimensional (2D) Well-Known Text (WKT).

**2: Selected fields:**  
- `postcode` — 4-digit postal code, e.g. `1095` in Amsterdam
- `omgevingsadressendichtheid` — renamed to `address_density`, representing the address density within each 4-digit postal code area
- `geometry` — converted to two-dimensional (2D) Well-Known Text (WKT) to represent the area coordinates

**3: Transformation to WKT:**  Yes

---
#### Output CSV information

**1: Output file:**  `postcode4_data_not_WGS84.csv`

---

### **2. CBS data for administrative districts and neighbourhood areas (GeoPackage)**

#### Data source information

**1: Provider:**  CBS

**2: Source / discovery URL:**  Data source site: `https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data `; API: `https://geodata.cbs.nl/files/Wijkenbuurtkaart/WijkBuurtkaart_2024_v2.zip` `https://geodata.cbs.nl/files/Wijkenbuurtkaart/WijkBuurtkaart_2026_v0.zip`

**3: Source selection:**  Fixed version

**4: Year:** 2024 and 2026

**5: Original format:**  GeoPackage (`.gpkg`), containing in the ZIP archive

---

#### Python script information

**1: Processing:**  
- Downloads and extracts the ZIP archive,
- Extracts the archive to the configured output directory,
- Finds the GeoPackage (`.gpkg`) file in the extracted folder,
- Reads the district (`wijken`) and neighbourhood (`buurten`) layers,
- Selects the required fields;
- Adds a `jaar` column containing the corresponding data source year,
- Converts geometric information to 2D WKT, removing any Z dimension if present,
- Exports each administrative level as a separate CSV file.

**2: Selected fields:**  
- `jaar` (year), 
- `geometry`, 
- the following year-specific attributes: { 
   2024:
  `wijken`: `wijknaam`, `wijkcode`, `gemeentecode`, `gemeentenaam`
  `buurten`: `buurtcode`, `buurtnaam`, `wijkcode`, `gemeentecode`, `gemeentenaam`;
   2026:
   `wijken`: `wk_code`, `wk_naam`, `gm_code`, `gm_naam`
   `buurten`: `bu_code`, `bu_naam`, `wk_code`, `gm_code`, `gm_naam`}

**3: Transformation to WKT:**  Yes

---

#### Output CSV information

**1: Output file:**  `wijken_2024.csv`, `buurten_2024.csv` `wijken_2026.csv`, `buurten_2026.csv` 

---

### **3. RIVM data for area proportion of green space and the Normalised Difference Vegetation Index (NDVI) in 10-meter grids (GeoTIFF)**
#### Data source information

**1: Provider:**  RIVM

**2: Source / discovery URL:**  Data source site: `https://data.rivm.nl/meta/srv/eng/catalog.search#/metadata/32494ae3-db92-469b-a3d7-458b90342a5e?tab=relations `; API: `https://data.rivm.nl/data/alo/rivm_20240101_groenkaart_2022.zip` `https://data.rivm.nl/data/ank/ndvi_sentinel_2022.zip`

**3: Source selection:**  Latest available, determined from the latest available `ndvi` and `groenkaart` archive 

**4: Year:** 2022

**5: Original format:**  GeoTIFF (`.tif`), containing in the ZIP archive


---
#### Python script information

**1: Processing:**  
- Finds the latest available ZIP containing `ndvi` or `groenkaart`, 
- Extracts the GeoTIFF,
- Processes it block by block,
- Converts valid raster cells to polygon WKT,
- NDVI values are retained unchanged, while the values of area proportion of green space are divided by 100.

**3: Transformation to WKT:**  Yes

---

#### Output CSV information

**1: Output file:**  `raster_ndvi_<source>.csv`, `raster_green_space_<source>.csv`

---


### 4. NDW data for Traffic safety (TXT)

#### Data source information

**1: Provider:**  NDW

**2: Source / discovery URL:**  Data source site: `https://verkeersveiligheid.ndw.nu/dataset/bestand-geregistreerde-ongevallen-in-nederland-bron `; API: `https://verkeersveiligheid.ndw.nu/cms/api/dataset` 

**3: Source selection:**  Latest available

**4: Year:** 2025

**5: Original format:**  TXT files (`.txt`), containing in the ZIP archive



#### Python script information
**1: Processing:**  
- Queries the NDW data source API,  
- Selects the latest ZIP archive by year,  
- Extracts the traffic-accident TXT file,  
- Retains the fields required for the traffic-accident observations,  
- Extracts the `puntlocaties` TXT file from the same ZIP archive,  
- Selects the location identifier and coordinate fields,  
- Converts the x/y coordinates to point WKT for the traffic-accident point locations.  

**2: Selected fields:**  
For ZIP registered traffic accidents:  
- `VKL_NUMMER`: Unique identifier of the traffic accident,  
- `DATUM_VKL`: Accident date,  
- `JAAR_VKL`: Year in which the traffic accident occurred,  
- `TIJDSTIP`: Time of the accident,  
- `DDL_ID`: Part of the day in which the accident occurred,  
- `JTE_ID`: Unique identifier of the junction where the accident occurred,  
- `WVK_ID`: Unique identifier of the road segment where the accident occurred,  
- `HECTOMETER`: Hectometre marker value at the accident location,  
- `FK_VELD5`: Link field used to connect the accident record to the Point Locations dataset,  
- `HUISNUMMER`: House number at the accident location,  
- `GME_ID`: Unique identifier of the municipality in which the accident occurred,  
- `GME_NAAM`: Name of the municipality in which the accident occurred,  
- `PVE_CODE`: Province code,  
- `PVE_NAAM`: Province name,  
- `KDD_NAAM`: Name of the framework act area in which the accident occurred,  
- `PLT_NAAM`: Name of the police district in which the accident occurred,  
- `DIENSTCODE`: Code of the sub-region within the region,  
- `DIENSTNAAM`: Name of the sub-region within the region,  
- `DISTRCODE`: District code,  
- `DISTRNAAM`: District name,  
- `DAGTYPE`: Indicates whether the accident occurred on a weekday or weekend.  

For ZIP traffic-accident point locations:  
- Location identifier fields,  
- x-coordinate,  
- y-coordinate.  

**3: Transformation to WKT:**  
Yes, from x/y coordinates to point WKT for the traffic-accident point-location data.

#### Output CSV information

**1: Output file:**  `traffic_safety_location_filter.csv`, `traffic_safety_filter.csv`

---


#### 5. KNMI data for weather stations and observations (NetCDF)
Before running the script, a personal KNMI API token must be stored in the `KNMI_API_TOKEN` environment variable. Each user must register at:

`https://dataplatform.knmi.nl/`

and provide their own token through the `KNMI_API_TOKEN` environment variable.

Windows PowerShell:

```powershell
$env:KNMI_API_TOKEN="YOUR_TOKEN_HERE"
python 05_weather.py
```
macOS/Linux:

```bash
export KNMI_API_TOKEN="YOUR_TOKEN_HERE"
python 05_weather.py
```
---
#### Data source information

**1: Provider:**  KNMI

**2: Source / discovery URL:**  `https://api.dataplatform.knmi.nl/edr/v1/collections/10-minute-in-situ-meteorological-observations` 

**3: Source selection:**  Latest available

**4: Year:** Weather stations (2026), meteorological observations (last 10 minutes)

**5: Original format:**  NetCDF

---
#### Python script information

**1: Processing:**  
For weather station data:  
- Requests `/locations` to retrieve metadata for available weather stations,  
- Selects station identifiers and descriptive fields,  
- Converts longitude and latitude coordinates to point WKT.  

For meteorological observations:  
- Requests `/position` using the configured longitude, latitude, UTC timestamp (e.g., `2026-07-26T10:30:00Z`), and weather parameters,  
- Extracts the returned weather measurements,  
- Converts the observation coordinates to point WKT.  

**2: Selected fields:**  
For weather station data:  
- `name`  
- `wmoId`  
- `station_type`  
- `geometry_type`  
- `coordinates_wkt`  
- `id`  

For weather observations:  
- `ta`: Air temperature measured at 1.5 m above ground level,  
- `Sav1H`: Wind speed over the past hour,  
- `pg`: Precipitation intensity over the past 10 minutes,  
- `rh`: Relative humidity measured at 1.5 m above ground level.  

**3: Transformation to WKT:**  
Yes, from longitude and latitude coordinates to point WKT for both weather-station and weather-observation data.
---
#### Output CSV information

**1: Output file:**  `weather.csv`, `weather_station.csv`

---


#### 6. NDOV data for taxi stops (xlsx)
In the Netherlands, haltetaxi refers to a demand-responsive taxi service that picks up and drops off passengers at designated stops, complementing regular public transport services.

#### Data source information

**1: Provider:**  NDOV

**2: Source / discovery URL:**  Data source site: `https://data.ndovloket.nl/`; API: `https://data.ndovloket.nl/htz/Rittenplanning%20haltetaxi%20ingang%204%20nov%209292%20format%20versie%2046.42.xlsx`

**3: Source selection:**  Fixed version

**4: Year:** 2018

**5: Original format:**  Excel workbook (`.xlsx`)

---
#### Python script information

**1: Processing:**  
- Reads all valid Excel sheets, 
- Identifies the actual header using the `haltenr` keyword, 
- Keeps the selected fields, 
- Converts x/y coordinates to WKT, 
- Optionally removes duplicate geometries.

**2: Selected fields:**  
- `haltenr`: stop station code
- `oord x`
- `coord y`  
- `plaats, halte`: stop station name
 

**3: Transformation to WKT:**  
Yes, from longitude and latitude coordinates to point WKT.
---
#### Output CSV information

**1: Output file:**  `clean_taxi.csv`

---


#### 7. NDOV public transport stops: Bus, ferry, metro, rail, and tram stations (XML)

#### Data source information

**1: Provider:**  NDOV

**2: Source / discovery URL:**  Data source site: `https://data.ndovloket.nl/`; API: `https://data.ndovloket.nl/htz/Rittenplanning%20haltetaxi%20ingang%204%20nov%209292%20format%20versie%2046.42.xlsx`

**3: Source selection:**  Fixed version

**4: Year:** 2026

**5: Original format:**  Excel workbook (`.xlsx`)

---
#### Python script information

**1: Processing:**  
- Dynamically locates the latest compressed XML export from NDOV,
- Downloads and decompresses it,
- Parses `stopplace` elements and flattens selected nested fields into columns,
- Creates point WKT from x/y coordinates.

**2: Selected fields:**  
- `ID`: Unique identifier of the StopPlace,  
- `stopplacename.publicname`: Public name of the StopPlace,  
- `stopplacename.validfrom`: Date from which the StopPlace name is valid,  
- `stopplacetype`: Type of StopPlace, including bus, ferry, rail, tram, and metro,
- `stopplacecode`: StopPlace code,  
- `stopplacelocation.rd-x`: x-coordinate of the StopPlace,  
- `stopplacelocation.rd-y`: y-coordinate of the StopPlace,  
- `stopplacename.street`: Street name of the StopPlace,  
- `stopplacename.town`: Town name of the StopPlace,  
- `quays.quay.ID`: Unique identifier of the quay,  
- `quays.quay.quaylocationdata.validfrom`: Date from which the quay location data is valid,  
- `quays.quay.validfrom`: Date from which the quay record is valid,  
- `quays.quay.quaycode`: Quay code,  
- `quays.quay.quaynamedata.quayname`: Name of the quay,  
- `quays.quay.quaytransportmodes.transportmodedata.transportmode`: Transport mode served by the quay,  
- `quays.quay.quaylocationdata.rd-x`: RD x-coordinate of the quay,  
- `quays.quay.quaylocationdata.rd-y`: RD y-coordinate of the quay,  
- `quays.quay.quaylocationdata.street`: Street name of the quay location,  
- `quays.quay.quaylocationdata.town`: Town name of the quay location,  
- `quays.quay.quaymunicipality.municipalitycode`: Municipality code of the quay.

**3: Transformation to WKT:**  Yes, from longitude and latitude coordinates to point WKT.

---
#### Output CSV information

**1: Output file:**  `public_transport_stops_not_WGS84.csv`

---
#### 8. RIVM data for the area proportion of green spaces in administrative districts and neighbourhoods (XML)
`08_green_space_administrative.py` uses WFS `GetCapabilities` to find the newest available `groenpercentage` layer separately for administrative district and neighbourhood areas. It then requests each feature layer, retains the requested statistics, divides them by 100, forces geometry to 2D, and exports WKT.



#### Data source information

**1: Provider:**  RIVM

**2: Source / discovery URL:**  Data source site: `https://data.rivm.nl/meta/srv/eng/catalog.search#/metadata/fad5f00d-cdb8-45f4-a180-e813b3ae6c74?tab=relations`; API: `https://data.rivm.nl/geo/ank/wfs`

**3: Source selection:**  Latest available

**4: Year:** 2022

**5: Original format:**  XML returned by a WFS service and determined from the latest available `groenpercentage` layers

---
#### Python script information

**1: Processing:**  
- Reads the WFS capabilities document, 
- Identifies the latest `groenpercentage` layers for `gemeente`, `wijk`, and `buurt`, 
- Retrieves the corresponding features, 
- Divides percentage fields by 100, 
- Converts geometry to polygon WKT. 

**2: Selected fields:**  
- For `wijk`:
  - `wk_code`: District code,  
  - `wk_naam`: District name,  
  - `gm_code`: Municipality code,  
  - `_mean`: Mean value,  
  - `_stdev`: Standard deviation,  
  - `_min`: Minimum value,  
  - `_max`: Maximum value.  

- For `buurt`:
  - `bu_code`: Neighbourhood code,  
  - `bu_naam`: Neighbourhood name,  
  - `wk_code`: District code,  
  - `gm_code`: Municipality code,  
  - `_mean`: Mean value,  
  - `_stdev`: Standard deviation,  
  - `_min`: Minimum value,  
  - `_max`: Maximum value.  

- `geometry`: Geometry of the administrative area.
 

**3: Transformation to WKT:**  Yes

---
#### Output CSV information

**1: Output file:**  `area_proportion_green_wijk.csv`, `area_proportion_green_buurt.csv`

---



## Reproducibility and maintenance notes
1. **Dynamic sources:** Scripts for PDOK Ducth four-digit postal code areas, RIVM data sources about area proportion of green space and NDVI in 10-meter grids, NDW traffic-safety data, NDOV public transport stops (Bus, ferry, metro, rail, and tram stations), and RIVM data sources about area proportion of green spaces in administrative wijk- en buurtkaart- area automatically identify and download the latest available source data.

2. **Fixed sources:** The CBS administrative wijk- and buurt- area, and the NDOV public transport stops (Taxi stops) currently use fixed URLs. Update the relevant constants when newer versions are required.

3. **Large outputs:** For RIVM data sources about area proportion of green space and NDVI in 10-meter grids, conversion can generate very large CSV files. Keep generated data outside Git version control and publish large derived datasets through an appropriate data repository when needed.

4. **Credentials:** The KNMI API token is user-specific and must not be stored in source control.

5. **Schema changes:** Source column names and XML structures may change over time. Where practical, the scripts raise explicit errors when required fields are missing so that such changes are detected rather than producing incomplete outputs silently.

In total, **17** CSV files can be generated: one CSV file containing crime safety data is downloaded in the **Data Acquisition and Selection** section, while the remaining 16 CSV files are generated in the **Preprocessing Non-CSV Data Sources into a Common CSV Format** section.

