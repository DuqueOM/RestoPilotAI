import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();

    // Forward the FormData to the backend
    const backendResponse = await fetch(
      `${BACKEND_URL}/api/v1/business/setup-wizard`,
      {
        method: 'POST',
        body: formData,
      }
    );

    const data = await backendResponse.json().catch(() => ({}));

    return NextResponse.json(data, { status: backendResponse.status });
  } catch (error: any) {
    console.error('[setup-wizard proxy] Error:', error?.message || error);
    return NextResponse.json(
      { detail: error?.message || 'Proxy error forwarding to backend' },
      { status: 502 }
    );
  }
}
