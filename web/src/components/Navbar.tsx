"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BookOpen, Sparkles, User, CreditCard, Feather, LayoutDashboard, Download } from "lucide-react";

export function Navbar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 bg-[#f8f9ff]/90 backdrop-blur-md border-b border-[#c6c6cd]/30 px-6 py-3 flex items-center justify-between">
      {/* Brand */}
      <Link href="/dashboard" className="flex items-center gap-3 group">
        <div className="w-9 h-9 rounded bg-[#0b1c30] text-[#f8f5f0] flex items-center justify-center shadow-sm group-hover:bg-[#131b2e] transition-colors">
          <Feather className="w-5 h-5 text-[#ffddb8]" />
        </div>
        <div>
          <span className="font-playfair text-lg font-bold tracking-tight text-[#0b1c30] block leading-none">
            Manuscript Studio
          </span>
          <span className="font-courier text-[10px] text-[#45464d] tracking-widest uppercase block mt-0.5">
            L'Architecte de Récits
          </span>
        </div>
      </Link>

      {/* Main Navigation Tabs */}
      <nav className="flex items-center gap-1 bg-[#eff4ff] p-1 rounded-md border border-[#c6c6cd]/20">
        <Link
          href="/dashboard"
          className={`px-3 py-1.5 rounded text-xs font-semibold flex items-center gap-2 transition-all ${
            pathname === "/dashboard"
              ? "bg-[#0b1c30] text-[#ffffff] shadow-sm"
              : "text-[#45464d] hover:text-[#0b1c30] hover:bg-[#e5eeff]"
          }`}
        >
          <LayoutDashboard className="w-3.5 h-3.5" />
          Mes Livres
        </Link>
        <Link
          href="/studio"
          className={`px-3 py-1.5 rounded text-xs font-semibold flex items-center gap-2 transition-all ${
            pathname.startsWith("/studio") && pathname !== "/studio/export"
              ? "bg-[#0b1c30] text-[#ffffff] shadow-sm"
              : "text-[#45464d] hover:text-[#0b1c30] hover:bg-[#e5eeff]"
          }`}
        >
          <BookOpen className="w-3.5 h-3.5" />
          Atelier
        </Link>
        <Link
          href="/studio/export"
          className={`px-3 py-1.5 rounded text-xs font-semibold flex items-center gap-2 transition-all ${
            pathname === "/studio/export"
              ? "bg-[#0b1c30] text-[#ffffff] shadow-sm"
              : "text-[#45464d] hover:text-[#0b1c30] hover:bg-[#e5eeff]"
          }`}
        >
          <Download className="w-3.5 h-3.5 text-[#b87500]" />
          Exportation
        </Link>
        <Link
          href="/pricing"
          className={`px-3 py-1.5 rounded text-xs font-semibold flex items-center gap-2 transition-all ${
            pathname === "/pricing"
              ? "bg-[#0b1c30] text-[#ffffff] shadow-sm"
              : "text-[#45464d] hover:text-[#0b1c30] hover:bg-[#e5eeff]"
          }`}
        >
          <CreditCard className="w-3.5 h-3.5" />
          Tarification
        </Link>
      </nav>

      {/* Auth / Profile & Status */}
      <div className="flex items-center gap-3">
        <div className="hidden md:flex items-center gap-2 px-2.5 py-1 rounded bg-[#ffddb8]/40 border border-[#b87500]/30 text-[11px] font-mono text-[#2a1700]">
          <span className="w-2 h-2 rounded-full bg-[#b87500] animate-pulse"></span>
          IA Canon: Actif
        </div>
        <Link
          href="/login"
          className="flex items-center gap-2 text-xs font-medium text-[#0b1c30] hover:bg-[#eff4ff] px-3 py-1.5 rounded border border-[#c6c6cd]/40 transition-colors"
        >
          <User className="w-3.5 h-3.5" />
          <span>Connexion</span>
        </Link>
      </div>
    </header>
  );
}
