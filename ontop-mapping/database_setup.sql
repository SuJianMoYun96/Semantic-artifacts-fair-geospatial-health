-- ============================================================
-- database_setup.sql
-- PostgreSQL/PostGIS setup for the Ontop virtual RDF workflow
-- ============================================================
--
-- Run with:
--
-- psql -h 127.0.0.1 -U postgres -d postgres -f database_setup.sql
--
-- This script:
--   1. Creates the four project databases
--   2. Enables PostGIS in each database
--   3. Creates the predefined geographic-area and contextual-indicator tables.
--       This process does not create tables for Normalized Difference Vegetation Index (NDVI) from https://data.rivm.nl/meta/srv/eng/catalog.search#/metadata/6c59f7e9-97ac-4a43-af92-1bdd595d69d4?tab=relations,
--       and area proportion of green space in 10-meter grids from https://data.rivm.nl/meta/srv/eng/catalog.search#/metadata/32494ae3-db92-469b-a3d7-458b90342a5e?tab=relations.
--       Their transformed CSVs are too big.
-- Contextual-indicator table structures depend on the transformed
-- CSV files. Inspect their CSV headers first, then add the required
-- CREATE TABLE statements in the marked section below.
--
-- ============================================================

\set ON_ERROR_STOP on

-- ------------------------------------------------------------
-- 1. Create project databases
-- ------------------------------------------------------------

CREATE DATABASE geographic_area_db;
CREATE DATABASE contextual_indicator_db;
CREATE DATABASE raster_green_space_db;
CREATE DATABASE raster_ndvi_db;

-- ------------------------------------------------------------
-- 2. Geographic-area database
-- ------------------------------------------------------------

\connect geographic_area_db

CREATE EXTENSION IF NOT EXISTS postgis;

-- buurten_2024.csv =====
-- jaar,buurtcode,buurtnaam,wijkcode,gemeentecode,gemeentenaam,geometry
CREATE TABLE IF NOT EXISTS buurten_2024 (
    jaar INTEGER,
    buurtcode TEXT,
    buurtnaam TEXT,
    wijkcode TEXT,
    gemeentecode TEXT,
    gemeentenaam TEXT,
    geometry TEXT
);

-- buurten_2026.csv =====
-- jaar,bu_code,bu_naam,wk_code,gm_code,gm_naam,geometry
CREATE TABLE IF NOT EXISTS buurten_2026 (
    jaar INTEGER,
    bu_code TEXT,
    bu_naam TEXT,
    wk_code TEXT,
    gm_code TEXT,
    gm_naam TEXT,
    geometry TEXT
);

-- postcode4_data_not_WGS84.csv =====
-- addressdensity,postcode,geometry
CREATE TABLE IF NOT EXISTS postcode4_data_not_wgs84 (
    address_density DOUBLE PRECISION,
    postcode TEXT,
    geometry TEXT
);

-- wijken_2024.csv =====
-- jaar,wijknaam,wijkcode,gemeentecode,gemeentenaam,geometry
CREATE TABLE IF NOT EXISTS wijken_2024 (
    jaar INTEGER,
    wijknaam TEXT,
    wijkcode TEXT,
    gemeentecode TEXT,
    gemeentenaam TEXT,
    geometry TEXT
);

-- wijken_2026.csv =====
-- jaar,wk_code,wk_naam,gm_code,gm_naam,geometry
CREATE TABLE IF NOT EXISTS wijken_2026 (
    jaar INTEGER,
    wk_code TEXT,
    wk_naam TEXT,
    gm_code TEXT,
    gm_naam TEXT,
    geometry TEXT
);
-- ------------------------------------------------------------
-- 3. Contextual-indicator database

\connect contextual_indicator_db

CREATE EXTENSION IF NOT EXISTS postgis;

-- area_proportion_green_space_buurt.csv
-- bu_code,bu_naam,wk_code,gm_code,_mean,_stdev,_min,_max,geometry
CREATE TABLE IF NOT EXISTS green_space_buurt (
    bu_code TEXT,
    bu_naam TEXT,
    wk_code TEXT,
    gm_code TEXT,
    mean DOUBLE PRECISION,
    stdev DOUBLE PRECISION,
    min DOUBLE PRECISION,
    max DOUBLE PRECISION,
    geometry TEXT
);

-- area_proportion_green_space_wijk.csv
-- wk_code,wk_naam,gm_code,_mean,_stdev,_min,_max,geometry
CREATE TABLE IF NOT EXISTS green_space_wijk (
    wk_code TEXT,
    wk_naam TEXT,
    gm_code TEXT,
    mean DOUBLE PRECISION,
    stdev DOUBLE PRECISION,
    min DOUBLE PRECISION,
    max DOUBLE PRECISION,
    geometry TEXT
);

-- CBS data calculation.csv
-- ID,AlleRegioIndelingen,Gemeentenaam_1,SoortRegio_2,Codering_3,TotaalLandEnWater_4,Spoorterrein_10,Woonterrein_15,OpenbareVoorziening_17,SociaalCultureleVoorziening_18,
-- Bedrijfsterrein_19,TotaalRecreatiefTerrein_27,TotaalBinnenwater_42,land_use_diversity
CREATE TABLE IF NOT EXISTS land_use (
    id TEXT,
    alle_regio_indelingen TEXT,
    gemeentenaam TEXT,
    soort_regio TEXT,
    codering TEXT,
    totaal_land_en_water TEXT,
    Spoorterrein TEXT,
    woonterrein TEXT,
    openbare_voorziening TEXT,
    sociaal_culturele_voorziening TEXT,
    bedrijfsterrein TEXT,
    totaal_recreatief_terrein TEXT,
    totaal_binnenwater TEXT,
    land_use_diversity TEXT
);

-- crime_safety.csv
-- "ID";"SoortMisdrijf";"WijkenEnBuurten";"Perioden";"GeregistreerdeMisdrijven_1"
CREATE TABLE IF NOT EXISTS crime_safety (
    id TEXT,
    soort_misdrijf TEXT,
    wijken_en_buurten TEXT,
    perioden TEXT,
    geregistreerde_misdrijven TEXT
);

-- public_transport_stops_not_WGS84.csv
-- ID,stopplacename.publicname,stopplacename.validfrom,stopplacetype,stopplacecode,stopplacelocation.rd-x,stopplacelocation.rd-y,
-- stopplacename.street,stopplacename.town,quays.quay.ID,quays.quay.quaylocationdata.validfrom,quays.quay.validfrom,quays.quay.quaycode,
-- quays.quay.quaynamedata.quayname,quays.quay.quaytransportmodes.transportmodedata.transportmode,quays.quay.quaylocationdata.rd-x,quays.quay.quaylocationdata.rd-y,
-- quays.quay.quaylocationdata.street,quays.quay.quaylocationdata.town,quays.quay.quaymunicipality.municipalitycode,geometry
CREATE TABLE IF NOT EXISTS public_transport (
    id TEXT,
    stopplace_publicname TEXT,
    stopplace_validfrom TEXT,
    stopplace_type TEXT,
    stopplace_code TEXT,
    stopplace_rd_x DOUBLE PRECISION,
    stopplace_rd_y DOUBLE PRECISION,
    stopplace_street TEXT,
    stopplace_town TEXT,
    quay_id TEXT,
    quay_location_validfrom TEXT,
    quay_validfrom TEXT,
    quay_code TEXT,
    quay_name TEXT,
    transport_mode TEXT,
    quay_rd_x DOUBLE PRECISION,
    quay_rd_y DOUBLE PRECISION,
    quay_street TEXT,
    quay_town TEXT,
    municipality_code TEXT,
    geometry TEXT
);

-- clean_taxi.csv
-- haltenr,coord x,coord y,"plaats, halte",sheet,geometry
CREATE TABLE IF NOT EXISTS taxi_stops (
    haltenr TEXT,
    coord_x DOUBLE PRECISION,
    coord_y DOUBLE PRECISION,
    plaats_halte TEXT,
    sheet TEXT,
    geometry TEXT
);

-- traffic_safety_filter.csv
-- VKL_NUMMER,DATUM_VKL,JAAR_VKL,TIJDSTIP,DDL_ID,JTE_ID,WVK_ID,HECTOMETER,FK_VELD5,HUISNUMMER,GME_ID,
-- GME_NAAM,PVE_CODE,PVE_NAAM,KDD_NAAM,PLT_NAAM,DIENSTCODE,DIENSTNAAM,DISTRCODE,DISTRNAAM,DAGTYPE
CREATE TABLE IF NOT EXISTS traffic_safety (
    vkl_nummer TEXT,
    datum_vkl TEXT,
    jaar_vkl TEXT,
    tijdstip TEXT,
    ddl_id TEXT,
    jte_id TEXT,
    wvk_id TEXT,
    hectometer TEXT,
    fk_veld5 TEXT,
    huisnummer TEXT,
    gme_id TEXT,
    gme_naam TEXT,
    pve_code TEXT,
    pve_naam TEXT,
    kdd_naam TEXT,
    plt_naam TEXT,
    dienstcode TEXT,
    dienstnaam TEXT,
    distrcode TEXT,
    distrnaam TEXT,
    dagtype TEXT
);

-- traffic_safety_location_filter.csv
-- FK_VELD5,X_COORD,Y_COORD,coordinates_wkt
CREATE TABLE IF NOT EXISTS traffic_safety_location (
    FK_VELD5        TEXT,
    X_COORD         DOUBLE PRECISION,
    Y_COORD         DOUBLE PRECISION,
    coordinates_wkt TEXT
);

-- weather.csv
-- coordinates_wkt,time,air_temperature_1_5m,wind_speed_past_hour,precipitation_intensity_past_10min,relative_humidity_1_5m
CREATE TABLE IF NOT EXISTS weather (
    coordinates_wkt TEXT,
    observation_time TEXT,
    air_temperature_1_5m DOUBLE PRECISION,
    wind_speed_past_hour DOUBLE PRECISION,
    precipitation_intensity_past_10min DOUBLE PRECISION,
    relative_humidity_1_5m DOUBLE PRECISION
);

-- weather_station.csv
-- name,wmoId,station_type,geometry_type,coordinates_wkt,id
CREATE TABLE IF NOT EXISTS weather_station (
    name TEXT,
    wmo_id TEXT,
    station_type TEXT,
    geometry_type TEXT,
    coordinates_wkt TEXT,
    id TEXT
);
