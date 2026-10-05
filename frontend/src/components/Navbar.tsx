"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ShieldAlert, Menu, X, ArrowRight } from "lucide-react";

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 10) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header
      className={`sticky top-0 z-50 transition-all duration-200 ${
        isScrolled
          ? "bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-xs"
          : "bg-white border-b border-slate-100"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-18">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-lg bg-slate-900 flex items-center justify-center text-white shadow-xs group-hover:bg-blue-600 transition-colors">
              <ShieldAlert className="w-5 h-5 text-blue-400 group-hover:text-white transition-colors" />
            </div>
            <div className="flex flex-col">
              <span className="font-extrabold text-xl tracking-tight text-slate-900 leading-none">
                JOBSAFE
              </span>
              <span className="text-[10px] text-slate-500 font-medium tracking-wider uppercase mt-0.5">
                Risk Assessment
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
            <Link
              href="/"
              className="hover:text-slate-900 transition-colors py-1"
            >
              Beranda
            </Link>
            <Link
              href="/#cara-kerja"
              className="hover:text-slate-900 transition-colors py-1"
            >
              Cara Kerja
            </Link>
            <Link
              href="/#indikator"
              className="hover:text-slate-900 transition-colors py-1"
            >
              Indikator Risiko
            </Link>
            <Link
              href="/#tentang"
              className="hover:text-slate-900 transition-colors py-1"
            >
              Tentang
            </Link>
          </nav>

          {/* Right Action Button */}
          <div className="hidden md:flex items-center gap-4">
            <Link
              href="/periksa"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-slate-900 text-white text-sm font-medium hover:bg-blue-600 transition-all shadow-xs hover:shadow-sm active:scale-98"
            >
              <span>Cek Lowongan</span>
              <ArrowRight className="w-4 h-4 text-blue-300" />
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="flex md:hidden">
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
              aria-label="Buka navigasi menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-slate-200 bg-white px-4 pt-3 pb-6 space-y-3 shadow-lg animate-in slide-in-from-top duration-200">
          <div className="flex flex-col space-y-2">
            <Link
              href="/"
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-2 rounded-md text-base font-medium text-slate-800 hover:bg-slate-50"
            >
              Beranda
            </Link>
            <Link
              href="/#cara-kerja"
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-2 rounded-md text-base font-medium text-slate-800 hover:bg-slate-50"
            >
              Cara Kerja
            </Link>
            <Link
              href="/#indikator"
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-2 rounded-md text-base font-medium text-slate-800 hover:bg-slate-50"
            >
              Indikator Risiko
            </Link>
            <Link
              href="/#tentang"
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-2 rounded-md text-base font-medium text-slate-800 hover:bg-slate-50"
            >
              Tentang
            </Link>
          </div>
          <div className="pt-2 border-t border-slate-100">
            <Link
              href="/periksa"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-slate-900 text-white font-medium text-sm hover:bg-blue-600 transition-colors shadow-xs"
            >
              <span>Cek Lowongan Sekarang</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
