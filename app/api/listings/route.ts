import { db } from '@vercel/postgres';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const client = await db.connect();
    
    // Fetch top 50 opportunities, sorted by highest score
    const properties = await client.sql`
      SELECT 
        id, 
        url, 
        price_pln_gross, 
        price_per_sqm, 
        rooms, 
        area_sqm, 
        floor, 
        district, 
        city, 
        opportunity_score, 
        annual_yield_percent,
        title as original_title,
        market_diff_percent,
        layout_quality,
        projected_capital_gain_pct,
        monthly_mortgage_pln,
        break_even_years
      FROM properties 
      ORDER BY opportunity_score DESC
      LIMIT 50;
    `;
    
    // Transform to match exactly what the UI needs (mocking the nested JSON blocks we built before)
    const mapped = properties.rows.map(row => ({
      id: row.id,
      url: row.url,
      price_pln_gross: Number(row.price_pln_gross),
      price_per_sqm: Number(row.price_per_sqm),
      rooms: row.rooms,
      area_sqm: Number(row.area_sqm),
      floor: row.floor,
      district: row.district,
      city: row.city,
      opportunity_score: Number(row.opportunity_score),
      annual_yield_percent: Number(row.annual_yield_percent),
      original_title: row.original_title,
      investment_analysis: {
        rent_sim: {
          gross_yield_pct: Number(row.annual_yield_percent),
          estimated_monthly_rent_pln: Number(row.price_per_sqm) * Number(row.area_sqm) * (Number(row.annual_yield_percent)/100) / 12, // approx math
          monthly_cashflow_pln: 0,
          break_even_years_from_rent: Number(row.break_even_years)
        },
        mortgage_sim: {
          monthly_payment_pln: Number(row.monthly_mortgage_pln)
        },
        projection_2031: {
          expected_capital_gain_pct: Number(row.projected_capital_gain_pct),
          estimated_value_pln: Number(row.price_pln_gross) * (1 + Number(row.projected_capital_gain_pct)/100),
          expected_capital_gain_pln: Number(row.price_pln_gross) * (Number(row.projected_capital_gain_pct)/100)
        },
        vision_ai_layout: row.layout_quality
      }
    }));

    return NextResponse.json(mapped);
  } catch (error) {
    console.error('Error fetching Postgres Listings:', error);
    return NextResponse.json({ error: 'Internal Server Error fetching Database' }, { status: 500 });
  }
}
