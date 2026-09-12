"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertTriangle, Check, ChevronRight, Clock3, FileText, GitBranch, Loader2, RefreshCw, ShieldCheck, X } from "lucide-react";
import { realApiClient, RealApiError } from "@/services/realApiClient";
import type { BackendCanonChangeImpact, BackendCanonChangeProposal, BackendCanonicalFact } from "@/types/api";
import { useProjectStore } from "@/lib/useProjectStore";

const STATUS_LABELS: Record<BackendCanonChangeProposal["status"], string> = { proposed: "À vérifier", accepted: "Confirmée", rejected: "Écartée", deferred: "À revoir plus tard" };
const STATUS_CLASSES: Record<BackendCanonChangeProposal["status"], string> = {
  proposed: "bg-[#ffddb8] text-[#2a1700]",
  accepted: "bg-[#d3e4fe] text-[#0b1c30]",
  rejected: "bg-[#f3d7d7] text-[#5c2020]",
  deferred: "bg-[#ececf0] text-[#45464d]",
};

function errorText(error: unknown, fallback: string): string {
  if (error instanceof RealApiError) return error.message;
  return fallback;
}

export function CanonChangeProposalPanel() {
  const { project } = useProjectStore();
  const [facts, setFacts] = useState<BackendCanonicalFact[]>([]);
  const [proposals, setProposals] = useState<BackendCanonChangeProposal[]>([]);
  const [selectedFactId, setSelectedFactId] = useState("");
  const [selectedProposalId, setSelectedProposalId] = useState<string | null>(null);
  const [newStatement, setNewStatement] = useState("");
  const [newObject, setNewObject] = useState("");
  const [rationale, setRationale] = useState("");
  const [reviewRationale, setReviewRationale] = useState("");
  const [impact, setImpact] = useState<BackendCanonChangeImpact | null>(null);
  const [impactLoading, setImpactLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [reviewing, setReviewing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const selectedFact = useMemo(() => facts.find((fact) => fact.id === selectedFactId) ?? null, [facts, selectedFactId]);
  const selectedProposal = useMemo(() => proposals.find((proposal) => proposal.id === selectedProposalId) ?? null, [proposals, selectedProposalId]);

  const load = useCallback(async () => {
    if (!project.id) return;
    setLoading(true);
    setError(null);
    try {
      const [nextFacts, nextProposals] = await Promise.all([
        realApiClient.listCanonicalFacts(project.id),
        realApiClient.listCanonChangeProposals(project.id),
      ]);
      setFacts(nextFacts);
      setProposals(nextProposals);
      setSelectedFactId((current) => current && nextFacts.some((fact) => fact.id === current) ? current : nextFacts[0]?.id ?? "");
      setSelectedProposalId((current) => current && nextProposals.some((proposal) => proposal.id === current) ? current : nextProposals[0]?.id ?? null);
    } catch (err) {
      setError(errorText(err, "Impossible de charger les propositions de modification."));
    } finally {
      setLoading(false);
    }
  }, [project.id]);

  useEffect(() => { void load(); }, [load]);

  useEffect(() => {
    if (!selectedFact) return;
    setNewStatement(selectedFact.statement);
    setNewObject(selectedFact.object);
    setImpact(null);
  }, [selectedFact]);

  useEffect(() => { setImpact(null); }, [selectedProposalId]);

  const analyzeImpact = async (factId: string) => {
    if (!project.id) return;
    setImpactLoading(true);
    setError(null);
    try {
      setImpact(await realApiClient.analyzeCanonChange(project.id, factId));
    } catch (err) {
      setImpact(null);
      setError(errorText(err, "Impossible de mesurer l'impact de cette modification."));
    } finally {
      setImpactLoading(false);
    }
  };

  const handlePropose = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!project.id || !selectedFact || !newStatement.trim() || !newObject.trim()) return;
    if (newStatement.trim() === selectedFact.statement && newObject.trim() === selectedFact.object) {
      setError("La nouvelle version doit modifier au moins une information.");
      return;
    }
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const proposal = await realApiClient.proposeCanonChange(project.id, selectedFact.id, newStatement.trim(), newObject.trim(), rationale.trim());
      setProposals((current) => [proposal, ...current]);
      setSelectedProposalId(proposal.id);
      setRationale("");
      setSuccess("La proposition a été enregistrée. L'information confirmée actuelle n'a pas encore changé.");
    } catch (err) {
      setError(errorText(err, "Impossible de créer la proposition."));
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (decision: "accept" | "reject") => {
    if (!project.id || !selectedProposal) return;
    setReviewing(true);
    setError(null);
    setSuccess(null);
    try {
      await realApiClient.reviewCanonChange(project.id, selectedProposal.id, decision, reviewRationale.trim());
      setProposals((current) => current.map((proposal) => proposal.id === selectedProposal.id ? { ...proposal, status: decision === "accept" ? "accepted" : "rejected" } : proposal));
      setReviewRationale("");
      setSuccess(decision === "accept" ? "Proposition confirmée : une nouvelle version de l'information est maintenant active." : "Proposition écartée : l'information confirmée reste inchangée.");
      await load();
    } catch (err) {
      setError(err instanceof RealApiError && err.status === 409 ? "Cette proposition est devenue obsolète. Rechargez les propositions avant de décider." : errorText(err, "La décision n'a pas pu être enregistrée."));
    } finally {
      setReviewing(false);
    }
  };

  const activeProposals = proposals.filter((proposal) => proposal.status === "proposed");
  const impactFindings = impact?.findings ?? [];
  const directCount = impactFindings.filter((finding) => finding.risk === "high" || finding.dependency_depth === 1).length;
  const indirectCount = impactFindings.length - directCount;

  return (
    <section className="bg-white rounded-xl border border-[#c6c6cd]/40 overflow-hidden">
      <div className="p-4 sm:p-5 border-b border-[#c6c6cd]/20 flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-[#b87500]" /><span className="text-[10px] font-mono uppercase tracking-wider text-[#b87500]">Évolution de la continuité</span></div>
          <h2 className="font-playfair font-bold text-lg text-[#0b1c30] mt-1">Proposer une modification</h2>
          <p className="text-xs text-[#76777d] mt-1 max-w-2xl">Une modification commence par une proposition. Mesurez son impact avant de la soumettre, puis confirmez-la ou écartez-la sans modifier directement les informations de référence.</p>
        </div>
        <button onClick={() => void load()} disabled={loading || reviewing || impactLoading} className="p-2 rounded border border-[#c6c6cd]/40 hover:bg-[#eff4ff] disabled:opacity-50" aria-label="Actualiser les propositions"><RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} /></button>
      </div>

      {(error || success) && <div className={`mx-4 mt-4 p-3 rounded-lg border text-xs flex items-start gap-2 ${error ? "bg-[#fff4f4] border-[#d9aaaa] text-[#5c2020]" : "bg-[#f3fbf5] border-[#b8d7bd] text-[#24552d]"}`} role={error ? "alert" : "status"}>{error ? <AlertTriangle className="w-4 h-4 shrink-0" /> : <Check className="w-4 h-4 shrink-0" />}<span>{error || success}</span></div>}

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_1.1fr] divide-y lg:divide-y-0 lg:divide-x divide-[#c6c6cd]/20">
        <div className="p-4 sm:p-5 space-y-5">
          <div>
            <div className="flex items-center justify-between gap-2"><h3 className="text-xs font-bold text-[#0b1c30]">1. Choisir une information confirmée</h3><span className="text-[10px] text-[#76777d]">{facts.length} information{facts.length > 1 ? "s" : ""}</span></div>
            {facts.length === 0 ? <p className="text-xs text-[#76777d] mt-3">Aucune information confirmée à modifier.</p> : <div className="mt-3 space-y-2 max-h-64 overflow-y-auto">{facts.map((fact) => <button key={fact.id} type="button" onClick={() => setSelectedFactId(fact.id)} className={`w-full text-left p-3 rounded-lg border transition ${selectedFactId === fact.id ? "border-[#b87500]/50 bg-[#fff8f0]" : "border-[#c6c6cd]/30 hover:bg-[#f8f9ff]"}`}><div className="flex items-start gap-2"><span className="text-[10px] font-mono text-[#76777d]">v{fact.version}</span><span className="text-xs font-semibold text-[#0b1c30] leading-relaxed">{fact.statement}</span></div></button>)}</div>}
          </div>

          {selectedFact && <form onSubmit={handlePropose} className="border-t border-[#c6c6cd]/20 pt-5 space-y-3">
            <h3 className="text-xs font-bold text-[#0b1c30]">2. Décrire la nouvelle version</h3>
            <div className="rounded-lg bg-[#f8f9ff] p-3 text-[10px] text-[#45464d]">Actuel : <span className="font-semibold">{selectedFact.statement}</span></div>
            <label className="block"><span className="text-[10px] font-mono uppercase text-[#76777d]">Nouvelle formulation</span><textarea value={newStatement} onChange={(event) => setNewStatement(event.target.value)} rows={2} className="mt-1 w-full px-3 py-2 text-xs border border-[#c6c6cd] rounded-lg resize-y" required /></label>
            <label className="block"><span className="text-[10px] font-mono uppercase text-[#76777d]">Élément concerné</span><input value={newObject} onChange={(event) => setNewObject(event.target.value)} className="mt-1 w-full px-3 py-2 text-xs border border-[#c6c6cd] rounded-lg" required /></label>
            <label className="block"><span className="text-[10px] font-mono uppercase text-[#76777d]">Pourquoi cette modification ? <span className="normal-case">(optionnelle)</span></span><textarea value={rationale} onChange={(event) => setRationale(event.target.value)} rows={2} placeholder="Expliquez cette modification, si vous le souhaitez." className="mt-1 w-full px-3 py-2 text-xs border border-[#c6c6cd] rounded-lg resize-y" /></label>
            <button type="button" onClick={() => void analyzeImpact(selectedFact.id)} disabled={impactLoading || loading || reviewing || (newStatement.trim() === selectedFact.statement && newObject.trim() === selectedFact.object)} className="w-full px-3 py-2.5 border border-[#0b1c30] text-[#0b1c30] text-xs font-bold rounded-lg flex items-center justify-center gap-2 disabled:opacity-50">{impactLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <GitBranch className="w-3.5 h-3.5" />}Mesurer l'impact</button>
            <button type="submit" disabled={loading || reviewing || !newStatement.trim() || !newObject.trim()} className="w-full px-3 py-2.5 bg-[#0b1c30] text-white text-xs font-bold rounded-lg flex items-center justify-center gap-2 disabled:opacity-50"><ChevronRight className="w-3.5 h-3.5" />Créer la proposition</button>
          </form>}
        </div>

        <div className="p-4 sm:p-5 space-y-5">
          {impact && selectedFact && <div className="rounded-lg border border-[#c6c6cd]/40 bg-[#f8f9ff] p-4 space-y-3">
            <div className="flex items-center justify-between gap-3"><div><div className="text-[10px] font-mono uppercase text-[#b87500]">Impact de la modification</div><p className="text-xs font-semibold text-[#0b1c30] mt-1">{selectedFact.statement}</p></div><span className="text-[10px] font-mono text-[#76777d]">{impactFindings.length} élément{impactFindings.length > 1 ? "s" : ""}</span></div>
            <div className="grid grid-cols-2 gap-2"><div className="rounded bg-[#fff8f0] p-2.5"><div className="text-[9px] uppercase text-[#76777d]">Directs</div><div className="text-lg font-bold text-[#5c2020]">{directCount}</div></div><div className="rounded bg-white p-2.5"><div className="text-[9px] uppercase text-[#76777d]">Indirects</div><div className="text-lg font-bold text-[#0b1c30]">{indirectCount}</div></div></div>
            {impactFindings.length > 0 && <div className="space-y-2">{impactFindings.slice(0, 3).map((finding) => <div key={`${finding.fact_id}-${finding.assertion_id}`} className="border border-[#c6c6cd]/40 rounded p-2.5 bg-white"><div className="flex items-center gap-2"><span className="text-[9px] font-bold uppercase text-[#5c2020]">{finding.risk === "high" || finding.dependency_depth === 1 ? "Impact direct" : "Impact indirect"}</span><span className="text-[9px] font-mono text-[#76777d]">Niveau {finding.dependency_depth ?? "—"}</span></div><p className="text-[10px] font-semibold text-[#0b1c30] mt-1">{finding.statement}</p><div className="mt-1.5 flex items-start gap-1.5"><FileText className="w-3 h-3 text-[#76777d] shrink-0 mt-0.5" /><p className="text-[9px] text-[#45464d] leading-relaxed line-clamp-3">{finding.excerpt}</p></div></div>)}</div>}
            {impactFindings.length === 0 && <p className="text-[10px] text-[#76777d]">Aucun extrait de référence concerné n'a été trouvé.</p>}
            <p className="text-[9px] text-[#76777d]">L'analyse signale les liens explicites entre les informations, sans interprétation automatique.</p>
          </div>}

          <div><div className="flex items-center justify-between gap-2"><h3 className="text-xs font-bold text-[#0b1c30]">3. Revoir les propositions</h3><span className="text-[10px] font-mono text-[#76777d]">{activeProposals.length} à vérifier</span></div>{proposals.length === 0 ? <div className="mt-4 rounded-lg border border-dashed border-[#c6c6cd]/50 p-6 text-center text-xs text-[#76777d]">Les propositions de modification apparaîtront ici.</div> : <div className="mt-3 space-y-2 max-h-72 overflow-y-auto">{proposals.map((proposal) => <button key={proposal.id} type="button" onClick={() => setSelectedProposalId(proposal.id)} className={`w-full text-left p-3 rounded-lg border ${selectedProposalId === proposal.id ? "border-[#b87500]/50 bg-[#fff8f0]" : "border-[#c6c6cd]/30 hover:bg-[#f8f9ff]"}`}><div className="flex items-start justify-between gap-3"><span className="text-xs font-semibold text-[#0b1c30]">{proposal.statement}</span><span className={`shrink-0 text-[10px] px-2 py-1 rounded-full font-semibold ${STATUS_CLASSES[proposal.status]}`}>{STATUS_LABELS[proposal.status]}</span></div><div className="mt-2 text-[10px] text-[#76777d]">Élément proposé : <span className="font-semibold text-[#45464d]">{proposal.object}</span></div></button>)}</div>}</div>

          {selectedProposal && <div className="border-t border-[#c6c6cd]/20 pt-5 space-y-4">
            <div><div className="text-[10px] font-mono uppercase text-[#76777d]">Comparaison</div><div className="mt-2 grid gap-2"><div className="p-3 rounded-lg bg-[#f8f9ff]"><div className="text-[10px] text-[#76777d]">Version proposée</div><div className="text-xs font-semibold text-[#0b1c30] mt-1">{selectedProposal.statement}</div><div className="text-[10px] text-[#45464d] mt-1">{selectedProposal.subject} → {selectedProposal.predicate} → {selectedProposal.object}</div></div><div className="flex justify-center"><ChevronRight className="w-4 h-4 text-[#b87500] rotate-90" /></div><div className="p-3 rounded-lg border border-[#b87500]/20 bg-[#fffaf3]"><div className="text-[10px] text-[#76777d]">État</div><div className="text-xs font-semibold text-[#0b1c30] mt-1">{STATUS_LABELS[selectedProposal.status]}</div></div></div></div>
            {selectedProposal.status === "proposed" ? <div className="space-y-3"><button type="button" onClick={() => void analyzeImpact(selectedProposal.canonical_fact_id)} disabled={impactLoading || reviewing} className="w-full px-3 py-2 border border-[#c6c6cd] text-[#0b1c30] text-xs font-bold rounded-lg flex items-center justify-center gap-2 disabled:opacity-50">{impactLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <GitBranch className="w-3.5 h-3.5" />}Actualiser l'impact avant décision</button><label className="block"><span className="text-[10px] font-mono uppercase text-[#76777d]">Note de décision <span className="normal-case">(optionnelle)</span></span><textarea value={reviewRationale} onChange={(event) => setReviewRationale(event.target.value)} rows={2} placeholder="Expliquez votre décision, si vous le souhaitez." className="mt-1 w-full px-3 py-2 text-xs border border-[#c6c6cd] rounded-lg resize-y" /></label><div className="flex gap-2"><button onClick={() => void handleReview("accept")} disabled={reviewing} className="flex-1 px-3 py-2.5 bg-[#0b1c30] text-white text-xs font-bold rounded-lg flex items-center justify-center gap-1.5 disabled:opacity-50">{reviewing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}Confirmer</button><button onClick={() => void handleReview("reject")} disabled={reviewing} className="flex-1 px-3 py-2.5 border border-[#c6c6cd] text-[#5c2020] text-xs font-bold rounded-lg flex items-center justify-center gap-1.5 disabled:opacity-50"><X className="w-3.5 h-3.5" />Écarter</button></div></div> : <div className="flex items-center gap-2 text-xs text-[#45464d] bg-[#f8f9ff] rounded-lg p-3"><Clock3 className="w-4 h-4 shrink-0" />Cette proposition a déjà reçu une décision.</div>}
          </div>}
        </div>
      </div>
    </section>
  );
}