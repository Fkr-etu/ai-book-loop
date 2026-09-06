"use client";

import React, { useEffect, useMemo, useState } from "react";
import { Check, History, Info, RotateCcw, Sparkles, X } from "lucide-react";
import { StudioLayout } from "@/components/StudioLayout";
import { StudioDecisionState } from "@/components/StudioDecisionState";
import { useProjectStore } from "@/lib/useProjectStore";
import { CanonicalContextResponse, ChapterVersion } from "@/types";

export default function StudioDeskPage() {
  const store = useProjectStore();
  const project = store.project;
  const chapters = project.chapters || [];
  const reviews = project.reviews || [];

  const [activeTab, setActiveTab] = useState<"manuscript" | "history" | "context">("manuscript");
  const [selectedChapterNumber, setSelectedChapterNumber] = useState<number | null>(null);
  const [selectedVersionNumber, setSelectedVersionNumber] = useState<number | null>(null);
  const [canonicalContext, setCanonicalContext] = useState<CanonicalContextResponse | null>(null);
  const [contextError, setContextError] = useState<string | null>(null);
  const [editorContent, setEditorContent] = useState("");
  const [isWorking, setIsWorking] = useState(false);

  const activeChapter = useMemo(() => {
    if (!chapters.length) return undefined;
    return chapters.find((chapter) => chapter.number === selectedChapterNumber) || chapters[0];
  }, [chapters, selectedChapterNumber]);

  const versions = activeChapter?.versions || [];

  const activeVersion: ChapterVersion | undefined = useMemo(() => {
    if (!versions.length) return undefined;
    return versions.find((version) => version.versionNumber === selectedVersionNumber) ||
      versions.find((version) => version.versionNumber === activeChapter?.currentVersion) ||
      versions[versions.length - 1];
  }, [versions, selectedVersionNumber, activeChapter?.currentVersion]);

  useEffect(() => {
    setSelectedChapterNumber((current) => {
      if (current !== null && chapters.some((chapter) => chapter.number === current)) return current;
      return chapters[0]?.number ?? null;
    });
  }, [chapters]);

  useEffect(() => {
    setSelectedVersionNumber(activeVersion?.versionNumber ?? null);
    setEditorContent(activeVersion?.content || activeChapter?.scenes?.[0]?.content || "");
  }, [activeChapter?.id, activeVersion?.id]);

  useEffect(() => {
    let cancelled = false;

    if (!activeChapter) {
      setCanonicalContext(null);
      setContextError(null);
      return;
    }

    setContextError(null);
    store.getCanonicalContext(activeChapter.number)
      .then((context) => {
        if (!cancelled) setCanonicalContext(context);
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          console.error("Unable to load canonical context", error);
          setCanonicalContext(null);
          setContextError("Impossible de charger le contexte canonique.");
        }
      });

    return () => {
      cancelled = true;
    };
  }, [activeChapter?.number, store]);

  const handleGenerateVersion = async () => {
    if (!activeChapter) return;
    setIsWorking(true);
    try {
      await store.generateChapter(activeChapter.number);
    } catch (error) {
      console.error("Chapter generation failed", error);
    } finally {
      setIsWorking(false);
    }
  };

  const handleReview = async () => {
    if (!activeChapter) return;
    setIsWorking(true);
    try {
      await store.reviewChapter(activeChapter.number, activeVersion?.versionNumber, editorContent);
    } catch (error) {
      console.error("Chapter review failed", error);
    } finally {
      setIsWorking(false);
    }
  };

  const handleApprove = async () => {
    if (!activeChapter) return;
    await store.approveChapter(activeChapter.number);
  };

  const handleReject = async () => {
    if (!activeChapter) return;
    await store.rejectChapter(activeChapter.number);
  };

  const canDecide = activeChapter?.status === "needs_review";
  const wordCount = editorContent.trim() ? editorContent.trim().split(/\s+/).length : 0;
  const latestReview = reviews[0];

  return (
    <StudioLayout>
      <div className="flex min-h-[calc(100vh-61px)] flex-col overflow-y-auto lg:flex-row lg:overflow-hidden">
        <main className="flex-1 overflow-y-auto bg-[#f8f5f0] p-4 sm:p-6 md:p-10">
          <div className="mx-auto flex w-full max-w-[760px] flex-col">
            <div className="mb-4 flex flex-col gap-3 border-b border-[#c6c6cd]/30 pb-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex flex-wrap items-center gap-2 text-xs font-mono text-[#0b1c30]">
                {chapters.length ? (
                  <select
                    value={activeChapter?.number ?? ""}
                    onChange={(event) => {
                      const number = Number(event.target.value);
                      setSelectedChapterNumber(number);
                      const chapter = chapters.find((item) => item.number === number);
                      setSelectedVersionNumber(chapter?.currentVersion ?? null);
                    }}
                    className="max-w-[240px] rounded border border-[#c6c6cd] bg-white px-2 py-1 font-bold"
                    aria-label="Sélectionner un chapitre"
                  >
                    {chapters.map((chapter) => (
                      <option key={chapter.id} value={chapter.number}>
                        Chapitre {chapter.number}: {chapter.title}
                      </option>
                    ))}
                  </select>
                ) : (
                  <span className="text-[#76777d]">Aucun chapitre disponible</span>
                )}
                <StudioDecisionState status={activeChapter?.status} />
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-mono text-[#76777d]">{wordCount} mots</span>
                <button
                  type="button"
                  onClick={handleGenerateVersion}
                  disabled={isWorking || !activeChapter || !project.outlineApproved}
                  className="flex items-center gap-1.5 rounded bg-[#0b1c30] px-3 py-1.5 text-xs font-semibold text-[#ffddb8] shadow-xs disabled:opacity-40"
                >
                  <Sparkles className={`h-3.5 w-3.5 ${isWorking ? "animate-spin" : ""}`} />
                  Générer une version
                </button>
                <button
                  type="button"
                  onClick={handleReview}
                  disabled={isWorking || !activeChapter}
                  className="flex items-center gap-1.5 rounded border border-[#c6c6cd]/40 bg-[#eff4ff] px-3 py-1.5 text-xs font-semibold text-[#0b1c30] disabled:opacity-40"
                >
                  <RotateCcw className="h-3.5 w-3.5 text-[#b87500]" />
                  Critiquer
                </button>
              </div>
            </div>

            <section className="mb-4 flex flex-col gap-3 rounded-lg border border-[#c6c6cd]/40 bg-[#fffdfc] p-4 shadow-xs sm:flex-row sm:items-center sm:justify-between" aria-live="polite">
              <div className="min-w-0">
                <p className="font-mono text-xs text-[#506070]">
                  {activeVersion ? `Version v${activeVersion.versionNumber}` : "Aucune version sélectionnée"}
                </p>
                {activeChapter?.objective && (
                  <p className="mt-1 text-xs text-[#13243a]">Objectif : <em>{activeChapter.objective}</em></p>
                )}
              </div>
              {canDecide && (
                <div className="flex shrink-0 flex-col gap-2 sm:flex-row">
                  <button type="button" onClick={handleApprove} className="flex items-center justify-center gap-1.5 rounded bg-[#9a6617] px-3 py-2 text-[11px] font-bold text-white">
                    <Check className="h-3.5 w-3.5" /> Approuver dans le Canon
                  </button>
                  <button type="button" onClick={handleReject} className="flex items-center justify-center gap-1.5 rounded border border-[#d98980] bg-white px-3 py-2 text-[11px] font-bold text-[#a33b32]">
                    <X className="h-3.5 w-3.5" /> Rejeter
                  </button>
                </div>
              )}
            </section>

            <section className="min-h-[450px] rounded border border-[#c6c6cd]/20 bg-[#f8f5f0] p-5 shadow-xs sm:p-8 md:p-12">
              {activeChapter ? (
                <>
                  <div className="mb-6 border-b border-[#c6c6cd]/20 pb-4">
                    <h1 className="mb-2 font-playfair text-2xl font-bold text-[#0f172a] sm:text-3xl">{activeChapter.title}</h1>
                    {activeChapter.objective && <p className="font-courier text-xs text-[#5f5e5b]">{activeChapter.objective}</p>}
                  </div>
                  <textarea
                    value={editorContent}
                    onChange={(event) => setEditorContent(event.target.value)}
                    placeholder="Écrivez votre récit ici ou générez une proposition avec l’IA."
                    className="min-h-[360px] w-full resize-none border-none bg-transparent font-merriweather text-sm leading-[1.8] text-[#0f172a] outline-none focus:ring-0 sm:text-base"
                    aria-label="Manuscrit du chapitre"
                  />
                  <div className="mt-8 flex flex-wrap justify-between gap-2 border-t border-[#c6c6cd]/20 pt-4 text-[11px] font-mono text-[#76777d]">
                    <span>Le texte affiché provient de la version sélectionnée.</span>
                    <StudioDecisionState status={activeChapter.status} />
                  </div>
                </>
              ) : (
                <div className="flex min-h-[360px] items-center justify-center text-center text-sm text-[#76777d]">
                  Créez ou sélectionnez un chapitre pour commencer.
                </div>
              )}
            </section>
          </div>
        </main>

        <aside className="w-full shrink-0 overflow-y-auto border-t border-[#c6c6cd]/30 bg-[#f8f9ff] p-4 lg:w-[360px] lg:border-l lg:border-t-0">
          <div className="mb-4 flex gap-1 rounded-lg border border-[#c6c6cd]/30 bg-[#e5eeff] p-1 text-xs font-mono font-bold text-[#0b1c30]">
            {(["manuscript", "history", "context"] as const).map((tab) => (
              <button
                key={tab}
                type="button"
                onClick={() => setActiveTab(tab)}
                className={`flex-1 rounded py-1.5 ${activeTab === tab ? "bg-white shadow-xs" : "text-[#76777d]"}`}
              >
                {tab === "manuscript" && "Analyse"}
                {tab === "history" && `Versions (${versions.length})`}
                {tab === "context" && "Canon"}
              </button>
            ))}
          </div>

          {activeTab === "manuscript" && (
            <div className="space-y-4">
              {latestReview ? (
                <section className="rounded-xl border border-[#c6c6cd]/30 bg-white p-4 shadow-xs">
                  <div className="mb-3 flex items-center justify-between">
                    <span className="text-xs font-bold text-[#0b1c30]">Dernière évaluation</span>
                    {latestReview.timestamp && <span className="text-[10px] font-mono text-[#76777d]">{latestReview.timestamp}</span>}
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-center">
                    <div className="rounded border border-[#c6c6cd]/20 bg-[#f8f9ff] p-2">
                      <div className="text-[10px] text-[#45464d]">Style</div>
                      <div className="text-sm font-bold">{latestReview.scoreStyle ?? "—"}{latestReview.scoreStyle !== undefined ? "/10" : ""}</div>
                    </div>
                    <div className="rounded border border-[#c6c6cd]/20 bg-[#f8f9ff] p-2">
                      <div className="text-[10px] text-[#45464d]">Cohérence</div>
                      <div className="text-sm font-bold">{latestReview.scoreCoherence ?? "—"}{latestReview.scoreCoherence !== undefined ? "/10" : ""}</div>
                    </div>
                  </div>
                  {latestReview.critique && <p className="mt-3 text-xs italic text-[#45464d]">{latestReview.critique}</p>}
                </section>
              ) : (
                <div className="rounded-xl border border-dashed border-[#c6c6cd]/50 p-5 text-xs text-[#76777d]">Aucune évaluation disponible.</div>
              )}

              {project.characters?.length ? (
                <section className="rounded-xl border border-[#c6c6cd]/30 bg-white p-4">
                  <span className="mb-2 block text-[11px] font-mono font-bold uppercase text-[#76777d]">Personnages du livre</span>
                  <div className="space-y-2">
                    {project.characters.slice(0, 5).map((character) => (
                      <div key={character.id} className="flex items-center gap-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#0b1c30] text-xs font-bold text-[#ffddb8]">{character.name.charAt(0)}</div>
                        <div>
                          <div className="text-xs font-bold text-[#0b1c30]">{character.name}</div>
                          <div className="text-[10px] text-[#45464d]">{character.role}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              ) : null}
            </div>
          )}

          {activeTab === "history" && (
            <div className="space-y-3">
              <span className="block text-xs font-mono font-bold uppercase tracking-wider text-[#76777d]">Historique des versions</span>
              {versions.length ? versions.map((version) => {
                const selected = version.versionNumber === activeVersion?.versionNumber;
                return (
                  <button
                    key={version.id || version.versionNumber}
                    type="button"
                    onClick={() => setSelectedVersionNumber(version.versionNumber)}
                    className={`w-full rounded-xl border p-3.5 text-left ${selected ? "border-[#0b1c30] bg-[#0b1c30] text-white" : "border-[#c6c6cd]/40 bg-white text-[#0b1c30]"}`}
                  >
                    <div className="flex items-center justify-between gap-2 text-xs font-mono font-bold">
                      <span>v{version.versionNumber} · {version.source}</span>
                      <span>{version.status}</span>
                    </div>
                    <p className={`mt-2 line-clamp-3 text-xs font-merriweather ${selected ? "text-[#c6c6cd]" : "text-[#5f5e5b]"}`}>{version.content}</p>
                  </button>
                );
              }) : <div className="rounded border border-dashed border-[#c6c6cd]/50 p-4 text-xs text-[#76777d]">Aucune version archivée.</div>}
            </div>
          )}

          {activeTab === "context" && (
            <div className="space-y-3">
              <span className="block text-xs font-mono font-bold uppercase tracking-wider text-[#76777d]">Contexte canonique</span>
              {contextError ? (
                <div className="rounded border border-[#e8aaa3] bg-[#ffdad6] p-3 text-xs text-[#a33b32]">{contextError}</div>
              ) : canonicalContext ? (
                <div className="space-y-3 text-xs">
                  <div className="rounded-lg border border-[#c6c6cd]/30 bg-white p-3"><strong>Intention auteur</strong><p className="mt-1 text-[#45464d]">{canonicalContext.authorIdea}</p></div>
                  <div className="rounded-lg border border-[#c6c6cd]/30 bg-white p-3"><strong>Lore & Bible canonique</strong><p className="mt-1 text-[#45464d]">{canonicalContext.lore}</p></div>
                  <div className="rounded-lg border border-[#c6c6cd]/30 bg-white p-3"><strong>Contraintes actives</strong><ul className="mt-1 list-disc pl-4 text-[#45464d]">{canonicalContext.constraints.map((constraint, index) => <li key={index}>{constraint}</li>)}</ul></div>
                  <div className="rounded-lg border border-[#c6c6cd]/30 bg-white p-3"><strong>Résumés précédents</strong><p className="mt-1 whitespace-pre-wrap text-[#45464d]">{canonicalContext.previousSummaries || "Aucun chapitre précédent approuvé."}</p></div>
                </div>
              ) : (
                <div className="rounded border border-dashed border-[#c6c6cd]/50 p-4 text-xs text-[#76777d]">Aucun contexte canonique disponible.</div>
              )}
            </div>
          )}
        </aside>
      </div>
    </StudioLayout>
  );
}
