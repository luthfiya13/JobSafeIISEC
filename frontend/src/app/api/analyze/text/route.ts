import { NextResponse } from "next/server";
import { analyzeJobText } from "@/lib/analyzer";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const text = body.text || "";
    if (!text || text.trim().length < 15) {
      return NextResponse.json(
        { detail: "Teks lowongan terlalu pendek. Masukkan minimal 15 karakter untuk analisis yang memadai." },
        { status: 400 }
      );
    }

    const result = analyzeJobText(text);
    return NextResponse.json(result);
  } catch (err: unknown) {
    return NextResponse.json(
      { detail: err instanceof Error ? err.message : "Gagal menganalisis teks lowongan." },
      { status: 500 }
    );
  }
}
