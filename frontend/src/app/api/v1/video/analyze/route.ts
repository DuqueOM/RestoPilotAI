import { NextRequest, NextResponse } from 'next/server';

// Allow up to 180 seconds for Gemini video analysis
export const maxDuration = 180;

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 180_000);

  try {
    const formData = await request.formData();

    const backendResponse = await fetch(
      `${BACKEND_URL}/api/v1/video/analyze`,
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
        { detail: 'Video analysis timed out after 180s. Try a shorter video.' },
        { status: 504 }
      );
    }
    console.error('[video-proxy] Error:', error?.message || error);
    return NextResponse.json(
      { detail: error?.message || 'Proxy error forwarding to backend' },
      { status: 502 }
    );
  }
}
