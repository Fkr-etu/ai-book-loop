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
  CheckCircle
} from "lucide-react";

export default function LorePage() {
  const { project, addLoreItem, deleteLoreItem } = useProjectStore();

  const [filterCategory, setFilterCategory] = useState<string>("all");
  const [isAdding, setIsAdding] = useState(false);
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState<"faction" | "location" | "artifact" | "rule">("artifact");
  const [description, setDescription] = useState("");

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    addLoreItem({
      title,
      category,
      description,
      importance: "high",
      canonStatus: "canonical"
    });
    setTitle("");
    setDescription("");
    setIsAdding(false);
  };

  const filteredItems =
    filterCategory === "all"
      ? project.loreItems
      : project.loreItems.filter((i) => i.category === filterCategory);

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
              La base de connaissances canoniques utilisées par les agents LLM pour prévenir les fausses notes et contradictions.
            </p>
          </div>

          <button
            onClick={() => setIsAdding(!isAdding)}
            className="px-4 py-2 bg-[#0b1c30] text-[#ffddb8] text-xs font-bold rounded hover:bg-[#131b2e] transition-colors flex items-center gap-2 shadow-xs shrink-0"
          >
            <Plus className="w-4 h-4" />
            <span>Ajouter une Entrée Canon</span>
          </button>
        </div>

        {/* Add Entry Form */}
        {isAdding && (
          <form
            onSubmit={handleAdd}
            className="p-6 bg-white rounded-xl border border-[#b87500]/40 shadow-sm space-y-4 animate-fadeIn"
          >
            <h2 className="text-sm font-mono font-bold text-[#0b1c30] uppercase">
              Nouvelle Fiche Lore Canonique
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
                className="px-4 py-1.5 text-xs font-bold bg-[#0b1c30] text-white rounded"
              >
                Verrouiller dans le Codex
              </button>
            </div>
          </form>
        )}

        {/* Category Filters */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-[#c6c6cd]/20">
          {[
            { id: "all", label: "Toutes les entrées" },
            { id: "artifact", label: "Artefacts & Reliques" },
            { id: "location", label: "Lieux & Cités" },
            { id: "faction", label: "Factions & Ordres" },
            { id: "rule", label: "Lois & Rituels" }
          ].map((f) => (
            <button
              key={f.id}
              onClick={() => setFilterCategory(f.id)}
              className={`px-3 py-1.5 rounded text-xs font-semibold whitespace-nowrap transition-colors ${
                filterCategory === f.id
                  ? "bg-[#0b1c30] text-white shadow-xs"
                  : "bg-white text-[#45464d] border border-[#c6c6cd]/40 hover:bg-[#eff4ff]"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Grid of Lore Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {filteredItems.map((item) => (
            <div
              key={item.id}
              className="p-5 bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs space-y-3 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#ffddb8] text-[#2a1700] font-bold">
                    {item.category}
                  </span>
                  <span className="text-[10px] font-mono text-[#b87500] font-bold flex items-center gap-1">
                    <CheckCircle className="w-3 h-3" /> Canon
                  </span>
                </div>

                <h3 className="font-playfair text-lg font-bold text-[#0b1c30]">
                  {item.title}
                </h3>
                <p className="text-xs text-[#45464d] font-merriweather leading-relaxed mt-2">
                  {item.description}
                </p>
              </div>

              <div className="pt-3 border-t border-[#c6c6cd]/20 flex items-center justify-between text-[11px] font-mono text-[#76777d]">
                <span>Niveau d'impact: Élevé</span>
                <button
                  onClick={() => deleteLoreItem(item.id)}
                  className="text-[#ba1a1a] hover:underline text-[10px]"
                >
                  Supprimer
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </StudioLayout>
  );
}
