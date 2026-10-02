"""
BOM Maquinados ETL

Description:
- Search all subfolders in J-Compras IHP
- Load files starting with:
      Rpt_DFTFeedC15_BOM_Maquinados_
- Read TXT data
- Force all columns as Text
- Add column headers
- Create BOM_Key
- Remove duplicates
- Export Parquet and CSV

Made by: Hazzard
"""

from pathlib import Path
import logging

import duckdb
import pandas as pd
from tqdm import tqdm

from config import (
    SOURCE_FOLDER,
    FILE_PREFIX,
    OUTPUT_PARQUET,
    OUTPUT_CSV,
    LOG_FILE
)


# ==========================================================
# LOGGING
# ==========================================================

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# ==========================================================
# FILE DISCOVERY
# ==========================================================

def get_source_files() -> list:
    """
    Search all matching files recursively.
    """

    files = [
        file
        for file in SOURCE_FOLDER.rglob("*")
        if file.is_file()
        and file.name.startswith(FILE_PREFIX)
    ]

    return sorted(files)


# ==========================================================
# FILE READER
# ==========================================================

def read_file(file_path: Path) -> pd.DataFrame:
    """
    Read text source file.
    """

    df = pd.read_csv(
        file_path,
        sep="\t",
        header=None,
        dtype=str,
        encoding="latin1",
        on_bad_lines="skip"
    )

    if df.shape[1] < 7:
        raise ValueError(
            f"{file_path.name}: Expected at least 7 columns. "
            f"Found {df.shape[1]}"
        )

    df = df.iloc[:, :7]

    df.columns = [
        "Parent_Model",
        "Item_Part",
        "Description",
        "Planner_Code",
        "Product_Line",
        "Item_Type",
        "Quantity"
    ]

    df = df.fillna("").astype(str)

    for column in df.columns:
        df[column] = df[column].str.strip()

    df["BOM_Key"] = (
        df["Parent_Model"]
        + "-"
        + df["Item_Part"]
    )

    return df


# ==========================================================
# MAIN
# ==========================================================

def main() -> None:

    print("\nSearching source files...")

    files = get_source_files()

    if not files:
        raise FileNotFoundError(
            f"No files found under: {SOURCE_FOLDER}"
        )

    print(f"Files Found: {len(files):,}")

    OUTPUT_PARQUET.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    con = duckdb.connect()

    con.execute("""
        CREATE OR REPLACE TABLE BOM (
            Parent_Model VARCHAR,
            Item_Part VARCHAR,
            Description VARCHAR,
            Planner_Code VARCHAR,
            Product_Line VARCHAR,
            Item_Type VARCHAR,
            Quantity VARCHAR,
            BOM_Key VARCHAR
        )
    """)

    total_rows = 0
    successful_files = 0
    failed_files = 0

    for file in tqdm(files, desc="Processing Files"):

        try:

            df = read_file(file)

            total_rows += len(df)

            con.register("temp_df", df)

            con.execute("""
                INSERT INTO BOM
                SELECT *
                FROM temp_df
            """)

            successful_files += 1

            logging.info(
                f"SUCCESS | {file.name} | Rows={len(df):,}"
            )

        except Exception as error:

            failed_files += 1

            logging.error(
                f"FAILED | {file.name} | {error}"
            )

            print(
                f"\nERROR: {file.name}"
                f"\n{error}"
            )

    print("\nRemoving duplicates...")

    con.execute("""
        CREATE OR REPLACE TABLE BOM_FINAL AS
        SELECT
            Parent_Model,
            Item_Part,
            Description,
            Planner_Code,
            Product_Line,
            Item_Type,
            Quantity,
            BOM_Key
        FROM (
            SELECT
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY BOM_Key
                    ORDER BY BOM_Key
                ) AS rn
            FROM BOM
        )
        WHERE rn = 1
    """)

    result_before = con.execute("""
        SELECT COUNT(*)
        FROM BOM
    """).fetchone()

    rows_before = result_before[0] if result_before else 0

    result_after = con.execute("""
        SELECT COUNT(*)
        FROM BOM_FINAL
    """).fetchone()

    rows_after = result_after[0] if result_after else 0

    duplicates_removed = rows_before - rows_after

    print("Exporting Parquet...")

    con.execute(f"""
        COPY BOM_FINAL
        TO '{OUTPUT_PARQUET.as_posix()}'
        (
            FORMAT PARQUET,
            COMPRESSION ZSTD
        )
    """)

    print("Exporting CSV...")

    con.execute(f"""
        COPY BOM_FINAL
        TO '{OUTPUT_CSV.as_posix()}'
        (
            HEADER,
            DELIMITER ','
        )
    """)

    con.close()

    print("\n" + "=" * 70)
    print("PROCESS COMPLETED")
    print("=" * 70)
    print(f"Files Found         : {len(files):,}")
    print(f"Files Processed     : {successful_files:,}")
    print(f"Files Failed        : {failed_files:,}")
    print(f"Rows Loaded         : {rows_before:,}")
    print(f"Rows Final          : {rows_after:,}")
    print(f"Duplicates Removed  : {duplicates_removed:,}")
    print(f"Parquet Output      : {OUTPUT_PARQUET}")
    print(f"CSV Output          : {OUTPUT_CSV}")
    print("=" * 70)


if __name__ == "__main__":
    main()