import { NextResponse } from "next/server";
import { adminIndicators } from "@/lib/admin-store";

export async function GET() {
  const total_weight = adminIndicators.reduce(
    (acc, curr) => acc + (curr.is_active ? curr.weight : 0),
    0
  );

  return NextResponse.json({
    indicators: adminIndicators,
    total_weight,
    is_valid_total: total_weight === 105
  });
}
