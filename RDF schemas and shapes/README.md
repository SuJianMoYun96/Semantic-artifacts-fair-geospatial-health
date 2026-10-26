# RDF Data Schemas

## RDF Data Schema for RDF-Native Kadaster Data

For the Kadaster Knowledge Graph (KKG), see the [Kadaster Knowledge Graph browser](https://data.labs.kadaster.nl/kadaster/kkg/browser?resource=https%3A%2F%2Fdata.kkg.kadaster.nl).

---

## RDF Data Schema for RDF-Native OpenStreetMap (OSM) Data

LinkedGeoData (LGD) adds a spatial dimension to the Web of Data and the Semantic Web by making OpenStreetMap (OSM) data available as an RDF knowledge base following Linked Data principles.

We used [sheXer](https://github.com/weso/shexer) to extract the RDF data schema from the OSM RDF data.

The Python script used for schema extraction is available here:

[`sheX_osm_local.py`](OpenStreetMap/shex_osm_local.py)

The resulting ShEx schema is available here:

[`osm_sample_10000.shex`](OpenStreetMap/osm_sample_10000.shex)

---

## RDF Data Schema for Python-Generated CSV Data from Non-RDF-Native Sources

Python-generated CSV data from non-RDF-native sources can be exposed as virtual RDF through Ontop or materialised as RDF using the Ontop CLI.

### Local Values Used in This Section

The following placeholders are used:

| Placeholder | Meaning |
|---|---|
| `<PSQL_PATH>` | Full path to `psql.exe` |
| `<OUTPUT_DIR>` | Folder containing the Python-generated CSV files |
| `<ONTOP_DIR>` | Ontop CLI installation folder |
| `<CONFIG_DIR>` | Folder containing the Ontop `.obda` and `.properties` files |
| `<RASTER_STORAGE_DIR>` | Storage location for large PostgreSQL raster tables |
| `<TEMP_STORAGE_DIR>` | Storage location for PostgreSQL temporary query files |
| `<RDF_OUTPUT_DIR>` | Storage location for materialised RDF files |

> Commands labelled `powershell` must be run in **PowerShell**.
>
> Commands labelled `sql` must be run inside the PostgreSQL **`psql` terminal** after connecting to the required database.
>
> A prompt such as `PS C:\...>` indicates PowerShell, while a prompt such as `postgres=#` or `raster_green_space_db=#` indicates the PostgreSQL `psql` terminal.

---

### General RDF Materialisation

The general Ontop materialisation command must be run in **PowerShell**, not inside the PostgreSQL `psql` terminal:

```powershell
& "<ONTOP_DIR>\ontop.bat" materialize `
  -m "<CONFIG_DIR>\<MAPPING_FILE>.obda" `
  -p "<CONFIG_DIR>\<PROPERTIES_FILE>.properties" `
  -f turtle `
  -o "<RDF_OUTPUT_DIR>\<OUTPUT_FILE>.ttl"
```

For most CSV files, the standard PostgreSQL import and Ontop materialisation workflow is sufficient.

However, `raster_green_space.csv` and `raster_ndvi.csv` are substantially larger than the other transformed CSV files. If the default PostgreSQL storage location does not have sufficient free space, additional storage configuration may be required.

The green-space raster is used below as the example. The same procedure can be applied to the NDVI raster.

---

### Special Case: Large Raster Data

The two large raster datasets are stored in separate PostgreSQL databases:

```text
raster_green_space.csv → raster_green_space_db
raster_ndvi.csv        → raster_ndvi_db
```

PostgreSQL **tablespaces** can be used to store the large raster tables and temporary query files in alternative storage locations with sufficient free space.

---

#### 1. Connect to the Raster Database

The raster databases are already created by `database_setup.sql`.

Run the following command in **PowerShell**:

```powershell
& "<PSQL_PATH>" -h 127.0.0.1 -U postgres -d raster_green_space_db
```

After the connection is established, the prompt should change to something similar to:

```text
raster_green_space_db=#
```

The following SQL commands should then be run inside the PostgreSQL **`psql` terminal**.

---

#### 2. Create a Tablespace for the Large Raster Table

A PostgreSQL tablespace allows a table to be physically stored outside the default PostgreSQL data directory.

First, manually create a folder in a storage location with sufficient free space:

```text
<RASTER_STORAGE_DIR>\green_tablespace
```

Make sure that the Windows account running the PostgreSQL service has read and write permissions for this folder.

Then, inside the PostgreSQL **`psql` terminal**, run:

```sql
CREATE TABLESPACE green_space_ts
LOCATION '<RASTER_STORAGE_DIR>/green_tablespace';
```

Verify the tablespace inside the PostgreSQL **`psql` terminal**:

```sql
SELECT
    spcname,
    pg_tablespace_location(oid)
FROM pg_tablespace
WHERE spcname = 'green_space_ts';
```

The returned path should correspond to:

```text
<RASTER_STORAGE_DIR>/green_tablespace
```

---

#### 3. Create the Raster Table in the Tablespace

Inside the PostgreSQL **`psql` terminal**, create the raster table and assign it to the tablespace:

```sql
CREATE TABLE green_space_raster (
    geometry_wkt TEXT NOT NULL,
    green_space_value DOUBLE PRECISION
)
TABLESPACE green_space_ts;
```

This stores the large raster table in the selected storage location rather than in the default PostgreSQL data directory.

Verify the table assignment inside the PostgreSQL **`psql` terminal**:

```sql
SELECT
    c.relname,
    COALESCE(t.spcname, 'pg_default') AS tablespace,
    pg_relation_filepath(c.oid)
FROM pg_class c
LEFT JOIN pg_tablespace t
    ON c.reltablespace = t.oid
WHERE c.oid = 'green_space_raster'::regclass;
```

The `tablespace` column should return:

```text
green_space_ts
```

---

#### 4. Import the Raster CSV

Inside the PostgreSQL **`psql` terminal**, import the raster CSV:

```sql
\copy green_space_raster
FROM '<OUTPUT_DIR>/raster_green_space.csv'
WITH (
    FORMAT csv,
    HEADER true,
    DELIMITER ',',
    ENCODING 'UTF8'
);
```

The CSV remains in `OUTPUT_DIR`, while the imported PostgreSQL table is stored in the tablespace defined above.

The same procedure can be used for `raster_ndvi.csv` in `raster_ndvi_db`.

---

#### 5. Configure Storage for PostgreSQL Temporary Files

Storing the raster table in another tablespace does not automatically move PostgreSQL temporary query files.

Large Ontop queries may require PostgreSQL to create temporary files for operations such as sorting, joins, window functions, and geometry processing.

Inside the PostgreSQL **`psql` terminal**, check the current PostgreSQL data directory:

```sql
SHOW data_directory;
```

Then check whether a temporary tablespace has already been configured:

```sql
SHOW temp_tablespaces;
```

If `temp_tablespaces` is empty and the default storage location has insufficient free space, create a separate temporary tablespace.

First, manually create a folder:

```text
<TEMP_STORAGE_DIR>\postgres_temp
```

Make sure that the Windows account running the PostgreSQL service has read and write permissions for this folder.

Then, inside the PostgreSQL **`psql` terminal**, run:

```sql
CREATE TABLESPACE temp_space
LOCATION '<TEMP_STORAGE_DIR>/postgres_temp';
```

Verify it:

```sql
SELECT
    spcname,
    pg_tablespace_location(oid)
FROM pg_tablespace
WHERE spcname = 'temp_space';
```

---

#### 6. Configure the Raster Database to Use the Temporary Tablespace

Inside the PostgreSQL **`psql` terminal**, assign the temporary tablespace to the example raster database:

```sql
ALTER DATABASE raster_green_space_db
SET temp_tablespaces = 'temp_space';
```

Apply the same setting to `raster_ndvi_db` if required.

The setting takes effect for new database connections.

Therefore:

1. Exit the PostgreSQL `psql` terminal:

```text
\q
```

2. Reconnect from **PowerShell**:

```powershell
& "<PSQL_PATH>" -h 127.0.0.1 -U postgres -d raster_green_space_db
```

3. Restart the corresponding Ontop process if it is already running.

4. Inside the PostgreSQL **`psql` terminal**, verify the setting:

```sql
SHOW temp_tablespaces;
```

The expected result is:

```text
temp_space
```

---

#### 7. Storage Overview

The resulting storage arrangement is:

```text
<OUTPUT_DIR>
│
├── raster_green_space.csv
└── raster_ndvi.csv

<RASTER_STORAGE_DIR>
│
└── green_tablespace
    └── Large raster table data

<TEMP_STORAGE_DIR>
│
└── postgres_temp
    └── PostgreSQL temporary query files

<RDF_OUTPUT_DIR>
│
└── Materialised RDF files
```

The locations can be on the same drive or on different drives, depending on the available disk space.

---

#### 8. RDF Materialisation

RDF materialisation is performed using the Ontop CLI and must be run in **PowerShell**, not inside the PostgreSQL `psql` terminal.

If you are still inside `psql`, exit first:

```text
\q
```

Then run the Ontop materialisation command in **PowerShell**.

For example, for the green-space raster:

```powershell
& "<ONTOP_DIR>\ontop.bat" materialize `
  -m "<CONFIG_DIR>\03_green_space_raster_data.obda" `
  -p "<CONFIG_DIR>\03_green_space_raster.properties" `
  -f turtle `
  -o "<RDF_OUTPUT_DIR>\03_green_space_raster_data.ttl"
```

Because raster-derived RDF files can be very large, `<RDF_OUTPUT_DIR>` should point to a storage location with sufficient free space.

The overall workflow is:

```text
PowerShell
    ↓
Connect to PostgreSQL with psql.exe
    ↓
PostgreSQL psql terminal
    ↓
Create tablespace and raster table
    ↓
Import raster CSV
    ↓
Configure temporary tablespace
    ↓
Exit psql
    ↓
PowerShell
    ↓
Run Ontop materialisation
    ↓
RDF output file
```