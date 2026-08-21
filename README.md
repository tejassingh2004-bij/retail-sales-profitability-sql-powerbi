# Retail / E-Commerce Sales & Profitability Analysis (SQL + Power BI)

**Status: SQL layer ✅ complete & verified — Power BI report 🚧 in progress**

A SQL-first analysis of retail order-line data — a normalized star-schema
database and eight analysis scripts answering real business questions, with
a Power BI report being built on top of it.

The SQL layer is done: schema, ETL, and all 8 analysis scripts run clean
against the included SQLite database (see **Running it yourself** below to
verify that in under a minute). The Power BI report is the next step — the
data export, every DAX measure, and a page-by-page build guide are already
in `powerbi/` and `docs/`, so it's a guided build rather than a blank
canvas. This README will be updated with the finished `.pbix` and real
report screenshots once that's done.

## Business questions this answers

- What's overall order volume, revenue, profit, and profit margin?
- Which regions generate the most revenue — and which actually convert it
  to profit?
- Which categories / sub-categories are profitable, and which are quietly
  losing money?
- How does discounting affect profitability, and at what point does a
  discount stop being worth it?
- Which customer segments and regions pair best (or worst)?
- Where are the loss-making orders concentrated?
- Does shipping method correlate with profitability?
- Which states are the best and worst performers?

## Key findings

- 18.73% of order lines are loss-making — concentrated in Furniture
  (33.7% loss rate) far more than Office Supplies or Technology (~15% each).
- Profit margin holds up fine through moderate discounting (11–20% margin
  through a 20% discount), then collapses — every discount band above 20%
  runs at a net loss, bottoming out at **-119% margin** for discounts of
  51%+.
- Tables and Bookcases are the two sub-categories dragging Furniture's
  margin negative; every other sub-category in the dataset is profitable.
- West is the strongest region (14.9% margin, highest revenue); Central is
  the weakest (7.9% margin) despite being the 3rd-largest by revenue.
- California and New York are the top two states by total profit; Texas is
  the single worst-performing state (not shown above — see
  `sql/08_top_bottom_states.sql`).

## Project structure

```
.
├── data/
│   ├── SampleSuperstore.csv          # raw input data
│   └── retail_sales.db               # SQLite database (star schema, pre-built)
├── sql/
│   ├── 00_schema.sql                 # DDL: fact + dimension tables, view
│   ├── 01_kpi_summary.sql
│   ├── 02_regional_performance.sql
│   ├── 03_category_subcategory_analysis.sql
│   ├── 04_discount_impact_on_profitability.sql
│   ├── 05_customer_segment_analysis.sql
│   ├── 06_loss_making_orders.sql
│   ├── 07_shipping_mode_analysis.sql
│   └── 08_top_bottom_states.sql
├── scripts/
│   ├── build_database.py             # cleans CSV -> loads SQLite star schema
│   └── run_sql.py                    # runs & prints results for every script
├── powerbi/
│   ├── data/                         # star-schema tables exported as CSV, ready to import
│   ├── DAX_measures.dax              # every measure/calculated column, ready to paste in
│   └── Retail_Sales_Profitability.pbix   # <- add this after following the build guide
├── docs/
│   ├── POWER_BI_BUILD_GUIDE.md       # page-by-page report build instructions
│   └── design_reference_layout.png   # visual target for layout/KPIs/color
└── README.md
```

## Data model

A small star schema: one fact table, five dimensions.

```
dim_region ──┐
dim_category ─┼──< fact_sales >── dim_segment
dim_subcategory ┘        └── dim_ship_mode
```

`dim_subcategory` also has a foreign key back to `dim_category` (e.g.
"Bookcases" belongs to "Furniture"), so category-level and sub-category-level
questions both roll up cleanly.

## Running it yourself

```bash
python3 -m pip install pandas
python3 scripts/build_database.py data/SampleSuperstore.csv data/retail_sales.db
python3 scripts/run_sql.py                       # runs every analysis script
python3 scripts/run_sql.py sql/04_discount_impact_on_profitability.sql   # or just one
```

Or open `data/retail_sales.db` directly in any SQLite client (DB Browser
for SQLite, DBeaver, VS Code's SQLite extension, etc.) and run the scripts
in `sql/` yourself.

## Data cleaning steps applied

- Trimmed whitespace from every text field.
- Removed exact-duplicate order lines.
- Cast quantity to integer, zero-padded postal codes to 5 digits.
- Normalized the flat CSV into a star schema (dimension tables built from
  each field's distinct values, surrogate integer keys assigned).

## Tech stack

SQL (SQLite), Python (pandas, sqlite3) for the ETL, Power BI for the
reporting layer.
