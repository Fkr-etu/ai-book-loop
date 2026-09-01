"use client";

import React, { useState } from "react";
import { StudioLayout } from "@/components/StudioLayout";
import { useProjectStore } from "@/lib/useProjectStore";
import {
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Feather,
  BookOpen,
  Save,
  RotateCcw,
  Sliders,
  ChevronRight,
  Bookmark,
  Layers
} from "lucide-react";

export default function StudioDeskPage() {
  const { project, updateSceneContent, runAiValidation } = useProjectStore();

  // Selected chapter and scene
  const [selectedChapterId, setSelectedChapterId] = useState(project.chapters[0]?.id || "");
  const [selectedSceneId, setSelectedSceneId] = useState(
    project.chapters[0]?.scenes[0]?.id || ""
  );

  const activeChapter = project.chapters.find((c) => c.id === selectedChapterId) || project.chapters[0];
  const activeScene =
    activeChapter?.scenes.find((s) => s.id === selectedSceneId) || activeChapter?.scenes[0];

  const [editorContent, setEditorContent] = useState(activeScene?.content || "");
  const [isValidating, setIsValidating] = useState(false);
  const [aiWingOpen, setAiWingOpen] = useState(true);

  // Sync editor content when active scene changes
  React.useEffect(() => {
    if (activeScene) {
      setEditorContent(activeScene.content || "");
    }
  }, [activeScene?.id]);

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setEditorContent(val);
    if (activeChapter && activeScene) {
      updateSceneContent(activeChapter.id, activeScene.id, val);
    }
  };

  const handleTriggerAiReview = async () => {
    if (!activeScene) return;
    setIsValidating(true);
    await runAiValidation(activeScene.id, editorContent);
    setIsValidating(false);
  };

  const wordCount = editorContent.trim().split(/\s+/).filter(Boolean).length;

  return (
    <StudioLayout>
      <div className="flex h-[calc(100vh-61px)] overflow-hidden">
        {/* CENTER WRITING CANVAS (The Parchment Desk) */}
        <div className="flex-1 overflow-y-auto bg-[#f8f5f0] p-6 md:p-10 flex flex-col items-center relative">
          {/* Top Bar for Canvas */}
          <div className="w-full max-w-[720px] mb-6 flex items-center justify-between text-xs border-b border-[#c6c6cd]/30 pb-3">
            <div className="flex items-center gap-2 text-[#0b1c30] font-mono">
              <span className="font-bold">
                Chapitre {activeChapter?.number || 1} • Scène {activeScene?.title || "Nouvelle Scène"}
              </span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                  activeScene?.status === "validated"
                    ? "bg-[#d3e4fe] text-[#0b1c30]"
                    : activeScene?.status === "rejected"
                    ? "bg-[#ffdad6] text-[#ba1a1a]"
                    : "bg-[#ffddb8] text-[#2a1700]"
                }`}
              >
                {activeScene?.status === "validated" ? "Validé Canon" : "En Rédaction"}
              </span>
            </div>

            <div className="flex items-center gap-3">
              <span className="font-mono text-[#76777d]">
                {wordCount} mots
              </span>
              <button
                onClick={handleTriggerAiReview}
                disabled={isValidating}
                className="px-3 py-1.5 rounded bg-[#0b1c30] text-[#ffddb8] font-semibold flex items-center gap-1.5 hover:bg-[#131b2e] transition-colors shadow-xs disabled:opacity-50"
              >
                <Sparkles className={`w-3.5 h-3.5 ${isValidating ? "animate-spin" : ""}`} />
                <span>{isValidating ? "Analyse IA..." : "Critique & Validation IA"}</span>
              </button>
            </div>
          </div>

          {/* PARCHMENT SHEET */}
          <div className="w-full max-w-[720px] bg-[#f8f5f0] min-h-[600px] p-8 md:p-12 shadow-sm border border-[#c6c6cd]/20 rounded relative flex flex-col">
            <div className="mb-6 pb-4 border-b border-[#c6c6cd]/20">
              <h1 className="font-playfair text-3xl font-bold text-[#0f172a] mb-2">
                {activeScene?.title || "Scène Sans Titre"}
              </h1>
              <p className="font-courier text-xs text-[#5f5e5b]">
                {activeScene?.summary || "Aucun résumé renseigné."}
              </p>
            </div>

            {/* Manuscript Editor Area */}
            <textarea
              value={editorContent}
              onChange={handleContentChange}
              placeholder="Commencez à écrire votre récit ici..."
              className="w-full flex-1 bg-transparent border-none outline-none font-merriweather text-lg leading-[1.8] text-[#0f172a] resize-none focus:ring-0 selection:bg-[#ffddb8]"
              rows={16}
            />

            {/* Subtle Footer watermark */}
            <div className="mt-8 pt-4 border-t border-[#c6c6cd]/20 flex justify-between items-center text-[11px] font-mono text-[#76777d]">
              <span>Manuscript Studio — Parchment Canvas</span>
              <span>Enregistré localement</span>
            </div>
          </div>
        </div>

        {/* RIGHT PANE: AI WING (Contextual Lore & Review Insights) */}
        {aiWingOpen && (
          <div className="w-[320px] shrink-0 bg-[#f8f9ff] border-l border-[#c6c6cd]/30 h-full overflow-y-auto p-4 flex flex-col gap-4">
            <div className="flex items-center justify-between pb-2 border-b border-[#c6c6cd]/30">
              <span className="text-xs font-mono font-bold text-[#0b1c30] uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-[#b87500]" /> AI Wing Assistant
              </span>
              <button
                onClick={() => setAiWingOpen(false)}
                className="text-[10px] font-mono text-[#76777d] hover:text-[#0b1c30]"
              >
                Masquer
              </button>
            </div>

            {/* Latest Scene Review Card */}
            {project.reviews.length > 0 && (
              <div className="p-3 bg-white rounded border-l-4 border-l-[#b87500] border border-[#c6c6cd]/30 shadow-xs space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-[#0b1c30]">
                    Dernière Évaluation
                  </span>
                  <span className="text-[10px] font-mono text-[#76777d]">
                    {project.reviews[0].timestamp}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 my-2 text-center">
                  <div className="p-1.5 bg-[#eff4ff] rounded">
                    <div className="text-[10px] text-[#45464d]">Style</div>
                    <div className="text-sm font-bold text-[#0b1c30]">
                      {project.reviews[0].scoreStyle}/10
                    </div>
                  </div>
                  <div className="p-1.5 bg-[#eff4ff] rounded">
                    <div className="text-[10px] text-[#45464d]">Cohérence</div>
                    <div className="text-sm font-bold text-[#0b1c30]">
                      {project.reviews[0].scoreCoherence}/10
                    </div>
                  </div>
                </div>

                <p className="text-xs text-[#45464d] font-merriweather italic leading-normal">
                  "{project.reviews[0].critique}"
                </p>

                {project.reviews[0].forbiddenPatternsFound.length > 0 && (
                  <div className="p-2 bg-[#ffdad6] text-[#93000a] text-[11px] rounded flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                    <span>
                      {project.reviews[0].forbiddenPatternsFound.join(", ")}
                    </span>
                  </div>
                )}
              </div>
            )}

            {/* Active Character Focus */}
            <div className="p-3 bg-white rounded border border-[#c6c6cd]/30 space-y-2">
              <span className="text-[11px] font-mono uppercase text-[#76777d] block font-bold">
                Personnage Présent
              </span>
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-full bg-[#0b1c30] text-[#ffddb8] flex items-center justify-center font-bold text-xs">
                  V
                </div>
                <div>
                  <div className="text-xs font-bold text-[#0b1c30]">
                    Archiviste Valerius
                  </div>
                  <div className="text-[10px] text-[#45464d]">
                    Protagoniste • Obsédé par le Codex
                  </div>
                </div>
              </div>
              <p className="text-[11px] text-[#45464d] bg-[#f8f5f0] p-2 rounded border border-[#c6c6cd]/20">
                <strong>Secret:</strong> A ordonné l'effacement de son propre passé.
              </p>
            </div>

            {/* Lore Connections */}
            <div className="p-3 bg-white rounded border border-[#c6c6cd]/30 space-y-2">
              <span className="text-[11px] font-mono uppercase text-[#76777d] block font-bold">
                Éléments du Lore Liés
              </span>
              <div className="space-y-1.5">
                {project.loreItems.slice(0, 2).map((item) => (
                  <div
                    key={item.id}
                    className="p-2 bg-[#eff4ff] rounded text-xs flex items-center justify-between"
                  >
                    <span className="font-semibold text-[#0b1c30]">
                      {item.title}
                    </span>
                    <span className="text-[10px] text-[#b87500] font-mono font-bold">
                      Canon
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </StudioLayout>
  );
}
