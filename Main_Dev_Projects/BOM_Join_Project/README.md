
BOM Maquinados ETL

Technical documentation for the BOM Maquinados ETL process.

Overview

Automated ETL process that consolidates BOM (Bill of Materials) TXT files from a shared drive, standardizes data structures, generates business keys, removes duplicate records, and exports analytical datasets in Parquet and CSV formats.

Workflow

1. Recursively scan source folders.
2. Identify files matching the configured prefix.
3. Load TXT files as text-only datasets.
4. Apply standardized column names.
5. Generate BOM_Key.
6. Load data into DuckDB.
7. Remove duplicate BOM records.
8. Export Parquet and CSV outputs.
9. Write execution logs.

Source Configuration

The source folder and the file prefix live in `config.local.json` next to `config.py` (ignored by git):

    { "source": "<carpeta con los TXT>", "file_prefix": "<prefijo de los archivos>" }

or in the environment variables `BOM_SOURCE_FOLDER` and `BOM_FILE_PREFIX`. Outputs in `Output/` stay local.

Output Schema

Parent_Model, Item_Part, Description, Planner_Code, Product_Line, Item_Type, Quantity, BOM_Key

Technology Stack

Python, Pandas, DuckDB, PyArrow, TQDM

Execution

python main.py

Dependencies

pandas>=2.2.0
duckdb>=1.3.0
pyarrow>=18.0.0
xlrd>=2.0.1
tqdm>=4.67.0

Author

Hazzard
