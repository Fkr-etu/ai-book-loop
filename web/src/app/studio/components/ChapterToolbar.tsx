"use client";

import { Sparkles, RotateCcw } from "lucide-react";
import { StudioDecisionState } from "@/components/StudioDecisionState";
import { StudioChapterController } from "../hooks/useStudioChapter";

export function ChapterToolbar({ controller }: { controller: StudioChapterController }) {
  const { chapters, activeChapter, selectedChapterNumber, setSelectedChapterNumber, setSelectedVersionNumber, isWorking, project, wordCount, handleGenerateVersion, handleReview } = controller;
  return (
    <div className="mb-4 flex flex-col gap-3 border-b border-[#c6c6cd]/30 pb-3 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex flex-wrap items-center gap-2 text-xs font-mono text-[#0b1c30]">
        {chapters.length ? (
          <select value={activeChapter?.number ?? ""} onChange={(event) => { const number = Number(event.target.value); setSelectedChapterNumber(number); const chapter = chapters.find((item) => item.number === number); setSelectedVersionNumber(chapter?.currentVersion ?? null); }} className="max-w-[240px] rounded border border-[#c6c6cd] bg-white px-2 py-1 font-bold" aria-label="Sélectionner un chapitre">
            {chapters.map((chapter) => <option key={chapter.id} value={chapter.number}>Chapitre {chapter.number}: {chapter.title}</option>)}
          </select>
        ) : <span className="text-[#76777d]">Aucun chapitre disponible</span>}
        <StudioDecisionState status={activeChapter?.status} />
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-mono text-[#76777d]">{wordCount} mots</span>
        <button type="button" onClick={handleGenerateVersion} disabled={isWorking || !activeChapter || !project.outlineApproved} className="flex items-center gap-1.5 rounded bg-[#0b1c30] px-3 py-1.5 text-xs font-semibold text-[#ffddb8] shadow-xs disabled:opacity-40">
          <Sparkles className={`h-3.5 w-3.5 ${isWorking ? "animate-spin" : ""}`} />
          Écrire une suite
        </button>
        <button type="button" onClick={handleReview} disabled={isWorking || !activeChapter} className="flex items-center gap-1.5 rounded border border-[#c6c6cd]/40 bg-[#eff4ff] px-3 py-1.5 text-xs font-semibold text-[#0b1c30] disabled:opacity-40">
          <RotateCcw className="h-3.5 w-3.5 text-[#b87500]" />
          Relire
        </button>
      </div>
    </div>
  );
}
