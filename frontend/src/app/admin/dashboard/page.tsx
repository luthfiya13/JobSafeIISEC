"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  AlertOctagon,
  BarChart3,
  PieChart,
  ArrowRight,
  TrendingUp,
  Clock,
  Sparkles
} from "lucide-react";
import AdminSidebar from "@/components/AdminSidebar";
import { getAdminDashboard } from "@/lib/api";

export default function AdminDashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("jobsafe_admin_token") : null;
    if (!token) {
      router.push("/admin/login");
      return;
    }

    const loadData = async () => {
      try {
        const data = await getAdminDashboard(token);
        setStats(data);
      } catch (err: any) {
        setErrorMsg(err.message || "Gagal memuat statistik admin.");
        // If unauthorized, redirect to login
        if (err.message && err.message.includes("tidak valid")) {
          router.push("/admin/login");
        }
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [router]);

  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-900">
      <AdminSidebar />

      <main className="flex-1 p-6 sm:p-10 max-w-7xl mx-auto overflow-y-auto">
        {/* Top Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-8 border-b border-slate-200">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Dashboard Ringkasan
            </h1>
            <p className="text-slate-500 text-xs sm:text-sm mt-1">
              Pemantauan metrik analisis risiko lowongan kerja digital secara berkala.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Sistem Aktif
            </span>
          </div>
        </div>

        {isLoading ? (
          <div className="py-20 text-center text-slate-500 text-sm">
            Memuat data statistik dashboard...
          </div>
        ) : errorMsg ? (
          <div className="py-12 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl my-6 text-sm">
            {errorMsg}
          </div>
        ) : (
          <div className="mt-8 space-y-8">
            {/* 4 SUMMARY STAT CARDS */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
              {/* Total Analisis */}
              <div className="clean-card p-5 bg-white flex flex-col justify-between">
                <div className="flex items-center justify-between text-slate-500 mb-2">
                  <span className="text-xs font-semibold uppercase tracking-wider">
                    Total Analisis
                  </span>
                  <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                    <BarChart3 className="w-4 h-4" />
                  </div>
                </div>
                <div>
                  <span className="text-3xl font-extrabold text-slate-900 tracking-tight">
                    {stats?.total_analyses || 0}
                  </span>
                  <p className="text-[11px] text-slate-400 mt-1">
                    Semua riwayat pemindaian
                  </p>
                </div>
              </div>

              {/* Risiko Rendah */}
              <div className="clean-card p-5 bg-white border-l-4 border-l-emerald-500 flex flex-col justify-between">
                <div className="flex items-center justify-between text-slate-500 mb-2">
                  <span className="text-xs font-semibold uppercase tracking-wider text-emerald-800">
                    Risiko Rendah
                  </span>
                  <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
                    <ShieldCheck className="w-4 h-4" />
                  </div>
                </div>
                <div>
                  <span className="text-3xl font-extrabold text-emerald-700 tracking-tight">
                    {stats?.risk_low || 0}
                  </span>
                  <p className="text-[11px] text-slate-400 mt-1">
                    {stats?.distribution?.low_pct || 0}% dari total
                  </p>
                </div>
              </div>

              {/* Risiko Sedang */}
              <div className="clean-card p-5 bg-white border-l-4 border-l-amber-500 flex flex-col justify-between">
                <div className="flex items-center justify-between text-slate-500 mb-2">
                  <span className="text-xs font-semibold uppercase tracking-wider text-amber-800">
                    Risiko Sedang
                  </span>
                  <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
                    <AlertTriangle className="w-4 h-4" />
                  </div>
                </div>
                <div>
                  <span className="text-3xl font-extrabold text-amber-700 tracking-tight">
                    {stats?.risk_medium || 0}
                  </span>
                  <p className="text-[11px] text-slate-400 mt-1">
                    {stats?.distribution?.med_pct || 0}% dari total
                  </p>
                </div>
              </div>

              {/* Risiko Tinggi */}
              <div className="clean-card p-5 bg-white border-l-4 border-l-red-500 flex flex-col justify-between">
                <div className="flex items-center justify-between text-slate-500 mb-2">
                  <span className="text-xs font-semibold uppercase tracking-wider text-red-800">
                    Risiko Tinggi
                  </span>
                  <div className="w-8 h-8 rounded-lg bg-red-50 text-red-600 flex items-center justify-center">
                    <AlertOctagon className="w-4 h-4" />
                  </div>
                </div>
                <div>
                  <span className="text-3xl font-extrabold text-red-700 tracking-tight">
                    {stats?.risk_high || 0}
                  </span>
                  <p className="text-[11px] text-slate-400 mt-1">
                    {stats?.distribution?.high_pct || 0}% dari total
                  </p>
                </div>
              </div>
            </div>

            {/* 2 CHARTS & ANALYTICS GRIDS */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Distribution Horizontal Bar */}
              <div className="lg:col-span-6 clean-card p-6 bg-white flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
                    <h3 className="font-bold text-slate-900 text-sm">
                      Distribusi Hasil Kategori Risiko
                    </h3>
                    <PieChart className="w-4 h-4 text-slate-400" />
                  </div>

                  {/* Multi-segment Progress Bar */}
                  <div className="h-4 w-full bg-slate-100 rounded-full overflow-hidden flex my-4">
                    <div
                      style={{ width: `${stats?.distribution?.low_pct || 0}%` }}
                      className="bg-emerald-500 h-full transition-all"
                      title={`Rendah: ${stats?.distribution?.low_pct}%`}
                    />
                    <div
                      style={{ width: `${stats?.distribution?.med_pct || 0}%` }}
                      className="bg-amber-500 h-full transition-all"
                      title={`Sedang: ${stats?.distribution?.med_pct}%`}
                    />
                    <div
                      style={{ width: `${stats?.distribution?.high_pct || 0}%` }}
                      className="bg-red-500 h-full transition-all"
                      title={`Tinggi: ${stats?.distribution?.high_pct}%`}
                    />
                  </div>

                  {/* Legend list */}
                  <div className="space-y-2.5 pt-2">
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-emerald-500" />
                        <span className="text-slate-600 font-medium">Risiko Rendah (0–29)</span>
                      </div>
                      <span className="font-bold text-slate-800">
                        {stats?.risk_low} ({stats?.distribution?.low_pct}%)
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-amber-500" />
                        <span className="text-slate-600 font-medium">Risiko Sedang (30–69)</span>
                      </div>
                      <span className="font-bold text-slate-800">
                        {stats?.risk_medium} ({stats?.distribution?.med_pct}%)
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-red-500" />
                        <span className="text-slate-600 font-medium">Risiko Tinggi (70–100)</span>
                      </div>
                      <span className="font-bold text-slate-800">
                        {stats?.risk_high} ({stats?.distribution?.high_pct}%)
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-100 text-[11px] text-slate-400">
                  Data diperbarui otomatis dari log analisis publik.
                </div>
              </div>

              {/* Indikator Paling Sering Terdeteksi */}
              <div className="lg:col-span-6 clean-card p-6 bg-white flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
                    <h3 className="font-bold text-slate-900 text-sm">
                      Indikator Paling Sering Muncul
                    </h3>
                    <TrendingUp className="w-4 h-4 text-slate-400" />
                  </div>

                  <div className="space-y-3">
                    {stats?.top_indicators && stats.top_indicators.length > 0 ? (
                      stats.top_indicators.map((item: any, idx: number) => {
                        const maxCount = stats.top_indicators[0]?.count || 1;
                        const pct = Math.round((item.count / maxCount) * 100);

                        return (
                          <div key={item.code} className="space-y-1">
                            <div className="flex items-center justify-between text-xs">
                              <span className="font-semibold text-slate-700">
                                {item.code}
                              </span>
                              <span className="text-slate-500 text-[11px]">
                                {item.count} kasus
                              </span>
                            </div>
                            <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-blue-600 rounded-full"
                                style={{ width: `${pct}%` }}
                              />
                            </div>
                          </div>
                        );
                      })
                    ) : (
                      <p className="text-xs text-slate-400 py-4 text-center">
                        Belum ada data indikator yang tercatat.
                      </p>
                    )}
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-100">
                  <Link
                    href="/admin/indicators"
                    className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center justify-between"
                  >
                    <span>Kelola bobot dan aturan indikator</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            </div>

            {/* RECENT ANALYSES TABLE PREVIEW */}
            <div className="clean-card bg-white p-6">
              <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
                <div>
                  <h3 className="font-bold text-slate-900 text-base">
                    Analisis Terbaru
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    5 riwayat pemindaian terakhir yang masuk ke dalam sistem
                  </p>
                </div>
                <Link
                  href="/admin/analyses"
                  className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1"
                >
                  <span>Lihat Semua</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-100 text-slate-400 uppercase tracking-wider">
                      <th className="pb-3 font-semibold">Waktu</th>
                      <th className="pb-3 font-semibold">Tipe</th>
                      <th className="pb-3 font-semibold">Cuplikan Input</th>
                      <th className="pb-3 font-semibold text-right">Score</th>
                      <th className="pb-3 font-semibold text-right">Level</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-slate-600">
                    {stats?.recent_analyses?.map((row: any) => (
                      <tr key={row.id} className="hover:bg-slate-50/50">
                        <td className="py-3 text-slate-400 whitespace-nowrap">
                          {row.created_at ? new Date(row.created_at).toLocaleDateString("id-ID", { hour: "2-digit", minute: "2-digit" }) : "-"}
                        </td>
                        <td className="py-3 font-medium uppercase text-slate-500">
                          {row.input_type}
                        </td>
                        <td className="py-3 max-w-xs truncate text-slate-800">
                          {row.input_preview}
                        </td>
                        <td className="py-3 text-right font-bold text-slate-900">
                          {row.risk_score}
                        </td>
                        <td className="py-3 text-right">
                          <span
                            className={`inline-block px-2 py-0.5 rounded-md font-bold text-[10px] ${
                              row.level_code === "HIGH"
                                ? "bg-red-50 text-red-700"
                                : row.level_code === "MEDIUM"
                                ? "bg-amber-50 text-amber-700"
                                : "bg-emerald-50 text-emerald-700"
                            }`}
                          >
                            {row.risk_level}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
