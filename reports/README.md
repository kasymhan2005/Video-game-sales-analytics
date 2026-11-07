# Reproducible analytical deliverables

Run `python scripts/generate_report.py` after downloading the dataset to produce:
- `insights.md`: measured observations and business interpretation
- `figures/platforms.png`: historical platform unit-sales ranking
- `figures/release_cohorts.png`: release-year cohort comparison
- `figures/nintendo_japan_boxplot.png`: sales distributions

Run `python scripts/run_sql_analysis.py` to produce `sql_results.md`.

Reports require the real CSV. Their figures and values are **not mocked** or bundled before computation.
