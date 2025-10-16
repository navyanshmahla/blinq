import polars as pl

df = pl.read_csv("data/data.csv")

query = "SELECT DISTINCT Merchant FROM self WHERE LOWER(Merchant) LIKE '%cafe%' OR LOWER(Merchant) LIKE '%coffee%' OR LOWER(Merchant) LIKE '%starbucks%' OR LOWER(Merchant) LIKE '%ccd%' OR LOWER(Merchant) LIKE '%barista%'"

result = df.sql(query)

print(result)
