"use client";

import Link from "next/link";
import { BookOpen, FileText, Sparkles } from "lucide-react";
import { useProjectStore } from "@/lib/useProjectStore";

export function StudioEmptyState() {
  const { project, loading, generateOutline } = useProjectStore();
  const hasOutline = Boolean(project.outline);
  const outlineApproved = Boolean(project.outlineApproved);

  return (
    <section aria-labelledby="studio-empty-title" className="rounded-xl border border-[#c6c6cd]/40 bg-white p-6 text-center shadow-xs sm:p-10">
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-[#fff1dc] text-[#9a6617]">
        <BookOpen className="h-7 w-7" aria-hidden="true" />
      </div>
      <p className="mt-5 text-xs font-mono font-bold uppercase tracking-wider text-[#b87500]">Votre atelier d’écriture</p>
      <h1 id="studio-empty-title" className="mt-2 font-playfair text-2xl font-bold text-[#0b1c30] sm:text-3xl">Votre histoire est prête à commencer</h1>
      <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-[#5f5e5b]">Vous avez posé les premières bases de votre livre. Choisissez comment faire apparaître votre premier chapitre.</p>

      <div className="mt-8 grid gap-3 text-left sm:grid-cols-3">
        <button type="button" onClick={() => void generateOutline()} disabled={loading} className="rounded-lg border border-[#b87500]/40 bg-[#fff8f0] p-4 transition hover:border-[#b87500] disabled:opacity-50">
          <Sparkles className="h-5 w-5 text-[#b87500]" aria-hidden="true" />
          <h2 className="mt-3 text-sm font-bold text-[#0b1c30]">Être guidé par l’IA</h2>
          <p className="mt-1 text-xs leading-5 text-[#5f5e5b]">Proposer un plan, puis préparer votre premier chapitre.</p>
          <span className="mt-3 block text-xs font-bold text-[#9a6617]">{hasOutline ? "Actualiser le plan" : "Proposer un plan"}</span>
        </button>
        <Link href="/studio/outline" className="rounded-lg border border-[#c6c6cd]/50 bg-[#f8f9ff] p-4 transition hover:border-[#0b1c30]">
          <FileText className="h-5 w-5 text-[#0b1c30]" aria-hidden="true" />
          <h2 className="mt-3 text-sm font-bold text-[#0b1c30]">Construire mon chapitre</h2>
          <p className="mt-1 text-xs leading-5 text-[#5f5e5b]">Choisir un titre, définir le fil conducteur et créer le chapitre.</p>
          <span className="mt-3 block text-xs font-bold text-[#0b1c30]">{outlineApproved ? "Créer un chapitre" : "Ouvrir le plan"}</span>
        </Link>
        <Link href="/studio/lore" className="rounded-lg border border-[#c6c6cd]/50 bg-[#f8f9ff] p-4 transition hover:border-[#0b1c30]">
          <BookOpen className="h-5 w-5 text-[#0b1c30]" aria-hidden="true" />
          <h2 className="mt-3 text-sm font-bold text-[#0b1c30]">Explorer mon univers</h2>
          <p className="mt-1 text-xs leading-5 text-[#5f5e5b]">Revoir les personnages, lieux et éléments qui nourriront le récit.</p>
          <span className="mt-3 block text-xs font-bold text-[#0b1c30]">Explorer l’univers</span>
        </Link>
      </div>
    </section>
  );
}
