"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Feather,
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Check,
  Compass,
  Plus
} from "lucide-react";
import { useProjectStore } from "@/lib/useProjectStore";

export default function SetupPage() {
  const router = useRouter();
  const { project, updateProjectInfo, addLoreItem } = useProjectStore();

  const [step, setStep] = useState(1);

  const [title, setTitle] = useState(project.title);
  const [subtitle, setSubtitle] = useState(project.subtitle);
  const [genre, setGenre] = useState(project.genre);
  const [targetAudience, setTargetAudience] = useState(project.targetAudience);
  const [theme, setTheme] = useState(project.theme);
  const [loreSummary, setLoreSummary] = useState(project.loreSummary);
  const [styleTone, setStyleTone] = useState(project.styleTone);
  const [wordCountTarget, setWordCountTarget] = useState(project.wordCountTarget);

  const [newLoreTitle, setNewLoreTitle] = useState("");
  const [newLoreDesc, setNewLoreDesc] = useState("");
  const [newLoreCategory, setNewLoreCategory] = useState<"faction" | "location" | "artifact" | "rule">("artifact");

  const handleAddLore = () => {
    if (!newLoreTitle.trim()) return;
    addLoreItem({
      title: newLoreTitle,
      category: newLoreCategory,
      description: newLoreDesc,
      importance: "high",
      canonStatus: "canonical"
    });
    setNewLoreTitle("");
    setNewLoreDesc("");
  };

  const handleFinishSetup = () => {
    updateProjectInfo({
      title,
      subtitle,
      genre,
      targetAudience,
      theme,
      loreSummary,
      styleTone,
      wordCountTarget
    });
    router.push("/studio");
  };

  return (
    <div className="min-h-screen bg-[#f8f5f0] text-[#0f172a] flex flex-col justify-between font-inter selection:bg-[#ffddb8] selection:text-[#0f172a]">
      {/* Top Header */}
      <header className="px-8 py-4 bg-white/80 backdrop-blur border-b border-[#c6c6cd]/30 flex justify-between items-center sticky top-0 z-20">
        <Link href="/studio" className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-[#0b1c30] text-[#ffddb8] flex items-center justify-center">
            <Feather className="w-4 h-4" />
          </div>
          <span className="font-playfair font-bold text-lg text-[#0b1c30]">
            Manuscript Studio
          </span>
        </Link>
        <div className="text-xs font-mono text-[#76777d]">
          Assistant de Configuration de Récit • Étape {step} sur 3
        </div>
      </header>

      {/* Progress Bar */}
      <div className="w-full bg-[#e5eeff] h-1.5">
        <div
          className="bg-[#0b1c30] h-1.5 transition-all duration-300"
          style={{ width: `${(step / 3) * 100}%` }}
        />
      </div>

      <main className="flex-1 max-w-3xl w-full mx-auto p-6 md:p-10">
        <div className="bg-white rounded-xl border border-[#c6c6cd]/30 shadow-sm p-8">
          {/* STEP 1: Title, Genre, Theme */}
          {step === 1 && (
            <div className="space-y-6 animate-fadeIn">
              <div>
                <span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider block mb-1">
                  Étape 1 • Fondations Narratives
                </span>
                <h1 className="font-playfair text-2xl font-bold text-[#0b1c30]">
                  Titre, Genre & Thème du Livre
                </h1>
                <p className="text-xs text-[#45464d] mt-1">
                  Définissez la ligne directrice de votre œuvre. Ces éléments guideront la génération IA.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#0b1c30] mb-1">
                    Titre du Livre
                  </label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Ex: La Porte d'Obsidienne"
                    className="w-full px-3 py-2 text-sm border-b border-[#c6c6cd] focus:border-[#b87500] focus:outline-none bg-[#f8f9ff] rounded-t"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-[#0b1c30] mb-1">
                    Sous-titre / Tome
                  </label>
                  <input
                    type="text"
                    value={subtitle}
                    onChange={(e) => setSubtitle(e.target.value)}
                    placeholder="Ex: Chronique des Chronomanciens - Tome I"
                    className="w-full px-3 py-2 text-sm border-b border-[#c6c6cd] focus:border-[#b87500] focus:outline-none bg-[#f8f9ff] rounded-t"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#0b1c30] mb-1">
                    Genre Littéraire
                  </label>
                  <input
                    type="text"
                    value={genre}
                    onChange={(e) => setGenre(e.target.value)}
                    placeholder="Ex: Dark Fantasy / Sci-Fi"
                    className="w-full px-3 py-2 text-sm border-b border-[#c6c6cd] focus:border-[#b87500] focus:outline-none bg-[#f8f9ff] rounded-t"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-[#0b1c30] mb-1">
                    Objectif de Mots (Longueur)
                  </label>
                  <input
                    type="number"
                    value={wordCountTarget}
                    onChange={(e) => setWordCountTarget(Number(e.target.value))}
                    className="w-full px-3 py-2 text-sm border-b border-[#c6c6cd] focus:border-[#b87500] focus:outline-none bg-[#f8f9ff] rounded-t font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#0b1c30] mb-1">
                  Thème Central & Intentions Narratives
                </label>
                <textarea
                  rows={4}
                  value={theme}
                  onChange={(e) => setTheme(e.target.value)}
                  placeholder="Décrivez l'intention philosophique, les questions morales ou la dynamique principale du récit..."
                  className="w-full p-3 text-sm border border-[#c6c6cd]/60 focus:border-[#b87500] focus:outline-none bg-[#f8f9ff] rounded font-merriweather leading-relaxed"
                />
              </div>
            </div>
          )}

          {/* STEP 2: Lore & World Building */}
          {step === 2 && (
            <div className="space-y-6 animate-fadeIn">
              <div>
                <span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider block mb-1">
                  Étape 2 • Ancrage du Lore & Bible du Monde
                </span>
                <h1 className="font-playfair text-2xl font-bold text-[#0b1c30]">
                  Règles, Reliques et Lieux Canoniques
                </h1>
                <p className="text-xs text-[#45464d] mt-1">
                  Définissez le cadre dans lequel s'inscrivent vos personnages. L'IA respectera scrupuleusement ces règles.
                </p>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#0b1c30] mb-1">
                  Résumé Global du Lore / Contextualisation
                </label>
                <textarea
                  rows={3}
                  value={loreSummary}
                  onChange={(e) => setLoreSummary(e.target.value)}
                  placeholder="Ex: Dans l'Empire de Cendres, les mages utilisent l'Obsidienne pour capturer la mémoire..."
                  className="w-full p-3 text-sm border border-[#c6c6cd]/60 focus:border-[#b87500] focus:outline-none bg-[#f8f9ff] rounded font-merriweather text-xs"
                />
              </div>

              {/* Quick Add Lore Item */}
              <div className="p-4 bg-[#eff4ff] rounded-lg border border-[#c6c6cd]/30 space-y-3">
                <div className="flex items-center justify-between text-xs font-bold text-[#0b1c30]">
                  <span className="flex items-center gap-1.5">
                    <Compass className="w-4 h-4 text-[#b87500]" />
                    Ajouter un Élément Canonique Majeur
                  </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                  <input
                    type="text"
                    placeholder="Nom (ex: Citadelle de Cendres)"
                    value={newLoreTitle}
                    onChange={(e) => setNewLoreTitle(e.target.value)}
                    className="px-2.5 py-1.5 text-xs border border-[#c6c6cd] rounded bg-white"
                  />
                  <select
                    value={newLoreCategory}
                    onChange={(e) => setNewLoreCategory(e.target.value as any)}
                    className="px-2.5 py-1.5 text-xs border border-[#c6c6cd] rounded bg-white"
                  >
                    <option value="artifact">Artefact / Relique</option>
                    <option value="location">Lieu Majeur</option>
                    <option value="faction">Faction / Ordre</option>
                    <option value="rule">Règle de Magie / Loi</option>
                  </select>
                  <button
                    type="button"
                    onClick={handleAddLore}
                    className="bg-[#0b1c30] text-white text-xs font-semibold py-1.5 px-3 rounded hover:bg-[#131b2e] flex items-center justify-center gap-1"
                  >
                    <Plus className="w-3.5 h-3.5" /> Ajouter
                  </button>
                </div>
                <input
                  type="text"
                  placeholder="Description canonique..."
                  value={newLoreDesc}
                  onChange={(e) => setNewLoreDesc(e.target.value)}
                  className="w-full px-2.5 py-1.5 text-xs border border-[#c6c6cd] rounded bg-white"
                />
              </div>

              {/* Added Lore Preview */}
              <div>
                <h3 className="text-xs font-mono font-bold text-[#76777d] uppercase tracking-wider mb-2">
                  Éléments Enregistrés ({project.loreItems.length})
                </h3>
                <div className="space-y-2">
                  {project.loreItems.map((item) => (
                    <div
                      key={item.id}
                      className="p-3 bg-white rounded border border-[#c6c6cd]/40 flex items-start justify-between"
                    >
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-[#0b1c30]">
                            {item.title}
                          </span>
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#ffddb8] text-[#2a1700] font-mono">
                            {item.category}
                          </span>
                        </div>
                        <p className="text-xs text-[#45464d] mt-1">
                          {item.description}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* STEP 3: Style, Tone & IA Constraints */}
          {step === 3 && (
            <div className="space-y-6 animate-fadeIn">
              <div>
                <span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider block mb-1">
                  Étape 3 • Directives de Rédaction & Style
                </span>
                <h1 className="font-playfair text-2xl font-bold text-[#0b1c30]">
                  Ton, Voix Narrative & Verrouillage Canon
                </h1>
                <p className="text-xs text-[#45464d] mt-1">
                  Définissez la couleur littéraire et les interdits stylistiques pour le linter IA.
                </p>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#0b1c30] mb-1">
                  Style et Ton Général
                </label>
                <input
                  type="text"
                  value={styleTone}
                  onChange={(e) => setStyleTone(e.target.value)}
                  placeholder="Ex: Scholastique, poétique, sombre, rythme soutenu mais descriptif."
                  className="w-full px-3 py-2 text-sm border-b border-[#c6c6cd] focus:border-[#b87500] focus:outline-none bg-[#f8f9ff] rounded-t font-merriweather"
                />
              </div>

              <div className="p-4 bg-[#f8f5f0] rounded-lg border border-[#b87500]/30 space-y-3">
                <div className="flex items-center gap-2 text-xs font-bold text-[#2a1700]">
                  <Sparkles className="w-4 h-4 text-[#b87500]" />
                  Contraintes Automatiques du Linter IA Actives
                </div>
                <div className="space-y-2">
                  {project.constraints.map((c) => (
                    <div
                      key={c.id}
                      className="flex items-center justify-between text-xs bg-white p-2.5 rounded border border-[#c6c6cd]/30"
                    >
                      <span className="text-[#0b1c30]">{c.description}</span>
                      <span className="text-[10px] font-mono text-[#b87500] font-bold">
                        VERROUILLÉ
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="p-4 bg-[#eff4ff] rounded border border-[#c6c6cd]/30 text-xs text-[#0b1c30]">
                <strong>Félicitations !</strong> Le socle de votre roman est prêt.
                Vous allez être redirigé vers l'Atelier de Rédaction pour commencer la structuration des chapitres et la création des personnages.
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="mt-8 pt-6 border-t border-[#c6c6cd]/30 flex justify-between items-center">
            {step > 1 ? (
              <button
                type="button"
                onClick={() => setStep((s) => s - 1)}
                className="px-4 py-2 text-xs font-semibold text-[#0b1c30] border border-[#c6c6cd] rounded hover:bg-[#eff4ff] flex items-center gap-1.5 cursor-pointer"
              >
                <ArrowLeft className="w-3.5 h-3.5" /> Précédent
              </button>
            ) : (
              <div />
            )}

            {step < 3 ? (
              <button
                type="button"
                data-testid="next-step-btn"
                onClick={() => setStep((s) => s + 1)}
                className="px-5 py-2.5 text-xs font-semibold bg-[#0b1c30] text-white rounded hover:bg-[#131b2e] flex items-center gap-1.5 shadow-xs cursor-pointer"
              >
                <span>Suivant</span>
                <ArrowRight className="w-3.5 h-3.5 text-[#ffddb8]" />
              </button>
            ) : (
              <button
                type="button"
                onClick={handleFinishSetup}
                className="px-6 py-2.5 text-xs font-bold bg-[#0b1c30] text-[#ffddb8] rounded hover:bg-[#131b2e] flex items-center gap-2 shadow-sm cursor-pointer"
              >
                <Check className="w-4 h-4 text-[#ffddb8]" />
                <span>Ouvrir l'Atelier de Rédaction</span>
              </button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
