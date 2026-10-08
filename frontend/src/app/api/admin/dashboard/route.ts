import { proxyBackend } from "@/app/api/_backend";
export async function GET(request: Request) { return proxyBackend("/admin/dashboard", request); }
