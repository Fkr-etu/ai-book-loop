"use client";

import React, { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/Navbar";
import { realApiClient, RealApiError } from "@/services/realApiClient";
import { getApiErrorMessage } from "@/services/apiErrorMessages";
import type { BackendBook, BackendUser } from "@/types/api";
import { ArrowRight, BookOpen, CheckCircle2, Feather, Plus, ShieldCheck, Sparkles, Upload } from "lucide-react";

function errorMessage(error: unknown): string {
  if (error instanceof RealApiError) return getApiErrorMessage(error, error.message);
  return "Impossible de charger vos livres.";
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<BackendUser | null>(null);
  const [books, setBooks] = useState<BackendBook[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    setLoading(true);
    setError(null);
    try {
      const currentUser = await realApiClient.getCurrentUser();
      if (!currentUser) {
        router.replace("/login");
        return;
      }
      setUser(currentUser);
      setBooks(await realApiClient.listBooks());
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void refresh(); }, []);

  const totalChapters = useMemo(() => books.reduce((total, book) => total + book.chapters.length, 0), [books]);

  return (
    <div className="min-h-screen bg-[#f8f5f0] text-[#0f172a] font-inter">
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-6 md:py-10 space-y-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#c6c6cd]/30 pb-6">
          <div>
            <span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider block mb-1 flex items-center gap-1.5"><Feather className="w-4 h-4" /> Espace Auteur</span>
            <h1 className="font-playfair text-2xl md:text-3xl font-bold text-[#0b1c30]">Bibliothèque & Tableau de Bord</h1>
            <p className="text-xs text-[#45464d] mt-1">{user?.name ? `Bonjour ${user.name}. ` : ""}Retrouvez vos œuvres et reprenez votre travail.</p>
          </div>
          <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
            <Link href="/import" className="px-4 py-2.5 border border-[#0b1c30] text-[#0b1c30] font-bold text-xs rounded hover:bg-white transition-colors flex items-center justify-center gap-2 shadow-xs shrink-0"><Upload className="w-4 h-4" /><span>Importer un manuscrit</span></Link>
            <Link href="/setup" className="px-5 py-2.5 bg-[#0b1c30] text-[#ffddb8] font-bold text-xs rounded hover:bg-[#131b2e] transition-colors flex items-center justify-center gap-2 shadow-xs shrink-0"><Plus className="w-4 h-4" /><span>Commencer un livre</span></Link>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-5 bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs"><div className="text-[10px] font-mono text-[#76777d] uppercase font-bold">Livres</div><div className="text-2xl font-bold text-[#0b1c30] font-mono mt-1">{loading ? "—" : books.length}</div><p className="text-[11px] text-[#5f5e5b] mt-1">Projets associés à votre compte</p></div>
          <div className="p-5 bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs"><div className="text-[10px] font-mono text-[#76777d] uppercase font-bold">Chapitres</div><div className="text-2xl font-bold text-[#0b1c30] font-mono mt-1">{loading ? "—" : totalChapters}</div><p className="text-[11px] text-[#5f5e5b] mt-1">À travers vos livres</p></div>
          <div className="p-5 bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs"><div className="text-[10px] font-mono text-[#76777d] uppercase font-bold">Session</div><div className="text-2xl font-bold text-[#0b1c30] font-mono mt-1 flex items-center gap-1.5">Active <ShieldCheck className="w-4 h-4 text-[#b87500]" /></div><p className="text-[11px] text-[#5f5e5b] mt-1">Session protégée par cookie HttpOnly</p></div>
        </div>

        {loading && <div className="bg-white rounded-xl border border-[#c6c6cd]/40 p-8 text-center text-xs text-[#5f5e5b]">Chargement de votre bibliothèque…</div>}
        {!loading && error && <div className="bg-white rounded-xl border border-red-200 p-6 space-y-3" role="alert"><h2 className="font-playfair text-lg font-bold text-[#0b1c30]">Votre bibliothèque n&apos;est pas disponible</h2><p className="text-xs text-[#5f5e5b]">{error}</p><button type="button" onClick={() => void refresh()} className="px-4 py-2 bg-[#0b1c30] text-white rounded text-xs font-semibold">Réessayer</button></div>}
        {!loading && !error && books.length === 0 && <div className="bg-white rounded-xl border border-dashed border-[#c6c6cd] p-10 text-center space-y-4"><BookOpen className="w-8 h-8 mx-auto text-[#b87500]" /><div><h2 className="font-playfair text-xl font-bold text-[#0b1c30]">Votre bibliothèque est vide</h2><p className="text-xs text-[#5f5e5b] mt-1">Commencez par nous parler de votre histoire, ou importez un manuscrit existant.</p></div><div className="flex flex-col sm:flex-row justify-center gap-2"><Link href="/setup" className="inline-flex px-5 py-2.5 bg-[#0b1c30] text-white rounded text-xs font-semibold justify-center">Commencer un livre</Link><Link href="/import" className="inline-flex px-5 py-2.5 border border-[#0b1c30] text-[#0b1c30] rounded text-xs font-semibold justify-center">Importer mon manuscrit</Link></div></div>}
        {!loading && !error && books.length > 0 && (
          <section className="space-y-4"><h2 className="text-xs font-mono font-bold text-[#76777d] uppercase tracking-wider">Vos récits ({books.length})</h2><div className="grid grid-cols-1 gap-4">
            {books.map((book) => { const chapters = book.chapters.length; const approved = book.chapters.filter((chapter) => chapter.status === "approved" || chapter.status === "canonical").length; return (
              <article key={book.id} className="p-5 sm:p-6 bg-white rounded-xl border border-[#c6c6cd]/40 hover:border-[#b87500]/50 transition-all shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="space-y-2 flex-1 min-w-0"><div className="flex flex-wrap items-center gap-2"><span className="text-xs font-mono px-2 py-0.5 rounded bg-[#ffddb8] text-[#2a1700] font-bold">{book.theme || "Projet narratif"}</span>{book.outline_approved && <span className="text-[10px] font-mono bg-[#eff4ff] text-[#0b1c30] px-2 py-0.5 rounded font-bold flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> OUTLINE VALIDÉ</span>}</div><h3 className="font-playfair text-xl md:text-2xl font-bold text-[#0b1c30] truncate">{book.title}</h3><p className="font-courier text-xs text-[#5f5e5b] line-clamp-2">{book.author_idea}</p><div className="pt-2 flex flex-wrap items-center gap-4 text-xs font-mono text-[#45464d]"><span>{chapters} chapitre{chapters > 1 ? "s" : ""}</span><span>{approved} validé{approved > 1 ? "s" : ""}</span><span className="text-[#b87500] font-bold">{book.constraints.length} contrainte{book.constraints.length > 1 ? "s" : ""}</span></div></div>
                <Link href={`/studio?bookId=${encodeURIComponent(book.id)}`} className="w-full sm:w-auto px-5 py-2.5 bg-[#0b1c30] text-white font-semibold text-xs rounded hover:bg-[#131b2e] transition-colors flex items-center justify-center gap-2 shadow-xs shrink-0"><span>Ouvrir l&apos;Atelier</span><ArrowRight className="w-3.5 h-3.5 text-[#ffddb8]" /></Link>
              </article>
            ); })}
          </div></section>
        )}
        <div className="flex items-center gap-2 text-[11px] text-[#76777d] font-mono"><Sparkles className="w-3.5 h-3.5 text-[#b87500]" />Le Canon reste la référence. L&apos;IA propose, vous décidez.</div>
      </main>
    </div>
  );
}
