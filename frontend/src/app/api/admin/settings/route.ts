import { proxyBackend } from "@/app/api/_backend";
export async function GET(request: Request) { return proxyBackend("/admin/settings", request); }
export async function PUT(request: Request) { return proxyBackend("/admin/settings", request); }
