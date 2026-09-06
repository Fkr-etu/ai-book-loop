"use client";

import React, { useState } from "react";
import { StudioLayout } from "@/components/StudioLayout";
import { useProjectStore } from "@/lib/useProjectStore";
import { Check, CheckCircle2, Lock, Plus, Sparkles, Unlock } from "lucide-react";

function chapterStatusLabel(status: string) {
  switch (status) {
    case "approved": return "Approuvé";
    case "needs_review": return "À relire";
    case "in_progress": return "En cours";
    case "rejected": return "Rejeté";
    case "draft": return "Brouillon";
    default: return status;
  }
}

export default function OutlinePage() {
  const store = useProjectStore();
  const project = store.project;
  const chapters = project.chapters ?? [];
  const [newChapterTitle, setNewChapterTitle] = useState("");
  const [newChapterObjective, setNewChapterObjective] = useState("");
  const [isAddingChapter, setIsAddingChapter] = useState(false);

  const handleCreateChapter = async (event: React.FormEvent) => {
    event.preventDefault();
    const title = newChapterTitle.trim();
    if (!title) return;
    await store.addChapter(title, newChapterObjective.trim());
    setNewChapterTitle("");
    setNewChapterObjective("");
    setIsAddingChapter(false);
  };

  return (
    <StudioLayout>
      <main className="p-4 sm:p-6 md:p-10 max-w-5xl mx-auto space-y-6 md:space-y-8">
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#c6c6cd]/30 pb-6">
          <div>
            <span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider block mb-1">Structure narrative</span>
            <h1 className="font-playfair text-2xl sm:text-3xl font-bold text-[#0b1c30]">Plan global</h1>
            <p className="text-xs text-[#45464d] mt-1">L&apos;IA propose le plan. L&apos;auteur décide quand il devient canonique.</p>
          </div>
          <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
            <button type="button" onClick={() => void store.generateOutline()} disabled={store.loading} className="px-3.5 py-2 bg-[#eff4ff] text-[#0b1c30] text-xs font-semibold rounded border border-[#c6c6cd]/40 hover:bg-[#e5eeff] flex items-center justify-center gap-1.5 disabled:opacity-50 flex-1 md:flex-none">
              <Sparkles className="w-3.5 h-3.5 text-[#b87500]" />
              {store.loading ? "Génération…" : "Générer le plan IA"}
            </button>
            {!project.outlineApproved ? (
              <button type="button" onClick={() => void store.approveOutline()} disabled={store.loading || !project.outline} data-testid="approve-outline-btn" className="px-4 py-2 bg-[#b87500] text-white text-xs font-bold rounded hover:bg-[#9a6200] flex items-center justify-center gap-1.5 disabled:opacity-50 flex-1 md:flex-none">
                <Check className="w-4 h-4" /> Approuver le plan
              </button>
            ) : (
              <div className="px-3.5 py-2 bg-[#d3e4fe] text-[#0b1c30] text-xs font-bold rounded flex items-center justify-center gap-1.5 border border-[#0b1c30]/20 flex-1 md:flex-none">
                <CheckCircle2 className="w-4 h-4" /> Plan approuvé
              </div>
            )}
            <button type="button" onClick={() => setIsAddingChapter((value) => !value)} disabled={!project.outlineApproved} data-testid="add-chapter-btn" className="px-4 py-2 bg-[#0b1c30] text-[#ffddb8] text-xs font-bold rounded hover:bg-[#131b2e] flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed w-full sm:w-auto" title={!project.outlineApproved ? "Approuvez le plan avant d'ajouter un chapitre" : undefined}>
              <Plus className="w-4 h-4" /> Nouveau chapitre
            </button>
          </div>
        </header>

        <section data-testid="outline-gate-banner" className={`p-4 border-l-4 border border-[#c6c6cd]/30 rounded-r-lg flex items-start gap-3 ${project.outlineApproved ? "bg-[#eff4ff] border-l-[#0b1c30]" : "bg-[#fff8f0] border-l-[#b87500]"}`}>
          {project.outlineApproved ? <Unlock className="w-5 h-5 text-[#0b1c30] shrink-0 mt-0.5" /> : <Lock className="w-5 h-5 text-[#b87500] shrink-0 mt-0.5" />}
          <div className="space-y-1">
            <h2 className="text-xs font-bold text-[#0b1c30]">{project.outlineApproved ? "Plan canonique approuvé" : "Plan proposé — approbation requise"}</h2>
            <p className="text-xs text-[#45464d]">{project.outlineApproved ? "Le plan persistant du livre peut maintenant être utilisé pour préparer les chapitres." : "Le plan affiché vient de l'état du livre. La génération des chapitres reste verrouillée jusqu'à votre décision explicite."}</p>
          </div>
        </section>

        {project.outline ? (
          <section className="p-4 sm:p-5 bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs space-y-2">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="text-xs font-mono font-bold text-[#0b1c30] uppercase">Plan proposé</h2>
              <span className="text-[10px] text-[#b87500]">{project.outlineApproved ? "Approuvé" : "En attente de décision"}</span>
            </div>
            <pre className="text-xs font-merriweather text-[#0f172a] whitespace-pre-wrap leading-relaxed bg-[#f8f5f0] p-3 sm:p-4 rounded border border-[#c6c6cd]/20 overflow-x-auto">{project.outline}</pre>
          </section>
        ) : (
          <section className="p-6 bg-white rounded-xl border border-dashed border-[#c6c6cd] text-center">
            <h2 className="text-sm font-semibold text-[#0b1c30]">Aucun plan disponible</h2>
            <p className="text-xs text-[#76777d] mt-1">Générez un plan pour obtenir une proposition à examiner.</p>
          </section>
        )}

        {isAddingChapter && project.outlineApproved && (
          <form onSubmit={handleCreateChapter} className="p-4 sm:p-5 bg-white rounded-xl border border-[#b87500]/40 shadow-xs space-y-4">
            <h2 className="text-xs font-mono font-bold text-[#0b1c30] uppercase">Ajouter un chapitre</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <label className="space-y-1"><span className="block text-[11px] font-semibold text-[#45464d]">Titre</span><input type="text" value={newChapterTitle} onChange={(event) => setNewChapterTitle(event.target.value)} required className="w-full px-3 py-2 text-xs border border-[#c6c6cd] rounded bg-[#f8f9ff]" /></label>
              <label className="space-y-1"><span className="block text-[11px] font-semibold text-[#45464d]">Objectif</span><input type="text" value={newChapterObjective} onChange={(event) => setNewChapterObjective(event.target.value)} className="w-full px-3 py-2 text-xs border border-[#c6c6cd] rounded bg-[#f8f9ff]" /></label>
            </div>
            <div className="flex justify-end gap-2">
              <button type="button" onClick={() => setIsAddingChapter(false)} className="px-3 py-1.5 text-xs text-[#45464d] border border-[#c6c6cd] rounded">Annuler</button>
              <button type="submit" disabled={store.loading} className="px-4 py-1.5 text-xs font-bold bg-[#0b1c30] text-white rounded disabled:opacity-50">Créer le chapitre</button>
            </div>
          </form>
        )}

        <section className="space-y-4">
          <div className="flex items-center justify-between"><div><h2 className="font-playfair text-xl font-bold text-[#0b1c30]">Chapitres</h2><p className="text-xs text-[#76777d] mt-1">État persistant retourné par le livre.</p></div><span className="text-xs font-mono text-[#76777d]">{chapters.length} chapitre(s)</span></div>
          {chapters.length === 0 ? (
            <div className="p-6 bg-white rounded-xl border border-dashed border-[#c6c6cd] text-center text-xs text-[#76777d]">Aucun chapitre disponible.</div>
          ) : chapters.map((chapter) => {
            const versionCount = chapter.versions?.length ?? 0;
            const currentVersion = chapter.currentVersion;
            return (
              <article key={chapter.id} className="bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs overflow-hidden">
                <div className="p-4 sm:p-5 bg-[#f8f9ff] border-b border-[#c6c6cd]/20 flex flex-col md:flex-row md:items-center justify-between gap-3">
                  <div className="flex items-start gap-3"><div className="w-8 h-8 rounded bg-[#0b1c30] text-[#ffddb8] font-mono font-bold text-xs flex items-center justify-center shrink-0">{chapter.number}</div><div><div className="flex flex-wrap items-center gap-2"><h3 className="font-playfair text-base sm:text-lg font-bold text-[#0b1c30]">{chapter.title}</h3><span className="text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold bg-[#ffddb8] text-[#2a1700]">{chapterStatusLabel(chapter.status)}</span></div>{(chapter.objective ?? chapter.summary) && <p className="text-xs text-[#45464d] mt-1 font-merriweather">{chapter.objective ?? chapter.summary}</p>}</div></div>
                  <button type="button" onClick={() => void store.generateChapter(chapter.number)} disabled={!project.outlineApproved || store.loading} className="px-3 py-1.5 text-xs font-semibold bg-[#0b1c30] text-white rounded hover:bg-[#131b2e] flex items-center justify-center gap-1 disabled:opacity-40"><Sparkles className="w-3.5 h-3.5 text-[#ffddb8]" />Générer une version</button>
                </div>
                <div className="p-4 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                  <div className="p-3 rounded border border-[#c6c6cd]/30 bg-[#f8f9ff]"><div className="text-[#76777d]">Version courante</div><div className="font-mono font-bold text-[#0b1c30] mt-1">{currentVersion == null ? "—" : `V${currentVersion}`}</div></div>
                  <div className="p-3 rounded border border-[#c6c6cd]/30 bg-[#f8f9ff]"><div className="text-[#76777d]">Versions disponibles</div><div className="font-mono font-bold text-[#0b1c30] mt-1">{versionCount}</div></div>
                  <div className="p-3 rounded border border-[#c6c6cd]/30 bg-[#f8f9ff]"><div className="text-[#76777d]">Décision</div><div className="font-mono font-bold text-[#0b1c30] mt-1">{chapter.status}</div></div>
                </div>
              </article>
            );
          })}
        </section>
      </main>
    </StudioLayout>
  );
}
