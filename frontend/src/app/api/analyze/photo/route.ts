import { NextResponse } from "next/server";
import Tesseract from "tesseract.js";
import { analyzeJobText } from "@/lib/analyzer";

export const runtime = "nodejs";

function normalizeExtractedText(text: string) {
  return text
    .replace(/\r/g, "")
    .replace(/[\u0000-\u001F\u007F]/g, " ")
    .replace(/\s{3,}/g, " \n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

async function extractTextFromImage(file: File) {
  const bytes = Buffer.from(await file.arrayBuffer());

  const result = await Tesseract.recognize(bytes, "eng+ind", {
    logger: () => undefined,
  });

  const extracted = normalizeExtractedText(result.data.text || "");
  return extracted;
}

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
      const result = analyzeJobText(fallbackText.trim());
      return NextResponse.json({
        ...result,
        input_type: "photo",
        raw_input: `Unggahan Screenshot: ${file.name}`,
        extracted_text: fallbackText.trim(),
      });
    }

    const extractedText = await extractTextFromImage(file);

    if (!extractedText || extractedText.length < 15) {
      return NextResponse.json(
        {
          detail: "Teks dari foto tidak terbaca dengan jelas. Silakan pilih foto yang lebih jelas atau unggah teks lowongan melalui tab Teks.",
        },
        { status: 400 }
      );
    }

    const result = analyzeJobText(extractedText);

    return NextResponse.json({
      ...result,
      input_type: "photo",
      raw_input: `Unggahan Screenshot: ${file.name}`,
      extracted_text: extractedText,
    });
  } catch (error: any) {
    console.error("Photo OCR analysis failed:", error);
    return NextResponse.json(
      {
        detail: error?.message || "Gagal memproses gambar dan membaca teks dari foto.",
      },
      { status: 500 }
    );
  }
}
