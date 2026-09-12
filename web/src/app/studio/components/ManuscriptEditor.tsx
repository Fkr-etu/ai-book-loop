"use client";

import { Check, X } from "lucide-react";
import { StudioDecisionState } from "@/components/StudioDecisionState";
import { StudioChapterController } from "../hooks/useStudioChapter";
import { CriticalEye } from "./CriticalEye";
import { StudioEmptyState } from "./StudioEmptyState";

export function ManuscriptEditor({ controller }: { controller: StudioChapterController }) {
  const { activeChapter, activeVersion, editorContent, setEditorContent, handleEditorFocus, canDecide, handleApprove, handleReject } = controller;
  if (!activeChapter) return <StudioEmptyState />;

  return (
    <>
      <CriticalEye controller={controller} />
      <section className="mb-4 flex flex-col gap-3 rounded-lg border border-[#c6c6cd]/40 bg-[#fffdfc] p-4 shadow-xs sm:flex-row sm:items-center sm:justify-between" aria-live="polite">
        <div className="min-w-0">
          <p className="font-mono text-xs text-[#506070]">{activeVersion ? `Version v${activeVersion.versionNumber}` : "Aucune version sélectionnée"}</p>
          {activeChapter.objective && <p className="mt-1 text-xs text-[#13243a]">À garder en tête : <em>{activeChapter.objective}</em></p>}
        </div>
        {canDecide && <div className="flex shrink-0 flex-col gap-2 sm:flex-row"><button type="button" onClick={handleApprove} className="flex items-center justify-center gap-1.5 rounded bg-[#9a6617] px-3 py-2 text-[11px] font-bold text-white"><Check className="h-3.5 w-3.5" /> Garder ce passage</button><button type="button" onClick={handleReject} className="flex items-center justify-center gap-1.5 rounded border border-[#d98980] bg-white px-3 py-2 text-[11px] font-bold text-[#a33b32]"><X className="h-3.5 w-3.5" /> Ne pas garder</button></div>}
      </section>
      <section className="min-h-[450px] rounded border border-[#c6c6cd]/20 bg-[#f8f5f0] p-5 shadow-xs sm:p-8 md:p-12">
        <div className="mb-6 border-b border-[#c6c6cd]/20 pb-4"><h1 className="mb-2 font-playfair text-2xl font-bold text-[#0f172a] sm:text-3xl">{activeChapter.title}</h1>{activeChapter.objective && <p className="font-courier text-xs text-[#5f5e5b]">{activeChapter.objective}</p>}</div>
        <textarea value={editorContent} onFocus={handleEditorFocus} onChange={(event) => setEditorContent(event.target.value)} placeholder="Écrivez votre récit ici, puis choisissez la suite qui vous convient." className="min-h-[360px] w-full resize-none border-none bg-transparent font-merriweather text-sm leading-[1.8] text-[#0f172a] outline-none focus:ring-0 sm:text-base" aria-label="Manuscrit du chapitre" />
        <div className="mt-8 flex flex-wrap justify-between gap-2 border-t border-[#c6c6cd]/20 pt-4 text-[11px] font-mono text-[#76777d]"><span>Vous consultez le texte de la version choisie.</span><StudioDecisionState status={activeChapter.status} /></div>
      </section>
    </>
  );
}
