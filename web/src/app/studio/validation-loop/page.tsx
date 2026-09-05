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
  XCircle,
  Clock,
  Sliders,
  FileCheck
} from "lucide-react";

export default function ValidationLoopPage() {
  const store = useProjectStore();
  const project = store.project;

  const chaptersList = project.chapters || [];
  const reviewsList = project.reviews || [];

  const activeChapter = chaptersList[0];
  const [content, setContent] = useState(
    activeChapter?.versions?.[0]?.content || "L'encre fraîche n'a pas le même poids que l'oubli. Valerius glissa ses doigts calleux sur la surface glacée du Codex d'Obsidienne."
  );

  const [isEvaluating, setIsEvaluating] = useState(false);
  const [attemptCount, setAttemptCount] = useState(1);
  const maxAttempts = 3;

  const [lintResults, setLintIssues] = useState<{
    passed: boolean;
    anachronisms: string[];
    lengthValid: boolean;
  }>({
    passed: true,
    anachronisms: [],
    lengthValid: true
  });

  const handleRunLoop = async () => {
    setIsEvaluating(true);

    // 1. Deterministic Linter Step
    const lower = content.toLowerCase();
    const foundWords = ["ordinateur", "robot", "telephone", "internet", "wifi", "voiture"].filter((w) =>
      lower.includes(w)
    );
    const lengthOk = content.trim().length >= 30;
    const linterPassed = foundWords.length === 0 && lengthOk;

    setLintIssues({
      passed: linterPassed,
      anachronisms: foundWords,
      lengthValid: lengthOk
    });

    // 2. AI Review Step
    if (activeChapter) {
      await store.reviewChapter(activeChapter.number, activeChapter.currentVersion, content);
      setAttemptCount((prev) => Math.min(prev + 1, maxAttempts));
    }

    setIsEvaluating(false);
  };

  return (
    <StudioLayout>
      <div className="p-4 sm:p-6 md:p-10 max-w-5xl mx-auto space-y-6 md:space-y-8">
        {/* Header */}
        <div className="border-b border-[#c6c6cd]/30 pb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider block mb-1 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-[#b87500]" /> Contrôle Métier & Qualité
            </span>
            <h1 className="font-playfair text-2xl sm:text-3xl font-bold text-[#0b1c30]">
              Boucle de Validation (Linter + AI Review)
            </h1>
            <p className="text-xs text-[#45464d] mt-1">
              Chaque extrait est d'abord soumis au Linter Déterministe puis à la Critique IA avant l'entrée dans le Canon.
            </p>
          </div>

          <div className="px-3.5 py-2 bg-[#0b1c30] text-[#ffddb8] font-mono text-xs font-bold rounded border border-[#b87500] shrink-0 w-max">
            Tentative {attemptCount} / {maxAttempts}
          </div>
        </div>

        {/* Interactive Validation Simulator */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left: Text Input for testing */}
          <div className="lg:col-span-7 space-y-4">
            <div className="bg-white rounded-xl border border-[#c6c6cd]/40 p-4 sm:p-5 shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-[#0b1c30] uppercase">
                  Extrait à Tester (Chapitre {activeChapter?.number || 1})
                </span>
                <span className="text-[10px] font-mono text-[#76777d]">
                  {content.length} caractères
                </span>
              </div>

              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                rows={10}
                className="w-full p-3 sm:p-4 font-merriweather text-xs sm:text-sm leading-relaxed border border-[#c6c6cd]/50 rounded bg-[#f8f5f0] focus:border-[#b87500] focus:outline-none"
              />

              <div className="flex flex-col sm:flex-row justify-between items-center gap-3 pt-2">
                <span className="text-[11px] text-[#76777d]">
                  Insérez "robot" ou "wifi" pour déclencher le rejet du linter déterministe.
                </span>
                <button
                  type="button"
                  onClick={handleRunLoop}
                  disabled={isEvaluating}
                  className="w-full sm:w-auto px-4 py-2 bg-[#0b1c30] text-[#ffddb8] font-bold text-xs rounded hover:bg-[#131b2e] flex items-center justify-center gap-2 shadow-xs disabled:opacity-50 cursor-pointer shrink-0"
                >
                  <Sparkles className={`w-3.5 h-3.5 ${isEvaluating ? "animate-spin" : ""}`} />
                  <span>{isEvaluating ? "Évaluation..." : "Exécuter la Boucle"}</span>
                </button>
              </div>
            </div>

            {/* Step 1: Deterministic Linter Output Panel */}
            <div className="p-4 bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs space-y-2">
              <div className="flex items-center justify-between text-xs font-mono font-bold uppercase">
                <span className="flex items-center gap-1.5 text-[#0b1c30]">
                  <FileCheck className="w-4 h-4 text-[#b87500]" /> 1. Linter Déterministe
                </span>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] ${
                    lintResults.passed ? "bg-[#d3e4fe] text-[#0b1c30]" : "bg-[#ffdad6] text-[#ba1a1a]"
                  }`}
                >
                  {lintResults.passed ? "Conforme" : "Violation Détectée"}
                </span>
              </div>

              <div className="space-y-1.5 text-xs text-[#45464d] pt-1">
                <div className="flex items-center justify-between p-2 bg-[#f8f5f0] rounded">
                  <span>Vérification anachronismes modernes:</span>
                  <strong className={lintResults.anachronisms.length === 0 ? "text-[#b87500]" : "text-[#ba1a1a]"}>
                    {lintResults.anachronisms.length === 0 ? "Aucun" : lintResults.anachronisms.join(", ")}
                  </strong>
                </div>

                <div className="flex items-center justify-between p-2 bg-[#f8f5f0] rounded">
                  <span>Longueur minimale du texte:</span>
                  <strong className={lintResults.lengthValid ? "text-[#b87500]" : "text-[#ba1a1a]"}>
                    {lintResults.lengthValid ? "Valide" : "Insuffisante (< 30 car.)"}
                  </strong>
                </div>
              </div>
            </div>
          </div>

          {/* Right: AI Review Results */}
          <div className="lg:col-span-5 space-y-4">
            <h2 className="text-xs font-mono font-bold text-[#76777d] uppercase tracking-wider">
              2. Critique & Review IA ({reviewsList.length})
            </h2>

            <div className="space-y-4">
              {reviewsList.map((rev) => (
                <div
                  key={rev.id || Math.random()}
                  className={`p-4 sm:p-5 rounded-xl bg-white border border-[#c6c6cd]/40 shadow-xs space-y-3 relative overflow-hidden border-l-4 ${
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
                        {rev.approved ? "Proposition Acceptable" : "Décision: REJETÉ"}
                      </span>
                    </div>
                    <span className="text-[10px] font-mono text-[#76777d]">
                      {rev.timestamp || "À l'instant"}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-center my-2">
                    <div className="p-2 bg-[#f8f9ff] rounded border border-[#c6c6cd]/20">
                      <div className="text-[10px] text-[#45464d]">Score Qualité</div>
                      <div className="text-base font-bold text-[#0b1c30]">
                        {rev.score || 8}/10
                      </div>
                    </div>
                    <div className="p-2 bg-[#f8f9ff] rounded border border-[#c6c6cd]/20">
                      <div className="text-[10px] text-[#45464d]">Approbation</div>
                      <div className="text-xs font-bold text-[#b87500]">
                        {rev.approved ? "Approuvé" : "Rejeté"}
                      </div>
                    </div>
                  </div>

                  {(rev.issues || []).length > 0 && (
                    <div className="p-2.5 bg-[#ffdad6] text-[#93000a] text-xs rounded space-y-1">
                      <span className="font-bold flex items-center gap-1">
                        <AlertTriangle className="w-3.5 h-3.5" /> Issues identifiées:
                      </span>
                      <ul className="list-disc list-inside text-[11px] space-y-0.5">
                        {(rev.issues || []).map((iss, i) => (
                          <li key={i}>{iss}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {(rev.suggestions || []).length > 0 && (
                    <div className="p-2.5 bg-[#eff4ff] text-[#0b1c30] text-xs rounded space-y-1">
                      <span className="font-bold">Suggestions d'amélioration:</span>
                      <ul className="list-disc list-inside text-[11px] text-[#45464d] space-y-0.5">
                        {(rev.suggestions || []).map((sug, i) => (
                          <li key={i}>{sug}</li>
                        ))}
                      </ul>
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
