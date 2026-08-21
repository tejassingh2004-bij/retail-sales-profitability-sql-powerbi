# Power BI Build Guide

This is a page-by-page guide to building the actual `.pbix` report in Power BI
Desktop. It should take roughly 30–45 minutes the first time through. Power BI
Desktop is Windows-only (or Windows via Parallels/Bootcamp on Mac) — there's
no way to generate the binary file outside of it, which is why this is a
guide rather than a finished file.

`docs/design_reference_layout.png` shows the target layout — it's a
screenshot of the companion Excel dashboard from this same dataset, included
so you have a concrete visual target for spacing, KPI cards, the heatmap, and
the color scheme. Rebuild each panel as a native Power BI visual rather than
trying to replicate it pixel-for-pixel; Power BI's own visuals (cards,
matrix, line/bar charts) will get you there.

## 1. Get the data in

You have two options in `powerbi/data/`:

- **Star schema (recommended — shows real modeling skill)**: import
  `fact_sales.csv`, `dim_region.csv`, `dim_category.csv`,
  `dim_subcategory.csv`, `dim_segment.csv`, `dim_ship_mode.csv` separately.
- **Flat single table (quick option)**: import just `vw_sales_flat.csv` if
  you want to skip relationship-building.

To import: **Home → Get Data → Text/CSV**, select each file, click **Load**
(not "Transform Data" — the CSVs are already clean).

## 2. Build relationships (star schema option only)

Go to **Model view** (left sidebar). Drag from each dimension table's ID
column to the matching ID column on `fact_sales`:

- `dim_region[region_id]` → `fact_sales[region_id]`
- `dim_category[category_id]` → `fact_sales[category_id]`
- `dim_subcategory[subcategory_id]` → `fact_sales[subcategory_id]`
- `dim_segment[segment_id]` → `fact_sales[segment_id]`
- `dim_ship_mode[ship_mode_id]` → `fact_sales[ship_mode_id]`

Each should auto-detect as a **one-to-many**, single-direction relationship
(one dimension row → many fact rows). Also connect
`dim_subcategory[category_id]` → `dim_category[category_id]`.

## 3. Add the DAX measures

Open `powerbi/DAX_measures.dax` — it has every measure and calculated column
used below, with the exact formulas. Add them under **fact_sales** (right
sidebar → right-click the table → **New measure** / **New column**). Don't
forget the "sort by column" step at the bottom of that file for the discount
band — otherwise the axis sorts alphabetically instead of 0% → 51%+.

## 4. Page 1 — Overview

- **Card visuals** (top row, 6 of them): Total Order Lines, Loss-Making
  Orders, Loss Rate %, Profit Margin %, Avg Discount %, Unique Sub-Categories.
  Format each with a small label above the number (Format pane → Callout
  value / Category label).
- **Matrix visual**: Rows = `dim_region[region]`, Columns =
  `dim_category[category]`, Values = `[Loss-Making Orders]`. Turn on
  **conditional formatting → background color** on the values (Format pane →
  Cell elements) for the heatmap effect.
- **Clustered bar chart**: Axis = region, Values = `[Loss-Making Orders]`.
- **Line chart**: Axis = `fact_sales[Discount Band]` (sorted, see step 3),
  Values = `[Profit Margin %]`.
- **Slicers**: Region, Segment, Category — place along the left or top so
  every visual on the page responds to them.

## 5. Page 2 — Regional & Category Detail

- **Table visual**: Region, `[Total Sales]`, `[Profit Margin %]`,
  `[Region Status]`. Add conditional formatting on `Region Status`
  (Format pane → Conditional formatting → Font color, rules: "Below Target"
  = red, "On Target" = amber, "Above Target" = green).
- **Clustered column chart**: Axis = category, Values =
  `[Profit Margin %]`.
- **Table or treemap**: sub-category rollup (from `03_category_subcategory_analysis.sql`)
  to show which sub-categories drag each category down.

## 6. Polish

- **Theme**: View → Themes → pick a teal/dark theme, or import a custom
  theme JSON if you want to match the Excel dashboard's palette exactly
  (`#0F5C5C` dark teal, `#128C8C` teal).
- **Page names**: rename the tabs at the bottom ("Overview", "Regional &
  Category Detail") instead of leaving "Page 1" / "Page 2".
- **Tooltips**: Power BI adds these automatically — no extra work needed,
  but worth checking they show sensible values.

## 7. Export for the repo

Once built:

1. **File → Export → PDF** (or `.pbix` File → Export) — actually, simplest:
   take screenshots of each page (Windows: `Win+Shift+S`) and save them into
   `screenshots/` in this repo, named `overview.png` and
   `regional_detail.png`.
2. Save the file as `powerbi/Retail_Sales_Profitability.pbix` in this repo
   folder.
3. Update the README's screenshot links to point at your real screenshots
   instead of the design-reference image.

## Alternative: publish to Power BI Service (adds a live link)

If you have a Power BI (Microsoft/work or school, or free) account: **Home →
Publish** from Power BI Desktop. This gives you a shareable web link to the
live report, which you can add to your GitHub README and your resume —
much stronger than a static screenshot, since viewers can filter it
themselves.
