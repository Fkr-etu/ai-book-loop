"use client";

import React, { useState } from "react";
import { StudioLayout } from "@/components/StudioLayout";
import { useProjectStore } from "@/lib/useProjectStore";
import {
  Download,
  BookOpen,
  FileText,
  CheckCircle2,
  Sparkles,
  ShieldCheck,
  Share2,
  Printer,
  Sliders,
  Layers
} from "lucide-react";

export default function ExportPage() {
  const { project } = useProjectStore();

  const [exportFormat, setExportFormat] = useState<"markdown" | "epub" | "pdf" | "docx">("markdown");
  const [includeLoreAppendix, setIncludeLoreInclude] = useState(true);
  const [includeSummaries, setIncludeSummaries] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const chaptersList = project.chapters || [];
  const loreList = project.loreItems || [];

  const totalValidatedScenes = chaptersList.reduce(
    (acc, chap) => acc + (chap.scenes || []).filter((s) => s.status === "validated").length,
    0
  );

  const handleDownload = () => {
    setDownloading(true);

    setTimeout(() => {
      // Create downloadable manuscript blob
      let compiledText = `# ${project.title}\n## ${project.subtitle || ""}\n\n`;
      compiledText += `**Genre:** ${project.genre || ""}\n`;
      compiledText += `**Thème:** ${project.theme}\n\n`;
      compiledText += `---\n\n`;

      chaptersList.forEach((chap) => {
        compiledText += `# Chapitre ${chap.number}: ${chap.title}\n\n`;
        compiledText += `> *${chap.summary || ""}*\n\n`;
        (chap.scenes || []).forEach((sc) => {
          compiledText += `### ${sc.title}\n\n`;
          compiledText += `${sc.content || "(Brouillon non rédigé)"}\n\n`;
        });
      });

      if (includeLoreAppendix) {
        compiledText += `\n---\n# Annexe: Bible du Monde & Lore\n\n`;
        loreList.forEach((item) => {
          compiledText += `## ${item.title} (${item.category})\n${item.description}\n\n`;
        });
      }

      const blob = new Blob([compiledText], { type: "text/markdown;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `${project.title.toLowerCase().replace(/\s+/g, "_")}_manuscript.md`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      setDownloading(false);
    }, 800);
  };

  return (
    <StudioLayout>
      <div className="p-4 sm:p-6 md:p-10 max-w-6xl mx-auto space-y-6 md:space-y-8">
        {/* Header */}
        <div className="border-b border-[#c6c6cd]/30 pb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider block mb-1 flex items-center gap-1.5">
              <Download className="w-4 h-4 text-[#b87500]" /> Finalisation & Publication
            </span>
            <h1 className="font-playfair text-2xl sm:text-3xl font-bold text-[#0b1c30]">
              Studio d'Exportation
            </h1>
            <p className="text-xs text-[#45464d] mt-1">
              Compilez l'intégralité de vos chapitres et scènes validés au format d'édition de votre choix.
            </p>
          </div>

          <button
            onClick={handleDownload}
            disabled={downloading}
            className="w-full sm:w-auto px-5 py-2.5 bg-[#0b1c30] text-[#ffddb8] font-bold text-xs rounded hover:bg-[#131b2e] flex items-center justify-center gap-2 shadow-xs disabled:opacity-50 shrink-0 cursor-pointer"
          >
            <Download className={`w-4 h-4 ${downloading ? "animate-bounce" : ""}`} />
            <span>{downloading ? "Compilation..." : "Exporter le Manuscrit"}</span>
          </button>
        </div>

        {/* Audit Status Banner */}
        <div className="p-4 sm:p-5 bg-white rounded-xl border border-[#c6c6cd]/40 shadow-xs grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-center">
          <div className="p-3 bg-[#f8f5f0] rounded border border-[#c6c6cd]/20">
            <div className="text-[10px] font-mono text-[#76777d] uppercase">Scènes Validées</div>
            <div className="text-base sm:text-xl font-bold text-[#0b1c30] font-mono mt-1">
              {totalValidatedScenes} scènes
            </div>
          </div>
          <div className="p-3 bg-[#f8f5f0] rounded border border-[#c6c6cd]/20">
            <div className="text-[10px] font-mono text-[#76777d] uppercase">Nombre de Mots</div>
            <div className="text-base sm:text-xl font-bold text-[#0b1c30] font-mono mt-1 truncate">
              {(project.currentWordCount || 0).toLocaleString()} / {(project.wordCountTarget || 80000).toLocaleString()}
            </div>
          </div>
          <div className="p-3 bg-[#f8f5f0] rounded border border-[#c6c6cd]/20">
            <div className="text-[10px] font-mono text-[#76777d] uppercase">Statut Canon</div>
            <div className="text-base sm:text-xl font-bold text-[#b87500] font-mono mt-1 flex items-center justify-center gap-1">
              <CheckCircle2 className="w-4 h-4" /> Verrouillé
            </div>
          </div>
          <div className="p-3 bg-[#f8f5f0] rounded border border-[#c6c6cd]/20">
            <div className="text-[10px] font-mono text-[#76777d] uppercase">Fiches Lore Incluses</div>
            <div className="text-base sm:text-xl font-bold text-[#0b1c30] font-mono mt-1">
              {loreList.length} entrées
            </div>
          </div>
        </div>

        {/* Options & Preview Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 md:gap-8">
          {/* Options Form */}
          <div className="lg:col-span-5 space-y-6">
            <div className="bg-white rounded-xl border border-[#c6c6cd]/40 p-4 sm:p-6 shadow-xs space-y-5">
              <h2 className="text-xs font-mono font-bold text-[#0b1c30] uppercase border-b border-[#c6c6cd]/20 pb-2">
                1. Format de Fichier
              </h2>

              <div className="grid grid-cols-2 gap-2">
                {[
                  { id: "markdown", label: "Markdown Studio", ext: ".md", icon: FileText },
                  { id: "epub", label: "eBook EPUB 3.0", ext: ".epub", icon: BookOpen },
                  { id: "pdf", label: "PDF Print Pro", ext: ".pdf", icon: Printer },
                  { id: "docx", label: "Word DOCX", ext: ".docx", icon: FileText }
                ].map((fmt) => {
                  const Icon = fmt.icon;
                  const isSel = exportFormat === fmt.id;
                  return (
                    <button
                      key={fmt.id}
                      type="button"
                      onClick={() => setExportFormat(fmt.id as any)}
                      className={`p-3 rounded-lg border text-left transition-all cursor-pointer ${
                        isSel
                          ? "bg-[#0b1c30] text-white border-[#0b1c30] shadow-xs"
                          : "bg-white text-[#0b1c30] border-[#c6c6cd]/40 hover:bg-[#eff4ff]"
                      }`}
                    >
                      <Icon className={`w-4 h-4 mb-1 ${isSel ? "text-[#ffddb8]" : "text-[#b87500]"}`} />
                      <div className="text-xs font-bold">{fmt.label}</div>
                      <div className={`text-[10px] font-mono ${isSel ? "text-[#7c839b]" : "text-[#76777d]"}`}>
                        {fmt.ext}
                      </div>
                    </button>
                  );
                })}
              </div>

              <h2 className="text-xs font-mono font-bold text-[#0b1c30] uppercase border-b border-[#c6c6cd]/20 pb-2 pt-2">
                2. Structure de Compilation
              </h2>

              <div className="space-y-3 text-xs">
                <label className="flex items-center justify-between p-2.5 bg-[#f8f5f0] rounded border border-[#c6c6cd]/20 cursor-pointer">
                  <span>Inclure la Bible du Monde en Annexe</span>
                  <input
                    type="checkbox"
                    checked={includeLoreAppendix}
                    onChange={(e) => setIncludeLoreInclude(e.target.checked)}
                    className="accent-[#0b1c30]"
                  />
                </label>

                <label className="flex items-center justify-between p-2.5 bg-[#f8f5f0] rounded border border-[#c6c6cd]/20 cursor-pointer">
                  <span>Afficher les résumés canoniques par chapitre</span>
                  <input
                    type="checkbox"
                    checked={includeSummaries}
                    onChange={(e) => setIncludeSummaries(e.target.checked)}
                    className="accent-[#0b1c30]"
                  />
                </label>
              </div>
            </div>
          </div>

          {/* Compilation Live Preview */}
          <div className="lg:col-span-7 space-y-4">
            <h2 className="text-xs font-mono font-bold text-[#76777d] uppercase tracking-wider">
              Aperçu du Manuscrit Compilé
            </h2>

            <div className="bg-[#f8f5f0] border border-[#c6c6cd]/30 rounded-xl p-5 sm:p-8 min-h-[400px] sm:min-h-[500px] font-merriweather shadow-xs text-[#0f172a] space-y-6">
              <div className="text-center pb-6 border-b border-[#c6c6cd]/30 space-y-2">
                <h1 className="font-playfair text-2xl sm:text-3xl font-bold text-[#0b1c30]">
                  {project.title}
                </h1>
                <p className="font-courier text-xs text-[#5f5e5b]">
                  {project.subtitle}
                </p>
                <div className="text-[11px] font-mono text-[#b87500] uppercase pt-1">
                  Édition Complète Canonique
                </div>
              </div>

              {/* Table of contents */}
              <div className="p-4 bg-white/60 rounded border border-[#c6c6cd]/20 font-inter text-xs space-y-2">
                <span className="font-mono font-bold text-[#0b1c30] uppercase block">
                  Table des Matières
                </span>
                <ol className="list-decimal list-inside space-y-1 text-[#45464d]">
                  {chaptersList.map((chap) => (
                    <li key={chap.id} className="truncate">
                      Chapitre {chap.number}: {chap.title} ({(chap.scenes || []).length} scènes)
                    </li>
                  ))}
                </ol>
              </div>

              {/* First chapter snippet */}
              {chaptersList[0] && (
                <div className="space-y-3">
                  <h2 className="font-playfair text-lg sm:text-xl font-bold text-[#0b1c30]">
                    Chapitre {chaptersList[0].number}: {chaptersList[0].title}
                  </h2>
                  <p className="text-xs sm:text-sm leading-relaxed font-merriweather text-[#0f172a]">
                    {(chaptersList[0].scenes || [])[0]?.content || (chaptersList[0].versions || [])[0]?.content || "Extrait de la première scène..."}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </StudioLayout>
  );
}
