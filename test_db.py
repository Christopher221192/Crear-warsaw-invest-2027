import duckdb
con = duckdb.connect("data/poland_real_estate.duckdb")
df = con.execute("SELECT DISTINCT lower(city) as c, lower(district) as d FROM listings;").df()
print(df.to_string())
con.close()
