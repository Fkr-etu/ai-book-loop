"use client";

import React, { useState } from "react";
import { StudioLayout } from "@/components/StudioLayout";
import { useProjectStore } from "@/lib/useProjectStore";
import {
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Sparkles,
  ShieldCheck,
  FileCheck,
  Check,
  XCircle,
  ArrowRight
} from "lucide-react";

export default function ValidationLoopPage() {
  const { project, runAiValidation } = useProjectStore();

  const activeScene = project.chapters[0]?.scenes[0];
  const [content, setContent] = useState(activeScene?.content || "");
  const [isEvaluating, setIsEvaluating] = useState(false);

  const handleTestRun = async () => {
    if (!activeScene) return;
    setIsEvaluating(true);
    await runAiValidation(activeScene.id, content);
    setIsEvaluating(false);
  };

  return (
    <StudioLayout>
      <div className="p-6 md:p-10 max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <div className="border-b border-[#c6c6cd]/30 pb-6">
          <span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider block mb-1 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-[#b87500]" /> Contrôle Créatif & Audit LLM
          </span>
          <h1 className="font-playfair text-3xl font-bold text-[#0b1c30]">
            Boucle de Validation & Critique
          </h1>
          <p className="text-xs text-[#45464d] mt-1">
            Chaque extrait passe par un filtre déterministe (Linter) puis une critique structurée. Si le score est ≥ 7 et sans interdictions, la scène est validée dans le Canon.
          </p>
        </div>

        {/* Interactive Validation Simulator */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
          {/* Left: Text Input for testing */}
          <div className="md:col-span-7 space-y-4">
            <div className="bg-white rounded-xl border border-[#c6c6cd]/40 p-5 shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-[#0b1c30] uppercase">
                  Brouillon à Tester ({activeScene?.title || "Scène 1.1"})
                </span>
                <span className="text-[10px] font-mono text-[#76777d]">
                  {content.length} caractères
                </span>
              </div>

              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                rows={10}
                className="w-full p-4 font-merriweather text-sm leading-relaxed border border-[#c6c6cd]/50 rounded bg-[#f8f5f0] focus:border-[#b87500] focus:outline-none"
              />

              <div className="flex justify-between items-center pt-2">
                <span className="text-[11px] text-[#76777d]">
                  Astuce: Insérez un mot moderne comme "robot" pour tester le rejet du linter.
                </span>
                <button
                  type="button"
                  onClick={handleTestRun}
                  disabled={isEvaluating}
                  className="px-4 py-2 bg-[#0b1c30] text-[#ffddb8] font-bold text-xs rounded hover:bg-[#131b2e] flex items-center gap-2 shadow-xs disabled:opacity-50"
                >
                  <Sparkles className={`w-3.5 h-3.5 ${isEvaluating ? "animate-spin" : ""}`} />
                  <span>{isEvaluating ? "Évaluation..." : "Lancer le Linter"}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Right: Validation Results */}
          <div className="md:col-span-5 space-y-4">
            <h2 className="text-xs font-mono font-bold text-[#76777d] uppercase tracking-wider">
              Historique des Revues ({project.reviews.length})
            </h2>

            <div className="space-y-4">
              {project.reviews.map((rev) => (
                <div
                  key={rev.id}
                  className={`p-5 rounded-xl bg-white border border-[#c6c6cd]/40 shadow-xs space-y-3 relative overflow-hidden border-l-4 ${
                    rev.approved ? "border-l-[#b87500]" : "border-l-[#ba1a1a]"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {rev.approved ? (
                        <CheckCircle2 className="w-4 h-4 text-[#b87500]" />
                      ) : (
                        <XCircle className="w-4 h-4 text-[#ba1a1a]" />
                      )}
                      <span className="text-xs font-bold text-[#0b1c30]">
                        {rev.approved ? "Accepté dans le Canon" : "Rejeté — Réécriture Requise"}
                      </span>
                    </div>
                    <span className="text-[10px] font-mono text-[#76777d]">
                      {rev.timestamp}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-center my-2">
                    <div className="p-2 bg-[#f8f9ff] rounded border border-[#c6c6cd]/20">
                      <div className="text-[10px] text-[#45464d]">Score Style</div>
                      <div className="text-base font-bold text-[#0b1c30]">
                        {rev.scoreStyle}/10
                      </div>
                    </div>
                    <div className="p-2 bg-[#f8f9ff] rounded border border-[#c6c6cd]/20">
                      <div className="text-[10px] text-[#45464d]">Cohérence Lore</div>
                      <div className="text-base font-bold text-[#0b1c30]">
                        {rev.scoreCoherence}/10
                      </div>
                    </div>
                  </div>

                  <p className="text-xs font-merriweather text-[#45464d] leading-normal bg-[#f8f5f0] p-3 rounded">
                    "{rev.critique}"
                  </p>

                  {rev.forbiddenPatternsFound.length > 0 && (
                    <div className="p-2 bg-[#ffdad6] text-[#93000a] text-xs rounded flex items-center gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                      <span>{rev.forbiddenPatternsFound.join(", ")}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </StudioLayout>
  );
}
