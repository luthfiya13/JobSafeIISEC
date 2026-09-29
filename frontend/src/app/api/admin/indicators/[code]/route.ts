import { NextResponse } from "next/server";

export async function PUT(
  req: Request,
  { params }: { params: Promise<{ code: string }> }
) {
  try {
    const { code } = await params;
    const body = await req.json();

    return NextResponse.json({
      success: true,
      message: `Indikator ${code} berhasil diperbarui.`,
      data: body
    });
  } catch (err: any) {
    return NextResponse.json({ detail: "Gagal memperbarui indikator." }, { status: 500 });
  }
}
