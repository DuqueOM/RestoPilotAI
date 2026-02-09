import { NextRequest, NextResponse } from 'next/server';

// Allow up to 120 seconds for Gemini menu extraction
export const maxDuration = 120;

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 120_000);

  try {
    const formData = await request.formData();

    const backendResponse = await fetch(
      `${BACKEND_URL}/api/v1/ingest/menu`,
      {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      }
    );

    clearTimeout(timeout);
    const data = await backendResponse.json().catch(() => ({}));
    return NextResponse.json(data, { status: backendResponse.status });
  } catch (error: any) {
    clearTimeout(timeout);
    if (error?.name === 'AbortError') {
      return NextResponse.json(
        { detail: 'Menu extraction timed out after 120s. Try a simpler image.' },
        { status: 504 }
      );
    }
    console.error('[menu-proxy] Error:', error?.message || error);
    return NextResponse.json(
      { detail: error?.message || 'Proxy error forwarding to backend' },
      { status: 502 }
    );
  }
}
