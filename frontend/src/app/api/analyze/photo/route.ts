import { NextResponse } from "next/server";
import { analyzeJobText } from "@/lib/analyzer";

export async function POST(req: Request) {
  try {
    const formData = await req.formData();
    const file = formData.get("file") as File | null;
    const fallbackText = formData.get("fallback_text") as string | null;

    if (!file) {
      return NextResponse.json(
        { detail: "Berkas foto belum dipilih." },
        { status: 400 }
      );
    }

    if (fallbackText && fallbackText.trim().length >= 15) {
      const result = analyzeJobText(fallbackText);
      return NextResponse.json({
        ...result,
        input_type: "photo",
        raw_input: `Unggahan Screenshot: ${file.name}`
      });
    }

    const backendUrl = (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api").replace(/\/$/, "");

    try {
      const backendFormData = new FormData();
      backendFormData.append("file", file, file.name);
      if (fallbackText && fallbackText.trim()) {
        backendFormData.append("fallback_text", fallbackText.trim());
      }

      const backendRes = await fetch(`${backendUrl}/analyze/photo`, {
        method: "POST",
        body: backendFormData,
      });

      const backendData = await backendRes.json().catch(() => null);

      if (backendRes.ok && backendData) {
        return NextResponse.json(backendData);
      }

      if (backendData?.detail) {
        return NextResponse.json({ detail: backendData.detail }, { status: backendRes.status || 400 });
      }
    } catch {
      // backend not running yet; fallback to friendly manual-text prompt
    }

    return NextResponse.json(
      {
        detail: "Fitur pemindaian OCR dari foto sedang menunggu backend OCR aktif. Silakan tempel teks lowongan ke tab Teks agar analisis dapat dilanjutkan."
      },
      { status: 400 }
    );
  } catch {
    return NextResponse.json(
      { detail: "Gagal memproses gambar." },
      { status: 500 }
    );
  }
}
