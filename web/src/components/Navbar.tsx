"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ArrowRight, BookOpen, CreditCard, Download, LayoutDashboard, Menu, PanelLeft, X } from "lucide-react";
import { getApiClient } from "@/services/api";

interface NavbarProps {
  onToggleSidebar?: () => void;
  showSidebarToggle?: boolean;
}

const PUBLIC_ROUTES = ["/", "/login", "/register", "/pricing"];

function isPublicRoute(pathname: string): boolean {
  return PUBLIC_ROUTES.includes(pathname);
}

export function Navbar({ onToggleSidebar, showSidebarToggle = false }: NavbarProps) {
  const pathname = usePathname();
  const publicRoute = isPublicRoute(pathname);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (pathname !== "/pricing") {
      setAuthenticated(null);
      return;
    }
    let active = true;
    void getApiClient().getCurrentUser().then((user) => {
      if (active) setAuthenticated(Boolean(user));
    }).catch(() => {
      if (active) setAuthenticated(false);
    });
    return () => { active = false; };
  }, [pathname]);

  const showAppNavigation = !publicRoute || (pathname === "/pricing" && authenticated === true);
  const logoHref = showAppNavigation ? "/dashboard" : "/";
  const logoLabel = showAppNavigation ? "Book Loop — mes livres" : "Book Loop — accueil";

  const appNav = (
    <>
      <Link href="/dashboard" onClick={() => setMobileMenuOpen(false)} className={`px-3 py-1.5 rounded text-xs font-semibold flex items-center gap-2 transition-all ${pathname === "/dashboard" ? "bg-[#0b1c30] text-white shadow-xs" : "text-[#45464d] hover:text-[#0b1c30] hover:bg-[#e5eeff]"}`}>
        <LayoutDashboard className="w-3.5 h-3.5" /> Mes livres
      </Link>
      <Link href="/studio" onClick={() => setMobileMenuOpen(false)} className={`px-3 py-1.5 rounded text-xs font-semibold flex items-center gap-2 transition-all ${pathname.startsWith("/studio") && pathname !== "/studio/export" ? "bg-[#0b1c30] text-white shadow-xs" : "text-[#45464d] hover:text-[#0b1c30] hover:bg-[#e5eeff]"}`}>
        <BookOpen className="w-3.5 h-3.5" /> Atelier
      </Link>
      <Link href="/studio/export" onClick={() => setMobileMenuOpen(false)} className={`px-3 py-1.5 rounded text-xs font-semibold flex items-center gap-2 transition-all ${pathname === "/studio/export" ? "bg-[#0b1c30] text-white shadow-xs" : "text-[#45464d] hover:text-[#0b1c30] hover:bg-[#e5eeff]"}`}>
        <Download className="w-3.5 h-3.5 text-[#b87500]" /> Exportation
      </Link>
      <Link href="/pricing" onClick={() => setMobileMenuOpen(false)} className={`px-3 py-1.5 rounded text-xs font-semibold flex items-center gap-2 transition-all ${pathname === "/pricing" ? "bg-[#0b1c30] text-white shadow-xs" : "text-[#45464d] hover:text-[#0b1c30] hover:bg-[#e5eeff]"}`}>
        <CreditCard className="w-3.5 h-3.5" /> Tarification
      </Link>
    </>
  );

  return (
    <header className="sticky top-0 z-50 bg-[#f8f9ff]/90 backdrop-blur-md border-b border-[#c6c6cd]/30 px-4 md:px-6 py-3">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-2 min-w-0">
          {showSidebarToggle && (
            <button onClick={onToggleSidebar} className="md:hidden p-2 rounded text-[#0b1c30] hover:bg-[#eff4ff] border border-[#c6c6cd]/40 transition-colors" title="Ouvrir le menu du Studio" aria-label="Ouvrir la navigation du Studio">
              <PanelLeft className="w-5 h-5 text-[#0b1c30]" />
            </button>
          )}
          <Link href={logoHref} className="flex items-center min-w-0 group" aria-label={logoLabel}>
            <Image
              src="/brand/lockup-horizontal.svg"
              alt="Book Loop"
              width={560}
              height={170}
              priority
              className="h-9 w-auto md:h-10 max-w-[145px] md:max-w-[170px] transition-opacity group-hover:opacity-80"
            />
          </Link>
        </div>

        <nav className="hidden md:flex items-center gap-1 bg-[#eff4ff] p-1 rounded-md border border-[#c6c6cd]/20" aria-label="Navigation principale">
          {showAppNavigation ? appNav : <><Link href="/#la-boucle" className="px-3 py-1.5 rounded text-xs font-semibold text-[#45464d] hover:text-[#0b1c30] hover:bg-[#e5eeff] transition-all">Fonctionnement</Link><Link href="/pricing" className={`px-3 py-1.5 rounded text-xs font-semibold transition-all ${pathname === "/pricing" ? "bg-[#0b1c30] text-white shadow-xs" : "text-[#45464d] hover:text-[#0b1c30] hover:bg-[#e5eeff]"}`}>Tarification</Link></>}
        </nav>

        <div className="hidden md:flex items-center gap-2 shrink-0">
          {showAppNavigation ? <Link href="/account" className={`flex items-center gap-2 text-xs font-medium px-3 py-1.5 rounded border transition-colors ${pathname === "/account" ? "border-[#0b1c30] bg-[#0b1c30] text-white" : "border-[#c6c6cd]/40 text-[#0b1c30] hover:bg-[#eff4ff]"}`}>Compte</Link> : <><Link href="/login" className="px-3 py-1.5 rounded text-xs font-semibold text-[#0b1c30] hover:bg-[#eff4ff] transition-colors">Se connecter</Link><Link href="/register" className="flex items-center gap-1.5 px-3.5 py-2 rounded-md bg-[#0b1c30] text-white text-xs font-semibold hover:bg-[#203b5b] transition-colors shadow-xs">Commencer <ArrowRight className="w-3.5 h-3.5" /></Link></>}
        </div>

        <div className="flex items-center md:hidden gap-2 shrink-0"><button onClick={() => setMobileMenuOpen((open) => !open)} className="p-2 rounded text-[#0b1c30] hover:bg-[#eff4ff] border border-[#c6c6cd]/40 transition-colors" aria-label={mobileMenuOpen ? "Fermer le menu" : "Ouvrir le menu"} aria-expanded={mobileMenuOpen}>{mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}</button></div>
      </div>

      {mobileMenuOpen && (
        <div className="absolute top-full left-0 right-0 bg-[#f8f9ff] border-b border-[#c6c6cd]/40 p-4 shadow-lg flex flex-col gap-3 md:hidden z-50">
          {showAppNavigation ? <><nav className="flex flex-col gap-1" aria-label="Navigation de l'espace auteur">{appNav}</nav><div className="border-t border-[#c6c6cd]/20 pt-3 mt-2"><Link href="/account" onClick={() => setMobileMenuOpen(false)} className={`px-3 py-2 rounded text-sm font-semibold flex items-center gap-2 ${pathname === "/account" ? "bg-[#0b1c30] text-white" : "text-[#45464d] hover:bg-[#e5eeff]"}`}>Compte</Link></div></> : <nav className="flex flex-col gap-1" aria-label="Navigation publique"><Link href="/#la-boucle" onClick={() => setMobileMenuOpen(false)} className="px-3 py-2 rounded text-sm font-semibold text-[#45464d] hover:bg-[#e5eeff]">Fonctionnement</Link><Link href="/pricing" onClick={() => setMobileMenuOpen(false)} className="px-3 py-2 rounded text-sm font-semibold text-[#45464d] hover:bg-[#e5eeff]">Tarification</Link><div className="border-t border-[#c6c6cd]/20 pt-3 mt-2 flex flex-col gap-2"><Link href="/login" onClick={() => setMobileMenuOpen(false)} className="px-3 py-2 rounded text-sm font-semibold text-[#0b1c30] border border-[#c6c6cd]/40 text-center">Se connecter</Link><Link href="/register" onClick={() => setMobileMenuOpen(false)} className="px-3 py-2.5 rounded-md bg-[#0b1c30] text-white text-sm font-semibold text-center flex items-center justify-center gap-2">Commencer <ArrowRight className="w-4 h-4" /></Link></div></nav>}
        </div>
      )}
    </header>
  );
}
