# Data Directory

This directory contains the LEGO parts database downloaded from [Rebrickable](https://rebrickable.com/downloads/).

## Files

When properly set up, this directory should contain:

- `colors.csv` - LEGO color information with RGB values
- `parts.csv` - LEGO part information and categories
- `part_categories.csv` - Part category definitions
- `inventory_parts.csv` - Part inventory data (large file)
- `elements.csv` - Element information
- `inventories.csv` - Inventory definitions
- `inventory_minifigs.csv` - Minifigure inventory data
- `inventory_sets.csv` - Set inventory data
- `minifigs.csv` - Minifigure information
- `part_relationships.csv` - Part relationship data
- `sets.csv` - LEGO set information
- `themes.csv` - Theme categories

## Setup

To download the data files, run:

```bash
python update_lego_parts_data.py
```

This will automatically download and extract the latest LEGO parts database from Rebrickable.

## Updates

The LEGO parts database is updated regularly. To get the latest data:

1. Delete the existing CSV files (optional)
2. Run the update script again

## Size Information

The complete database is approximately 500MB-1GB when extracted. The largest file is typically `inventory_parts.csv` which contains millions of records.

## Data Source

All data is sourced from [Rebrickable.com](https://rebrickable.com/) under their terms of service. Rebrickable provides comprehensive LEGO parts data for the community.
