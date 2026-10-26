
# PostgreSQL Data Loading and Virtual RDF Creation and Exposure Using Ontop

This guide describes how to configure **PostgreSQL 16**, **PostGIS**, and **Ontop** to load the transformed environmental data and expose them as virtual RDF.

The implementation uses four PostgreSQL databases and four Ontop SPARQL endpoints:

```text
PostgreSQL 16
│
├── geographic_area_db
│   └── Ontop → http://localhost:<GA_ENDPOINT_PORT>/sparql
│
├── contextual_indicator_db
│   └── Ontop → http://localhost:<CI_ENDPOINT_PORT>/sparql
│
├── raster_green_space_db
│   └── Ontop → http://localhost:<GREEN_ENDPOINT_PORT>/sparql
│
└── raster_ndvi_db
    └── Ontop → http://localhost:<NDVI_ENDPOINT_PORT>/sparql
```

PostGIS is enabled where spatial functionality is required.

The source data remain in PostgreSQL. Ontop exposes them dynamically as RDF through the mapping files, so full RDF materialisation is not required. For very large raster-derived datasets, additional PostgreSQL storage configuration may be required if the default storage location does not have sufficient free space.

---

### 1. Local Values Used in this Guide

Some paths and ports depend on the local computer and should not be hard-coded.

| Placeholder | Meaning | Example / source |
|---|---|---|
| `<PSQL_PATH>` | Location of `psql.exe` | Usually `C:\Program Files\PostgreSQL\16\bin\psql.exe` |
| `<POSTGRES_PORT>` | PostgreSQL port | Obtain with `SHOW port;` |
| `<OUTPUT_DIR>` | Folder containing the Python-generated CSV files | Defined by `OUTPUT_DIR` in `Python coding\config.py` |
| `<ONTOP_DIR>` | Ontop CLI installation folder | User-defined |
| `<CONFIG_DIR>` | `Ontop mapping` folder containing the `.obda`, `.properties`, and `database_setup.sql` files | User-defined |
| `<RASTER_STORAGE_DIR>` | Storage location used for large raster PostgreSQL tablespaces when the default PostgreSQL data directory has insufficient free space | User-defined |
| `<TEMP_STORAGE_DIR>` | Storage location used for PostgreSQL temporary query files | User-defined |
| `<RDF_OUTPUT_DIR>` | Storage location used for optional materialised RDF output files | User-defined |
| `<GA_ENDPOINT_PORT>` | Geographic-area Ontop HTTP port | e.g. `8080` |
| `<CI_ENDPOINT_PORT>` | Contextual-indicator Ontop HTTP port | e.g. `8081` |
| `<GREEN_ENDPOINT_PORT>` | Green-space raster Ontop HTTP port | e.g. `8082` |
| `<NDVI_ENDPOINT_PORT>` | NDVI raster Ontop HTTP port | e.g. `8083` |

The location of the CSV folder must match the `OUTPUT_DIR` value defined in `Python coding\config.py`.

Two different types of ports are used:

```text
PostgreSQL -- <POSTGRES_PORT> --> Ontop -- <ENDPOINT_PORT> --> SPARQL
               e.g. 5432                   e.g. 8080–8083
```

`<POSTGRES_PORT>` is used by Ontop to connect to PostgreSQL.

The four Ontop HTTP ports expose the four corresponding SPARQL endpoints:

```text
<GA_ENDPOINT_PORT>      → geographic_area_db
<CI_ENDPOINT_PORT>      → contextual_indicator_db
<GREEN_ENDPOINT_PORT>   → raster_green_space_db
<NDVI_ENDPOINT_PORT>    → raster_ndvi_db
```

---

# Part I. PostgreSQL and PostGIS

### 2. Install PostgreSQL 16

Install PostgreSQL 16 in **PowerShell**:

```powershell
winget install -e --id PostgreSQL.PostgreSQL.16
```

The PostgreSQL command-line client is typically located at:

```text
C:\Program Files\PostgreSQL\16\bin\psql.exe
```

This path is referred to as:

```text
<PSQL_PATH>
```

---

### 3. Install and Enable PostGIS

PostGIS extends PostgreSQL with support for storing, managing, and querying geospatial data, including geometries, coordinates, and spatial relationships.

PostGIS can be installed using **Stack Builder**, which is included with PostgreSQL.

If Stack Builder is not located at the default path, run the following command in **PowerShell**:

```powershell
Get-ChildItem -Path "C:\Program Files\PostgreSQL" -Recurse -Filter "stackbuilder.exe" -ErrorAction SilentlyContinue
```

Open Stack Builder and:

1. Select the **PostgreSQL 16** installation.
2. Select **Spatial Extensions**.
3. Select a compatible **PostGIS** version.
4. Complete the installation.

After installation, open **PowerShell** and connect to PostgreSQL:

```powershell
& "<PSQL_PATH>" -h 127.0.0.1 -U postgres -d postgres
```

After the connection is established, run the following commands inside the PostgreSQL `psql` terminal.

Check whether PostGIS is available:

```sql
SELECT name, default_version, installed_version
FROM pg_available_extensions
WHERE name = 'postgis';
```

If the query returns a `postgis` entry together with version information, PostGIS has been installed successfully.

PostGIS must then be enabled in each database where spatial functionality is required:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

To verify that PostGIS has been enabled successfully, run:

```sql
SELECT postgis_full_version();
```

If version information is returned, PostGIS is ready to use.

---

### 4. Check the PostgreSQL Port

Connect to PostgreSQL:

```powershell
& "<PSQL_PATH>" -h 127.0.0.1 -U postgres -d postgres
```

Then run:

```sql
SHOW port;
```

Record the returned value as:

```text
<POSTGRES_PORT>
```

A standard installation commonly uses:

```text
5432
```

This value is used later in the Ontop `.properties` files.

---

# Part II. Import Python-Generated CSV Data from Non-RDF-Native Sources

### 5. Inspect CSV Filenames and Columns

Before importing the transformed CSV files, inspect their filenames and column headers.

All transformed CSV files are stored in the folder specified by `OUTPUT_DIR` in `Python coding\config.py`.

Run the following command in **PowerShell**, not in the **PostgreSQL** psql terminal:

```powershell
$folder="<OUTPUT_DIR>"

Get-ChildItem -Path $folder -Filter "*.csv" | ForEach-Object {
    Write-Host "`n===== $($_.Name) ====="
    Get-Content -LiteralPath $_.FullName -First 1
}
```

For example:

```powershell
$folder="D:\4 Mapping CSVs"

Get-ChildItem -Path $folder -Filter "*.csv" | ForEach-Object {
    Write-Host "`n===== $($_.Name) ====="
    Get-Content -LiteralPath $_.FullName -First 1
}
```

This command lists each CSV filename and displays its first row, allowing the column names to be checked before importing the files into PostgreSQL.

> Replace the example path with the `OUTPUT_DIR` value defined in `Python coding\config.py`.

---

### 6. Create the Databases and Standard Tables

Database creation, PostGIS activation where required, and creation of the standard geographic-area and contextual-indicator tables are defined in:

```text
<CONFIG_DIR>\
└── database_setup.sql
```

The script should create the four project databases:

```text
geographic_area_db
contextual_indicator_db
raster_green_space_db
raster_ndvi_db
```

The large raster tables are created separately in Section 8 so that they can be assigned to dedicated PostgreSQL tablespaces when additional storage is required.

Run `database_setup.sql` from **PowerShell**:

```powershell
& "<PSQL_PATH>" -h 127.0.0.1 -U postgres -d postgres -f "<CONFIG_DIR>\database_setup.sql"
```

For example:

```powershell
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" `
  -h 127.0.0.1 `
  -U postgres `
  -d postgres `
  -f "D:\project\Ontop mapping\database_setup.sql"
```

The first two databases contain the geographic-area and contextual-indicator tables. The two raster-derived datasets are stored in separate databases because their tables are substantially larger and may require additional disk-space management.

---

### 7. CSV-to-Database Mapping and Import

The CSV files are distributed across four databases as follows:

| CSV file | Source / script | PostgreSQL database | PostgreSQL table |
|---|---|---|---|
| `postcode4_data_not_WGS84.csv` | `01_postcode4.py` | `geographic_area_db` | `postcode4_data_not_wgs84` |
| `wijken_2024.csv` | `02_cbs_administrative_areas.py` | `geographic_area_db` | `wijken_2024` |
| `buurten_2024.csv` | `02_cbs_administrative_areas.py` | `geographic_area_db` | `buurten_2024` |
| `wijken_2026.csv` | `02_cbs_administrative_areas.py` | `geographic_area_db` | `wijken_2026` |
| `buurten_2026.csv` | `02_cbs_administrative_areas.py` | `geographic_area_db` | `buurten_2026` |
| `raster_green_space.csv` | `03_rivm_rasters.py` | `raster_green_space_db` | `green_space_raster` |
| `raster_ndvi.csv` | `03_rivm_rasters.py` | `raster_ndvi_db` | `ndvi_raster` |
| `traffic_safety_filter.csv` | `04_traffic_safety.py` | `contextual_indicator_db` | `traffic_safety` |
| `traffic_safety_location_filter.csv` | `04_traffic_safety.py` | `contextual_indicator_db` | `traffic_safety_location` |
| `weather_station.csv` | `05_weather.py` | `contextual_indicator_db` | `weather_station` |
| `weather.csv` | `05_weather.py` | `contextual_indicator_db` | `weather` |
| `clean_taxi.csv` | `06_taxi_stops.py` | `contextual_indicator_db` | `taxi_stops` |
| `public_transport_stops_not_WGS84.csv` | `07_public_transport_stops.py` | `contextual_indicator_db` | `public_transport` |
| `area_proportion_green_wijk.csv` | `08_green_space_administrative.py` | `contextual_indicator_db` | `green_space_wijk` |
| `area_proportion_green_buurt.csv` | `08_green_space_administrative.py` | `contextual_indicator_db` | `green_space_buurt` |
| `CBS data calculation.csv` | `09_land_use_diversity.py` | `contextual_indicator_db` | `land_use` |
| `crime_safety.csv` | Not specified in the script overview | `contextual_indicator_db` | `crime_safety` |

For the standard CSV files, connect to the corresponding database in **PowerShell**:

```powershell
& "<PSQL_PATH>" -h 127.0.0.1 -U postgres -d <DATABASE_NAME>
```

Then import the CSV inside the PostgreSQL `psql` terminal:

```text
\copy <table_name> FROM '<OUTPUT_DIR>/<file_name>.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');
```

For example, to import `weather.csv`:

```powershell
& "<PSQL_PATH>" -h 127.0.0.1 -U postgres -d contextual_indicator_db
```

Then inside `psql`:

```text
\copy weather FROM '<OUTPUT_DIR>/weather.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');
```

On Windows, forward slashes (`/`) are recommended in PostgreSQL file paths used inside `psql`.

Verify the import with:

```sql
SELECT COUNT(*)
FROM <table_name>;
```

> For `raster_green_space.csv` and `raster_ndvi.csv`, follow the additional storage procedure in Section 8.

---




### 8. Optional: Inspect the Databases in pgAdmin

If pgAdmin 4 is installed, the databases and tables can be inspected through:

```text
Servers
└── PostgreSQL 16
    └── Databases
        ├── geographic_area_db
        ├── contextual_indicator_db
        ├── raster_green_space_db
        └── raster_ndvi_db
```

For example:

```text
Right-click a table
→ View/Edit Data
→ All Rows
```

pgAdmin is optional and is not required for the Ontop workflow.

---

# Part III. Configure Ontop

### 9. Install Ontop CLI and the PostgreSQL JDBC Driver

Install Ontop CLI as follows:

```text
https://amsterdamumc.github.io/ontop-vkg-tutorial/
```

The Ontop installation directory is represented as:

```text
<ONTOP_DIR>
```

A typical structure is:

```text
<ONTOP_DIR>
│
├── ontop.bat
├── jdbc
│   └── postgresql-<version>.jar
├── lib
└── ...
```

The PostgreSQL JDBC driver must be available in the Ontop `jdbc` directory.

---

### 10. Prepare the Ontop Files

All Ontop mapping and database-connection files used in this project are stored in the same `Ontop mapping` folder, represented in this guide as:

```text
<CONFIG_DIR>
```

A typical structure is:

```text
<CONFIG_DIR>\
│
├── 01_contextual_indicator.obda
├── 01_contextual_indicator.properties
├── 02_geographic_area.obda
├── 02_geographic_area.properties
├── 03_green_space_raster_data.obda
├── 03_green_space_raster.properties
├── 04_ndvi_raster_data.obda
├── 04_ndvi_raster_data.properties
└── database_setup.sql
```

A separate configuration folder is **not** required for each endpoint.

Each PostgreSQL database has one corresponding Ontop mapping file and one corresponding `.properties` file:

| Database | Mapping file | Properties file |
|---|---|---|
| `geographic_area_db` | `02_geographic_area.obda` | `02_geographic_area.properties` |
| `contextual_indicator_db` | `01_contextual_indicator.obda` | `01_contextual_indicator.properties` |
| `raster_green_space_db` | `03_green_space_raster_data.obda` | `03_green_space_raster.properties` |
| `raster_ndvi_db` | `04_ndvi_raster_data.properties` | `04_ndvi_raster_data.properties` |

The `.obda` files define how PostgreSQL tables are exposed as RDF.

The main GeoSPARQL terms used in this project and their roles  are:

- `geo:Feature`: represents a geographic entity, such as a neighbourhood, district, grid cell, or taxi stop.
- `geo:hasGeometry`: links a geographic feature to its geometry.
- `geo:asWKT`: links a geometry resource to its WKT representation.
- `geo:wktLiteral`: specifies the datatype of the WKT geometry literal.
   For example: ```text geo:asWKT "<http://www.opengis.net/def/crs/EPSG/0/28992> {geometry}"^^geo:wktLiteral```
- `geo:sfWithin`: represents a spatial containment relationship between geographic features.
---
The `.properties` files define how Ontop connects to each PostgreSQL database.


For example: 
#### `geographic_area.properties`

```properties
jdbc.url=jdbc:postgresql://127.0.0.1:<POSTGRES_PORT>/geographic_area_db?defaultRowFetchSize=100
jdbc.user=postgres
jdbc.password=<your_password>
jdbc.driver=org.postgresql.Driver
```

`defaultRowFetchSize=100` is used because geographic-area datasets contain large geometries and fetching fewer rows at a time can reduce memory consumption.

> Use the `<POSTGRES_PORT>` obtained earlier with `SHOW port;`.

> Replace `<your_password>` locally. Do not commit passwords to a public repository.

---

# Part IV. Start the Ontop SPARQL Endpoints

### 11. Start the Four Ontop Endpoints

Start one Ontop endpoint for each PostgreSQL database using its corresponding `.obda` and `.properties` files.

The four endpoints are configured as follows:

| Endpoint | Database | Mapping file | Properties file | Example port |
|---|---|---|---|---|
| Geographic area | `geographic_area_db` | `02_geographic_area.obda` | `02_geographic_area.properties` | `8080` |
| Contextual indicator | `contextual_indicator_db` | `01_contextual_indicator.obda` | `01_contextual_indicator.properties` | `8081` |
| Green-space raster | `raster_green_space_db` | `03_green_space_raster_data.obda` | `03_green_space_raster.properties` | `8082` |
| NDVI raster | `raster_ndvi_db` | `04_ndvi_raster_data.properties` | `04_ndvi_raster_data.properties` | `8083` |

The general command is:

```powershell
& "<ONTOP_DIR>\ontop.bat" endpoint `
  -m "<CONFIG_DIR>\<MAPPING_FILE>.obda" `
  -p "<CONFIG_DIR>\<PROPERTIES_FILE>.properties" `
  --port <ENDPOINT_PORT>
```

For example, to start the geographic-area endpoint:

```powershell
& "<ONTOP_DIR>\ontop.bat" endpoint `
  -m "<CONFIG_DIR>\geographic_area.obda" `
  -p "<CONFIG_DIR>\geographic_area.properties" `
  --port 8080
```

The corresponding endpoint is:

```text
http://localhost:8080/sparql
```

The Ontop endpoint ports are chosen by the user and are different from `<POSTGRES_PORT>`, which is used for the PostgreSQL database connection.

Each endpoint must use a different available HTTP port.

Keep each PowerShell window open while its Ontop endpoint is running.

---

### 12. Test the Four Endpoints

Open each Ontop web interface and run:

```sparql
SELECT ?s ?p ?o
WHERE {
    ?s ?p ?o .
}
LIMIT 10
```

If results are returned, the corresponding connection is working:

```text
PostgreSQL
    ↓
Ontop mapping
    ↓
Virtual RDF
    ↓
SPARQL
```

The four endpoints are:

```text
Geographic-area SPARQL endpoint:
http://localhost:<GA_ENDPOINT_PORT>/sparql

Contextual-indicator SPARQL endpoint:
http://localhost:<CI_ENDPOINT_PORT>/sparql

Green-space raster SPARQL endpoint:
http://localhost:<GREEN_ENDPOINT_PORT>/sparql

NDVI raster SPARQL endpoint:
http://localhost:<NDVI_ENDPOINT_PORT>/sparql
```

---

# Final Architecture

The complete virtual RDF architecture is:

```text
PostgreSQL 16
│
├── geographic_area_db
│       ↓
│   geographic_area.properties
│       ↓
│   geographic_area.obda
│       ↓
│      Ontop
│       ↓
│   http://localhost:<GA_ENDPOINT_PORT>/sparql
│
├── contextual_indicator_db
│       ↓
│   contextual_indicator.properties
│       ↓
│   contextual_indicator.obda
│       ↓
│      Ontop
│       ↓
│   http://localhost:<CI_ENDPOINT_PORT>/sparql
│
├── raster_green_space_db
│       ↓
│   raster_green_space.properties
│       ↓
│   raster_green_space.obda
│       ↓
│      Ontop
│       ↓
│   http://localhost:<GREEN_ENDPOINT_PORT>/sparql
│
└── raster_ndvi_db
        ↓
    raster_ndvi.properties
        ↓
    raster_ndvi.obda
        ↓
       Ontop
        ↓
    http://localhost:<NDVI_ENDPOINT_PORT>/sparql
```

All Ontop configuration files and `database_setup.sql` are stored in the same `Ontop mapping` directory:

```text
<CONFIG_DIR>\
│
├── geographic_area.obda
├── geographic_area.properties
├── contextual_indicator.obda
├── contextual_indicator.properties
├── raster_green_space.obda
├── raster_green_space.properties
├── raster_ndvi.obda
├── raster_ndvi.properties
└── database_setup.sql
```

The four Ontop processes use different mapping/property pairs from the same directory and expose four separate SPARQL endpoints.

Ontop provides virtual RDF access to the PostgreSQL databases while the transformed source data remain stored in relational form.

For the large raster-derived datasets, additional storage can be configured:

```text
Source raster CSVs
        ↓
PostgreSQL raster databases
        ↓
<RASTER_STORAGE_DIR>
        ↓
Raster tablespaces
        ↓
Ontop mappings
        ↓
Separate Ontop endpoints
```

PostgreSQL temporary query files can also be redirected to a temporary tablespace under `<TEMP_STORAGE_DIR>` when the default PostgreSQL storage location has insufficient free space.
