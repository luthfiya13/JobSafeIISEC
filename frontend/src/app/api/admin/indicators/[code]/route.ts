import { NextResponse } from "next/server";
import { updateIndicator } from "@/lib/admin-store";

export async function PUT(
  req: Request,
  { params }: { params: Promise<{ code: string }> }
) {
  try {
    const { code } = await params;
    const body = await req.json();
    const weight = Number(body.weight);
    if (
      !Number.isFinite(weight) || weight < 0 || weight > 100 ||
      typeof body.is_active !== "boolean" ||
      typeof body.description !== "string"
    ) {
      return NextResponse.json({ detail: "Bobot, status, atau deskripsi indikator tidak valid." }, { status: 400 });
    }

    const updated = updateIndicator(code, {
      weight,
      is_active: body.is_active,
      description: body.description.trim().slice(0, 1000),
    });
    if (!updated) {
      return NextResponse.json({ detail: "Indikator tidak ditemukan." }, { status: 404 });
    }

    return NextResponse.json({
      success: true,
      message: `Indikator ${code} berhasil diperbarui.`,
      data: updated
    });
  } catch {
    return NextResponse.json({ detail: "Gagal memperbarui indikator." }, { status: 500 });
  }
}
