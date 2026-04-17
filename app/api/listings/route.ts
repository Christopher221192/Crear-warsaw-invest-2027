import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    // Fetch from GitHub API for the Scraper Repo (supports private repos)
    const OWNER = process.env.GITHUB_REPO_OWNER || "Christopher221192";
    const REPO = process.env.GITHUB_REPO_NAME || "Crear-warsaw-scraper-pipeline";
    const PATH = "warsaw_apartments_scored.json";
    const TOKEN = process.env.GITHUB_TOKEN;

    const GITHUB_API_URL = `https://api.github.com/repos/${OWNER}/${REPO}/contents/${PATH}`;
    
    const response = await fetch(GITHUB_API_URL, { 
      headers: {
        "Authorization": `Bearer ${TOKEN}`,
        "Accept": "application/vnd.github.v3.raw"
      },
      next: { revalidate: 3600 } 
    });

    if (!response.ok) {
        return NextResponse.json({ 
            error: "Data source unavailable", 
            details: `GitHub API returned ${response.status}: ${response.statusText}` 
        }, { status: response.status });
    }

    const json = await response.json();
    
    if (!Array.isArray(json)) {
        console.error("Data received is not an array:", json);
        return NextResponse.json({ 
            error: "Invalid data format", 
            details: "Source JSON must be an array of objects." 
        }, { status: 500 });
    }
    
    // Map JSON to the UI contract using VALID JavaScript syntax
    const mapped = json.map((d: any) => ({
      id: String(d.id),
      url: d.url || "#",
      price_pln_gross: d.total_price || 0,
      price_per_sqm: d.price_per_m2 || 0,
      rooms: d.title?.includes("2-pok") ? 2 : 3,
      area_sqm: d.total_price && d.price_per_m2 ? Math.round((d.total_price / d.price_per_m2) * 10) / 10 : 0,
      floor: 0,
      district: d.district || "Unknown",
      city: "Warszawa",
      opportunity_score: d.opportunity_score || 50,
      annual_yield_percent: d.investment_analysis?.rent_sim?.gross_yield_pct || 0,
      original_title: d.title,
      investment_analysis: d.investment_analysis
    }));

    return NextResponse.json(mapped);
  } catch (error: any) {
    console.error('Error fetching Local JSON Listings:', error);
    return NextResponse.json({ 
      error: 'Internal Server Error reading JSON',
      details: error.message 
    }, { status: 500 });
  }
}
