"use client";

import React, { useState } from "react";
import { StudioLayout } from "@/components/StudioLayout";
import { useProjectStore } from "@/lib/useProjectStore";
import {
  Users,
  Plus,
  User,
  Shield,
  Key,
  Heart,
  Trash2,
  CheckCircle2,
  Tag,
  BookOpen
} from "lucide-react";

export default function CharactersPage() {
  const store = useProjectStore();
  const project = store.project;

  const charactersList = project.characters || [];

  const [selectedCharId, setSelectedCharId] = useState(
    charactersList[0]?.id || ""
  );

  const activeChar =
    charactersList.find((c) => c.id === selectedCharId) || charactersList[0];

  const [isCreating, setIsCreating] = useState(false);
  const [newCharName, setNewCharName] = useState("");
  const [newCharRole, setNewCharRole] = useState("Protagoniste");
  const [newCharArchetype, setNewCharArchetype] = useState("");
  const [newCharPsychology, setNewCharPsychology] = useState("");
  const [newCharGoal, setNewCharGoal] = useState("");
  const [newCharSecret, setNewCharSecret] = useState("");

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCharName.trim()) return;
    await store.addCharacter({
      name: newCharName,
      role: newCharRole,
      archetype: newCharArchetype || "Archétype Littéraire",
      psychology: newCharPsychology,
      goal: newCharGoal,
      secret: newCharSecret,
      status: "proposed",
      traits: ["Déterminé"],
      canonicalFacts: [],
      source: "Auteur"
    });
    setNewCharName("");
    setNewCharArchetype("");
    setNewCharPsychology("");
    setNewCharGoal("");
    setNewCharSecret("");
    setIsCreating(false);
  };

  return (
    <StudioLayout>
      <div className="p-6 md:p-10 max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#c6c6cd]/30 pb-6">
          <div>
            <span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider block mb-1">
              Psychologie & Motivation
            </span>
            <h1 className="font-playfair text-3xl font-bold text-[#0b1c30]">
              Éditeur de Personnages Profonds
            </h1>
            <p className="text-xs text-[#45464d] mt-1">
              Les personnages sont des objets du canon. Définissez leurs faits canoniques et traits psychologiques.
            </p>
          </div>

          <button
            onClick={() => setIsCreating(!isCreating)}
            className="px-4 py-2 bg-[#0b1c30] text-[#ffddb8] text-xs font-bold rounded hover:bg-[#131b2e] transition-colors flex items-center gap-2 shadow-xs shrink-0 cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>Nouveau Personnage</span>
          </button>
        </div>

        {/* Create Character Form Modal / Panel */}
        {isCreating && (
          <form
            onSubmit={handleCreate}
            className="p-6 bg-white rounded-xl border border-[#b87500]/40 shadow-sm space-y-4 animate-fadeIn"
          >
            <h2 className="text-sm font-mono font-bold text-[#0b1c30] uppercase">
              Création d'un Profil de Personnage (Canon)
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <input
                type="text"
                placeholder="Nom complet (ex: Lyra Vane)"
                value={newCharName}
                onChange={(e) => setNewCharName(e.target.value)}
                required
                className="px-3 py-2 text-xs border border-[#c6c6cd] rounded bg-[#f8f9ff]"
              />
              <select
                value={newCharRole}
                onChange={(e) => setNewCharRole(e.target.value)}
                className="px-3 py-2 text-xs border border-[#c6c6cd] rounded bg-[#f8f9ff]"
              >
                <option value="Protagoniste">Protagoniste</option>
                <option value="Antagoniste">Antagoniste</option>
                <option value="Allié Majeur">Allié Majeur</option>
                <option value="Secondaire">Personnage Secondaire</option>
              </select>
              <input
                type="text"
                placeholder="Archétype (ex: Le Savant Maudit)"
                value={newCharArchetype}
                onChange={(e) => setNewCharArchetype(e.target.value)}
                className="px-3 py-2 text-xs border border-[#c6c6cd] rounded bg-[#f8f9ff]"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <textarea
                placeholder="Psychologie & Faiblesses..."
                rows={3}
                value={newCharPsychology}
                onChange={(e) => setNewCharPsychology(e.target.value)}
                className="p-3 text-xs border border-[#c6c6cd] rounded bg-[#f8f9ff]"
              />
              <textarea
                placeholder="Objectif & Désir Inconscient..."
                rows={3}
                value={newCharGoal}
                onChange={(e) => setNewCharGoal(e.target.value)}
                className="p-3 text-xs border border-[#c6c6cd] rounded bg-[#f8f9ff]"
              />
              <textarea
                placeholder="Secret Canonique ou Fardeau..."
                rows={3}
                value={newCharSecret}
                onChange={(e) => setNewCharSecret(e.target.value)}
                className="p-3 text-xs border border-[#c6c6cd] rounded bg-[#f8f9ff]"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setIsCreating(false)}
                className="px-3 py-1.5 text-xs text-[#45464d] border border-[#c6c6cd] rounded hover:bg-[#eff4ff]"
              >
                Annuler
              </button>
              <button
                type="submit"
                className="px-4 py-1.5 text-xs font-bold bg-[#0b1c30] text-white rounded hover:bg-[#131b2e] cursor-pointer"
              >
                Enregistrer le Profil
              </button>
            </div>
          </form>
        )}

        {/* MAIN LAYOUT: LEFT CHARACTER CARDS - RIGHT DETAIL EDITOR */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
          {/* Left Cards List */}
          <div className="md:col-span-4 space-y-3">
            <span className="text-xs font-mono font-bold text-[#76777d] uppercase tracking-wider block">
              Casting du Récit ({charactersList.length})
            </span>
            {charactersList.map((char) => {
              const isSelected = activeChar?.id === char.id;
              return (
                <button
                  key={char.id}
                  onClick={() => setSelectedCharId(char.id)}
                  className={`w-full p-4 rounded-xl text-left transition-all border cursor-pointer ${
                    isSelected
                      ? "bg-[#0b1c30] text-white border-[#0b1c30] shadow-sm"
                      : "bg-white text-[#0b1c30] border-[#c6c6cd]/40 hover:bg-[#eff4ff]"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-playfair text-base font-bold truncate">
                      {char.name}
                    </span>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                        isSelected
                          ? "bg-[#ffddb8] text-[#2a1700]"
                          : "bg-[#d3e4fe] text-[#0b1c30]"
                      }`}
                    >
                      {char.role}
                    </span>
                  </div>
                  <p
                    className={`text-xs font-mono truncate ${
                      isSelected ? "text-[#7c839b]" : "text-[#5f5e5b]"
                    }`}
                  >
                    {char.archetype}
                  </p>
                </button>
              );
            })}
          </div>

          {/* Right Detail Card */}
          {activeChar && (
            <div className="md:col-span-8 bg-white rounded-xl border border-[#c6c6cd]/40 p-6 shadow-xs space-y-6">
              <div className="flex items-start justify-between border-b border-[#c6c6cd]/30 pb-4">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-[#0b1c30] text-[#ffddb8] font-playfair font-bold text-xl flex items-center justify-center">
                    {activeChar.name.charAt(0)}
                  </div>
                  <div>
                    <h2 className="font-playfair text-2xl font-bold text-[#0b1c30]">
                      {activeChar.name}
                    </h2>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs font-mono text-[#b87500] font-bold">
                        {activeChar.role} • {activeChar.archetype}
                      </span>
                      <span className="text-[10px] font-mono bg-[#d3e4fe] text-[#0b1c30] px-2 py-0.5 rounded-full font-semibold">
                        Provenance: {activeChar.source || "Auteur"}
                      </span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => store.deleteCharacter(activeChar.id)}
                  className="p-2 text-[#ba1a1a] hover:bg-[#ffdad6] rounded transition-colors cursor-pointer"
                  title="Supprimer ce personnage"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              {/* Traits & Canonical Facts Badges */}
              {(activeChar.traits || []).length > 0 && (
                <div className="space-y-1.5">
                  <span className="text-xs font-mono font-bold text-[#76777d] uppercase flex items-center gap-1">
                    <Tag className="w-3.5 h-3.5 text-[#b87500]" /> Traits de Caractère
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {(activeChar.traits || []).map((t, idx) => (
                      <span
                        key={idx}
                        className="text-xs font-mono bg-[#f8f5f0] text-[#0b1c30] border border-[#c6c6cd]/30 px-2.5 py-1 rounded"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Psychological Profile Attributes */}
              <div className="grid grid-cols-1 gap-4">
                <div className="p-4 bg-[#f8f5f0] rounded-lg border border-[#c6c6cd]/30 space-y-1">
                  <div className="text-xs font-mono font-bold text-[#0b1c30] flex items-center gap-2">
                    <User className="w-4 h-4 text-[#b87500]" />
                    Psychologie & Profil Cognitif
                  </div>
                  <p className="text-xs text-[#0f172a] font-merriweather leading-relaxed">
                    {activeChar.psychology || "Aucune description psychologique renseignée."}
                  </p>
                </div>

                <div className="p-4 bg-[#f8f5f0] rounded-lg border border-[#c6c6cd]/30 space-y-1">
                  <div className="text-xs font-mono font-bold text-[#0b1c30] flex items-center gap-2">
                    <Heart className="w-4 h-4 text-[#b87500]" />
                    Quête Dramatique & Désir Majeur
                  </div>
                  <p className="text-xs text-[#0f172a] font-merriweather leading-relaxed">
                    {activeChar.goal || "Aucun objectif renseigné."}
                  </p>
                </div>

                <div className="p-4 bg-[#2a1700] text-[#ffddb8] rounded-lg border border-[#b87500] space-y-1">
                  <div className="text-xs font-mono font-bold text-[#ffddb8] flex items-center gap-2">
                    <Key className="w-4 h-4 text-[#ffddb8]" />
                    Secret Canonique
                  </div>
                  <p className="text-xs font-merriweather leading-relaxed">
                    {activeChar.secret || "Aucun secret canonique verrouillé."}
                  </p>
                </div>

                {(activeChar.canonicalFacts || []).length > 0 && (
                  <div className="p-4 bg-white rounded-lg border border-[#c6c6cd]/30 space-y-2">
                    <div className="text-xs font-mono font-bold text-[#0b1c30] flex items-center gap-2">
                      <BookOpen className="w-4 h-4 text-[#b87500]" />
                      Faits Canoniques Inviolables
                    </div>
                    <ul className="list-disc list-inside text-xs font-merriweather text-[#45464d] space-y-1">
                      {(activeChar.canonicalFacts || []).map((fact, idx) => (
                        <li key={idx}>{fact}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </StudioLayout>
  );
}
