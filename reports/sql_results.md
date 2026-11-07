# SQL Analysis Results

Generated from cleaned local VGSales data.

## Query 1

```sql
-- SQL portfolio: SQLite queries over the cleaned 'games' table.
-- Sales fields represent MILLION COPIES, not USD.

-- 1. Platform market leaders: volume and release counts.
SELECT Platform,
       COUNT(*) AS game_platform_releases,
       ROUND(SUM(Global_Sales), 2) AS global_sales_m
FROM games
GROUP BY Platform
ORDER BY global_sales_m DESC
LIMIT 10
```

```text
Platform  game_platform_releases  global_sales_m
     PS2                    2127         1233.46
    X360                    1234          969.60
     PS3                    1304          949.35
     Wii                    1290          909.81
      DS                    2131          818.91
      PS                    1189          727.39
     GBA                     786          305.62
     PSP                    1197          291.71
     PS4                     336          278.10
      PC                     938          254.70
```

## Query 2

```sql
-- 2. Highest-selling publishers (historical cumulative copies).
SELECT Publisher,
       COUNT(*) AS game_platform_releases,
       ROUND(SUM(Global_Sales), 2) AS global_sales_m
FROM games
GROUP BY Publisher
ORDER BY global_sales_m DESC
LIMIT 10
```

```text
                   Publisher  game_platform_releases  global_sales_m
                    Nintendo                     696         1784.43
             Electronic Arts                    1339         1093.39
                  Activision                     966          721.41
 Sony Computer Entertainment                     682          607.28
                     Ubisoft                     918          473.54
        Take-Two Interactive                     412          399.30
                         THQ                     712          340.44
Konami Digital Entertainment                     823          278.56
                        Sega                     632          270.70
          Namco Bandai Games                     928          253.65
```

## Query 3

```sql
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
ORDER BY sales_m DESC
```

```text
       region  sales_m  share_pct
North America  4327.65      49.14
       Europe  2406.69      27.33
        Japan  1284.27      14.58
Other regions   788.91       8.96
```

## Query 4

```sql
-- 4. Nintendo in Japan: group-level means and release counts.
SELECT Genre,
       COUNT(*) AS game_platform_releases,
       ROUND(AVG(JP_Sales), 3) AS japan_mean_m,
       ROUND(SUM(JP_Sales), 3) AS japan_sum_m
FROM games
WHERE Publisher = 'Nintendo'
GROUP BY Genre
ORDER BY japan_sum_m DESC
```

```text
       Genre  game_platform_releases  japan_mean_m  japan_sum_m
    Platform                     111         0.922       102.36
Role-Playing                     105         0.971       101.95
        Misc                     100         0.552        55.25
      Puzzle                      74         0.501        37.09
      Sports                      55         0.652        35.87
      Racing                      37         0.790        29.22
      Action                      78         0.374        29.16
  Simulation                      28         0.845        23.65
    Fighting                      18         0.830        14.94
    Strategy                      31         0.337        10.46
   Adventure                      35         0.257         9.01
     Shooter                      24         0.251         6.03
```

## Query 5

```sql
-- 5. Nintendo Sports: cumulative sales by RELEASE year, not calendar-year sales.
SELECT Year AS release_year,
       ROUND(SUM(Global_Sales), 2) AS global_sales_m
FROM games
WHERE Publisher = 'Nintendo' AND Genre = 'Sports'
GROUP BY Year
ORDER BY global_sales_m DESC
LIMIT 10
```

```text
 release_year  global_sales_m
         2006           84.62
         2009           56.67
         2007           25.63
         1984            6.18
         1989            5.72
         1998            4.01
         2005            3.75
         2000            3.57
         1983            3.20
         2008            2.72
```
