"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  AlertTriangle,
  CheckCircle2,
  Save,
  Edit2,
  X
} from "lucide-react";
import AdminSidebar from "@/components/AdminSidebar";
import { AdminIndicator, getAdminIndicators, updateAdminIndicator } from "@/lib/api";

export default function AdminIndicatorsPage() {
  const router = useRouter();
  const [indicators, setIndicators] = useState<AdminIndicator[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingItem, setEditingItem] = useState<AdminIndicator | null>(null);
  const [editWeight, setEditWeight] = useState<number>(0);
  const [editActive, setEditActive] = useState<boolean>(true);
  const [editDesc, setEditDesc] = useState<string>("");
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("jobsafe_admin_token");
    if (!token) {
      router.push("/admin/login");
      return;
    }

    let isCurrentRequest = true;
    getAdminIndicators(token)
      .then((data) => {
        if (isCurrentRequest) setIndicators(data.indicators);
      })
      .catch((error: unknown) => {
        if (isCurrentRequest) console.error(error);
      })
      .finally(() => {
        if (isCurrentRequest) setIsLoading(false);
      });

    return () => {
      isCurrentRequest = false;
    };
  }, [router]);

  // Compute live total weight of currently active indicators
  const totalWeight = indicators.reduce((acc, curr) => {
    return acc + (curr.is_active ? Number(curr.weight) : 0);
  }, 0);

  const isWeightValid = totalWeight === 100;

  const handleStartEdit = (ind: AdminIndicator) => {
    setEditingItem(ind);
    setEditWeight(ind.weight);
    setEditActive(ind.is_active);
    setEditDesc(ind.description);
    setSaveSuccessMsg(null);
  };

  const handleSaveEdit = async () => {
    if (!editingItem) return;
    const token = typeof window !== "undefined" ? localStorage.getItem("jobsafe_admin_token") : null;
    if (!token) return;

    try {
      await updateAdminIndicator(token, editingItem.code, {
        weight: Number(editWeight),
        is_active: editActive,
        description: editDesc,
      });

      // Update local state
      setIndicators((prev) =>
        prev.map((item) =>
          item.code === editingItem.code
            ? { ...item, weight: Number(editWeight), is_active: editActive, description: editDesc }
            : item
        )
      );

      setSaveSuccessMsg(`Indikator ${editingItem.code} berhasil diperbarui.`);
      setEditingItem(null);

      setTimeout(() => setSaveSuccessMsg(null), 3500);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Gagal menyimpan perubahan indikator.");
    }
  };

  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-900">
      <AdminSidebar />

      <main className="flex-1 p-6 sm:p-10 max-w-7xl mx-auto overflow-y-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-8 border-b border-slate-200">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Kelola 10 Indikator Risiko
            </h1>
            <p className="text-slate-500 text-xs sm:text-sm mt-1">
              Atur bobot persentase, status aktif/nonaktif, dan deskripsi indikator penipuan digital.
            </p>
          </div>

          {/* Realtime Total Weight Badge with Warning */}
          <div className="flex items-center gap-2">
            <div
              className={`flex items-center gap-2 px-4 py-2 rounded-xl border text-xs font-bold transition-all shadow-xs ${
                isWeightValid
                  ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                  : "bg-red-50 text-red-800 border-red-300 animate-pulse"
              }`}
            >
              {isWeightValid ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-red-600" />
              )}
              <span>Total Bobot Aktif: {totalWeight}%</span>
            </div>
          </div>
        </div>

        {/* Warn when active weights do not form a complete 100% distribution. */}
        {!isWeightValid && (
          <div className="mt-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
            <div>
              <p className="font-bold">Peringatan: Total bobot aktif harus 100% ({totalWeight}% saat ini).</p>
              <p className="mt-0.5 text-red-700">Bobot hard flag tetap dapat memicu eskalasi ke skor 100%, sedangkan bobot indikator lain digunakan dalam perhitungan risiko.</p>
            </div>
          </div>
        )}

        {saveSuccessMsg && (
          <div className="mt-6 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>{saveSuccessMsg}</span>
          </div>
        )}

        {/* Table of Indicators */}
        <div className="mt-8 clean-card bg-white overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider">
                <tr>
                  <th className="py-3.5 px-4 font-semibold">Kode</th>
                  <th className="py-3.5 px-4 font-semibold">Nama Indikator</th>
                  <th className="py-3.5 px-4 font-semibold">Kategori</th>
                  <th className="py-3.5 px-4 font-semibold text-center">Bobot</th>
                  <th className="py-3.5 px-4 font-semibold text-center">Status</th>
                  <th className="py-3.5 px-4 font-semibold">Deskripsi</th>
                  <th className="py-3.5 px-4 font-semibold text-right">Aksi</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-600">
                {isLoading ? (
                  <tr>
                    <td colSpan={7} className="py-12 text-center text-slate-400">
                      Memuat daftar indikator risiko...
                    </td>
                  </tr>
                ) : (
                  indicators.map((ind) => (
                    <tr
                      key={ind.code}
                      className={`hover:bg-slate-50/60 transition-colors ${
                        !ind.is_active ? "opacity-50 bg-slate-50/30" : ""
                      }`}
                    >
                      <td className="py-3.5 px-4 font-extrabold text-slate-900">
                        {ind.code}
                      </td>
                      <td className="py-3.5 px-4 font-bold text-slate-800">
                        {ind.name}
                        <span className={`block mt-1 text-[10px] font-semibold ${ind.hard_flag ? "text-red-700" : "text-blue-700"}`}>
                          {ind.hard_flag ? "Hard Flag · Bypass S" : "Soft Flag · Terbobot"}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 text-[10px] font-semibold">
                          {ind.category || "Umum"}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <span className="font-extrabold text-blue-600 text-sm">
                          {ind.weight}%
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        {ind.is_active ? (
                          <span className="inline-block px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 font-bold text-[10px] border border-emerald-200">
                            Aktif
                          </span>
                        ) : (
                          <span className="inline-block px-2 py-0.5 rounded-md bg-slate-100 text-slate-500 font-bold text-[10px]">
                            Nonaktif
                          </span>
                        )}
                      </td>
                      <td className="py-3.5 px-4 max-w-xs truncate text-slate-500">
                        {ind.description}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          type="button"
                          onClick={() => handleStartEdit(ind)}
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 text-xs font-semibold transition-colors shadow-xs"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                          <span>Ubah</span>
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Edit Modal */}
        {editingItem && (
          <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
            <div className="fixed inset-0" onClick={() => setEditingItem(null)} />
            <div className="relative bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200 z-10 animate-in fade-in zoom-in-95">
              <button
                type="button"
                onClick={() => setEditingItem(null)}
                className="absolute top-4 right-4 p-2 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>

              <div className="flex items-center gap-2 mb-4">
                <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-md border border-blue-100">
                  {editingItem.code}
                </span>
                <h3 className="text-lg font-bold text-slate-900">
                  Ubah {editingItem.name}
                </h3>
              </div>

              <div className="space-y-4 text-xs">
                {/* Bobot */}
                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
                    Bobot Persentase (%)
                  </label>
                  <input
                    type="number"
                    min={1}
                    max={100}
                    value={editWeight}
                    onChange={(e) => setEditWeight(Number(e.target.value))}
                    className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 font-bold focus:outline-hidden focus:ring-2 focus:ring-blue-600"
                  />
                  <span className="text-[11px] text-slate-400 mt-1 block">
                    Bobot awal standar: {editingItem.weight}%
                  </span>
                </div>

                {/* Status Toggle */}
                <div className="pt-2">
                  <label className="flex items-center gap-2.5 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={editActive}
                      onChange={(e) => setEditActive(e.target.checked)}
                      className="w-4 h-4 text-blue-600 rounded-md focus:ring-blue-500"
                    />
                    <span className="font-semibold text-slate-800 text-xs">
                      Aktifkan Indikator ini dalam Analisis
                    </span>
                  </label>
                </div>

                {/* Deskripsi */}
                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
                    Deskripsi Indikator
                  </label>
                  <textarea
                    rows={3}
                    value={editDesc}
                    onChange={(e) => setEditDesc(e.target.value)}
                    className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-900 leading-relaxed focus:outline-hidden focus:ring-2 focus:ring-blue-600"
                  />
                </div>
              </div>

              <div className="mt-6 flex items-center justify-end gap-2.5">
                <button
                  type="button"
                  onClick={() => setEditingItem(null)}
                  className="px-4 py-2 rounded-lg border border-slate-200 text-slate-600 text-xs font-semibold hover:bg-slate-50"
                >
                  Batal
                </button>
                <button
                  type="button"
                  onClick={handleSaveEdit}
                  className="px-5 py-2 rounded-lg bg-blue-600 text-white text-xs font-semibold hover:bg-blue-500 flex items-center gap-1.5 shadow-xs"
                >
                  <Save className="w-3.5 h-3.5" />
                  <span>Simpan Perubahan</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
