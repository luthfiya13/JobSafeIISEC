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

    // If fallback text provided (or mock extracted sample)
    if (fallbackText && fallbackText.trim().length >= 15) {
      const result = analyzeJobText(fallbackText);
      return NextResponse.json({
        ...result,
        input_type: "photo",
        raw_input: `Unggahan Screenshot: ${file.name}`
      });
    }

    // In serverless environment without Tesseract binary:
    // Prompt user friendly message to copy text
    return NextResponse.json(
      {
        detail: "Fitur pemindaian OCR gambar serverless menyarankan untuk menyalin teks lowongan ke tab Teks agar akurasi deteksi 10 indikator mencapai hasil maksimal."
      },
      { status: 400 }
    );
  } catch (err: any) {
    return NextResponse.json(
      { detail: "Gagal memproses gambar." },
      { status: 500 }
    );
  }
}
