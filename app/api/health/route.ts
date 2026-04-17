import { db } from '@vercel/postgres';
import { NextResponse } from 'next/server';

export async function GET() {
  const diagnostics: Record<string, string> = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    db: 'disconnected',
    properties_count: '0',
  };

  try {
    const client = await db.connect();
    const result = await client.sql`SELECT COUNT(*) as total FROM properties;`;
    diagnostics.db = 'connected';
    diagnostics.properties_count = result.rows[0]?.total?.toString() || '0';
  } catch (error: any) {
    diagnostics.status = 'degraded';
    diagnostics.db = `error: ${error.message?.substring(0, 100)}`;
  }

  return NextResponse.json(diagnostics, {
    status: diagnostics.status === 'ok' ? 200 : 503,
  });
}
