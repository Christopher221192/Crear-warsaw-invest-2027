import json
import yaml
from analysis.market_analysis import MarketAnalysis
config = yaml.safe_load(open("config.yaml"))
analyzer = MarketAnalysis("data/poland_real_estate.duckdb", config)
df = analyzer.get_ranked_listings()
res = df.to_dict(orient="records")
print(json.dumps(res[0], indent=2))
