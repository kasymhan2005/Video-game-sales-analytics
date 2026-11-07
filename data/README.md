# Data provenance

`games.csv` in the user's downloadable ZIP is the exact file supplied by the user during this conversation. Dataset schema: 16,598 rows × 11 columns, as in the historic VGSales dataset.

- Public reference: https://www.kaggle.com/datasets/gregorut/videogamesales
- Archival reference: https://zenodo.org/records/5898311
- Course mirror: https://disk.360.yandex.ru/i/eQEYbmT4YSCUHQ

The raw file is intentionally ignored by Git (`.gitignore`). The downloadable personal ZIP includes the original for easy local use. Do not commit or redistribute the raw CSV until you have verified the dataset licensing/permissions.

SHA-256 of supplied `games.csv`: `e2076095ffcae2a92dbc6de6ecbd54455ee034bb38da550b2dc385e9265d4ebe`

All analytic outputs can be recreated with `python scripts/generate_report.py` and `python scripts/run_sql_analysis.py`.
