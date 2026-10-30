# Semantic artifacts for fair geospatial health

Semantic artifacts accompanying the manuscript:

> **Making geospatial data FAIR for digital health: a semantic interoperability framework**
> Xi Yang, Rowdy de Groot, Daniel Fernández-Álvarez, Ronald Cornet, Andra Waagmeester.
> *Submitted to Scientific Data, collection "10 years of the FAIR principles".*
> DOI: `<ADD WHEN AVAILABLE>`

Archived release: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)

This repository contains the semantic artifacts, data-preprocessing code, mappings, schemas and
queries required to reproduce the interoperability framework described in the manuscript. It does
**not** contain the source geospatial data, which remain with their original providers (Statistics
Netherlands, PDOK, RIVM, KNMI, NDW, NDOV, Dutch Police, Kadaster, OpenStreetMap/LinkedGeoData), nor
materialised RDF: RDF is generated virtually from relational databases using Ontop and is therefore
never stored as standalone files.

## Repository structure

Each top-level directory corresponds to a component of the framework as presented in the manuscript.

| Directory | Manuscript component | Contents |
|---|---|---|
| `python-preprocessing/` | Component 2 — characterising data sources | Per-source preprocessing scripts that convert GeoPackage, GeoTIFF, NetCDF, XML, XLSX, CSV and plain-text sources into a common CSV format, plus shared helpers (`common_functions.py`), configuration (`config.py`) and pinned dependencies (`requirements.txt`). |
| `ontop-mapping/` | Component 3 — unified interoperable RDF layer | PostgreSQL/PostGIS database setup (`database_setup.sql`), Ontop OBDA mapping files (`*.obda`) and connection templates (`*.properties`) that expose the relational data as a virtual RDF layer. |
| `rdf-schemas-shapes/` | Component 3 — schema documentation | ShEx schemas extracted with sheXer from the RDF-native sources (OpenStreetMap) and from the virtual RDF generated over non-RDF-native sources. |
| `geosparql-endpoint-tests/` | Component 3 — endpoint selection | Function-by-function GeoSPARQL conformance tests across Ontop, Strabon, QLever, Kadaster, GraphDB and Apache Jena, with the SPARQL queries used and a written results summary. |
| `unified-graphdb-queries/` | Component 3 — federated access | Query demonstrating unified access through the GraphDB endpoint. |
| `wikidata-mappings/` | Component 4 — standards-based representation | SSSOM mapping sets aligning geographic-area, and measurement and facility/event-type fields of contextual indicators to Wikidata identifiers. |

Every directory carries its own `README.md` with step-by-step instructions; start there for
operational detail.

## Reproduction order

1. `python-preprocessing/` — install `requirements.txt`, set `OUTPUT_DIR` in `config.py`, run the scripts to produce the intermediate CSVs.
2. `ontop-mapping/` — create the PostgreSQL/PostGIS databases, load the CSVs, then configure Ontop with the supplied `.obda` and `.properties` files to expose the virtual RDF layer.
3. `rdf-schemas-shapes/` — optionally regenerate the ShEx schemas from the virtual RDF with sheXer.
4. `geosparql-endpoint-tests/` — reproduce the endpoint conformance assessment.
5. `wikidata-mappings/` — apply the SSSOM mappings to represent retrieved values with Wikidata identifiers and health data standards.

## Configuration

The `.properties` files contain placeholders (`<POSTGRES_PORT>`, `<YOUR_PASSWORD>`) rather than real
credentials. Substitute local values before running Ontop; do not commit the substituted files.

## Licence

- **Code** (`*.py`, `*.sql`): MIT — see [`LICENSE`](LICENSE).
- **Data, mappings, schemas, queries and documentation** (`*.obda`, `*.shex`, `*.sparql`, `*.tsv`, `*.xlsx`, `*.md`): CC BY 4.0 — see [`LICENSE-DATA.md`](LICENSE-DATA.md).

Source geospatial data are subject to the licences of their original providers and are not
redistributed here.

## AI assistance

The research design, data preprocessing scripts, Ontop mappings, ShEx schemas,
SPARQL queries and SSSOM mapping sets in this repository were produced by the authors.

A generative AI assistant (Claude Opus 5, Anthropic) was used in October 2026 for
repository engineering only:

- renaming directories and files to kebab-case and rewriting the corresponding
  markdown link targets;
- identifying and repairing eight pre-existing broken links in
  `geosparql-endpoint-tests/README.md`;
- removing tracked Python bytecode and adding `.gitignore`;
- drafting this README and the repository metadata files (`LICENSE`,
  `LICENSE-DATA.md`, `CITATION.cff`, `.zenodo.json`).

All suggested changes were reviewed and applied by the authors, who take full
responsibility for the content of this repository. No AI tool is listed as an
author or contributor.

## Citation

If you use these artifacts, please cite both the manuscript and the archived release. Machine-readable
metadata is in [`CITATION.cff`](CITATION.cff); GitHub renders it under "Cite this repository".
