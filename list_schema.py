import duckdb
con = duckdb.connect("data/poland_real_estate.duckdb")
df = con.execute("DESCRIBE listings;").df()
print(df.to_string())
con.close()
