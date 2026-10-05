import { NextResponse } from "next/server";

let settings = {
  site_name: "JOBSAFE",
  threshold_low_max: "4",
  threshold_med_max: "39",
  threshold_high_min: "40",
  analysis_engine_version: "v2.6-standard",
  maintenance_mode: "false"
};

export async function GET() {
  return NextResponse.json(settings);
}

export async function PUT(req: Request) {
  try {
    const body = await req.json();
    settings = { ...settings, ...body };
    return NextResponse.json({ success: true, message: "Pengaturan berhasil diperbarui.", settings });
  } catch {
    return NextResponse.json({ detail: "Gagal memperbarui pengaturan." }, { status: 500 });
  }
}
