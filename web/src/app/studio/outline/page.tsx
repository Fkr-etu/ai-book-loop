"use client";

import React, { useState } from "react";
import { StudioLayout } from "@/components/StudioLayout";
import { useProjectStore } from "@/lib/useProjectStore";
import {
  ListOrdered,
  Plus,
  CheckCircle2,
  Clock,
  ChevronDown,
  ChevronRight,
  Sparkles,
  FileText,
  Edit2,
  Trash2,
  Check
} from "lucide-react";

export default function OutlinePage() {
  const { project, addChapter, addScene } = useProjectStore();

  const [newChapterTitle, setNewChapterTitle] = useState("");
  const [newChapterSummary, setNewChapterSummary] = useState("");
  const [isAddingChapter, setIsAddingChapter] = useState(false);

  const [activeChapterForScene, setActiveChapterForScene] = useState<string | null>(null);
  const [newSceneTitle, setNewSceneTitle] = useState("");
  const [newSceneSummary, setNewSceneSummary] = useState("");

  const handleCreateChapter = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newChapterTitle.trim()) return;
    addChapter(newChapterTitle, newChapterSummary);
    setNewChapterTitle("");
    setNewChapterSummary("");
    setIsAddingChapter(false);
  };

  const handleCreateScene = (chapterId: string) => {
    if (!newSceneTitle.trim()) return;
    addScene(chapterId, newSceneTitle, newSceneSummary);
    setNewSceneTitle("");
    setNewSceneSummary("");
    setActiveChapterForScene(null);
  };

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
              Organisez les chapitres et les scènes de votre livre. Chaque chapitre doit être approuvé avant la génération IA.
            </p>
          </div>

          <button
            onClick={() => setIsAddingChapter(!isAddingChapter)}
            className="px-4 py-2 bg-[#0b1c30] text-[#ffddb8] text-xs font-bold rounded hover:bg-[#131b2e] transition-colors flex items-center gap-2 shadow-xs shrink-0"
          >
            <Plus className="w-4 h-4" />
            <span>Nouveau Chapitre</span>
          </button>
        </div>

        {/* Add Chapter Form */}
        {isAddingChapter && (
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
                placeholder="Résumé ou enjeu dramatique du chapitre..."
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
          {project.chapters.map((chapter) => (
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
                        {chapter.status === "approved" ? "Approuvé pour Génération" : "En cours de structure"}
                      </span>
                    </div>
                    <p className="text-xs text-[#45464d] mt-1 font-merriweather">
                      {chapter.summary}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() =>
                      setActiveChapterForScene(
                        activeChapterForScene === chapter.id ? null : chapter.id
                      )
                    }
                    className="px-3 py-1.5 text-xs font-semibold bg-[#eff4ff] text-[#0b1c30] rounded border border-[#c6c6cd]/30 hover:bg-[#e5eeff] flex items-center gap-1"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Ajouter une Scène</span>
                  </button>
                </div>
              </div>

              {/* Form to add scene under this chapter */}
              {activeChapterForScene === chapter.id && (
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
                {chapter.scenes.length === 0 ? (
                  <div className="text-center py-6 text-xs text-[#76777d]">
                    Aucune scène créée pour ce chapitre. Cliquez sur "Ajouter une Scène".
                  </div>
                ) : (
                  chapter.scenes.map((scene, idx) => (
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
