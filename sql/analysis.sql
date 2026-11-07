-- SQL portfolio: SQLite queries over the cleaned 'games' table.
-- Sales fields represent MILLION COPIES, not USD.

-- 1. Platform market leaders: volume and release counts.
SELECT Platform,
       COUNT(*) AS game_platform_releases,
       ROUND(SUM(Global_Sales), 2) AS global_sales_m
FROM games
GROUP BY Platform
ORDER BY global_sales_m DESC
LIMIT 10;

-- 2. Highest-selling publishers (historical cumulative copies).
SELECT Publisher,
       COUNT(*) AS game_platform_releases,
       ROUND(SUM(Global_Sales), 2) AS global_sales_m
FROM games
GROUP BY Publisher
ORDER BY global_sales_m DESC
LIMIT 10;

-- 3. Region mix as shares of the sum of regional estimates.
WITH region_units AS (
  SELECT 'North America' AS region, SUM(NA_Sales) AS units_m FROM games
  UNION ALL SELECT 'Europe', SUM(EU_Sales) FROM games
  UNION ALL SELECT 'Japan', SUM(JP_Sales) FROM games
  UNION ALL SELECT 'Other regions', SUM(Other_Sales) FROM games
)
SELECT region, ROUND(units_m, 2) AS sales_m,
       ROUND(100.0 * units_m / (SELECT SUM(units_m) FROM region_units), 2) AS share_pct
FROM region_units
ORDER BY sales_m DESC;

-- 4. Nintendo in Japan: group-level means and release counts.
SELECT Genre,
       COUNT(*) AS game_platform_releases,
       ROUND(AVG(JP_Sales), 3) AS japan_mean_m,
       ROUND(SUM(JP_Sales), 3) AS japan_sum_m
FROM games
WHERE Publisher = 'Nintendo'
GROUP BY Genre
ORDER BY japan_sum_m DESC;

-- 5. Nintendo Sports: cumulative sales by RELEASE year, not calendar-year sales.
SELECT Year AS release_year,
       ROUND(SUM(Global_Sales), 2) AS global_sales_m
FROM games
WHERE Publisher = 'Nintendo' AND Genre = 'Sports'
GROUP BY Year
ORDER BY global_sales_m DESC
LIMIT 10;
