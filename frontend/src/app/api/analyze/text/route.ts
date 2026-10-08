import { proxyBackend } from "@/app/api/_backend";
export async function POST(request: Request) { return proxyBackend("/analyze/text", request); }
