import { NextResponse } from "next/server";

const BACKEND_URL = (process.env.BACKEND_API_URL || "http://127.0.0.1:8000/api").replace(/\/$/, "");

export async function proxyBackend(path: string, request: Request) {
  try {
    const headers = new Headers(request.headers);
    headers.delete("host");
    const hasBody = !["GET", "HEAD"].includes(request.method);
    const response = await fetch(`${BACKEND_URL}${path}`, {
      method: request.method,
      headers,
      body: hasBody ? await request.arrayBuffer() : undefined,
      cache: "no-store",
    });
    return new NextResponse(response.body, { status: response.status, headers: response.headers });
  } catch {
    return NextResponse.json(
      { detail: "Backend JOBSAFE tidak dapat dihubungi. Pastikan API FastAPI sedang berjalan." },
      { status: 503 },
    );
  }
}
