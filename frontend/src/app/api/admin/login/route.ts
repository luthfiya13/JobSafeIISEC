import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const email = (body.email || "").trim().toLowerCase();
    const password = body.password || "";

    if (email === "admin@jobsafe.id" && password === "admin123") {
      return NextResponse.json({
        access_token: "mock_jwt_token_jobsafe_admin_" + Date.now(),
        token_type: "bearer",
        admin: {
          id: 1,
          email: "admin@jobsafe.id",
          name: "Administrator JOBSAFE"
        }
      });
    }

    return NextResponse.json(
      { detail: "Email atau kata sandi admin tidak sesuai." },
      { status: 401 }
    );
  } catch (err: any) {
    return NextResponse.json(
      { detail: "Terjadi kesalahan pada server autentikasi." },
      { status: 500 }
    );
  }
}
