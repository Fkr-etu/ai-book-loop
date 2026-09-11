"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AlertTriangle, CheckCircle2, Loader2, RefreshCw, Sparkles } from "lucide-react";
import { realApiClient, RealApiError } from "@/services/realApiClient";
import { track } from "@/lib/analytics";
import type { BackendAnalysisJob, BackendConsistencyIssue } from "@/types/api";

const STORAGE_PREFIX = "book-loop:consistency-analysis:";
const TERMINAL = new Set(["succeeded", "failed", "cancelled"]);

function labelForStep(step: string | null): string {
  if (!step) return "Préparation de l’analyse";
  if (step === "analyzing") return "Analyse du Canon en cours";
  return step;
}

export function ConsistencyAnalysisPanel({ bookId }: { bookId: string }) {
  const [job, setJob] = useState<BackendAnalysisJob | null>(null);
  const [starting, setStarting] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const resultViewedJob = useRef<string | null>(null);
  const completedJob = useRef<string | null>(null);

  const refreshJob = useCallback(async (jobId: string) => {
    try {
      const next = await realApiClient.getConsistencyAnalysis(bookId, jobId);
      setJob(next);
      if (next.status === "succeeded") {
        if (completedJob.current !== next.job_id) {
          completedJob.current = next.job_id;
          track("analysis_completed", { issue_count: next.result?.issues?.length ?? 0 });
        }
        if (resultViewedJob.current !== next.job_id) {
          resultViewedJob.current = next.job_id;
          track("analysis_result_viewed", { issue_count: next.result?.issues?.length ?? 0 });
        }
      }
      if (TERMINAL.has(next.status)) window.localStorage.removeItem(`${STORAGE_PREFIX}${bookId}`);
      return next;
    } catch (err) {
      if (err instanceof RealApiError && err.status === 404) {
        window.localStorage.removeItem(`${STORAGE_PREFIX}${bookId}`);
        setJob(null);
        return null;
      }
      throw err;
    }
  }, [bookId]);

  useEffect(() => {
    const jobId = window.localStorage.getItem(`${STORAGE_PREFIX}${bookId}`);
    if (!jobId) return;
    setLoading(true);
    void refreshJob(jobId).catch(() => setError("Impossible de retrouver l’état de l’analyse.")).finally(() => setLoading(false));
  }, [bookId, refreshJob]);

  useEffect(() => {
    if (!job || TERMINAL.has(job.status)) return;
    const timer = window.setInterval(() => {
      void refreshJob(job.job_id).catch(() => setError("Impossible d’actualiser l’analyse."));
    }, 2000);
    return () => window.clearInterval(timer);
  }, [job, refreshJob]);

  const start = async () => {
    setStarting(true);
    setError(null);
    try {
      const next = await realApiClient.startConsistencyAnalysis(bookId);
      setJob(next);
      window.localStorage.setItem(`${STORAGE_PREFIX}${bookId}`, next.job_id);
      track("analysis_started");
    } catch (err) {
      setError(err instanceof RealApiError ? err.message : "L’analyse n’a pas pu être lancée.");
    } finally {
      setStarting(false);
    }
  };

  const issues = (job?.result?.issues ?? []) as BackendConsistencyIssue[];
  const running = job?.status === "queued" || job?.status === "running";

  return (
    <section className="bg-white rounded-xl border border-[#c6c6cd]/40 overflow-hidden" aria-labelledby="consistency-analysis-title">
      <div className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#c6c6cd]/20">
        <div className="flex items-start gap-3">
          <Sparkles className="w-5 h-5 text-[#b87500] mt-0.5" />
          <div>
            <h2 id="consistency-analysis-title" className="font-playfair font-bold text-lg text-[#0b1c30]">Analyse de cohérence</h2>
            <p className="text-xs text-[#76777d] mt-1 max-w-xl">Vérifiez l’ensemble du récit à la recherche de contradictions et de ruptures de continuité.</p>
          </div>
        </div>
        <button type="button" onClick={() => void start()} disabled={starting || running || loading} className="shrink-0 px-4 py-2.5 bg-[#0b1c30] text-white text-xs font-bold rounded-lg flex items-center justify-center gap-2 disabled:opacity-50">
          {starting || running ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5" />}
          {starting ? "Lancement…" : running ? "Analyse en cours…" : "Lancer l’analyse"}
        </button>
      </div>

      {error && <div role="alert" className="m-4 p-3 bg-[#fff4f4] border border-[#d9aaaa] rounded-lg text-xs text-[#5c2020] flex items-start gap-2"><AlertTriangle className="w-4 h-4 shrink-0" /><span>{error}</span></div>}

      {job && <div className="p-4 sm:p-5 space-y-4">
        {running && <div aria-live="polite" className="space-y-2"><div className="flex justify-between text-xs font-mono text-[#45464d]"><span>{job.status === "queued" ? "En attente dans la file" : labelForStep(job.current_step)}</span><span>{job.progress}%</span></div><div className="h-2 bg-[#ececf0] rounded-full overflow-hidden"><div className="h-full bg-[#b87500] transition-all" style={{ width: `${Math.min(100, Math.max(0, job.progress))}%` }} /></div><p className="text-[11px] text-[#76777d]">Vous pouvez quitter cette page : l’analyse continue en arrière-plan.</p></div>}
        {job.status === "succeeded" && <div className="flex items-center gap-2 text-xs font-semibold text-[#0b1c30]"><CheckCircle2 className="w-4 h-4 text-[#3f7d55]" />Analyse terminée — {issues.length} problème{issues.length > 1 ? "s" : ""} détecté{issues.length > 1 ? "s" : ""}.</div>}
        {job.status === "failed" && <div role="alert" className="text-xs text-[#5c2020]">L’analyse a échoué. {job.error_message || "Vous pouvez relancer l’analyse."}</div>}
        {job.status === "cancelled" && <div className="text-xs text-[#5f5e5b]">L’analyse a été annulée.</div>}
        {issues.length > 0 && <div className="space-y-2">{issues.map((issue) => <article key={issue.id} className="rounded-lg border border-[#c6c6cd]/30 p-3"><div className="flex items-start justify-between gap-3"><p className="text-xs font-semibold text-[#0b1c30]">{issue.message}</p><span className="text-[10px] font-mono uppercase text-[#76777d] shrink-0">{issue.severity}</span></div><p className="text-[11px] text-[#5f5e5b] mt-2">{issue.left_statement}</p><p className="text-[11px] text-[#5f5e5b] mt-1">{issue.right_statement}</p></article>)}</div>}
      </div>}
    </section>
  );
}
