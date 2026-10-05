import { DEFAULT_INDICATORS } from "@/lib/analyzer";

// In-memory demo state. Replace this module with a database-backed store for durable Vercel data.
const globalAdminState = globalThis as typeof globalThis & {
  __jobsafeAdminIndicators?: typeof DEFAULT_INDICATORS;
};

export const adminIndicators =
  globalAdminState.__jobsafeAdminIndicators ??= [...DEFAULT_INDICATORS];

export function updateIndicator(
  code: string,
  data: { weight: number; is_active: boolean; description: string }
) {
  const indicator = adminIndicators.find((item) => item.code === code);
  if (!indicator) return null;

  indicator.weight = data.weight;
  indicator.is_active = data.is_active;
  indicator.description = data.description;
  return indicator;
}
