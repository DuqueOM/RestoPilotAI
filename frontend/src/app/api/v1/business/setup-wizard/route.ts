import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Extended timeout for setup-wizard — processes files with Gemini (menu extraction, etc.)
export const maxDuration = 300; // 5 minutes

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 290_000); // 290s

    const backendResponse = await fetch(
      `${BACKEND_URL}/api/v1/business/setup-wizard`,
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
    console.error('[setup-wizard proxy] Error:', error?.message || error);
    if (error?.name === 'AbortError') {
      return NextResponse.json(
        { detail: 'Setup wizard timed out — try uploading fewer files' },
        { status: 504 }
      );
    }
    return NextResponse.json(
      { detail: error?.message || 'Proxy error forwarding to backend' },
      { status: 502 }
    );
  }
}
