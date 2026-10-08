import { proxyBackend } from "@/app/api/_backend";

export async function PUT(
  req: Request,
  { params }: { params: Promise<{ code: string }> }
) {
  const { code } = await params;
  return proxyBackend(`/admin/indicators/${encodeURIComponent(code)}`, req);
}
