"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen,
  User,
  CreditCard,
  Feather,
  LayoutDashboard,
  Download,
  Menu,
  X,
  PanelLeft
} from "lucide-react";

interface NavbarProps {
  onToggleSidebar?: () => void;
  showSidebarToggle?: boolean;
}

export function Navbar({ onToggleSidebar, showSidebarToggle = false }: NavbarProps) {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-[#f8f9ff]/90 backdrop-blur-md border-b border-[#c6c6cd]/30 px-4 md:px-6 py-3 flex items-center justify-between">
      {/* Brand & Studio Sidebar Toggle */}
      <div className="flex items-center gap-2">
        {showSidebarToggle && (
          <button
            onClick={onToggleSidebar}
            className="md:hidden p-2 rounded text-[#0b1c30] hover:bg-[#eff4ff] border border-[#c6c6cd]/40 transition-colors"
            title="Ouvrir le menu du Studio"
            aria-label="Toggle Studio Sidebar"
          >
            <PanelLeft className="w-5 h-5 text-[#0b1c30]" />
          </button>
        )}
        <Link href="/dashboard" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 md:w-9 md:h-9 rounded bg-[#0b1c30] text-[#f8f5f0] flex items-center justify-center shadow-xs group-hover:bg-[#131b2e] transition-colors shrink-0">
            <Feather className="w-4 h-4 md:w-5 md:h-5 text-[#ffddb8]" />
          </div>
          <div>
            <span className="font-playfair text-base md:text-lg font-bold tracking-tight text-[#0b1c30] block leading-none">
              Manuscript Studio
            </span>
            <span className="font-courier text-[9px] md:text-[10px] text-[#45464d] tracking-widest uppercase block mt-0.5">
              L'Architecte de Récits
            </span>
          </div>
        </Link>
      </div>

      {/* Main Navigation Tabs (Desktop) */}
      <nav className="hidden md:flex items-center gap-1 bg-[#eff4ff] p-1 rounded-md border border-[#c6c6cd]/20">
        <Link
          href="/dashboard"
          className={`px-3 py-1.5 rounded text-xs font-semibold flex items-center gap-2 transition-all ${
            pathname === "/dashboard"
              ? "bg-[#0b1c30] text-[#ffffff] shadow-xs"
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
              ? "bg-[#0b1c30] text-[#ffffff] shadow-xs"
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
              ? "bg-[#0b1c30] text-[#ffffff] shadow-xs"
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
              ? "bg-[#0b1c30] text-[#ffffff] shadow-xs"
              : "text-[#45464d] hover:text-[#0b1c30] hover:bg-[#e5eeff]"
          }`}
        >
          <CreditCard className="w-3.5 h-3.5" />
          Tarification
        </Link>
      </nav>

      {/* Auth / Profile & Status (Desktop) */}
      <div className="hidden md:flex items-center gap-3">
        <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-[#ffddb8]/40 border border-[#b87500]/30 text-[11px] font-mono text-[#2a1700]">
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

      {/* Hamburger Toggle Button (Mobile) */}
      <div className="flex items-center md:hidden gap-2">
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-2 rounded text-[#0b1c30] hover:bg-[#eff4ff] border border-[#c6c6cd]/40 transition-colors"
          aria-label="Toggle Menu"
        >
          {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Mobile Navigation Dropdown */}
      {mobileMenuOpen && (
        <div className="absolute top-full left-0 right-0 bg-[#f8f9ff] border-b border-[#c6c6cd]/40 p-4 shadow-lg flex flex-col gap-3 md:hidden z-50">
          <div className="flex items-center justify-between pb-2 border-b border-[#c6c6cd]/20">
            <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-[#ffddb8]/40 border border-[#b87500]/30 text-[11px] font-mono text-[#2a1700]">
              <span className="w-2 h-2 rounded-full bg-[#b87500] animate-pulse"></span>
              IA Canon: Actif
            </div>
            <Link
              href="/login"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-2 text-xs font-medium text-[#0b1c30] bg-[#eff4ff] px-3 py-1.5 rounded border border-[#c6c6cd]/40 transition-colors"
            >
              <User className="w-3.5 h-3.5" />
              <span>Connexion</span>
            </Link>
          </div>

          <nav className="flex flex-col gap-1">
            <Link
              href="/dashboard"
              onClick={() => setMobileMenuOpen(false)}
              className={`px-3 py-2 rounded text-xs font-semibold flex items-center gap-2 transition-all ${
                pathname === "/dashboard"
                  ? "bg-[#0b1c30] text-[#ffffff]"
                  : "text-[#45464d] hover:bg-[#e5eeff]"
              }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              Mes Livres
            </Link>
            <Link
              href="/studio"
              onClick={() => setMobileMenuOpen(false)}
              className={`px-3 py-2 rounded text-xs font-semibold flex items-center gap-2 transition-all ${
                pathname.startsWith("/studio") && pathname !== "/studio/export"
                  ? "bg-[#0b1c30] text-[#ffffff]"
                  : "text-[#45464d] hover:bg-[#e5eeff]"
              }`}
            >
              <BookOpen className="w-4 h-4" />
              Atelier
            </Link>
            <Link
              href="/studio/export"
              onClick={() => setMobileMenuOpen(false)}
              className={`px-3 py-2 rounded text-xs font-semibold flex items-center gap-2 transition-all ${
                pathname === "/studio/export"
                  ? "bg-[#0b1c30] text-[#ffffff]"
                  : "text-[#45464d] hover:bg-[#e5eeff]"
              }`}
            >
              <Download className="w-4 h-4 text-[#b87500]" />
              Exportation
            </Link>
            <Link
              href="/pricing"
              onClick={() => setMobileMenuOpen(false)}
              className={`px-3 py-2 rounded text-xs font-semibold flex items-center gap-2 transition-all ${
                pathname === "/pricing"
                  ? "bg-[#0b1c30] text-[#ffffff]"
                  : "text-[#45464d] hover:bg-[#e5eeff]"
              }`}
            >
              <CreditCard className="w-4 h-4" />
              Tarification
            </Link>
          </nav>
        </div>
      )}
    </header>
  );
}
