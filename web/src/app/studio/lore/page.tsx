"use client";

import React, { useEffect, useState } from "react";
import { StudioLayout } from "@/components/StudioLayout";
import { useProjectStore } from "@/lib/useProjectStore";
import { Sparkles, FileText, Upload, Database, Check, X } from "lucide-react";
import { Assertion } from "@/types";

export default function LorePage() {
  const store = useProjectStore();
  const [showIngestForm, setShowIngestForm] = useState(false);
  const [docName, setDocName] = useState("");
  const [docContent, setDocContent] = useState("");
  const [isIngesting, setIsIngesting] = useState(false);
  const [assertions, setAssertions] = useState<Assertion[]>([]);

  useEffect(() => {
    store.listAssertions().then((list) => setAssertions(list || [])).catch(() => {});
  }, []);

  const handleIngestSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!docName || !docContent) return;
    setIsIngesting(true);
    try {
      const res = await store.ingestDocument(docName, docContent, "markdown");
      if (res.assertions) setAssertions((prev) => [...res.assertions!, ...prev]);
      setDocName("");
      setDocContent("");
      setShowIngestForm(false);
    } finally {
      setIsIngesting(false);
    }
  };

  const handleAssertionDecision = async (assertionId: string, decision: "accept" | "reject" | "defer") => {
    await store.reviewAssertion(assertionId, decision);
    setAssertions((prev) => prev.map((a) =>
      a.id === assertionId
        ? { ...a, status: decision === "accept" ? "accepted" : decision === "reject" ? "rejected" : "deferred" }
        : a
    ));
  };

  return (
    <StudioLayout>
      <div className="p-4 sm:p-6 md:p-10 max-w-6xl mx-auto space-y-6 md:space-y-8">
        <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#c6c6cd]/30 pb-6">
          <div>
            <span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider block mb-1">Bible du Monde & Ingestion Source</span>
            <h1 className="font-playfair text-2xl sm:text-3xl font-bold text-[#0b1c30]">Ancrage du Lore & Codex</h1>
            <p className="text-xs text-[#45464d] mt-1">Les sources produisent des assertions qui doivent être revues avant d'alimenter le Canon.</p>
          </div>
          <button type="button" onClick={() => setShowIngestForm((value) => !value)} className="px-3.5 py-2 bg-[#eff4ff] text-[#0b1c30] border border-[#c6c6cd]/40 text-xs font-bold rounded flex items-center justify-center gap-2 cursor-pointer">
            <Upload className="w-4 h-4 text-[#b87500]" /> Ingérer un Document Source
          </button>
        </header>

        {showIngestForm && (
          <form onSubmit={handleIngestSubmit} className="p-4 sm:p-6 bg-white rounded-xl border border-[#0b1c30]/40 shadow-xs space-y-4">
            <h2 className="text-xs font-mono font-bold text-[#0b1c30] uppercase flex items-center gap-2"><FileText className="w-4 h-4 text-[#b87500]" /> Ingestion de Document Source</h2>
            <input type="text" placeholder="Nom du document" value={docName} onChange={(e) => setDocName(e.target.value)} required className="w-full px-3 py-2 text-xs border border-[#c6c6cd] rounded bg-[#f8f9ff]" />
            <textarea placeholder="Collez ici le contenu source..." rows={6} value={docContent} onChange={(e) => setDocContent(e.target.value)} required className="w-full p-3 text-xs border border-[#c6c6cd] rounded bg-[#f8f9ff] font-merriweather" />
            <div className="flex justify-end gap-2">
              <button type="button" onClick={() => setShowIngestForm(false)} className="px-3 py-1.5 text-xs text-[#45464d]">Annuler</button>
              <button type="submit" disabled={isIngesting} className="px-4 py-1.5 text-xs font-bold bg-[#0b1c30] text-[#ffddb8] rounded disabled:opacity-50 flex items-center gap-1.5"><Sparkles className={`w-3.5 h-3.5 ${isIngesting ? "animate-spin" : ""}`} /> {isIngesting ? "Analyse & Découpage..." : "Ingérer & Extraire les Assertions"}</button>
            </div>
          </form>
        )}

        {assertions.length > 0 && (
          <section className="p-4 sm:p-5 bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs space-y-4">
            <div className="border-b border-[#c6c6cd]/20 pb-3 flex items-center gap-1.5 text-xs font-mono font-bold text-[#0b1c30] uppercase"><Database className="w-4 h-4 text-[#b87500]" /> Assertions Extraites à Revoir ({assertions.length})</div>
            <div className="divide-y divide-[#c6c6cd]/20">
              {assertions.map((ast) => {
                const isAccepted = ast.status === "accepted";
                const isRejected = ast.status === "rejected";
                return <div key={ast.id} className="py-3 flex flex-col md:flex-row md:items-center justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex flex-wrap items-center gap-2"><span className="text-xs font-bold text-[#0b1c30]">{ast.statement}</span><span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#eff4ff]">Confiance: {Math.round(ast.confidence * 100)}%</span><span className="text-[10px] font-mono px-2 py-0.5 rounded uppercase font-bold">{ast.status}</span></div>
                    <p className="text-[11px] text-[#45464d] font-mono">Sujet: <strong>{ast.subject}</strong> | Prédicat: <strong>{ast.predicate}</strong> | Objet: <strong>{ast.object}</strong></p>
                  </div>
                  {ast.status === "proposed" && <div className="flex items-center gap-2 shrink-0"><button type="button" onClick={() => handleAssertionDecision(ast.id, "accept")} className="px-2.5 py-1 bg-[#b87500] text-white font-bold text-[11px] rounded flex items-center gap-1"><Check className="w-3.5 h-3.5" /> Accepter (Canon)</button><button type="button" onClick={() => handleAssertionDecision(ast.id, "reject")} className="px-2.5 py-1 bg-[#ffdad6] text-[#ba1a1a] font-bold text-[11px] rounded flex items-center gap-1"><X className="w-3.5 h-3.5" /> Rejeter</button></div>}
                </div>;
              })}
            </div>
          </section>
        )}

        <div className="p-4 sm:p-5 bg-[#f8f9ff] rounded-xl border border-[#c6c6cd]/30 text-xs text-[#45464d]">La gestion structurée des personnages et des éléments de lore sera ajoutée ultérieurement avec un contrat API dédié.</div>
      </div>
    </StudioLayout>
  );
}
