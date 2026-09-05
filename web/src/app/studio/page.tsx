"use client";

import React, { useState, useEffect } from "react";
import { StudioLayout } from "@/components/StudioLayout";
import { useProjectStore } from "@/lib/useProjectStore";
import {
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Feather,
  BookOpen,
  RotateCcw,
  Sliders,
  History,
  Info,
  Check,
  X,
  Compass,
  User
} from "lucide-react";
import { CanonicalContextResponse, ChapterVersion } from "@/types";

export default function StudioDeskPage() {
  const store = useProjectStore();
  const project = store.project;

  const chaptersList = project.chapters || [];
  const reviewsList = project.reviews || [];
  const loreList = project.loreItems || [];

  const [activeTab, setActiveTab] = useState<"manuscript" | "history" | "context">("manuscript");
  const [selectedChapterNumber, setSelectedChapterNumber] = useState<number>(1);
  const [canonicalContext, setCanonicalContext] = useState<CanonicalContextResponse | null>(null);

  const activeChapter = chaptersList.find((c) => c.number === selectedChapterNumber) || chaptersList[0];
  const versionsList = activeChapter?.versions || [];

  const [selectedVerNum, setSelectedVerNum] = useState<number>(activeChapter?.currentVersion || 1);

  const activeVersion: ChapterVersion | undefined =
    versionsList.find((v) => v.versionNumber === selectedVerNum) ||
    versionsList[versionsList.length - 1];

  const [editorContent, setEditorContent] = useState(
    activeVersion?.content || activeChapter?.scenes?.[0]?.content || ""
  );
  const [isValidating, setIsValidating] = useState(false);

  useEffect(() => {
    if (activeChapter) {
      const curVer = (activeChapter.versions || []).find((v) => v.versionNumber === selectedVerNum) ||
        (activeChapter.versions || [])[(activeChapter.versions || []).length - 1];
      setEditorContent(curVer?.content || (activeChapter.scenes || [])[0]?.content || "");
    }
  }, [selectedChapterNumber, selectedVerNum, activeChapter]);

  useEffect(() => {
    if (activeChapter) {
      store.getCanonicalContext(activeChapter.number).then((ctx) => {
        setCanonicalContext(ctx);
      }).catch(() => {});
    }
  }, [selectedChapterNumber, activeChapter]);

  const handleGenerateVersion = async () => {
    if (!activeChapter) return;
    setIsValidating(true);
    try {
      await store.generateChapter(activeChapter.number);
      const nextV = (activeChapter.currentVersion || 0) + 1;
      setSelectedVerNum(nextV);
    } catch (err: any) {
      console.error(err);
    } finally {
      setIsValidating(false);
    }
  };

  const handleReviewCurrent = async () => {
    if (!activeChapter) return;
    setIsValidating(true);
    try {
      await store.reviewChapter(activeChapter.number, selectedVerNum, editorContent);
    } catch (err: any) {
      console.error(err);
    } finally {
      setIsValidating(false);
    }
  };

  const handleApproveChapter = async () => {
    if (!activeChapter) return;
    await store.approveChapter(activeChapter.number);
  };

  const handleRejectChapter = async () => {
    if (!activeChapter) return;
    await store.rejectChapter(activeChapter.number);
  };

  const wordCount = editorContent.trim().split(/\s+/).filter(Boolean).length;

  return (
    <StudioLayout>
      <div className="flex flex-col lg:flex-row min-h-[calc(100vh-61px)] lg:h-[calc(100vh-61px)] overflow-y-auto lg:overflow-hidden">
        {/* CENTER WRITING CANVAS (Parchment Desk) */}
        <div className="flex-1 overflow-y-auto bg-[#f8f5f0] p-4 sm:p-6 md:p-10 flex flex-col items-center relative">
          {/* Top Bar for Canvas */}
          <div className="w-full max-w-[760px] mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs border-b border-[#c6c6cd]/30 pb-3">
            <div className="flex flex-wrap items-center gap-2 text-[#0b1c30] font-mono">
              <select
                value={selectedChapterNumber}
                onChange={(e) => {
                  const num = Number(e.target.value);
                  setSelectedChapterNumber(num);
                  const ch = chaptersList.find((c) => c.number === num);
                  if (ch) setSelectedVerNum(ch.currentVersion || 1);
                }}
                className="font-bold text-xs bg-white border border-[#c6c6cd] rounded px-2 py-1 max-w-[200px] truncate"
              >
                {chaptersList.map((ch) => (
                  <option key={ch.id} value={ch.number}>
                    Chapitre {ch.number}: {ch.title}
                  </option>
                ))}
              </select>

              <span
                className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                  activeChapter?.status === "approved"
                    ? "bg-[#d3e4fe] text-[#0b1c30]"
                    : activeChapter?.status === "rejected"
                    ? "bg-[#ffdad6] text-[#ba1a1a]"
                    : "bg-[#ffddb8] text-[#2a1700]"
                }`}
              >
                {activeChapter?.status === "approved" ? "Approuvé (Canon)" : activeChapter?.status || "Brouillon"}
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-[#76777d] text-xs">
                {wordCount} mots
              </span>

              <button
                onClick={handleGenerateVersion}
                disabled={isValidating || !project.outlineApproved}
                className="px-3 py-1.5 rounded bg-[#0b1c30] text-[#ffddb8] font-semibold text-xs flex items-center gap-1.5 hover:bg-[#131b2e] transition-colors shadow-xs disabled:opacity-40 cursor-pointer"
              >
                <Sparkles className={`w-3.5 h-3.5 ${isValidating ? "animate-spin" : ""}`} />
                <span>Générer Nouvelle Version</span>
              </button>

              <button
                onClick={handleReviewCurrent}
                disabled={isValidating}
                className="px-3 py-1.5 rounded bg-[#eff4ff] text-[#0b1c30] border border-[#c6c6cd]/40 font-semibold text-xs flex items-center gap-1.5 hover:bg-[#e5eeff] transition-colors cursor-pointer"
              >
                <RotateCcw className="w-3.5 h-3.5 text-[#b87500]" />
                <span>Critique & Lint</span>
              </button>
            </div>
          </div>

          {/* Workflow Actions Bar */}
          <div className="w-full max-w-[760px] mb-4 p-3 bg-white rounded-lg border border-[#c6c6cd]/30 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-[#76777d]">
                Version courante: <strong>v{selectedVerNum}</strong>
              </span>
              <span className="text-[#c6c6cd] hidden sm:inline">|</span>
              <span className="text-[#45464d]">
                Objectif: <em>{activeChapter?.objective || "Non spécifié"}</em>
              </span>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={handleApproveChapter}
                className="px-3 py-1 bg-[#b87500] text-white font-bold rounded hover:bg-[#9a6200] flex items-center gap-1 text-[11px] cursor-pointer"
              >
                <Check className="w-3.5 h-3.5" /> Approuver (Canon)
              </button>

              <button
                onClick={handleRejectChapter}
                className="px-3 py-1 bg-[#ffdad6] text-[#ba1a1a] font-bold rounded hover:bg-[#ffb4ab] flex items-center gap-1 text-[11px] cursor-pointer"
              >
                <X className="w-3.5 h-3.5" /> Rejeter
              </button>
            </div>
          </div>

          {/* PARCHMENT SHEET */}
          <div className="w-full max-w-[760px] bg-[#f8f5f0] min-h-[450px] sm:min-h-[550px] p-5 sm:p-8 md:p-12 shadow-xs border border-[#c6c6cd]/20 rounded relative flex flex-col">
            <div className="mb-6 pb-4 border-b border-[#c6c6cd]/20">
              <h1 className="font-playfair text-2xl sm:text-3xl font-bold text-[#0f172a] mb-2">
                {activeChapter?.title || "Chapitre Sans Titre"}
              </h1>
              <p className="font-courier text-xs text-[#5f5e5b]">
                {activeChapter?.objective || "Objectif canonique du chapitre..."}
              </p>
            </div>

            {/* Manuscript Editor Area */}
            <textarea
              value={editorContent}
              onChange={(e) => setEditorContent(e.target.value)}
              placeholder="Commencez à écrire votre récit ici ou générez une version avec l'IA..."
              className="w-full flex-1 bg-transparent border-none outline-none font-merriweather text-sm sm:text-base leading-[1.8] text-[#0f172a] resize-none focus:ring-0 selection:bg-[#ffddb8]"
              rows={14}
            />

            {/* Subtle Footer watermark */}
            <div className="mt-8 pt-4 border-t border-[#c6c6cd]/20 flex flex-wrap justify-between items-center text-[11px] font-mono text-[#76777d] gap-2">
              <span>Manuscript Studio — Parchment Canvas</span>
              <span>Canon State: {activeChapter?.status}</span>
            </div>
          </div>
        </div>

        {/* RIGHT PANE: TABBED PANEL (Manuscript Insights / Version History / Context Inspector) */}
        <div className="w-full lg:w-[360px] shrink-0 bg-[#f8f9ff] border-t lg:border-t-0 lg:border-l border-[#c6c6cd]/30 h-auto lg:h-full overflow-y-auto p-4 flex flex-col gap-4">
          {/* Tab Controls */}
          <div className="flex items-center gap-1 bg-[#e5eeff] p-1 rounded-lg border border-[#c6c6cd]/30 text-xs font-mono font-bold text-[#0b1c30]">
            <button
              onClick={() => setActiveTab("manuscript")}
              className={`flex-1 py-1.5 rounded transition-all flex items-center justify-center gap-1 cursor-pointer ${
                activeTab === "manuscript" ? "bg-white shadow-xs text-[#0b1c30]" : "text-[#76777d]"
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-[#b87500]" /> Review
            </button>

            <button
              onClick={() => setActiveTab("history")}
              className={`flex-1 py-1.5 rounded transition-all flex items-center justify-center gap-1 cursor-pointer ${
                activeTab === "history" ? "bg-white shadow-xs text-[#0b1c30]" : "text-[#76777d]"
              }`}
            >
              <History className="w-3.5 h-3.5 text-[#0b1c30]" /> Versions ({versionsList.length})
            </button>

            <button
              onClick={() => setActiveTab("context")}
              className={`flex-1 py-1.5 rounded transition-all flex items-center justify-center gap-1 cursor-pointer ${
                activeTab === "context" ? "bg-white shadow-xs text-[#0b1c30]" : "text-[#76777d]"
              }`}
            >
              <Info className="w-3.5 h-3.5 text-[#b87500]" /> Context
            </button>
          </div>

          {/* TAB 1: MANUSCRIPT REVIEW */}
          {activeTab === "manuscript" && (
            <div className="space-y-4">
              {reviewsList.length > 0 && (
                <div className="p-4 bg-white rounded-xl border border-[#c6c6cd]/30 shadow-xs space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-[#0b1c30] flex items-center gap-1.5">
                      <Sparkles className="w-4 h-4 text-[#b87500]" /> Dernière Évaluation
                    </span>
                    <span className="text-[10px] font-mono text-[#76777d]">
                      {reviewsList[0].timestamp || "À l'instant"}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-center my-2">
                    <div className="p-2 bg-[#f8f9ff] rounded border border-[#c6c6cd]/20">
                      <div className="text-[10px] text-[#45464d]">Score Style</div>
                      <div className="text-sm font-bold text-[#0b1c30]">
                        {reviewsList[0].scoreStyle || reviewsList[0].score || 8}/10
                      </div>
                    </div>
                    <div className="p-2 bg-[#f8f9ff] rounded border border-[#c6c6cd]/20">
                      <div className="text-[10px] text-[#45464d]">Cohérence</div>
                      <div className="text-sm font-bold text-[#0b1c30]">
                        {reviewsList[0].scoreCoherence || reviewsList[0].score || 8}/10
                      </div>
                    </div>
                  </div>

                  {reviewsList[0].critique && (
                    <p className="text-xs text-[#45464d] font-merriweather italic leading-normal">
                      "{reviewsList[0].critique}"
                    </p>
                  )}

                  {(reviewsList[0].issues || []).length > 0 && (
                    <div className="p-2.5 bg-[#ffdad6] text-[#93000a] text-xs rounded space-y-1">
                      <span className="font-bold flex items-center gap-1">
                        <AlertTriangle className="w-3.5 h-3.5" /> Problèmes Détectés:
                      </span>
                      <ul className="list-disc list-inside text-[11px] space-y-0.5">
                        {(reviewsList[0].issues || []).map((iss, i) => (
                          <li key={i}>{iss}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Active Character Focus */}
              <div className="p-4 bg-white rounded-xl border border-[#c6c6cd]/30 space-y-2">
                <span className="text-[11px] font-mono uppercase text-[#76777d] block font-bold">
                  Personnage Canonique Actif
                </span>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-[#0b1c30] text-[#ffddb8] flex items-center justify-center font-bold text-xs">
                    V
                  </div>
                  <div>
                    <div className="text-xs font-bold text-[#0b1c30]">
                      Archiviste Valerius
                    </div>
                    <div className="text-[10px] text-[#45464d]">
                      Protagoniste • Provenance: Auteur
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: VERSION HISTORY */}
          {activeTab === "history" && (
            <div className="space-y-3">
              <span className="text-xs font-mono font-bold text-[#76777d] uppercase tracking-wider block">
                Historique des Versions ({versionsList.length})
              </span>

              {versionsList.length === 0 ? (
                <div className="p-4 bg-white rounded border border-[#c6c6cd]/30 text-xs text-[#76777d] text-center">
                  Aucune version archivée pour ce chapitre. Cliquez sur "Générer Nouvelle Version".
                </div>
              ) : (
                versionsList.map((ver) => {
                  const isSel = ver.versionNumber === selectedVerNum;
                  return (
                    <div
                      key={ver.id || ver.versionNumber}
                      onClick={() => setSelectedVerNum(ver.versionNumber)}
                      className={`p-3.5 rounded-xl border transition-all cursor-pointer space-y-2 ${
                        isSel
                          ? "bg-[#0b1c30] text-white border-[#0b1c30] shadow-xs"
                          : "bg-white text-[#0b1c30] border-[#c6c6cd]/40 hover:bg-[#eff4ff]"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-mono font-bold text-xs">
                          v{ver.versionNumber} — Source: {ver.source}
                        </span>
                        <span
                          className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase ${
                            ver.status === "approved"
                              ? "bg-[#ffddb8] text-[#2a1700]"
                              : ver.status === "rejected"
                              ? "bg-[#ffdad6] text-[#ba1a1a]"
                              : "bg-[#d3e4fe] text-[#0b1c30]"
                          }`}
                        >
                          {ver.status}
                        </span>
                      </div>

                      <p
                        className={`text-xs font-merriweather line-clamp-2 ${
                          isSel ? "text-[#c6c6cd]" : "text-[#5f5e5b]"
                        }`}
                      >
                        {ver.content}
                      </p>

                      {ver.review && (
                        <div
                          className={`text-[11px] font-mono p-1.5 rounded flex items-center justify-between ${
                            isSel ? "bg-white/10 text-[#ffddb8]" : "bg-[#f8f5f0] text-[#b87500]"
                          }`}
                        >
                          <span>Score Linter: {ver.review.score}/10</span>
                          <span>{ver.review.approved ? "Conforme" : "Issues"}</span>
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          )}

          {/* TAB 3: CONTEXT INSPECTOR */}
          {activeTab === "context" && (
            <div className="space-y-3">
              <span className="text-xs font-mono font-bold text-[#76777d] uppercase tracking-wider block">
                Context Inspector — Invariants Canoniques
              </span>

              {canonicalContext ? (
                <div className="space-y-3 text-xs">
                  <div className="p-3 bg-white rounded-lg border border-[#c6c6cd]/30 space-y-1">
                    <span className="font-mono font-bold text-[#0b1c30] flex items-center gap-1">
                      <User className="w-3.5 h-3.5 text-[#b87500]" /> Intention Auteur
                    </span>
                    <p className="font-merriweather text-[#45464d] text-[11px]">
                      {canonicalContext.authorIdea}
                    </p>
                  </div>

                  <div className="p-3 bg-white rounded-lg border border-[#c6c6cd]/30 space-y-1">
                    <span className="font-mono font-bold text-[#0b1c30] flex items-center gap-1">
                      <Compass className="w-3.5 h-3.5 text-[#b87500]" /> Lore & Bible Canonique
                    </span>
                    <p className="font-merriweather text-[#45464d] text-[11px]">
                      {canonicalContext.lore}
                    </p>
                  </div>

                  <div className="p-3 bg-white rounded-lg border border-[#c6c6cd]/30 space-y-1">
                    <span className="font-mono font-bold text-[#0b1c30] flex items-center gap-1">
                      <Sliders className="w-3.5 h-3.5 text-[#b87500]" /> Contraintes Actives
                    </span>
                    <ul className="list-disc list-inside text-[11px] text-[#45464d]">
                      {canonicalContext.constraints.map((c, i) => (
                        <li key={i}>{c}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="p-3 bg-white rounded-lg border border-[#c6c6cd]/30 space-y-1">
                    <span className="font-mono font-bold text-[#0b1c30] flex items-center gap-1">
                      <BookOpen className="w-3.5 h-3.5 text-[#b87500]" /> Résumés Précédents
                    </span>
                    <p className="font-merriweather text-[#45464d] text-[11px] whitespace-pre-wrap">
                      {canonicalContext.previousSummaries || "Aucun chapitre précédent approuvé."}
                    </p>
                  </div>

                  <details className="p-3 bg-white rounded-lg border border-[#c6c6cd]/30 space-y-1 text-[11px] font-mono">
                    <summary className="font-bold text-[#0b1c30] cursor-pointer">
                      Aperçu du Prompt Formaté Envoyé au LLM
                    </summary>
                    <pre className="p-2 bg-[#f8f5f0] rounded text-[#45464d] whitespace-pre-wrap font-mono mt-2 text-[10px]">
                      {canonicalContext.formattedContext}
                    </pre>
                  </details>
                </div>
              ) : (
                <div className="text-xs text-[#76777d]">Chargement du contexte canonique...</div>
              )}
            </div>
          )}
        </div>
      </div>
    </StudioLayout>
  );
}
