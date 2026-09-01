"use client";

import React, { useState } from "react";
import { StudioLayout } from "@/components/StudioLayout";
import { useProjectStore } from "@/lib/useProjectStore";
import {
  ListOrdered,
  Plus,
  CheckCircle2,
  Clock,
  Sparkles,
  FileText,
  AlertTriangle,
  Lock,
  Unlock,
  Check
} from "lucide-react";

export default function OutlinePage() {
  const store = useProjectStore();
  const project = store.project;

  const [newChapterTitle, setNewChapterTitle] = useState("");
  const [newChapterSummary, setNewChapterSummary] = useState("");
  const [isAddingChapter, setIsAddingChapter] = useState(false);

  const [activeChapterForScene, setActiveChapterForScene] = useState<string | null>(null);
  const [newSceneTitle, setNewSceneTitle] = useState("");
  const [newSceneSummary, setNewSceneSummary] = useState("");

  const handleCreateChapter = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newChapterTitle.trim()) return;
    store.addChapter(newChapterTitle, newChapterSummary);
    setNewChapterTitle("");
    setNewChapterSummary("");
    setIsAddingChapter(false);
  };

  const handleCreateScene = (chapterId: string) => {
    if (!newSceneTitle.trim()) return;
    if (store.addScene) {
      store.addScene(chapterId, newSceneTitle, newSceneSummary);
    }
    setNewSceneTitle("");
    setNewSceneSummary("");
    setActiveChapterForScene(null);
  };

  const chaptersList = project.chapters || [];

  return (
    <StudioLayout>
      <div className="p-6 md:p-10 max-w-5xl mx-auto space-y-8">
        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#c6c6cd]/30 pb-6">
          <div>
            <span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider block mb-1">
              Structure Narrative & Canon
            </span>
            <h1 className="font-playfair text-3xl font-bold text-[#0b1c30]">
              Éditeur de Plan Global
            </h1>
            <p className="text-xs text-[#45464d] mt-1">
              L'IA propose le plan. Vous devez l'approuver avant de commencer la génération des chapitres.
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => store.generateOutline()}
              disabled={store.loading}
              className="px-3.5 py-2 bg-[#eff4ff] text-[#0b1c30] text-xs font-semibold rounded border border-[#c6c6cd]/40 hover:bg-[#e5eeff] flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
            >
              <Sparkles className="w-3.5 h-3.5 text-[#b87500]" />
              <span>{store.loading ? "Génération..." : "Générer le plan IA"}</span>
            </button>

            {!project.outlineApproved ? (
              <button
                onClick={() => store.approveOutline()}
                disabled={store.loading || !project.outline}
                data-testid="approve-outline-btn"
                className="px-4 py-2 bg-[#b87500] text-white text-xs font-bold rounded hover:bg-[#9a6200] transition-colors flex items-center gap-1.5 shadow-xs cursor-pointer disabled:opacity-50"
              >
                <Check className="w-4 h-4" />
                <span>Approuver le plan</span>
              </button>
            ) : (
              <div className="px-3.5 py-2 bg-[#d3e4fe] text-[#0b1c30] text-xs font-bold rounded flex items-center gap-1.5 border border-[#0b1c30]/20">
                <CheckCircle2 className="w-4 h-4 text-[#0b1c30]" />
                <span>Plan Approuvé par l'Auteur</span>
              </div>
            )}

            <button
              onClick={() => setIsAddingChapter(!isAddingChapter)}
              disabled={!project.outlineApproved}
              title={
                !project.outlineApproved
                  ? "L'outline doit être approuvé avant d'ajouter des chapitres"
                  : ""
              }
              data-testid="add-chapter-btn"
              className="px-4 py-2 bg-[#0b1c30] text-[#ffddb8] text-xs font-bold rounded hover:bg-[#131b2e] transition-colors flex items-center gap-2 shadow-xs cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <Plus className="w-4 h-4" />
              <span>Nouveau Chapitre</span>
            </button>
          </div>
        </div>

        {/* Outline Approval Gate Warning Banner */}
        {!project.outlineApproved ? (
          <div
            data-testid="outline-gate-banner"
            className="p-4 bg-[#fff8f0] border-l-4 border-[#b87500] border border-[#c6c6cd]/30 rounded-r-lg flex items-start gap-3"
          >
            <Lock className="w-5 h-5 text-[#b87500] shrink-0 mt-0.5" />
            <div className="space-y-1">
              <h3 className="text-xs font-bold text-[#2a1700]">
                Outline proposé — Approbation requise
              </h3>
              <p className="text-xs text-[#5f5e5b]">
                L'IA propose le plan ci-dessous. Vous devez l'approuver avant de commencer la génération des chapitres. La création et la génération de chapitres restent verrouillées jusqu'à votre approbation explicite.
              </p>
            </div>
          </div>
        ) : (
          <div className="p-4 bg-[#eff4ff] border-l-4 border-[#0b1c30] border border-[#c6c6cd]/30 rounded-r-lg flex items-start gap-3">
            <Unlock className="w-5 h-5 text-[#0b1c30] shrink-0 mt-0.5" />
            <div>
              <h3 className="text-xs font-bold text-[#0b1c30]">
                Plan Canonique Approuvé
              </h3>
              <p className="text-xs text-[#45464d]">
                Le plan a été validé par l'auteur. Les chapitres et scènes peuvent être librement ajoutés et générés par l'IA.
              </p>
            </div>
          </div>
        )}

        {/* Outline Raw Text Preview */}
        {project.outline && (
          <div className="p-5 bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs space-y-2">
            <div className="text-xs font-mono font-bold text-[#0b1c30] uppercase flex items-center justify-between">
              <span>Aperçu du Plan Global Proposé</span>
              <span className="text-[10px] text-[#b87500]">
                {project.outlineApproved ? "Statut: Approuvé" : "Statut: En Attente d'Approbation"}
              </span>
            </div>
            <pre className="text-xs font-merriweather text-[#0f172a] whitespace-pre-wrap leading-relaxed bg-[#f8f5f0] p-4 rounded border border-[#c6c6cd]/20">
              {project.outline}
            </pre>
          </div>
        )}

        {/* Add Chapter Form */}
        {isAddingChapter && project.outlineApproved && (
          <form
            onSubmit={handleCreateChapter}
            className="p-5 bg-white rounded-xl border border-[#b87500]/40 shadow-sm space-y-4 animate-fadeIn"
          >
            <h3 className="text-xs font-mono font-bold text-[#0b1c30] uppercase">
              Ajouter un Chapitre au Plan
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <input
                type="text"
                placeholder="Titre du Chapitre (ex: Le Scriptorium Oublié)"
                value={newChapterTitle}
                onChange={(e) => setNewChapterTitle(e.target.value)}
                required
                className="px-3 py-2 text-xs border border-[#c6c6cd] rounded bg-[#f8f9ff]"
              />
              <input
                type="text"
                placeholder="Objectif dramatique du chapitre..."
                value={newChapterSummary}
                onChange={(e) => setNewChapterSummary(e.target.value)}
                className="px-3 py-2 text-xs border border-[#c6c6cd] rounded bg-[#f8f9ff]"
              />
            </div>
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setIsAddingChapter(false)}
                className="px-3 py-1.5 text-xs text-[#45464d] border border-[#c6c6cd] rounded hover:bg-[#eff4ff]"
              >
                Annuler
              </button>
              <button
                type="submit"
                className="px-4 py-1.5 text-xs font-bold bg-[#0b1c30] text-white rounded hover:bg-[#131b2e]"
              >
                Créer le Chapitre
              </button>
            </div>
          </form>
        )}

        {/* CHAPTERS LIST */}
        <div className="space-y-6">
          {chaptersList.map((chapter) => (
            <div
              key={chapter.id}
              className="bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs overflow-hidden"
            >
              {/* Chapter Card Header */}
              <div className="p-5 bg-[#f8f9ff] border-b border-[#c6c6cd]/20 flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded bg-[#0b1c30] text-[#ffddb8] font-mono font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
                    {chapter.number}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="font-playfair text-lg font-bold text-[#0b1c30]">
                        {chapter.title}
                      </h2>
                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold ${
                          chapter.status === "approved"
                            ? "bg-[#d3e4fe] text-[#0b1c30]"
                            : "bg-[#ffddb8] text-[#2a1700]"
                        }`}
                      >
                        {chapter.status === "approved" ? "Approuvé pour Génération" : chapter.status}
                      </span>
                    </div>
                    <p className="text-xs text-[#45464d] mt-1 font-merriweather">
                      Objectif: {chapter.objective || chapter.summary || "Non défini"}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => store.generateChapter(chapter.number)}
                    disabled={!project.outlineApproved || store.loading}
                    className="px-3 py-1.5 text-xs font-semibold bg-[#0b1c30] text-white rounded hover:bg-[#131b2e] flex items-center gap-1 disabled:opacity-40"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-[#ffddb8]" />
                    <span>Générer V{(chapter.currentVersion || 0) + 1}</span>
                  </button>

                  <button
                    onClick={() =>
                      setActiveChapterForScene(
                        activeChapterForScene === chapter.id ? null : chapter.id
                      )
                    }
                    disabled={!project.outlineApproved}
                    className="px-3 py-1.5 text-xs font-semibold bg-[#eff4ff] text-[#0b1c30] rounded border border-[#c6c6cd]/30 hover:bg-[#e5eeff] flex items-center gap-1 disabled:opacity-40"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Ajouter une Scène</span>
                  </button>
                </div>
              </div>

              {/* Form to add scene under this chapter */}
              {activeChapterForScene === chapter.id && project.outlineApproved && (
                <div className="p-4 bg-[#f8f5f0] border-b border-[#c6c6cd]/30 space-y-3">
                  <div className="text-xs font-mono font-bold text-[#0b1c30]">
                    Nouvelle Scène pour le Chapitre {chapter.number}
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    <input
                      type="text"
                      placeholder="Titre de la scène..."
                      value={newSceneTitle}
                      onChange={(e) => setNewSceneTitle(e.target.value)}
                      className="px-3 py-1.5 text-xs border border-[#c6c6cd] rounded bg-white"
                    />
                    <input
                      type="text"
                      placeholder="Objectif de la scène..."
                      value={newSceneSummary}
                      onChange={(e) => setNewSceneSummary(e.target.value)}
                      className="px-3 py-1.5 text-xs border border-[#c6c6cd] rounded bg-white"
                    />
                  </div>
                  <div className="flex justify-end gap-2">
                    <button
                      type="button"
                      onClick={() => setActiveChapterForScene(null)}
                      className="px-3 py-1 text-xs text-[#45464d]"
                    >
                      Annuler
                    </button>
                    <button
                      type="button"
                      onClick={() => handleCreateScene(chapter.id)}
                      className="px-3 py-1 text-xs font-bold bg-[#0b1c30] text-white rounded"
                    >
                      Ajouter
                    </button>
                  </div>
                </div>
              )}

              {/* Scenes Cards Inside Chapter */}
              <div className="p-4 divide-y divide-[#c6c6cd]/20">
                {(chapter.scenes || []).length === 0 ? (
                  <div className="text-center py-6 text-xs text-[#76777d]">
                    {(chapter.versions || []).length > 0
                      ? `${(chapter.versions || []).length} version(s) générée(s) par l'IA pour ce chapitre.`
                      : 'Aucune scène créée pour ce chapitre. Cliquez sur "Ajouter une Scène".'}
                  </div>
                ) : (
                  (chapter.scenes || []).map((scene, idx) => (
                    <div
                      key={scene.id}
                      className="py-3 flex items-start justify-between gap-4 first:pt-0 last:pb-0"
                    >
                      <div className="flex items-start gap-3">
                        <FileText className="w-4 h-4 text-[#b87500] shrink-0 mt-0.5" />
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-[#0b1c30]">
                              Scène {chapter.number}.{idx + 1} — {scene.title}
                            </span>
                            <span
                              className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${
                                scene.status === "validated"
                                  ? "bg-[#d3e4fe] text-[#0b1c30]"
                                  : "bg-[#eff4ff] text-[#45464d]"
                              }`}
                            >
                              {scene.status}
                            </span>
                          </div>
                          <p className="text-xs text-[#45464d] mt-0.5">
                            {scene.summary}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-3 shrink-0 font-mono text-xs">
                        {scene.scoreStyle && (
                          <span className="text-[11px] text-[#b87500] bg-[#ffddb8]/40 px-2 py-0.5 rounded">
                            Score IA: {scene.scoreStyle}/10
                          </span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </StudioLayout>
  );
}
