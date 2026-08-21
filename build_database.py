"""
build_database.py

Cleans the raw Superstore CSV and loads it into a SQLite star schema
(sql/00_schema.sql) so the analysis scripts in sql/ can run against it.

Usage:
    python3 -m pip install pandas
    python3 scripts/build_database.py data/SampleSuperstore.csv data/retail_sales.db
"""
import sys
import sqlite3
import pandas as pd


def load_and_clean(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, dtype={"Postal Code": str})
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].str.strip()
    df = df.drop_duplicates().reset_index(drop=True)
    df["Quantity"] = df["Quantity"].astype(int)
    df["Postal Code"] = df["Postal Code"].astype(str).str.zfill(5)
    df.insert(0, "row_id", range(1, len(df) + 1))
    return df


def build_db(df: pd.DataFrame, schema_path: str, db_path: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    with open(schema_path) as f:
        cur.executescript(f.read())

    def load_dim(table, id_col, name_col, values):
        cur.executemany(f"INSERT INTO {table} ({id_col}, {name_col}) VALUES (?, ?)",
                         list(enumerate(sorted(values), start=1)))
        return {v: i for i, v in enumerate(sorted(values), start=1)}

    ship_mode_map = load_dim("dim_ship_mode", "ship_mode_id", "ship_mode", df["Ship Mode"].unique())
    segment_map = load_dim("dim_segment", "segment_id", "segment", df["Segment"].unique())
    region_map = load_dim("dim_region", "region_id", "region", df["Region"].unique())
    category_map = load_dim("dim_category", "category_id", "category", df["Category"].unique())

    subcat_to_cat = df.drop_duplicates("Sub_Category").set_index("Sub_Category")["Category"].to_dict()
    subcategory_map = {}
    for i, (sc, cat) in enumerate(sorted(subcat_to_cat.items()), start=1):
        cur.execute("INSERT INTO dim_subcategory (subcategory_id, subcategory, category_id) VALUES (?, ?, ?)",
                    (i, sc, category_map[cat]))
        subcategory_map[sc] = i

    rows = [
        (
            r.row_id,
            ship_mode_map[r._1],       # Ship Mode (positional due to space in name)
            segment_map[r.Segment],
            region_map[r.Region],
            category_map[r.Category],
            subcategory_map[r.Sub_Category],
            r.Country, r.City, r.State, getattr(r, "_6"),  # Postal Code
            r.Sales, r.Quantity, r.Discount, r.Profit,
        )
        for r in df.itertuples(index=False)
    ]
    cur.executemany(
        """INSERT INTO fact_sales
           (row_id, ship_mode_id, segment_id, region_id, category_id, subcategory_id,
            country, city, state, postal_code, sales, quantity, discount, profit)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        rows,
    )
    conn.commit()
    n = cur.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
    conn.close()
    return n


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 build_database.py <input_csv> <output_db>")
        sys.exit(1)
    csv_path, db_path = sys.argv[1], sys.argv[2]
    df = load_and_clean(csv_path)
    n = build_db(df, "sql/00_schema.sql", db_path)
    print(f"Loaded {n} rows into {db_path}")


if __name__ == "__main__":
    main()
