import sys
import yaml
from analysis.market_analysis import MarketAnalysis
import yaml
def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

config = load_config()
analyzer = MarketAnalysis("data/poland_real_estate.duckdb", config)
df = analyzer.get_ranked_listings()
print(df.to_dict(orient="records")[0])
