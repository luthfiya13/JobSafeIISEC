import { NextResponse } from "next/server";
import { analyzeJobText } from "@/lib/analyzer";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const text = typeof body.text === "string" ? body.text.trim() : "";
    const fileName = typeof body.file_name === "string" ? body.file_name.slice(0, 160) : "foto";

    if (text.length < 15) {
      return NextResponse.json(
        { detail: "Teks dari foto belum cukup untuk dianalisis. Coba foto yang lebih jelas atau salin teks lowongan ke tab Teks." },
        { status: 400 }
      );
    }

    // Bound request processing and keep OCR itself on the user's device, outside Vercel function limits.
    const extractedText = text.slice(0, 20_000);
    const result = analyzeJobText(extractedText);
    return NextResponse.json({
      ...result,
      input_type: "photo",
      raw_input: `Unggahan Screenshot: ${fileName}`,
      extracted_text: extractedText,
    });
  } catch (error: unknown) {
    console.error("Photo analysis failed:", error);
    return NextResponse.json(
      { detail: error instanceof Error ? error.message : "Gagal menganalisis teks dari foto." },
      { status: 500 }
    );
  }
}
