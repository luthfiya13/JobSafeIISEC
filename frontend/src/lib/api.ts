import { analyzeJobText } from "./analyzer";

export interface IndicatorItem {
  code: string;
  name: string;
  category?: string;
  weight: number;
  status: "TIDAK_TERDETEKSI" | "PERLU_PERHATIAN" | "RISIKO_TINGGI";
  status_label: string;
  status_badge: "safe" | "attention" | "high";
  description: string;
  why_important: string;
  reason?: string | null;
  legal_basis?: string | null;
  syariah_basis?: string | null;
  matches_count?: number;
  evidence?: string | null;
}

export interface VerificationStep {
  id: string;
  title: string;
  desc: string;
}

export interface AnalysisResult {
  id?: number;
  risk_score: number | null;
  risk_level: "RISIKO RENDAH" | "RISIKO SEDANG" | "RISIKO TINGGI" | "INSUFFICIENT_INPUT";
  risk_color: "green" | "amber" | "red" | "gray";
  risk_theme: string;
  level_code: "LOW" | "MEDIUM" | "HIGH" | "INSUFFICIENT_INPUT";
  summary: string;
  findings_summary?: string;
  preventive_advice?: string;
  indicators_detected_count: number;
  indicators_attention_count: number;
  indicators_high_count: number;
  indicators: IndicatorItem[];
  verification_steps: VerificationStep[];
  disclaimer: string;
  model?: {
    context_llm_enabled?: boolean;
    context_llm_used?: boolean;
    context_llm_model?: string | null;
    context_llm_findings?: number;
  };
  model_meta?: { engine_version?: string; ml_enabled?: boolean; [key: string]: unknown };
  risk_thresholds?: { low_max: number; high_min: number };
  raw_input?: string;
  input_type?: "text" | "photo" | "link";
  extracted_text?: string;
  page_title?: string;
}

export interface AdminAnalysisRecord {
  id: number;
  input_type: "text" | "photo" | "link";
  input_preview: string;
  risk_score: number;
  risk_level: string;
  level_code: "LOW" | "MEDIUM" | "HIGH";
  detected_count: number;
  created_at: string;
  indicators?: Array<{ code?: string; name?: string }>;
  summary: string;
}

export interface AdminDashboardStats {
  total_analyses: number;
  risk_low: number;
  risk_medium: number;
  risk_high: number;
  distribution: { low_pct: number; med_pct: number; high_pct: number };
  top_indicators: Array<{ code: string; count: number }>;
  recent_analyses: AdminAnalysisRecord[];
}

export interface AdminIndicator {
  code: string;
  name: string;
  weight: number;
  hard_flag: boolean;
  is_active: boolean;
  category: string;
  description: string;
  why_important: string;
  keywords: string[];
}

export interface AdminSettings {
  site_name: string;
  threshold_low_max: number | string;
  threshold_med_max: number | string;
  threshold_high_min: number | string;
  analysis_engine_version: string;
  maintenance_mode: boolean | string;
}

export interface PublicIndicator {
  code: string;
  name: string;
  category: string;
  weight: number;
  description: string;
  why_important: string;
}

export interface AdminReportRecord {
  id: number;
  analysis_id: number | null;
  listing_preview: string;
  complaint: string;
  created_at: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api";

export async function analyzeText(text: string, inputType: "text" | "photo" = "text"): Promise<AnalysisResult> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/analyze/text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, input_type: inputType }),
    });
  } catch {
    // Keep text analysis usable when the optional FastAPI service is offline.
    return { ...analyzeJobText(text), input_type: inputType };
  }

  if (res.status === 503) {
    // The Next.js proxy returns 503 when FastAPI is not running. The browser
    // engine uses the same indicator contract and lets the user still see a
    // report instead of getting stuck after the progress animation.
    return { ...analyzeJobText(text), input_type: inputType };
  }

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Terjadi kendala saat menganalisis teks lowongan.");
  }

  return res.json();
}

export async function analyzeUrl(url: string): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/analyze/url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Kami belum dapat mengakses tautan lowongan ini. Silakan tempel teks secara manual.");
  }

  return res.json();
}

export async function analyzePhoto(file: File, fallbackText?: string): Promise<AnalysisResult> {
  if (file.size > 10 * 1024 * 1024) {
    throw new Error("Ukuran foto melebihi 10 MB. Kompres gambar atau pilih screenshot yang lebih kecil.");
  }

  const extractedText = fallbackText?.trim() || await readTextFromImage(file);
  if (extractedText.length < 15) {
    throw new Error("Teks dari foto belum terbaca dengan jelas. Coba foto yang lebih tajam, lurus, dan memiliki kontras yang baik.");
  }

  // OCR is already complete in the browser. Send only the reviewed text so
  // the backend does not decode the same image a second time.
  return analyzeText(extractedText, "photo");
}

function normalizeOcrText(text: string) {
  return text
    .replace(/\r/g, "")
    .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, " ")
    .replace(/[ \t]+/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function ocrQualityScore(text: string, confidence: number, wordConfidence: number) {
  const tokens = text.match(/[A-Za-zÀ-ÿ0-9]{2,}/g) || [];
  const nonSpace = text.replace(/\s/g, "");
  const usefulCharacterRatio = nonSpace.length ? tokens.join("").length / nonSpace.length : 0;
  const plausibleTokenRatio = tokens.length
    ? tokens.filter((token) => /[A-Za-zÀ-ÿ]/.test(token)).length / tokens.length
    : 0;
  return confidence * 0.5
    + wordConfidence * 0.35
    + Math.min(text.length, 1800) * 0.012
    + usefulCharacterRatio * 12
    + plausibleTokenRatio * 8;
}

function mergeTiledOcrText(tileTexts: string[]) {
  const mergedLines: string[] = [];
  for (const tileText of tileTexts) {
    const previousTileLines = mergedLines.slice(-10);
    for (const line of normalizeOcrText(tileText).split("\n")) {
      const normalizedLine = line.toLowerCase().replace(/[^a-z0-9]+/g, "");
      if (!normalizedLine) continue;
      const duplicateAtBoundary = previousTileLines.some((previousLine) => {
        const previous = previousLine.toLowerCase().replace(/[^a-z0-9]+/g, "");
        if (normalizedLine === previous) return true;
        if (Math.min(normalizedLine.length, previous.length) < 14) return false;
        const shorter = normalizedLine.length < previous.length ? normalizedLine : previous;
        const longer = normalizedLine.length < previous.length ? previous : normalizedLine;
        return longer.includes(shorter) && shorter.length / longer.length >= 0.82;
      });
      if (!duplicateAtBoundary) mergedLines.push(line);
    }
  }
  return mergedLines.join("\n");
}

function createOcrTiles(image: HTMLCanvasElement) {
  const vertical = image.height >= image.width * 0.85;
  const axisLength = vertical ? image.height : image.width;
  const count = axisLength >= 1800 ? 3 : 2;
  const baseLength = axisLength / count;
  const overlap = baseLength * 0.14;
  const tiles: HTMLCanvasElement[] = [];

  for (let index = 0; index < count; index++) {
    const start = Math.max(0, Math.round(index * (baseLength - overlap)));
    const end = index === count - 1
      ? axisLength
      : Math.min(axisLength, Math.round(start + baseLength + overlap));
    const tile = document.createElement("canvas");
    tile.width = vertical ? image.width : end - start;
    tile.height = vertical ? end - start : image.height;
    const context = tile.getContext("2d");
    if (!context) continue;
    if (vertical) {
      context.drawImage(image, 0, start, image.width, end - start, 0, 0, tile.width, tile.height);
    } else {
      context.drawImage(image, start, 0, end - start, image.height, 0, 0, tile.width, tile.height);
    }
    tiles.push(tile);
  }
  return tiles;
}

async function createOcrVariants(file: File): Promise<HTMLCanvasElement[]> {
  const bitmap = await createImageBitmap(file);
  try {
    // Enlarge small screenshots and bound large phone photos to avoid excessive browser memory use.
    const longestSide = Math.max(bitmap.width, bitmap.height);
    const targetSide = Math.min(4600, Math.max(2400, longestSide));
    const scale = Math.min(
      4,
      targetSide / longestSide,
      Math.sqrt(8_000_000 / (bitmap.width * bitmap.height)),
    );
    const width = Math.max(1, Math.round(bitmap.width * scale));
    const height = Math.max(1, Math.round(bitmap.height * scale));
    const source = document.createElement("canvas");
    source.width = width;
    source.height = height;
    const sourceContext = source.getContext("2d", { willReadFrequently: true });
    if (!sourceContext) throw new Error("Browser tidak dapat menyiapkan gambar untuk OCR.");
    sourceContext.fillStyle = "#fff";
    sourceContext.fillRect(0, 0, width, height);
    sourceContext.imageSmoothingEnabled = true;
    sourceContext.imageSmoothingQuality = "high";
    sourceContext.drawImage(bitmap, 0, 0, width, height);

    const sourcePixels = sourceContext.getImageData(0, 0, width, height);
    const sourceData = sourcePixels.data;
    const histogram = new Uint32Array(256);
    let brightnessTotal = 0;
    for (let i = 0; i < sourceData.length; i += 4) {
      const gray = Math.round(0.299 * sourceData[i] + 0.587 * sourceData[i + 1] + 0.114 * sourceData[i + 2]);
      histogram[gray]++;
      brightnessTotal += gray;
    }

    // Use percentile contrast limits so a few shadows/highlights do not wash out the text.
    const pixelCount = width * height;
    const percentileLimit = Math.floor(pixelCount * 0.015);
    let low = 0;
    let high = 255;
    let cumulative = 0;
    for (let value = 0; value < 255; value++) {
      cumulative += histogram[value];
      if (cumulative >= percentileLimit) {
        low = value;
        break;
      }
    }
    cumulative = 0;
    for (let value = 255; value > 0; value--) {
      cumulative += histogram[value];
      if (cumulative >= percentileLimit) {
        high = value;
        break;
      }
    }
    if (high - low < 40) {
      low = 0;
      high = 255;
    }

    const contrast = document.createElement("canvas");
    contrast.width = width;
    contrast.height = height;
    const contrastContext = contrast.getContext("2d", { willReadFrequently: true });
    if (!contrastContext) throw new Error("Browser tidak dapat meningkatkan kontras foto.");
    const contrastPixels = contrastContext.createImageData(width, height);
    const contrastData = contrastPixels.data;
    for (let i = 0; i < sourceData.length; i += 4) {
      const gray = 0.299 * sourceData[i] + 0.587 * sourceData[i + 1] + 0.114 * sourceData[i + 2];
      const enhanced = Math.max(0, Math.min(255, Math.round(((gray - low) * 255) / (high - low))));
      contrastData[i] = enhanced;
      contrastData[i + 1] = enhanced;
      contrastData[i + 2] = enhanced;
      contrastData[i + 3] = 255;
    }
    contrastContext.putImageData(contrastPixels, 0, 0);

    // Adaptive thresholding handles uneven lighting and paper shadows better than a single global threshold.
    const sampleSide = 64;
    const sampleWidth = Math.max(1, Math.round(width / Math.max(width, height) * sampleSide));
    const sampleHeight = Math.max(1, Math.round(height / Math.max(width, height) * sampleSide));
    const localMeansCanvas = document.createElement("canvas");
    localMeansCanvas.width = sampleWidth;
    localMeansCanvas.height = sampleHeight;
    const localMeansContext = localMeansCanvas.getContext("2d", { willReadFrequently: true });
    if (!localMeansContext) throw new Error("Browser tidak dapat menganalisis pencahayaan foto.");
    localMeansContext.drawImage(source, 0, 0, sampleWidth, sampleHeight);
    const localMeans = localMeansContext.getImageData(0, 0, sampleWidth, sampleHeight).data;
    const darkBackground = brightnessTotal / pixelCount < 128;
    const binary = document.createElement("canvas");
    binary.width = width;
    binary.height = height;
    const binaryContext = binary.getContext("2d", { willReadFrequently: true });
    if (!binaryContext) throw new Error("Browser tidak dapat menyiapkan ambang kontras OCR.");
    const binaryPixels = binaryContext.createImageData(width, height);
    const binaryData = binaryPixels.data;
    const scaleX = sampleWidth / width;
    const scaleY = sampleHeight / height;
    for (let y = 0; y < height; y++) {
      const sampleY = Math.min(sampleHeight - 1, Math.floor(y * scaleY));
      for (let x = 0; x < width; x++) {
        const i = (y * width + x) * 4;
        const sampleX = Math.min(sampleWidth - 1, Math.floor(x * scaleX));
        const sampleIndex = (sampleY * sampleWidth + sampleX) * 4;
        const gray = 0.299 * sourceData[i] + 0.587 * sourceData[i + 1] + 0.114 * sourceData[i + 2];
        const localMean = 0.299 * localMeans[sampleIndex] + 0.587 * localMeans[sampleIndex + 1] + 0.114 * localMeans[sampleIndex + 2];
        const isText = darkBackground ? gray > localMean + 12 : gray < localMean - 12;
        const value = isText ? 0 : 255;
        binaryData[i] = value;
        binaryData[i + 1] = value;
        binaryData[i + 2] = value;
        binaryData[i + 3] = 255;
      }
    }
    binaryContext.putImageData(binaryPixels, 0, 0);

    return [source, contrast, binary];
  } finally {
    bitmap.close();
  }
}

export async function readTextFromImage(file: File): Promise<string> {
  if (!file.type.startsWith("image/")) {
    throw new Error("Berkas harus berupa gambar PNG, JPG, atau JPEG.");
  }

  const [{ createWorker }, variants] = await Promise.all([
    import("tesseract.js"),
    createOcrVariants(file),
  ]);
  let worker: Awaited<ReturnType<typeof createWorker>>;
  try {
    worker = await createWorker("ind+eng", undefined, { logger: () => undefined });
  } catch (error) {
    console.error("Could not initialize browser OCR:", error);
    throw new Error("Mesin OCR tidak dapat dimuat. Pastikan koneksi internet aktif lalu coba kembali.");
  }

  try {
    await worker.setParameters({
      tessedit_pageseg_mode: "6" as import("tesseract.js").PSM,
      preserve_interword_spaces: "1",
      user_defined_dpi: "300",
    });
    let bestText = "";
    let bestScore = Number.NEGATIVE_INFINITY;

    // Try layouts suited to job-post screenshots, scattered text, and full-page photos.
    const passes: Array<{ image: HTMLCanvasElement; pageMode: import("tesseract.js").PSM; rotateAuto?: boolean }> = [
      { image: variants[0], pageMode: "6" as import("tesseract.js").PSM, rotateAuto: true },
      { image: variants[0], pageMode: "3" as import("tesseract.js").PSM },
      { image: variants[1], pageMode: "6" as import("tesseract.js").PSM },
      { image: variants[2], pageMode: "6" as import("tesseract.js").PSM },
      { image: variants[0], pageMode: "11" as import("tesseract.js").PSM },
      { image: variants[2], pageMode: "11" as import("tesseract.js").PSM },
    ];
    for (const pass of passes) {
      await worker.setParameters({ tessedit_pageseg_mode: pass.pageMode });
      const { data } = await worker.recognize(pass.image, { rotateAuto: pass.rotateAuto }, { text: true, blocks: true });
      const text = normalizeOcrText(data.text || "");
      const words = (data.blocks || []).flatMap((block) =>
        block.paragraphs.flatMap((paragraph) => paragraph.lines.flatMap((line) => line.words))
      ).filter((word) => word.text.trim());
      const wordConfidence = words.length
        ? words.reduce((sum, word) => sum + word.confidence, 0) / words.length
        : data.confidence;
      const score = ocrQualityScore(text, data.confidence, wordConfidence);
      if (score > bestScore) {
        bestText = text;
        bestScore = score;
      }
      if (score >= 105 && text.length >= 120 && wordConfidence >= 88) {
        break;
      }
    }

    // Cropping makes small print larger and prevents large page layouts from hiding lower sections.
    const tiles = createOcrTiles(variants[1]);
    const tileTexts: string[] = [];
    let tileConfidence = 0;
    for (const tile of tiles) {
      await worker.setParameters({ tessedit_pageseg_mode: "6" as import("tesseract.js").PSM });
      const { data } = await worker.recognize(tile, {}, { text: true, blocks: true });
      let tileText = normalizeOcrText(data.text || "");
      let tileScore = data.confidence;
      const words = (data.blocks || []).flatMap((block) =>
        block.paragraphs.flatMap((paragraph) => paragraph.lines.flatMap((line) => line.words))
      ).filter((word) => word.text.trim());
      let wordConfidence = words.length
        ? words.reduce((sum, word) => sum + word.confidence, 0) / words.length
        : data.confidence;
      if (data.confidence < 72 || wordConfidence < 72) {
        await worker.setParameters({ tessedit_pageseg_mode: "11" as import("tesseract.js").PSM });
        const sparseResult = await worker.recognize(tile, {}, { text: true, blocks: true });
        const sparseText = normalizeOcrText(sparseResult.data.text || "");
        const sparseWords = (sparseResult.data.blocks || []).flatMap((block) =>
          block.paragraphs.flatMap((paragraph) => paragraph.lines.flatMap((line) => line.words))
        ).filter((word) => word.text.trim());
        const sparseWordConfidence = sparseWords.length
          ? sparseWords.reduce((sum, word) => sum + word.confidence, 0) / sparseWords.length
          : sparseResult.data.confidence;
        const sparseScore = ocrQualityScore(sparseText, sparseResult.data.confidence, sparseWordConfidence);
        const standardScore = ocrQualityScore(tileText, data.confidence, wordConfidence);
        if (sparseScore > standardScore) {
          tileText = sparseText;
          tileScore = sparseResult.data.confidence;
          wordConfidence = sparseWordConfidence;
        }
      }
      tileTexts.push(tileText);
      tileConfidence += (tileScore + wordConfidence) / 2;
    }

    const tiledText = normalizeOcrText(mergeTiledOcrText(tileTexts));
    const tiledScore = ocrQualityScore(tiledText, tileConfidence / Math.max(tiles.length, 1), tileConfidence / Math.max(tiles.length, 1));
    if (tiledText.length > bestText.length && tiledScore >= bestScore - 8) {
      bestText = tiledText;
    }

    return bestText;
  } catch (error) {
    console.error("Browser OCR failed:", error);
    throw new Error("Mesin OCR gagal memproses gambar. Pastikan koneksi internet aktif lalu coba unggah kembali.");
  } finally {
    await worker.terminate();
  }
}

export async function getPublicIndicators(): Promise<PublicIndicator[]> {
  try {
    const res = await fetch(`${API_BASE}/public-indicators`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Using fallback indicators list", err);
  }
  return [];
}

// Admin API
export async function adminLogin(email: string, password: string) {
  const res = await fetch(`${API_BASE}/admin/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Email atau kata sandi admin tidak sesuai.");
  }

  return res.json();
}

export async function getAdminDashboard(token: string): Promise<AdminDashboardStats> {
  const res = await fetch(`${API_BASE}/admin/dashboard`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Gagal memuat statistik dashboard.");
  return res.json();
}

export async function getAdminAnalyses(
  token: string,
  q?: string,
  level?: string
): Promise<{ items: AdminAnalysisRecord[]; count: number }> {
  const params = new URLSearchParams();
  if (q) params.set("q", q);
  if (level) params.set("level", level);

  const res = await fetch(`${API_BASE}/admin/analyses?${params.toString()}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Gagal memuat riwayat analisis.");
  return res.json();
}

export async function getAdminIndicators(token: string): Promise<{
  indicators: AdminIndicator[];
  total_weight: number;
  is_valid_total: boolean;
}> {
  const res = await fetch(`${API_BASE}/admin/indicators`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Gagal memuat daftar indikator.");
  return res.json();
}

export async function updateAdminIndicator(
  token: string,
  code: string,
  data: { weight: number; is_active: boolean; description: string }
) {
  const res = await fetch(`${API_BASE}/admin/indicators/${code}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Gagal memperbarui indikator.");
  return res.json();
}

export async function getAdminSettings(token: string): Promise<AdminSettings> {
  const res = await fetch(`${API_BASE}/admin/settings`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Gagal memuat pengaturan sistem.");
  return res.json();
}

export async function updateAdminSettings(token: string, data: Partial<AdminSettings>) {
  const res = await fetch(`${API_BASE}/admin/settings`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Gagal menyimpan pengaturan.");
  return res.json();
}

export async function submitReport(report: {
  analysis_id?: number;
  listing_text: string;
  complaint: string;
}) {
  const res = await fetch(`${API_BASE}/reports`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(report),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Aduan gagal disimpan.");
  return data as { success: boolean; report_id: number; message: string };
}

export async function getAdminReports(token: string): Promise<{ items: AdminReportRecord[]; count: number }> {
  const res = await fetch(`${API_BASE}/admin/reports`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Gagal memuat aduan.");
  return res.json();
}
