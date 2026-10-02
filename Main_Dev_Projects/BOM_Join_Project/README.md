
BOM Maquinados ETL

Technical documentation for the BOM Maquinados ETL process.

Overview

Automated ETL process that consolidates BOM (Bill of Materials) TXT files from the J: drive, standardizes data structures, generates business keys, removes duplicate records, and exports analytical datasets in Parquet and CSV formats.

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

Source Folder: J:\Compras IHP
File Prefix: Rpt_DFTFeedC15_BOM_Maquinados_

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

Pablo "Hazzard" Acosta
