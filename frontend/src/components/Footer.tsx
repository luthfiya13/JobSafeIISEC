import React from "react";
import Link from "next/link";
import { ShieldCheck, Lock } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-white border-t border-slate-200 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand & Tagline */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center text-white">
                <ShieldCheck className="w-4 h-4 text-blue-400" />
              </div>
              <span className="font-bold text-lg text-slate-900 tracking-tight">
                JOBSAFE
              </span>
            </div>
            <p className="text-slate-600 text-sm italic">
              &ldquo;Kenali risikonya. Verifikasi informasinya.&rdquo;
            </p>
            <p className="text-xs text-slate-500 leading-relaxed max-w-md pt-2">
              Platform independen pendukung pengambilan keputusan cerdas untuk pencari kerja digital, fresh graduate, dan mahasiswa Indonesia.
            </p>
          </div>

          {/* Navigasi Cepat */}
          <div>
            <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-3">
              Navigasi
            </h4>
            <ul className="space-y-2 text-sm text-slate-600">
              <li>
                <Link href="/" className="hover:text-blue-600 transition-colors">
                  Beranda
                </Link>
              </li>
              <li>
                <Link href="/#cara-kerja" className="hover:text-blue-600 transition-colors">
                  Cara Kerja
                </Link>
              </li>
              <li>
                <Link href="/#indikator" className="hover:text-blue-600 transition-colors">
                  10 Indikator Risiko
                </Link>
              </li>
              <li>
                <Link href="/#tentang" className="hover:text-blue-600 transition-colors">
                  Tentang Kami
                </Link>
              </li>
              <li>
                <Link href="/periksa" className="hover:text-blue-600 font-medium text-slate-800 transition-colors">
                  Periksa Lowongan
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal & Admin */}
          <div>
            <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-3">
              Keamanan & Privasi
            </h4>
            <p className="text-xs text-slate-500 leading-relaxed mb-4">
              Tanpa akun &amp; tanpa pelacakan data pribadi pengguna. Analisis berjalan secara anonim dan langsung.
            </p>
            <div className="pt-2 border-t border-slate-100">
              <Link
                href="/admin/login"
                className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-700 transition-colors"
              >
                <Lock className="w-3.5 h-3.5" />
                <span>Portal Admin</span>
              </Link>
            </div>
          </div>
        </div>

        {/* Disclaimer Note */}
        <div className="mt-10 pt-6 border-t border-slate-100">
          <div className="bg-slate-50 rounded-lg p-4 text-center border border-slate-200/60">
            <p className="text-xs text-slate-600 leading-relaxed max-w-4xl mx-auto">
              <strong className="text-slate-700">Disclaimer:</strong> JOBSAFE adalah alat bantu penilaian risiko dan bukan pengganti verifikasi mandiri atau keputusan hukum. Pengguna dianjurkan untuk selalu memeriksa keabsahan pihak perekrut melalui saluran resmi pemerintah dan instansi terkait.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-6 text-xs text-slate-500 text-center sm:text-left">
            <p>&copy; {new Date().getFullYear()} JOBSAFE. Hak cipta dilindungi.</p>
            <p>Dibangun untuk perlindungan pencari kerja digital Indonesia.</p>
          </div>
        </div>
      </div>
    </footer>
  );
}
