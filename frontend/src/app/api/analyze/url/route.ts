import { NextResponse } from "next/server";
import { analyzeJobText } from "@/lib/analyzer";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    let url = (body.url || "").trim();
    if (!url) {
      return NextResponse.json(
        { detail: "Tautan lowongan belum diisi. Masukkan URL lowongan yang ingin diperiksa." },
        { status: 400 }
      );
    }

    if (!url.startsWith("http://") && !url.startsWith("https://")) {
      url = "https://" + url;
    }

    try {
      const fetchRes = await fetch(url, {
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
          "Accept-Language": "id,en-US;q=0.9,en;q=0.8"
        },
        signal: AbortSignal.timeout(6000)
      });

      if (!fetchRes.ok) {
        return NextResponse.json(
          { detail: `Halaman tidak dapat diakses (Status: ${fetchRes.status}). Silakan salin teks lowongan secara manual.` },
          { status: 400 }
        );
      }

      const html = await fetchRes.text();
      // Simple HTML tags strip
      const cleanText = html
        .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, " ")
        .replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, " ")
        .replace(/<[^>]+>/g, " ")
        .replace(/\s+/g, " ")
        .trim();

      if (cleanText.length < 20) {
        return NextResponse.json(
          { detail: "Teks konten web terlalu sedikit atau dilindungi login/captcha. Silakan tempel teks secara manual." },
          { status: 400 }
        );
      }

      const result = analyzeJobText(cleanText.substring(0, 3000));
      return NextResponse.json({
        ...result,
        input_type: "link",
        raw_input: url,
        extracted_text: cleanText.substring(0, 1000)
      });
    } catch {
      return NextResponse.json(
        { detail: "Kami belum dapat mengakses tautan ini. Silakan salin teks lowongan secara langsung ke tab Teks." },
        { status: 400 }
      );
    }
  } catch (err: unknown) {
    return NextResponse.json(
      { detail: err instanceof Error ? err.message : "Gagal memproses tautan." },
      { status: 500 }
    );
  }
}
