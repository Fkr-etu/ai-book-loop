"use client";

import { useEffect, useMemo, useState } from "react";
import { Check, ChevronRight, RotateCcw, Sparkles, X } from "lucide-react";
import { StudioLayout } from "@/components/StudioLayout";
import { StudioDecisionState } from "@/components/StudioDecisionState";
import { useProjectStore } from "@/lib/useProjectStore";
import type { ChapterVersion, SceneReview } from "@/types";
import type { BackendWorkflowRun } from "@/types/api";

const TERMINAL_STATUSES = new Set<BackendWorkflowRun["status"]>(["completed", "needs_review", "failed"]);

export default function ChaptersPage() {
  const store = useProjectStore();
  const { project, loading, error } = store;
  const chapters = project.chapters || [];
  const [selectedNumber, setSelectedNumber] = useState<number | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<number | null>(null);
  const [draftText, setDraftText] = useState("");
  const [review, setReview] = useState<SceneReview | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [activeRun, setActiveRun] = useState<BackendWorkflowRun | null>(null);

  const chapter = useMemo(() => chapters.find((item) => item.number === selectedNumber) || chapters[0], [chapters, selectedNumber]);
  const versions = chapter?.versions || [];
  const version: ChapterVersion | undefined = useMemo(() => versions.find((item) => item.versionNumber === selectedVersion) || versions.find((item) => item.versionNumber === chapter?.currentVersion) || versions[versions.length - 1], [versions, selectedVersion, chapter?.currentVersion]);

  useEffect(() => {
    if (!chapter) { setSelectedNumber(null); setSelectedVersion(null); setDraftText(""); return; }
    setSelectedNumber(chapter.number);
    setSelectedVersion(chapter.currentVersion || null);
  }, [chapter?.id, chapter?.number, chapter?.currentVersion]);

  useEffect(() => { setDraftText(version?.content || ""); setReview(version?.review || null); }, [version?.id]);

  // Reconstruct execution state from the backend on mount/chapter change: no client-side timer is authoritative.
  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      if (!chapter) { setActiveRun(null); return; }
      try {
        const run = await store.getLatestChapterWorkflowRun(chapter.number);
        if (!cancelled) setActiveRun(run && !TERMINAL_STATUSES.has(run.status) ? run : null);
      } catch (err) {
        if (!cancelled) setActionError(err instanceof Error ? err.message : "Impossible de récupérer l'état de la génération.");
      }
    };
    void load();
    return () => { cancelled = true; };
  }, [chapter?.id, chapter?.number, store.getLatestChapterWorkflowRun]);

  // Poll only while the persisted run is running. Completion reloads BookState from the API.
  useEffect(() => {
    if (!activeRun || activeRun.status !== "running") return;
    let cancelled = false;
    const poll = async () => {
      try {
        const run = await store.getChapterWorkflowRun(activeRun.chapter_number, activeRun.id);
        if (cancelled) return;
        setActiveRun(TERMINAL_STATUSES.has(run.status) ? null : run);
        if (run.status === "completed" || run.status === "needs_review") {
          await store.refreshProject();
          if (!cancelled) setSelectedVersion(run.attempt || null);
        } else if (run.status === "failed") {
          setActionError(run.error || "La génération du chapitre a échoué.");
        }
      } catch (err) {
        if (!cancelled) setActionError(err instanceof Error ? err.message : "Impossible de suivre la génération.");
      }
    };
    const timer = window.setInterval(() => { void poll(); }, 1500);
    void poll();
    return () => { cancelled = true; window.clearInterval(timer); };
  }, [activeRun?.id, activeRun?.status, activeRun?.chapter_number, store.getChapterWorkflowRun, store.refreshProject]);

  const run = async (operation: () => Promise<void>) => { setActionError(null); try { await operation(); } catch (err: unknown) { setActionError(err instanceof Error ? err.message : "Une erreur est survenue."); } };

  const generate = () => run(async () => {
    if (!chapter) return;
    if (activeRun?.status === "running") return;
    const started = await store.generateChapter(chapter.number);
    setActiveRun(started.status === "running" ? started : null);
  });
  const critique = () => run(async () => { if (!chapter) return; const result = await store.reviewChapter(chapter.number, version?.versionNumber, draftText); setReview(result); });
  const approve = () => run(async () => { if (!chapter) return; await store.approveChapter(chapter.number); });
  const reject = () => run(async () => { if (!chapter) return; await store.rejectChapter(chapter.number); });

  const canDecide = chapter?.status === "needs_review" || chapter?.status === "proposed";
  const wordCount = draftText.trim() ? draftText.trim().split(/\s+/).length : 0;
  const workflowBusy = activeRun?.status === "running";

  return (
    <StudioLayout>
      <div className="flex min-h-[calc(100vh-61px)] flex-col bg-[#f8f5f0] lg:flex-row">
        <main className="min-w-0 flex-1 overflow-y-auto p-4 sm:p-6 md:p-10">
          <div className="mx-auto max-w-5xl">
            <header className="mb-6 flex flex-col gap-4 border-b border-[#c6c6cd]/30 pb-5 sm:flex-row sm:items-end sm:justify-between">
              <div><p className="font-mono text-[10px] font-bold uppercase tracking-wider text-[#b87500]">Chapitres</p><h1 className="mt-1 font-playfair text-3xl font-bold text-[#0b1c30]">Écrire, relire, décider</h1><p className="mt-2 max-w-2xl text-sm text-[#5f5e5b]">Chaque version affichée correspond à l&apos;état du livre. L&apos;IA propose ; l&apos;auteur décide.</p></div>
              {chapter && <StudioDecisionState status={chapter.status} />}
            </header>
            {workflowBusy && <div className="mb-4 rounded border border-[#c6c6cd]/40 bg-white p-3 text-sm text-[#0b1c30]" role="status" aria-live="polite">Génération en cours · progression <strong>{activeRun.step}</strong> · tentative {activeRun.attempt || 1}.</div>}
            {error && <div className="mb-4 rounded border border-[#d98980] bg-[#fff5f3] p-3 text-sm text-[#8f3028]">{error}</div>}
            {actionError && <div className="mb-4 rounded border border-[#d98980] bg-[#fff5f3] p-3 text-sm text-[#8f3028]">{actionError}</div>}

            {!chapters.length ? <section className="rounded-lg border border-dashed border-[#c6c6cd] bg-white p-10 text-center"><h2 className="font-playfair text-xl font-bold text-[#0b1c30]">Aucun chapitre</h2><p className="mt-2 text-sm text-[#76777d]">Approuvez d&apos;abord le plan, puis créez un chapitre depuis l&apos;espace Plan.</p></section> : (
              <div className="grid gap-6 lg:grid-cols-[260px_minmax(0,1fr)]">
                <aside className="space-y-2"><p className="px-1 font-mono text-[10px] font-bold uppercase tracking-wider text-[#76777d]">Chapitres</p>{chapters.map((item) => { const active = item.number === chapter?.number; return <button key={item.id} type="button" onClick={() => { setSelectedNumber(item.number); setSelectedVersion(item.currentVersion || null); }} className={`w-full rounded-lg border p-3 text-left transition ${active ? "border-[#0b1c30] bg-[#0b1c30] text-white" : "border-[#c6c6cd]/40 bg-white text-[#0b1c30] hover:bg-[#e5eeff]"}`}><div className="flex items-center justify-between gap-2"><span className="font-mono text-[10px] font-bold uppercase">Chapitre {item.number}</span><ChevronRight className="h-3.5 w-3.5" /></div><div className="mt-1 truncate font-playfair text-sm font-bold">{item.title}</div><div className={`mt-2 text-[10px] ${active ? "text-[#c6c6cd]" : "text-[#76777d]"}`}>{item.status} · v{item.currentVersion}</div></button>; })}</aside>
                <section className="min-w-0 rounded-lg border border-[#c6c6cd]/30 bg-white shadow-xs">
                  {chapter && <>
                    <div className="border-b border-[#c6c6cd]/30 p-4 sm:p-6"><div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between"><div><p className="font-mono text-[10px] uppercase tracking-wider text-[#76777d]">Chapitre {chapter.number}</p><h2 className="mt-1 font-playfair text-2xl font-bold text-[#0b1c30]">{chapter.title}</h2>{chapter.objective && <p className="mt-2 text-xs italic text-[#5f5e5b]">{chapter.objective}</p>}</div><div className="flex flex-wrap gap-2"><button type="button" onClick={generate} disabled={loading || workflowBusy || !project.outlineApproved} className="inline-flex items-center gap-1.5 rounded bg-[#0b1c30] px-3 py-2 text-xs font-semibold text-[#ffddb8] disabled:opacity-40"><Sparkles className="h-3.5 w-3.5" /> {workflowBusy ? "Génération…" : "Générer une version"}</button><button type="button" onClick={critique} disabled={loading || workflowBusy || !version} className="inline-flex items-center gap-1.5 rounded border border-[#c6c6cd] bg-[#eff4ff] px-3 py-2 text-xs font-semibold text-[#0b1c30] disabled:opacity-40"><RotateCcw className="h-3.5 w-3.5 text-[#b87500]" /> Analyser le chapitre</button></div></div></div>
                    <div className="border-b border-[#c6c6cd]/30 bg-[#f8f9ff] p-3"><div className="flex flex-wrap gap-2">{versions.length ? versions.map((item) => <button key={item.id} type="button" onClick={() => setSelectedVersion(item.versionNumber)} className={`rounded border px-2.5 py-1.5 text-[11px] font-mono ${item.versionNumber === version?.versionNumber ? "border-[#0b1c30] bg-[#0b1c30] text-white" : "border-[#c6c6cd]/40 bg-white text-[#45464d]"}`}>Version {item.versionNumber} · {item.source} · {item.status}</button>) : <span className="px-1 text-xs text-[#76777d]">Aucune version disponible.</span>}</div></div>
                    <div className="p-4 sm:p-6"><div className="mb-3 flex items-center justify-between gap-3 font-mono text-[10px] text-[#76777d]"><span>{version ? `Version ${version.versionNumber}` : "Aucune version"}</span><span>{wordCount} mots</span></div><textarea value={draftText} onChange={(event) => setDraftText(event.target.value)} disabled={!version || workflowBusy} className="min-h-[480px] w-full resize-y rounded border border-[#c6c6cd]/30 bg-[#fffdfc] p-5 font-merriweather text-sm leading-[1.85] text-[#0f172a] outline-none focus:border-[#0b1c30]" placeholder="Le contenu de la version sélectionnée apparaîtra ici." aria-label="Contenu du chapitre" />{canDecide && !workflowBusy && <div className="mt-4 flex flex-wrap gap-2 rounded border border-[#c6c6cd]/30 bg-[#f8f9ff] p-3"><button type="button" onClick={approve} disabled={loading} className="inline-flex items-center gap-1.5 rounded bg-[#9a6617] px-3 py-2 text-xs font-bold text-white disabled:opacity-40"><Check className="h-3.5 w-3.5" /> Approuver</button><button type="button" onClick={reject} disabled={loading} className="inline-flex items-center gap-1.5 rounded border border-[#d98980] bg-white px-3 py-2 text-xs font-bold text-[#a33b32] disabled:opacity-40"><X className="h-3.5 w-3.5" /> Rejeter</button></div>}</div>
                  </>}
                </section>
              </div>
            )}
          </div>
        </main>
        <aside className="w-full shrink-0 border-t border-[#c6c6cd]/30 bg-[#f8f9ff] p-4 lg:w-[320px] lg:border-l lg:border-t-0"><div className="sticky top-0 space-y-4"><section className="rounded-lg border border-[#c6c6cd]/30 bg-white p-4"><h3 className="font-mono text-[10px] font-bold uppercase tracking-wider text-[#76777d]">État du livre</h3><div className="mt-3 space-y-2 text-xs text-[#45464d]"><div className="flex justify-between gap-3"><span>Plan approuvé</span><strong>{project.outlineApproved ? "Oui" : "Non"}</strong></div><div className="flex justify-between gap-3"><span>Versions</span><strong>{versions.length}</strong></div><div className="flex justify-between gap-3"><span>Version actuelle</span><strong>{chapter?.currentVersion || "—"}</strong></div>{activeRun && <div className="flex justify-between gap-3"><span>Génération</span><strong>{activeRun.status} · {activeRun.step}</strong></div>}</div></section><section className="rounded-lg border border-[#c6c6cd]/30 bg-white p-4"><h3 className="font-mono text-[10px] font-bold uppercase tracking-wider text-[#76777d]">Dernière analyse</h3>{review ? <div className="mt-3 space-y-3 text-xs text-[#45464d]"><div className="flex items-center justify-between"><span>Score</span><strong>{review.score}/10</strong></div>{review.critique && <p className="rounded bg-[#f8f9ff] p-3 italic">{review.critique}</p>}{review.issues.length > 0 && <div><p className="font-bold">Points à revoir</p><ul className="mt-1 list-disc space-y-1 pl-4">{review.issues.map((issue, index) => <li key={`${issue}-${index}`}>{issue}</li>)}</ul></div>}</div> : <p className="mt-3 text-xs text-[#76777d]">Aucune analyse pour la version sélectionnée.</p>}</section><section className="rounded-lg border border-dashed border-[#c6c6cd]/50 p-4 text-xs text-[#76777d]">Les décisions et les versions sont enregistrées automatiquement.</section></div></aside>
      </div>
    </StudioLayout>
  );
}
