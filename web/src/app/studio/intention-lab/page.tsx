"use client";

import React, { useState } from "react";
import { StudioLayout } from "@/components/StudioLayout";
import { useProjectStore } from "@/lib/useProjectStore";
import {
  Sliders,
  Sparkles,
  Plus,
  ShieldAlert,
  Zap,
  Lock,
  CheckCircle,
  ToggleLeft,
  ToggleRight
} from "lucide-react";

export default function IntentionLabPage() {
  const { project, toggleConstraint, addConstraint } = useProjectStore();

  const [newConstraintType, setNewConstraintType] = useState<"forbidden_word" | "pacing" | "tone" | "pov">("forbidden_word");
  const [newConstraintDesc, setNewConstraintDesc] = useState("");

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newConstraintDesc.trim()) return;
    addConstraint(newConstraintType, newConstraintDesc);
    setNewConstraintDesc("");
  };

  return (
    <StudioLayout>
      <div className="p-6 md:p-10 max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <div className="border-b border-[#c6c6cd]/30 pb-6">
          <span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider block mb-1 flex items-center gap-1.5">
            <Sliders className="w-4 h-4" /> Pilotage Créatif & Directives LLM
          </span>
          <h1 className="font-playfair text-3xl font-bold text-[#0b1c30]">
            Laboratoire d'Intention
          </h1>
          <p className="text-xs text-[#45464d] mt-1">
            Ajustez les contraintes stylistiques, les interdictions de vocabulaire et le ton de narration appliqués lors de la rédaction par l'IA.
          </p>
        </div>

        {/* Form Add Constraint */}
        <form
          onSubmit={handleAdd}
          className="p-6 bg-white rounded-xl border border-[#b87500]/40 shadow-xs space-y-4"
        >
          <h2 className="text-xs font-mono font-bold text-[#0b1c30] uppercase flex items-center gap-2">
            <Plus className="w-4 h-4 text-[#b87500]" />
            Ajouter une Nouvelle Contrainte Linter
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <select
              value={newConstraintType}
              onChange={(e) => setNewConstraintType(e.target.value as any)}
              className="px-3 py-2 text-xs border border-[#c6c6cd] rounded bg-[#f8f9ff]"
            >
              <option value="forbidden_word">Mots / Termes Interdits</option>
              <option value="tone">Ton & Registre Littéraire</option>
              <option value="pacing">Rythme & Descriptions</option>
              <option value="pov">Point de Vue (POV)</option>
            </select>
            <input
              type="text"
              placeholder="Ex: Ne pas utiliser de mots argotiques modernes"
              value={newConstraintDesc}
              onChange={(e) => setNewConstraintDesc(e.target.value)}
              required
              className="md:col-span-2 px-3 py-2 text-xs border border-[#c6c6cd] rounded bg-[#f8f9ff]"
            />
          </div>
          <div className="flex justify-end">
            <button
              type="submit"
              className="px-4 py-2 bg-[#0b1c30] text-[#ffddb8] text-xs font-bold rounded hover:bg-[#131b2e] flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Injecter la Contrainte</span>
            </button>
          </div>
        </form>

        {/* Active Constraints List */}
        <div className="space-y-4">
          <h2 className="text-xs font-mono font-bold text-[#76777d] uppercase tracking-wider">
            Directives Actives ({project.constraints.length})
          </h2>

          <div className="space-y-3">
            {project.constraints.map((c) => (
              <div
                key={c.id}
                className={`p-4 rounded-xl border transition-all flex items-center justify-between gap-4 ${
                  c.active
                    ? "bg-white border-[#c6c6cd]/40 shadow-xs"
                    : "bg-[#eff4ff]/40 border-[#c6c6cd]/20 opacity-60"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-8 h-8 rounded flex items-center justify-center shrink-0 ${
                      c.active
                        ? "bg-[#2a1700] text-[#ffddb8]"
                        : "bg-[#c6c6cd] text-white"
                    }`}
                  >
                    <ShieldAlert className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-[#0b1c30]">
                        {c.type === "forbidden_word"
                          ? "Terme Interdit"
                          : c.type === "tone"
                          ? "Registre de Langue"
                          : "Contrainte Narrative"}
                      </span>
                      <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-[#ffddb8] text-[#2a1700]">
                        Active
                      </span>
                    </div>
                    <p className="text-xs text-[#45464d] mt-1 font-merriweather">
                      {c.description}
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => toggleConstraint(c.id)}
                  className="p-1.5 text-[#0b1c30] hover:bg-[#eff4ff] rounded transition-colors shrink-0"
                  title="Activer/Désactiver"
                >
                  {c.active ? (
                    <ToggleRight className="w-6 h-6 text-[#b87500]" />
                  ) : (
                    <ToggleLeft className="w-6 h-6 text-[#76777d]" />
                  )}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </StudioLayout>
  );
}
