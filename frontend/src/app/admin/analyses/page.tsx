"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  Filter,
  Eye,
  X,
  FileText,
  AlertOctagon,
  AlertTriangle,
  ShieldCheck,
  Calendar,
  Layers
} from "lucide-react";
import AdminSidebar from "@/components/AdminSidebar";
import { getAdminAnalyses } from "@/lib/api";

export default function AdminAnalysesPage() {
  const router = useRouter();
  const [items, setItems] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [levelFilter, setLevelFilter] = useState("ALL");
  const [selectedRecord, setSelectedRecord] = useState<any | null>(null);

  const fetchAnalyses = async () => {
    setIsLoading(true);
    const token = typeof window !== "undefined" ? localStorage.getItem("jobsafe_admin_token") : null;
    if (!token) {
      router.push("/admin/login");
      return;
    }

    try {
      const data = await getAdminAnalyses(token, searchQuery, levelFilter);
      setItems(data.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalyses();
  }, [levelFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchAnalyses();
  };

  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-900">
      <AdminSidebar />

      <main className="flex-1 p-6 sm:p-10 max-w-7xl mx-auto overflow-y-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-8 border-b border-slate-200">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Riwayat Analisis
            </h1>
            <p className="text-slate-500 text-xs sm:text-sm mt-1">
              Daftar seluruh pemindaian lowongan kerja yang diproses oleh sistem (Anonim tanpa PII).
            </p>
          </div>
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-slate-200/80 text-slate-700">
            Total {items.length} Entri Ditampilkan
          </span>
        </div>

        {/* Search & Filter Bar */}
        <div className="my-6 flex flex-col sm:flex-row items-center gap-3">
          <form onSubmit={handleSearchSubmit} className="flex-1 w-full relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Cari teks input atau ringkasan..."
              className="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-hidden focus:ring-2 focus:ring-blue-600"
            />
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          </form>

          {/* Level Filter Tabs */}
          <div className="flex items-center gap-1.5 bg-white p-1 rounded-xl border border-slate-200 w-full sm:w-auto">
            {["ALL", "HIGH", "MEDIUM", "LOW"].map((lvl) => (
              <button
                key={lvl}
                type="button"
                onClick={() => setLevelFilter(lvl)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  levelFilter === lvl
                    ? "bg-slate-900 text-white shadow-xs"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                {lvl === "ALL"
                  ? "Semua"
                  : lvl === "HIGH"
                  ? "Tinggi"
                  : lvl === "MEDIUM"
                  ? "Sedang"
                  : "Rendah"}
              </button>
            ))}
          </div>
        </div>

        {/* Table */}
        <div className="clean-card bg-white overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider">
                <tr>
                  <th className="py-3.5 px-4 font-semibold">Tanggal</th>
                  <th className="py-3.5 px-4 font-semibold">Tipe</th>
                  <th className="py-3.5 px-4 font-semibold">Cuplikan Input</th>
                  <th className="py-3.5 px-4 font-semibold text-center">Risk Score</th>
                  <th className="py-3.5 px-4 font-semibold">Level</th>
                  <th className="py-3.5 px-4 font-semibold">Indikator</th>
                  <th className="py-3.5 px-4 font-semibold text-right">Aksi</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-600">
                {isLoading ? (
                  <tr>
                    <td colSpan={7} className="py-12 text-center text-slate-400">
                      Memuat riwayat analisis...
                    </td>
                  </tr>
                ) : items.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-12 text-center text-slate-400">
                      Tidak ada rekaman analisis yang cocok dengan filter.
                    </td>
                  </tr>
                ) : (
                  items.map((row) => (
                    <tr key={row.id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="py-3 px-4 whitespace-nowrap text-slate-400">
                        {row.created_at
                          ? new Date(row.created_at).toLocaleString("id-ID", {
                              day: "2-digit",
                              month: "short",
                              year: "numeric",
                              hour: "2-digit",
                              minute: "2-digit",
                            })
                          : "-"}
                      </td>
                      <td className="py-3 px-4 font-medium uppercase text-slate-500">
                        {row.input_type}
                      </td>
                      <td className="py-3 px-4 max-w-sm truncate text-slate-800 font-medium">
                        {row.input_preview}
                      </td>
                      <td className="py-3 px-4 text-center font-bold text-slate-900">
                        {row.risk_score} / 100
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`inline-block px-2.5 py-0.5 rounded-md font-bold text-[10px] ${
                            row.level_code === "HIGH"
                              ? "bg-red-50 text-red-700 border border-red-200"
                              : row.level_code === "MEDIUM"
                              ? "bg-amber-50 text-amber-700 border border-amber-200"
                              : "bg-emerald-50 text-emerald-700 border border-emerald-200"
                          }`}
                        >
                          {row.risk_level}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-[11px] font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded-md">
                          {row.detected_count} terdeteksi
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          type="button"
                          onClick={() => setSelectedRecord(row)}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold text-blue-600 hover:bg-blue-50 transition-colors"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>Detail</span>
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Record Detail Modal */}
        {selectedRecord && (
          <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
            <div className="fixed inset-0" onClick={() => setSelectedRecord(null)} />
            <div className="relative bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-slate-200 z-10 animate-in fade-in zoom-in-95">
              <button
                type="button"
                onClick={() => setSelectedRecord(null)}
                className="absolute top-4 right-4 p-2 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>

              <div className="flex items-center gap-2 mb-4">
                <span className="text-xs font-bold text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-md">
                  ID #{selectedRecord.id}
                </span>
                <span className="text-xs text-slate-400">
                  {selectedRecord.created_at}
                </span>
              </div>

              <h3 className="text-lg font-bold text-slate-900 mb-2">
                Rincian Analisis
              </h3>

              <div className="space-y-4 text-xs">
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                    Input ({selectedRecord.input_type})
                  </span>
                  <p className="text-slate-800 whitespace-pre-wrap leading-relaxed">
                    {selectedRecord.input_preview}
                  </p>
                </div>

                <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="font-semibold text-slate-700">Risk Score &amp; Level</span>
                  <div className="flex items-center gap-2">
                    <span className="font-extrabold text-base text-slate-900">{selectedRecord.risk_score}/100</span>
                    <span className="font-bold text-[10px] px-2 py-0.5 rounded-md bg-slate-200">
                      {selectedRecord.risk_level}
                    </span>
                  </div>
                </div>

                <div>
                  <span className="font-semibold text-slate-700 block mb-1.5">
                    Indikator yang Terdeteksi:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedRecord.indicators && selectedRecord.indicators.length > 0 ? (
                      selectedRecord.indicators.map((ind: any, i: number) => (
                        <span
                          key={i}
                          className="px-2.5 py-1 rounded-md bg-red-50 text-red-700 border border-red-200 font-semibold text-[11px]"
                        >
                          {ind.code || ind.name}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-400 italic">Tidak ada indikator terpicu.</span>
                    )}
                  </div>
                </div>

                <div className="p-3 bg-blue-50/50 rounded-xl border border-blue-100">
                  <span className="font-semibold text-blue-900 block mb-1">
                    Ringkasan Sistem:
                  </span>
                  <p className="text-slate-700 leading-relaxed">
                    {selectedRecord.summary}
                  </p>
                </div>
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  type="button"
                  onClick={() => setSelectedRecord(null)}
                  className="px-5 py-2 rounded-lg bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800"
                >
                  Tutup
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
