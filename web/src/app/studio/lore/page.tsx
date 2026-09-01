"use client";

import React, { useState } from "react";
import { StudioLayout } from "@/components/StudioLayout";
import { useProjectStore } from "@/lib/useProjectStore";
import {
  Compass,
  Plus,
  Shield,
  MapPin,
  Bookmark,
  Sparkles,
  Trash2,
  CheckCircle2,
  XCircle,
  Clock,
  Check,
  X
} from "lucide-react";

export default function LorePage() {
  const store = useProjectStore();
  const project = store.project;

  const [filterCategory, setFilterCategory] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");

  const [isAdding, setIsAdding] = useState(false);
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState<"faction" | "location" | "artifact" | "rule">("artifact");
  const [description, setDescription] = useState("");

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    await store.addLoreItem({
      title,
      category,
      description,
      importance: "high",
      canonStatus: "proposed",
      source: "Auteur"
    });
    setTitle("");
    setDescription("");
    setIsAdding(false);
  };

  const handleApproveLore = async (id: string) => {
    await store.updateLoreItem(id, { canonStatus: "canonical" });
  };

  const handleRejectLore = async (id: string) => {
    await store.updateLoreItem(id, { canonStatus: "rejected" });
  };

  const loreItemsList = project.loreItems || [];

  const filteredItems = loreItemsList.filter((item) => {
    const matchCat = filterCategory === "all" || item.category === filterCategory;
    const matchStat = filterStatus === "all" || item.canonStatus === filterStatus;
    return matchCat && matchStat;
  });

  return (
    <StudioLayout>
      <div className="p-6 md:p-10 max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#c6c6cd]/30 pb-6">
          <div>
            <span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider block mb-1">
              Bible du Monde & Continuité
            </span>
            <h1 className="font-playfair text-3xl font-bold text-[#0b1c30]">
              Ancrage du Lore & Codex
            </h1>
            <p className="text-xs text-[#45464d] mt-1">
              Seuls les éléments approuvés deviennent canoniques et servent de contexte aux générations suivantes.
            </p>
          </div>

          <button
            onClick={() => setIsAdding(!isAdding)}
            className="px-4 py-2 bg-[#0b1c30] text-[#ffddb8] text-xs font-bold rounded hover:bg-[#131b2e] transition-colors flex items-center gap-2 shadow-xs shrink-0 cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>Ajouter une Entrée Lore</span>
          </button>
        </div>

        {/* Add Entry Form */}
        {isAdding && (
          <form
            onSubmit={handleAdd}
            className="p-6 bg-white rounded-xl border border-[#b87500]/40 shadow-sm space-y-4 animate-fadeIn"
          >
            <h2 className="text-sm font-mono font-bold text-[#0b1c30] uppercase">
              Proposer une Nouvelle Fiche Lore (Proposé par Défaut)
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <input
                type="text"
                placeholder="Titre de l'entrée (ex: Citadelle de Cendres)"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                className="px-3 py-2 text-xs border border-[#c6c6cd] rounded bg-[#f8f9ff]"
              />
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value as any)}
                className="px-3 py-2 text-xs border border-[#c6c6cd] rounded bg-[#f8f9ff]"
              >
                <option value="artifact">Artefact / Relique</option>
                <option value="location">Lieu / Géographie</option>
                <option value="faction">Faction / Ordre / Guilde</option>
                <option value="rule">Règle de Magie / Lois de la Physique</option>
              </select>
            </div>
            <textarea
              placeholder="Description détaillée et règles d'utilisation par les mages..."
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full p-3 text-xs border border-[#c6c6cd] rounded bg-[#f8f9ff] font-merriweather"
            />
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setIsAdding(false)}
                className="px-3 py-1.5 text-xs text-[#45464d]"
              >
                Annuler
              </button>
              <button
                type="submit"
                className="px-4 py-1.5 text-xs font-bold bg-[#0b1c30] text-white rounded cursor-pointer"
              >
                Proposer au Codex
              </button>
            </div>
          </form>
        )}

        {/* Status & Category Filters */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#c6c6cd]/20 pb-3">
          <div className="flex items-center gap-2 overflow-x-auto">
            {[
              { id: "all", label: "Toutes les catégories" },
              { id: "artifact", label: "Artefacts & Reliques" },
              { id: "location", label: "Lieux & Cités" },
              { id: "faction", label: "Factions & Ordres" },
              { id: "rule", label: "Lois & Rituels" }
            ].map((f) => (
              <button
                key={f.id}
                onClick={() => setFilterCategory(f.id)}
                className={`px-3 py-1.5 rounded text-xs font-semibold whitespace-nowrap transition-colors cursor-pointer ${
                  filterCategory === f.id
                    ? "bg-[#0b1c30] text-white shadow-xs"
                    : "bg-white text-[#45464d] border border-[#c6c6cd]/40 hover:bg-[#eff4ff]"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2 font-mono text-xs">
            <span className="text-[#76777d] uppercase font-bold">Statut Canon:</span>
            {[
              { id: "all", label: "Tous" },
              { id: "canonical", label: "Canonique" },
              { id: "proposed", label: "Proposé" },
              { id: "rejected", label: "Rejeté" }
            ].map((s) => (
              <button
                key={s.id}
                onClick={() => setFilterStatus(s.id)}
                className={`px-2.5 py-1 rounded text-[11px] font-bold cursor-pointer ${
                  filterStatus === s.id
                    ? "bg-[#b87500] text-white"
                    : "bg-white text-[#45464d] border border-[#c6c6cd]/40"
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

        {/* Grid of Lore Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {filteredItems.map((item) => {
            const isCanon = item.canonStatus === "canonical";
            const isProposed = item.canonStatus === "proposed";
            const isRejected = item.canonStatus === "rejected";

            return (
              <div
                key={item.id}
                className="p-5 bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs space-y-3 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#ffddb8] text-[#2a1700] font-bold">
                      {item.category}
                    </span>
                    <span
                      className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full flex items-center gap-1 ${
                        isCanon
                          ? "bg-[#d3e4fe] text-[#0b1c30]"
                          : isRejected
                          ? "bg-[#ffdad6] text-[#ba1a1a]"
                          : "bg-[#fff8f0] text-[#b87500] border border-[#b87500]/30"
                      }`}
                    >
                      {isCanon ? (
                        <>
                          <CheckCircle2 className="w-3 h-3" /> Canonique
                        </>
                      ) : isRejected ? (
                        <>
                          <XCircle className="w-3 h-3" /> Rejeté
                        </>
                      ) : (
                        <>
                          <Clock className="w-3 h-3" /> Proposé — Approbation requise
                        </>
                      )}
                    </span>
                  </div>

                  <h3 className="font-playfair text-lg font-bold text-[#0b1c30]">
                    {item.title}
                  </h3>
                  <p className="text-xs text-[#45464d] font-merriweather leading-relaxed mt-2">
                    {item.description}
                  </p>

                  <div className="mt-3 text-[11px] font-mono text-[#76777d]">
                    Source: <strong className="text-[#0b1c30]">{item.source || "Auteur"}</strong>
                  </div>
                </div>

                <div className="pt-3 border-t border-[#c6c6cd]/20 flex items-center justify-between text-[11px] font-mono">
                  {isProposed ? (
                    <div className="flex items-center gap-2 w-full justify-between">
                      <button
                        onClick={() => handleApproveLore(item.id)}
                        className="px-2.5 py-1 bg-[#b87500] text-white font-bold rounded flex items-center gap-1 cursor-pointer"
                      >
                        <Check className="w-3 h-3" /> Approuver
                      </button>
                      <button
                        onClick={() => handleRejectLore(item.id)}
                        className="px-2.5 py-1 bg-[#ffdad6] text-[#ba1a1a] font-bold rounded flex items-center gap-1 cursor-pointer"
                      >
                        <X className="w-3 h-3" /> Rejeter
                      </button>
                    </div>
                  ) : (
                    <div className="flex items-center justify-between w-full">
                      <span className="text-[#5f5e5b]">Inclus dans le contexte: {isCanon ? "Oui" : "Non"}</span>
                      <button
                        onClick={() => store.deleteLoreItem(item.id)}
                        className="text-[#ba1a1a] hover:underline text-[10px] cursor-pointer"
                      >
                        Supprimer
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </StudioLayout>
  );
}
