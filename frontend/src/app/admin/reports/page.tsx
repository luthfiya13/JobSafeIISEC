"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import AdminSidebar from "@/components/AdminSidebar";
import { AdminReportRecord, getAdminReports } from "@/lib/api";

export default function AdminReportsPage() {
  const router = useRouter();
  const [items, setItems] = useState<AdminReportRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("jobsafe_admin_token");
    if (!token) {
      router.push("/admin/login");
      return;
    }
    getAdminReports(token)
      .then((data) => setItems(data.items))
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Gagal memuat aduan."))
      .finally(() => setLoading(false));
  }, [router]);

  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-900">
      <AdminSidebar />
      <main className="flex-1 p-6 sm:p-10 max-w-6xl mx-auto overflow-y-auto">
        <header className="pb-6 border-b border-slate-200">
          <h1 className="text-2xl sm:text-3xl font-extrabold">Aduan Pengguna</h1>
          <p className="mt-1 text-sm text-slate-500">Aduan yang dikirim pengguna dan tersimpan untuk ditinjau admin.</p>
        </header>
        {error && <p role="alert" className="mt-5 text-sm text-red-700">{error}</p>}
        {loading ? (
          <p className="mt-8 text-sm text-slate-500">Memuat aduan…</p>
        ) : items.length === 0 ? (
          <div className="mt-8 rounded-xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">Belum ada aduan yang masuk.</div>
        ) : (
          <div className="mt-6 space-y-4">
            {items.map((item) => (
              <article key={item.id} className="rounded-xl border border-slate-200 bg-white p-5">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
                  <h2 className="font-bold">Aduan #{item.id}</h2>
                  <time className="text-xs text-slate-500" dateTime={item.created_at}>{new Date(item.created_at).toLocaleString("id-ID")}</time>
                </div>
                <div className="mt-4 grid gap-4 md:grid-cols-2">
                  <section>
                    <h3 className="mb-1 text-xs font-bold uppercase tracking-wide text-slate-500">Teks lowongan yang dilaporkan</h3>
                    <p className="whitespace-pre-wrap rounded-lg bg-slate-50 p-3 text-sm text-slate-700">{item.listing_preview}</p>
                  </section>
                  <section>
                    <h3 className="mb-1 text-xs font-bold uppercase tracking-wide text-slate-500">Keterangan pengguna</h3>
                    <p className="whitespace-pre-wrap rounded-lg bg-slate-50 p-3 text-sm text-slate-700">{item.complaint}</p>
                  </section>
                </div>
              </article>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
