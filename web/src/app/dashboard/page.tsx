"use client";

import React from "react";
import Link from "next/link";
import { Navbar } from "@/components/Navbar";
import { useProjectStore } from "@/lib/useProjectStore";
import {
  BookOpen,
  Plus,
  ArrowRight,
  Sparkles,
  BarChart3,
  Feather,
  CheckCircle2,
  Clock,
  Layers,
  ShieldCheck
} from "lucide-react";

export default function DashboardPage() {
  const { project } = useProjectStore();

  const userProjects = [
    {
      id: project.id,
      title: project.title,
      subtitle: project.subtitle || "Chronique des Chronomanciens",
      genre: project.genre || "Dark Fantasy",
      words: project.currentWordCount || 24500,
      targetWords: project.wordCountTarget || 80000,
      chaptersCount: (project.chapters || []).length,
      updatedAt: "Il y a 10 min",
      status: "En rédaction active",
      isCurrent: true
    },
    {
      id: "proj-002",
      title: "Les Ombres d'Aethelgard",
      subtitle: "Tome II - L'Héritage des Arcanes",
      genre: "High Fantasy",
      words: 42000,
      targetWords: 90000,
      chaptersCount: 6,
      updatedAt: "Hier à 18:45",
      status: "En attente de relecture",
      isCurrent: false
    },
    {
      id: "proj-003",
      title: "Le Silencieux de Procyon",
      subtitle: "Hard Science-Fiction",
      genre: "Sci-Fi",
      words: 15400,
      targetWords: 60000,
      chaptersCount: 3,
      updatedAt: "Il y a 3 jours",
      status: "Brouillon initial",
      isCurrent: false
    }
  ];

  return (
    <div className="min-h-screen bg-[#f8f5f0] text-[#0f172a] font-inter">
      <Navbar />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-6 md:py-10 space-y-8">
        {/* Header Hero */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#c6c6cd]/30 pb-6">
          <div>
            <span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider block mb-1 flex items-center gap-1.5">
              <Feather className="w-4 h-4 text-[#b87500]" /> Espace Auteur Pro
            </span>
            <h1 className="font-playfair text-2xl md:text-3xl font-bold text-[#0b1c30]">
              Bibliothèque & Tableau de Bord
            </h1>
            <p className="text-xs text-[#45464d] mt-1">
              Gérez l'ensemble de vos œuvres, suivez vos statistiques de rédaction et accédez directement aux ateliers.
            </p>
          </div>

          <Link
            href="/setup"
            className="px-5 py-2.5 bg-[#0b1c30] text-[#ffddb8] font-bold text-xs rounded hover:bg-[#131b2e] transition-colors flex items-center justify-center gap-2 shadow-xs shrink-0 w-full sm:w-auto"
          >
            <Plus className="w-4 h-4" />
            <span>Nouveau Livre</span>
          </Link>
        </div>

        {/* Global Analytics Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs space-y-1">
            <div className="text-[10px] font-mono text-[#76777d] uppercase font-bold">Livres Actifs</div>
            <div className="text-2xl font-bold text-[#0b1c30] font-mono">3 Romans</div>
            <p className="text-[11px] text-[#5f5e5b]">1 en cours de rédaction</p>
          </div>

          <div className="p-5 bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs space-y-1">
            <div className="text-[10px] font-mono text-[#76777d] uppercase font-bold">Mots Totaux Rédigés</div>
            <div className="text-2xl font-bold text-[#0b1c30] font-mono">81 900 mots</div>
            <p className="text-[11px] text-[#b87500] font-semibold">+2 450 cette semaine</p>
          </div>

          <div className="p-5 bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs space-y-1">
            <div className="text-[10px] font-mono text-[#76777d] uppercase font-bold">Abonnement Studio</div>
            <div className="text-2xl font-bold text-[#0b1c30] font-mono flex items-center gap-1.5">
              Pro Architecte <Sparkles className="w-4 h-4 text-[#b87500]" />
            </div>
            <p className="text-[11px] text-[#5f5e5b]">Illimité avec IA Canon</p>
          </div>

          <div className="p-5 bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs space-y-1">
            <div className="text-[10px] font-mono text-[#76777d] uppercase font-bold">Score Qualité Linter</div>
            <div className="text-2xl font-bold text-[#b87500] font-mono">9.2 / 10</div>
            <p className="text-[11px] text-[#5f5e5b]">Continuité canonique 100%</p>
          </div>
        </div>

        {/* Projects Cards List */}
        <div className="space-y-4">
          <h2 className="text-xs font-mono font-bold text-[#76777d] uppercase tracking-wider">
            Vos Récits en Cours ({userProjects.length})
          </h2>

          <div className="grid grid-cols-1 gap-4">
            {userProjects.map((p) => {
              const progressPct = Math.round((p.words / p.targetWords) * 100);
              return (
                <div
                  key={p.id}
                  className={`p-5 sm:p-6 bg-white rounded-xl border transition-all shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-6 ${
                    p.isCurrent
                      ? "border-[#b87500] ring-1 ring-[#b87500]/30"
                      : "border-[#c6c6cd]/40 hover:border-[#c6c6cd]"
                  }`}
                >
                  <div className="space-y-2 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-xs font-mono px-2 py-0.5 rounded bg-[#ffddb8] text-[#2a1700] font-bold">
                        {p.genre}
                      </span>
                      {p.isCurrent && (
                        <span className="text-[10px] font-mono bg-[#0b1c30] text-white px-2 py-0.5 rounded font-bold">
                          PROJET ACTIF
                        </span>
                      )}
                      <span className="text-xs text-[#76777d] font-mono ml-auto sm:ml-0">
                        {p.updatedAt}
                      </span>
                    </div>

                    <h3 className="font-playfair text-xl md:text-2xl font-bold text-[#0b1c30]">
                      {p.title}
                    </h3>
                    <p className="font-courier text-xs text-[#5f5e5b]">
                      {p.subtitle}
                    </p>

                    <div className="pt-2 flex flex-wrap items-center gap-4 sm:gap-6 text-xs font-mono text-[#45464d]">
                      <span>{p.chaptersCount} Chapitres</span>
                      <span>
                        {p.words.toLocaleString()} / {p.targetWords.toLocaleString()} mots
                      </span>
                      <span className="text-[#b87500] font-bold">{progressPct}% complété</span>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full max-w-md bg-[#e5eeff] h-1.5 rounded-full overflow-hidden mt-2">
                      <div
                        className="bg-[#0b1c30] h-1.5 rounded-full"
                        style={{ width: `${progressPct}%` }}
                      />
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <Link
                      href="/studio"
                      className="w-full sm:w-auto px-5 py-2.5 bg-[#0b1c30] text-white font-semibold text-xs rounded hover:bg-[#131b2e] transition-colors flex items-center justify-center gap-2 shadow-xs"
                    >
                      <span>Ouvrir l'Atelier</span>
                      <ArrowRight className="w-3.5 h-3.5 text-[#ffddb8]" />
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </main>
    </div>
  );
}
