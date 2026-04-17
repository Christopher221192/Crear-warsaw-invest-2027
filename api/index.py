import os
import sys

# Ensure DuckDB/MotherDuck has a writable home directory in Vercel
if os.environ.get("VERCEL"):
    os.environ["HOME"] = "/tmp"

import yaml
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Add root to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from analysis.market_analysis import MarketAnalysis
from analysis.listing_analyzer import analyze_listing, ListingAnalysis
from chatbot.chatbot_engine import ChatbotEngine

app = FastAPI(title="Poland House Hunter API")

# Enable CORS for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class ChatQuery(BaseModel):
    query: str

class AnalysisQuery(BaseModel):
    url: str
    city: str = ""
    district: str = ""
    floor: int = 0
    total_floors: int = 0
    area: float = 0
    rooms: int = 0
    price: float = 0

# --- DB HELPERS ---
def get_db_path():
    # Production: MotherDuck
    # Local: SQLite/DuckDB file
    token = os.getenv("MOTHERDUCK_TOKEN")
    if token:
        return f"md:poland_listings?motherduck_token={token}"
    return "data/poland_real_estate.duckdb"

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

# --- ENDPOINTS ---
@app.get("/api/listings")
async def get_listings():
    try:
        import json
        with open("public/data/apartments.json", "r") as f:
            data = json.load(f)
        
        # Map our JSON items to the contract the NextJS frontend expects
        mapped = []
        for d in data:
            mapped.append({
                "id": str(d.get("id")),
                "url": "#", # No direct URL available in scrape natively rn
                "price_pln_gross": d.get("total_price", 0),
                "price_per_sqm": d.get("price_per_m2", 0),
                "rooms": 2 if "2-pok" in d.get("title", "") else 3,
                "area_sqm": round(d.get("total_price", 1) / d.get("price_per_m2", 1), 1) if d.get("price_per_m2") else 0,
                "floor": 0,
                "district": d.get("district", "Unknown"),
                "city": "Warszawa",
                "opportunity_score": d.get("opportunity_score", 50),
                "annual_yield_percent": d.get("investment_analysis", {}).get("rent_sim", {}).get("gross_yield_pct", 0),
                # Custom fields for our UI
                "original_title": d.get("title"),
                "investment_analysis": d.get("investment_analysis")
            })
        return mapped
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze(query: AnalysisQuery):
    try:
        analysis = analyze_listing(
            url=query.url,
            city=query.city,
            district=query.district,
            floor=query.floor,
            total_floors=query.total_floors,
            area=query.area,
            rooms=query.rooms,
            price=query.price
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(query: ChatQuery):
    try:
        config = load_config()
        analyzer = MarketAnalysis(get_db_path(), config)
        df = analyzer.get_ranked_listings()
        engine = ChatbotEngine(df)
        response, filtered_df = engine.process_query(query.query)
        
        return {
            "response": response,
            "results": filtered_df.to_dict(orient="records") if filtered_df is not None else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health():
    return {"status": "ok"}
