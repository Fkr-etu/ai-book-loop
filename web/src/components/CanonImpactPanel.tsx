"use client";

import { useCallback, useEffect, useState } from "react";
import { AlertTriangle, ArrowDown, FileText, GitBranch, Loader2, RefreshCw, ShieldAlert } from "lucide-react";
import { useProjectStore } from "@/lib/useProjectStore";
import { realApiClient, RealApiError } from "@/services/realApiClient";
import type { BackendCanonChangeImpact, BackendCanonicalFact, BackendRegressionFinding } from "@/types/api";

const riskClasses = { high: "bg-[#f3d7d7] text-[#5c2020] border-[#d9aaaa]", medium: "bg-[#ffddb8] text-[#2a1700] border-[#e0bd91]" };
function riskLabel(risk: BackendRegressionFinding["risk"]): string { return risk === "high" ? "Impact direct" : "Impact indirect"; }
function errorMessage(error: unknown): string { if (error instanceof RealApiError) return error.message; return "Impossible d'analyser l'impact de cette information."; }

export function CanonImpactPanel() {
  const { project } = useProjectStore();
  const [facts, setFacts] = useState<BackendCanonicalFact[]>([]);
  const [selectedFactId, setSelectedFactId] = useState<string | null>(null);
  const [report, setReport] = useState<BackendCanonChangeImpact | null>(null);
  const [loadingFacts, setLoadingFacts] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadFacts = useCallback(async () => {
    if (!project.id) return;
    setLoadingFacts(true); setError(null);
    try {
      const nextFacts = await realApiClient.listCanonicalFacts(project.id);
      setFacts(nextFacts);
      setSelectedFactId((current) => current && nextFacts.some((fact) => fact.id === current) ? current : nextFacts[0]?.id ?? null);
      setReport(null);
    } catch (err) { setError(errorMessage(err)); } finally { setLoadingFacts(false); }
  }, [project.id]);

  useEffect(() => { void loadFacts(); }, [loadFacts]);

  const analyze = async (factId: string) => {
    if (!project.id) return;
    setSelectedFactId(factId); setAnalyzing(true); setError(null);
    try { setReport(await realApiClient.analyzeCanonChange(project.id, factId)); }
    catch (err) { setReport(null); setError(errorMessage(err)); }
    finally { setAnalyzing(false); }
  };

  const selectedFact = facts.find((fact) => fact.id === selectedFactId) ?? null;
  const findings = report?.findings ?? [];
  const directCount = findings.filter((finding) => finding.risk === "high" || finding.dependency_depth === 1).length;
  const indirectCount = findings.length - directCount;

  return (
    <section className="bg-white rounded-xl border border-[#c6c6cd]/40 overflow-hidden">
      <div className="p-4 sm:p-5 border-b border-[#c6c6cd]/20 flex items-start justify-between gap-4">
        <div className="flex items-start gap-3"><GitBranch className="w-5 h-5 text-[#b87500] mt-0.5" /><div><h2 className="font-playfair font-bold text-lg text-[#0b1c30]">Mesurer l’impact d’une modification</h2><p className="text-xs text-[#76777d] mt-1 max-w-2xl">Avant de modifier une information confirmée, voyez quelles informations de votre histoire pourraient être concernées.</p></div></div>
        <button type="button" onClick={() => void loadFacts()} disabled={loadingFacts || analyzing} className="p-2 rounded border border-[#c6c6cd]/40 hover:bg-[#eff4ff] disabled:opacity-50" aria-label="Actualiser les informations confirmées"><RefreshCw className={`w-4 h-4 ${loadingFacts ? "animate-spin" : ""}`} /></button>
      </div>
      {error && <div role="alert" className="m-4 p-3 bg-[#fff4f4] border border-[#d9aaaa] rounded-lg text-xs text-[#5c2020] flex items-start gap-2"><AlertTriangle className="w-4 h-4 shrink-0" /><span>{error}</span></div>}
      {loadingFacts ? <div className="p-8 text-center text-xs text-[#76777d] flex items-center justify-center gap-2"><Loader2 className="w-4 h-4 animate-spin" />Chargement…</div> : facts.length === 0 ? <div className="p-8 text-center"><ShieldAlert className="w-7 h-7 mx-auto text-[#b87500]" /><p className="text-sm font-semibold text-[#0b1c30] mt-3">Aucune information confirmée</p><p className="text-xs text-[#76777d] mt-1">Confirmez une proposition dans la revue de la continuité pour pouvoir mesurer son impact.</p></div> :
        <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.4fr)] divide-y lg:divide-y-0 lg:divide-x divide-[#c6c6cd]/20">
          <div className="max-h-[520px] overflow-y-auto divide-y divide-[#c6c6cd]/20">{facts.map((fact) => <div key={fact.id} className={`p-4 ${selectedFactId === fact.id ? "bg-[#eff4ff]" : ""}`}><p className="text-xs font-semibold text-[#0b1c30] leading-relaxed">{fact.statement}</p><button type="button" onClick={() => void analyze(fact.id)} disabled={analyzing} className="mt-3 px-3 py-1.5 text-[10px] font-bold rounded border border-[#0b1c30] text-[#0b1c30] hover:bg-white disabled:opacity-50 flex items-center gap-1.5">{analyzing && selectedFactId === fact.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <GitBranch className="w-3 h-3" />}Mesurer l’impact</button></div>)}</div>
          <div className="p-4 sm:p-6 min-h-[320px]">{!selectedFact ? <div className="h-full flex items-center justify-center text-xs text-[#76777d]">Sélectionnez une information confirmée.</div> : !report ? <div className="h-full flex items-center justify-center text-center text-xs text-[#76777d] max-w-sm mx-auto">Choisissez une information puis mesurez son impact pour voir les éléments susceptibles d’être concernés.</div> : <div className="space-y-5"><div><span className="text-[10px] font-bold text-[#b87500]">Information examinée</span><h3 className="font-playfair text-lg font-bold text-[#0b1c30] mt-1">{selectedFact.statement}</h3></div><div className="grid grid-cols-2 gap-3"><div className="bg-[#fff8f0] rounded-lg p-3"><div className="text-[10px] uppercase text-[#76777d]">Impacts directs</div><div className="text-xl font-bold text-[#5c2020] mt-1">{directCount}</div></div><div className="bg-[#f8f9ff] rounded-lg p-3"><div className="text-[10px] uppercase text-[#76777d]">Impacts indirects</div><div className="text-xl font-bold text-[#0b1c30] mt-1">{indirectCount}</div></div></div>{findings.length === 0 ? <div className="p-5 rounded-lg border border-dashed border-[#c6c6cd] text-center"><p className="text-xs font-semibold text-[#0b1c30]">Aucun élément concerné trouvé</p><p className="text-[10px] text-[#76777d] mt-1">Aucune référence exploitable n’a été trouvée dans les informations actuellement enregistrées.</p></div> : <div className="space-y-3"><div className="flex items-center justify-between"><p className="text-[10px] font-bold uppercase text-[#76777d]">Éléments potentiellement concernés</p><span className="text-[10px] text-[#76777d]">{findings.length} résultat{findings.length > 1 ? "s" : ""}</span></div>{findings.map((finding, index) => { const risk = finding.risk ?? (finding.dependency_depth === 1 ? "high" : "medium"); return <article key={`${finding.fact_id}-${finding.assertion_id}`} className="border border-[#c6c6cd]/50 rounded-lg p-4 space-y-3"><div className="flex items-start justify-between gap-3"><div className="flex items-center gap-2"><span className={`text-[10px] px-2 py-1 rounded-full border font-bold ${riskClasses[risk]}`}>{riskLabel(risk)}</span>{index > 0 && <ArrowDown className="w-3.5 h-3.5 text-[#b87500]" />}</div></div><p className="text-xs font-semibold text-[#0b1c30]">{finding.statement}</p><div className="bg-[#f8f9ff] border-l-2 border-[#b87500]/50 rounded-r p-3 flex items-start gap-2"><FileText className="w-3.5 h-3.5 text-[#76777d] shrink-0 mt-0.5" /><p className="text-[11px] text-[#45464d] font-merriweather leading-relaxed">{finding.excerpt}</p></div></article>; })}</div>}</div>}</div>
        </div>}
    </section>
  );
}
