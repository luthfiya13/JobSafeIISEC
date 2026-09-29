import { NextResponse } from "next/server";
import { DEFAULT_INDICATORS } from "@/lib/analyzer";

export async function GET() {
  return NextResponse.json(
    DEFAULT_INDICATORS.map((i) => ({
      code: i.code,
      name: i.name,
      category: i.category,
      weight: i.weight,
      description: i.description,
      why_important: i.why_important
    }))
  );
}
