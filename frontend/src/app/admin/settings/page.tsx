"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Settings,
  Save,
  AlertTriangle,
  CheckCircle2,
  Sliders,
  ShieldCheck,
  Server
} from "lucide-react";
import AdminSidebar from "@/components/AdminSidebar";
import { getAdminSettings, updateAdminSettings } from "@/lib/api";

export default function AdminSettingsPage() {
  const router = useRouter();
  const [siteName, setSiteName] = useState("JOBSAFE");
  const [thresholdLow, setThresholdLow] = useState(29);
  const [thresholdMed, setThresholdMed] = useState(69);
  const [thresholdHigh, setThresholdHigh] = useState(70);
  const [engineVersion, setEngineVersion] = useState("v2.6-standard");
  const [maintenance, setMaintenance] = useState(false);

  const [isLoading, setIsLoading] = useState(true);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("jobsafe_admin_token") : null;
    if (!token) {
      router.push("/admin/login");
      return;
    }

    const loadSettings = async () => {
      try {
        const data = await getAdminSettings(token);
        if (data.site_name) setSiteName(data.site_name);
        if (data.threshold_low_max) setThresholdLow(Number(data.threshold_low_max));
        if (data.threshold_med_max) setThresholdMed(Number(data.threshold_med_max));
        if (data.threshold_high_min) setThresholdHigh(Number(data.threshold_high_min));
        if (data.analysis_engine_version) setEngineVersion(data.analysis_engine_version);
        if (data.maintenance_mode) setMaintenance(data.maintenance_mode === "true");
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    loadSettings();
  }, [router]);

  const handleConfirmSave = async () => {
    setShowConfirmModal(false);
    const token = typeof window !== "undefined" ? localStorage.getItem("jobsafe_admin_token") : null;
    if (!token) return;

    try {
      await updateAdminSettings(token, {
        site_name: siteName,
        threshold_low_max: thresholdLow,
        threshold_med_max: thresholdMed,
        threshold_high_min: thresholdHigh,
        maintenance_mode: maintenance,
      });

      setSaveSuccessMsg("Pengaturan sistem JOBSAFE berhasil diperbarui.");
      setTimeout(() => setSaveSuccessMsg(null), 4000);
    } catch (err: any) {
      alert(err.message || "Gagal menyimpan pengaturan.");
    }
  };

  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-900">
      <AdminSidebar />

      <main className="flex-1 p-6 sm:p-10 max-w-4xl mx-auto overflow-y-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-8 border-b border-slate-200">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Pengaturan Sistem
            </h1>
            <p className="text-slate-500 text-xs sm:text-sm mt-1">
              Konfigurasi ambang batas risiko (threshold), nama platform, dan parameter mesin analisis.
            </p>
          </div>
        </div>

        {saveSuccessMsg && (
          <div className="my-6 p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>{saveSuccessMsg}</span>
          </div>
        )}

        <div className="mt-8 space-y-6">
          {/* Section 1: Identitas Platform */}
          <div className="clean-card bg-white p-6 space-y-4">
            <h3 className="font-bold text-slate-900 text-sm border-b border-slate-100 pb-2">
              Identitas &amp; Tampilan Platform
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                  Nama Aplikasi / Website
                </label>
                <input
                  type="text"
                  value={siteName}
                  onChange={(e) => setSiteName(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-900 focus:outline-hidden focus:ring-2 focus:ring-blue-600"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                  Versi Mesin Analisis
                </label>
                <input
                  type="text"
                  disabled
                  value={engineVersion}
                  className="w-full p-2.5 bg-slate-100 border border-slate-200 rounded-lg text-xs font-medium text-slate-500"
                />
              </div>
            </div>
          </div>

          {/* Section 2: Threshold Kategori Risiko */}
          <div className="clean-card bg-white p-6 space-y-4">
            <div className="border-b border-slate-100 pb-2">
              <h3 className="font-bold text-slate-900 text-sm">
                Threshold Kategori Risiko
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Nilai rentang batas penilaian untuk menentukan klasifikasi Rendah, Sedang, atau Tinggi.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              <div className="p-3.5 rounded-xl bg-emerald-50/50 border border-emerald-200">
                <span className="font-bold text-emerald-800 block mb-1">
                  Batas Maksimal Risiko Rendah
                </span>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    min={10}
                    max={50}
                    value={thresholdLow}
                    onChange={(e) => setThresholdLow(Number(e.target.value))}
                    className="w-20 p-2 bg-white border border-emerald-300 rounded-lg font-bold text-slate-900 text-center"
                  />
                  <span className="text-emerald-700 font-semibold">(0 – {thresholdLow})</span>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-amber-50/50 border border-amber-200">
                <span className="font-bold text-amber-800 block mb-1">
                  Batas Maksimal Risiko Sedang
                </span>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    min={thresholdLow + 1}
                    max={85}
                    value={thresholdMed}
                    onChange={(e) => setThresholdMed(Number(e.target.value))}
                    className="w-20 p-2 bg-white border border-amber-300 rounded-lg font-bold text-slate-900 text-center"
                  />
                  <span className="text-amber-700 font-semibold">({thresholdLow + 1} – {thresholdMed})</span>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-red-50/50 border border-red-200">
                <span className="font-bold text-red-800 block mb-1">
                  Batas Minimal Risiko Tinggi
                </span>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    min={thresholdMed + 1}
                    max={100}
                    value={thresholdHigh}
                    onChange={(e) => setThresholdHigh(Number(e.target.value))}
                    className="w-20 p-2 bg-white border border-red-300 rounded-lg font-bold text-slate-900 text-center"
                  />
                  <span className="text-red-700 font-semibold">({thresholdHigh} – 100)</span>
                </div>
              </div>
            </div>
          </div>

          {/* Section 3: Save Button */}
          <div className="pt-2 flex justify-end">
            <button
              type="button"
              onClick={() => setShowConfirmModal(true)}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-slate-900 text-white font-semibold text-xs hover:bg-blue-600 transition-colors shadow-xs"
            >
              <Save className="w-4 h-4" />
              <span>Simpan Pengaturan</span>
            </button>
          </div>
        </div>

        {/* Confirmation Modal */}
        {showConfirmModal && (
          <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
            <div className="fixed inset-0" onClick={() => setShowConfirmModal(false)} />
            <div className="relative bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200 z-10 animate-in fade-in zoom-in-95">
              <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center mb-4">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-1.5">
                Konfirmasi Simpan Pengaturan
              </h3>
              <p className="text-xs text-slate-500 leading-relaxed mb-6">
                Apakah Anda yakin ingin memperbarui konfigurasi sistem? Perubahan ambang batas risiko akan mempengaruhi penentuan level analisis berikutnya.
              </p>

              <div className="flex items-center justify-end gap-2.5">
                <button
                  type="button"
                  onClick={() => setShowConfirmModal(false)}
                  className="px-4 py-2 rounded-lg border border-slate-200 text-slate-600 text-xs font-semibold hover:bg-slate-50"
                >
                  Batal
                </button>
                <button
                  type="button"
                  onClick={handleConfirmSave}
                  className="px-5 py-2 rounded-lg bg-blue-600 text-white text-xs font-semibold hover:bg-blue-500 shadow-xs"
                >
                  Ya, Simpan Perubahan
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
