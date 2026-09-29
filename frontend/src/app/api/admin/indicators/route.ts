import { NextResponse } from "next/server";
import { DEFAULT_INDICATORS } from "@/lib/analyzer";

let dynamicIndicators = [...DEFAULT_INDICATORS];

export async function GET() {
  const total_weight = dynamicIndicators.reduce(
    (acc, curr) => acc + (curr.is_active ? curr.weight : 0),
    0
  );

  return NextResponse.json({
    indicators: dynamicIndicators,
    total_weight,
    is_valid_total: total_weight === 100
  });
}
