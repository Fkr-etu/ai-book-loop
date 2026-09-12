"use client";

import { useCallback, useEffect, useState } from "react";
import { AlertTriangle, Check, FileText, RefreshCw, Sparkles, X } from "lucide-react";
import { StudioLayout } from "@/components/StudioLayout";
import { CanonImpactPanel } from "@/components/CanonImpactPanel";
import { CanonChangeProposalPanel } from "@/components/CanonChangeProposalPanel";
import { ConsistencyAnalysisPanel } from "@/components/ConsistencyAnalysisPanel";
import { useProjectStore } from "@/lib/useProjectStore";
import type { Assertion } from "@/types";

const STATUS_LABELS: Record<Assertion["status"], string> = {
  proposed: "À vérifier",
  accepted: "Confirmée",
  rejected: "Écartée",
  deferred: "À revoir plus tard",
};
const STATUS_CLASSES: Record<Assertion["status"], string> = { proposed: "bg-[#ffddb8] text-[#2a1700]", accepted: "bg-[#d3e4fe] text-[#0b1c30]", rejected: "bg-[#f3d7d7] text-[#5c2020]", deferred: "bg-[#ececf0] text-[#45464d]" };

export default function CanonPage() {
  const store = useProjectStore();
  const [assertions, setAssertions] = useState<Assertion[]>([]);
  const [loadingAssertions, setLoadingAssertions] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [rationale, setRationale] = useState("");
  const [sourceName, setSourceName] = useState("");
  const [sourceContent, setSourceContent] = useState("");
  const [ingesting, setIngesting] = useState(false);
  const [pageError, setPageError] = useState<string | null>(null);

  const loadAssertions = useCallback(async () => {
    if (!store.project.id) return;
    setLoadingAssertions(true); setPageError(null);
    try {
      const data = await store.listAssertions();
      setAssertions(data);
      setSelectedId((current) => current && data.some((item) => item.id === current) ? current : data[0]?.id ?? null);
    } catch (error) {
      console.error("Error loading continuity proposals:", error);
      setPageError("Impossible de charger les propositions de continuité.");
    } finally { setLoadingAssertions(false); }
  }, [store.project.id, store.listAssertions]);

  useEffect(() => { void loadAssertions(); }, [loadAssertions]);

  const handleDecision = async (decision: "accept" | "reject" | "defer") => {
    if (!selectedId) return;
    try { await store.reviewAssertion(selectedId, decision, rationale.trim()); setRationale(""); await loadAssertions(); }
    catch (error) { console.error("Error reviewing continuity proposal:", error); setPageError("La décision n'a pas pu être enregistrée."); }
  };

  const handleIngest = async (event: React.FormEvent) => {
    event.preventDefault(); if (!sourceName.trim() || !sourceContent.trim()) return;
    setIngesting(true); setPageError(null);
    try { await store.ingestDocument(sourceName.trim(), sourceContent); setSourceName(""); setSourceContent(""); await loadAssertions(); }
    catch (error) { console.error("Error analyzing reference source:", error); setPageError("Le document n'a pas pu être analysé."); }
    finally { setIngesting(false); }
  };

  const selected = assertions.find((item) => item.id === selectedId) ?? null;
  const proposedCount = assertions.filter((item) => item.status === "proposed").length;
  const acceptedCount = assertions.filter((item) => item.status === "accepted").length;

  return (
    <StudioLayout>
      <div className="p-4 sm:p-6 md:p-10 max-w-6xl mx-auto space-y-6 md:space-y-8">
        <header className="border-b border-[#c6c6cd]/30 pb-6">
          <span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider">Continuité</span>
          <h1 className="font-playfair text-2xl sm:text-3xl font-bold text-[#0b1c30] mt-1">Continuité du livre</h1>
          <p className="text-xs text-[#45464d] mt-2 max-w-2xl">L'IA repère des informations dans vos sources. Vous décidez lesquelles deviennent des références fiables pour la suite de votre histoire.</p>
        </header>

        <ConsistencyAnalysisPanel bookId={store.project.id} />
        <CanonImpactPanel />
        <CanonChangeProposalPanel />

        {pageError && <div role="alert" className="p-3 bg-[#fff4f4] border border-[#d9aaaa] rounded-lg text-xs text-[#5c2020] flex items-start gap-2"><AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" /><span>{pageError}</span></div>}

        <section className="grid grid-cols-1 sm:grid-cols-3 gap-3" aria-label="État de la continuité">
          <div className="bg-white border border-[#c6c6cd]/40 rounded-xl p-4"><div className="text-[10px] font-mono uppercase text-[#76777d]">Informations à vérifier</div><div className="text-2xl font-bold text-[#0b1c30] mt-1">{proposedCount}</div></div>
          <div className="bg-white border border-[#c6c6cd]/40 rounded-xl p-4"><div className="text-[10px] font-mono uppercase text-[#76777d]">Informations confirmées</div><div className="text-2xl font-bold text-[#0b1c30] mt-1">{acceptedCount}</div></div>
          <div className="bg-[#fff8f0] border border-[#b87500]/30 rounded-xl p-4"><div className="text-[10px] font-mono uppercase text-[#76777d]">Principe</div><div className="text-xs font-semibold text-[#2a1700] mt-2">Une information n'est confirmée qu'après votre décision.</div></div>
        </section>

        <section className="bg-white rounded-xl border border-[#c6c6cd]/40 overflow-hidden">
          <div className="p-4 sm:p-5 border-b border-[#c6c6cd]/20 flex items-center justify-between gap-3"><div><h2 className="font-playfair font-bold text-lg text-[#0b1c30]">Informations repérées dans vos sources</h2><p className="text-xs text-[#76777d] mt-1">Vérifiez chaque information avant de l'utiliser comme référence pour votre livre.</p></div><button onClick={() => void loadAssertions()} disabled={loadingAssertions} className="p-2 rounded border border-[#c6c6cd]/40 hover:bg-[#eff4ff] disabled:opacity-50" aria-label="Actualiser les informations"><RefreshCw className={`w-4 h-4 ${loadingAssertions ? "animate-spin" : ""}`} /></button></div>
          {assertions.length === 0 && !loadingAssertions ? <div className="p-10 text-center"><FileText className="w-8 h-8 mx-auto text-[#b87500]" /><p className="text-sm font-semibold text-[#0b1c30] mt-3">Aucune information à vérifier</p><p className="text-xs text-[#76777d] mt-1">Ajoutez une source pour demander à l'IA d'en repérer les informations importantes.</p></div> : <div className="grid grid-cols-1 lg:grid-cols-[1fr_1.15fr] divide-y lg:divide-y-0 lg:divide-x divide-[#c6c6cd]/20">
            <div className="max-h-[620px] overflow-y-auto divide-y divide-[#c6c6cd]/20">{assertions.map((assertion) => <button key={assertion.id} onClick={() => setSelectedId(assertion.id)} className={`w-full text-left p-4 hover:bg-[#f8f9ff] ${selectedId === assertion.id ? "bg-[#eff4ff]" : ""}`}><div className="flex items-start justify-between gap-3"><span className="text-xs font-semibold text-[#0b1c30] leading-relaxed">{assertion.statement}</span><span className={`shrink-0 text-[10px] px-2 py-1 rounded-full font-semibold ${STATUS_CLASSES[assertion.status]}`}>{STATUS_LABELS[assertion.status]}</span></div><div className="flex items-center justify-between mt-3 text-[10px] text-[#76777d] font-mono"><span>{assertion.subject} → {assertion.predicate}</span><span>Fiabilité estimée {Math.round(assertion.confidence * 100)}%</span></div></button>)}</div>
            <div className="p-4 sm:p-6 min-h-[360px]">{selected ? <div className="space-y-5"><div><div className="flex flex-wrap items-center gap-2"><span className={`text-[10px] px-2 py-1 rounded-full font-semibold ${STATUS_CLASSES[selected.status]}`}>{STATUS_LABELS[selected.status]}</span><span className="text-[10px] text-[#76777d]">Fiabilité estimée : {Math.round(selected.confidence * 100)}%</span></div><h3 className="font-playfair text-xl font-bold text-[#0b1c30] mt-3">{selected.statement}</h3></div><div className="bg-[#f8f9ff] rounded-lg p-4"><p className="text-[10px] font-mono uppercase text-[#76777d]">Information repérée</p><p className="text-sm font-semibold text-[#0b1c30] mt-2">{selected.subject} {selected.predicate} {selected.object}</p><p className="text-xs text-[#76777d] mt-2">Ces détails servent à l'analyse interne ; vous pouvez vous concentrer sur la phrase ci-dessus pour décider si elle correspond à votre histoire.</p></div>{selected.status === "proposed" && <div className="space-y-3 border-t border-[#c6c6cd]/20 pt-5"><label className="block text-xs font-semibold text-[#0b1c30]" htmlFor="decision-rationale">Note de l'auteur <span className="font-normal text-[#76777d]">(optionnelle)</span></label><textarea id="decision-rationale" value={rationale} onChange={(event) => setRationale(event.target.value)} rows={3} placeholder="Ajoutez une note pour expliquer votre décision, si vous le souhaitez." className="w-full px-3 py-2 text-xs border border-[#c6c6cd] rounded-lg bg-white resize-y" /><div className="flex flex-wrap gap-2"><button onClick={() => void handleDecision("accept")} disabled={store.loading} className="px-3 py-2 text-xs font-bold bg-[#0b1c30] text-white rounded-lg flex items-center gap-1.5 disabled:opacity-50"><Check className="w-3.5 h-3.5" />Confirmer</button><button onClick={() => void handleDecision("reject")} disabled={store.loading} className="px-3 py-2 text-xs font-bold border border-[#c6c6cd] text-[#5c2020] rounded-lg flex items-center gap-1.5 disabled:opacity-50"><X className="w-3.5 h-3.5" />Écarter</button><button onClick={() => void handleDecision("defer")} disabled={store.loading} className="px-3 py-2 text-xs font-bold border border-[#c6c6cd] text-[#45464d] rounded-lg disabled:opacity-50">À revoir plus tard</button></div></div>}</div> : <div className="h-full min-h-[320px] flex items-center justify-center text-center text-xs text-[#76777d]">Sélectionnez une information pour l'examiner.</div>}</div>
          </div>}
        </section>

        <section className="bg-white rounded-xl border border-[#c6c6cd]/40 p-4 sm:p-6"><div className="flex items-start gap-3 mb-5"><Sparkles className="w-5 h-5 text-[#b87500] mt-0.5" /><div><h2 className="font-playfair font-bold text-lg text-[#0b1c30]">Ajouter une source de référence</h2><p className="text-xs text-[#76777d] mt-1">Book Loop lit le document et vous propose les informations qui pourraient servir de référence.</p></div></div><form onSubmit={handleIngest} className="space-y-3"><input value={sourceName} onChange={(event) => setSourceName(event.target.value)} placeholder="Nom de la source" className="w-full px-3 py-2 text-xs border border-[#c6c6cd] rounded-lg" required /><textarea value={sourceContent} onChange={(event) => setSourceContent(event.target.value)} placeholder="Contenu de la source à analyser…" rows={6} className="w-full px-3 py-2 text-xs border border-[#c6c6cd] rounded-lg resize-y" required /><div className="flex justify-end"><button type="submit" disabled={ingesting || !sourceName.trim() || !sourceContent.trim()} className="px-4 py-2 bg-[#0b1c30] text-white text-xs font-bold rounded-lg flex items-center gap-2 disabled:opacity-50"><Sparkles className="w-3.5 h-3.5 text-[#ffddb8]" />{ingesting ? "Lecture et analyse…" : "Analyser la source"}</button></div></form></section>
      </div>
    </StudioLayout>
  );
}
