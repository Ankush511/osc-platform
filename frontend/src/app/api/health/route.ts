/**
 * Health check endpoint for frontend service
 */
import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    service: 'oscp-frontend',
    timestamp: new Date().toISOString(),
  });
}
