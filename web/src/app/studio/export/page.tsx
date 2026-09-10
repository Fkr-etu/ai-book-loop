"use client";

import React, { useState } from "react";
import { StudioLayout } from "@/components/StudioLayout";
import { useProjectStore } from "@/lib/useProjectStore";
import { Download, CheckCircle2, BookOpen } from "lucide-react";

type ExportFormat = "markdown" | "epub" | "pdf" | "docx";

const formats: Array<{ id: ExportFormat; label: string; description: string; extension: string }> = [
  { id: "markdown", label: "Markdown", description: "Disponible maintenant", extension: ".md" },
  { id: "epub", label: "EPUB", description: "Bientôt disponible", extension: ".epub" },
  { id: "pdf", label: "PDF", description: "Bientôt disponible", extension: ".pdf" },
  { id: "docx", label: "Word", description: "Bientôt disponible", extension: ".docx" }
];

export default function ExportPage() {
  const { project } = useProjectStore();
  const [exportFormat, setExportFormat] = useState<ExportFormat>("markdown");
  const [includeLoreAppendix, setIncludeLoreAppendix] = useState(false);
  const [includeSummaries, setIncludeSummaries] = useState(false);
  const [downloading, setDownloading] = useState(false);

  if (!project.id) {
    return (
      <StudioLayout>
        <main className="min-h-[70vh] flex items-center justify-center px-4 sm:px-6">
          <section className="max-w-md text-center space-y-4">
            <BookOpen className="w-10 h-10 mx-auto text-[#b87500]" />
            <h1 className="font-playfair text-2xl font-bold text-[#0b1c30]">L’exportation viendra avec votre livre</h1>
            <p className="text-sm leading-relaxed text-[#5f5e5b]">Créez d’abord un livre. Les options d’exportation apparaîtront ici dès que vous aurez un récit à exporter.</p>
          </section>
        </main>
      </StudioLayout>
    );
  }

  const chapters = project.chapters || [];
  const loreItems = project.loreItems || [];
  const totalScenes = chapters.reduce((total, chapter) => total + (chapter.scenes || []).length, 0);

  const handleDownload = () => {
    if (exportFormat !== "markdown") return;
    setDownloading(true);

    let compiledText = `# ${project.title}\n\n`;
    if (project.subtitle) compiledText += `${project.subtitle}\n\n`;
    if (project.genre) compiledText += `**Genre :** ${project.genre}\n`;
    if (project.theme) compiledText += `**Thème :** ${project.theme}\n`;
    compiledText += "\n---\n\n";

    chapters.forEach((chapter) => {
      compiledText += `# Chapitre ${chapter.number} : ${chapter.title}\n\n`;
      if (includeSummaries && chapter.summary) compiledText += `> ${chapter.summary}\n\n`;
      (chapter.scenes || []).forEach((scene) => {
        compiledText += `## ${scene.title}\n\n${scene.content || ""}\n\n`;
      });
    });

    if (includeLoreAppendix && loreItems.length > 0) {
      compiledText += "\n---\n\n# Annexe — Univers\n\n";
      loreItems.forEach((item) => {
        compiledText += `## ${item.title}\n\n${item.description}\n\n`;
      });
    }

    const blob = new Blob([compiledText], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${project.title.toLowerCase().replace(/[^a-z0-9]+/gi, "_")}_manuscrit.md`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    setDownloading(false);
  };

  return (
    <StudioLayout>
      <main className="p-4 sm:p-6 md:p-10 max-w-5xl mx-auto space-y-8">
        <header className="border-b border-[#c6c6cd]/30 pb-6">
          <p className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider mb-1">Publication</p>
          <h1 className="font-playfair text-3xl font-bold text-[#0b1c30]">Exporter votre livre</h1>
          <p className="text-sm text-[#5f5e5b] mt-2 max-w-2xl">Préparez une version de votre récit à partager ou à retravailler ailleurs. L’export Markdown est disponible aujourd’hui ; les formats éditoriaux suivront.</p>
        </header>

        <section className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="p-4 bg-white rounded-xl border border-[#c6c6cd]/40"><div className="text-[10px] font-mono uppercase text-[#76777d]">Chapitres</div><div className="text-xl font-bold text-[#0b1c30] mt-1">{chapters.length}</div></div>
          <div className="p-4 bg-white rounded-xl border border-[#c6c6cd]/40"><div className="text-[10px] font-mono uppercase text-[#76777d]">Scènes</div><div className="text-xl font-bold text-[#0b1c30] mt-1">{totalScenes}</div></div>
          <div className="p-4 bg-white rounded-xl border border-[#c6c6cd]/40"><div className="text-[10px] font-mono uppercase text-[#76777d]">Format disponible</div><div className="text-xl font-bold text-[#b87500] mt-1">Markdown</div></div>
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          <div className="lg:col-span-2 bg-white rounded-xl border border-[#c6c6cd]/40 p-5 sm:p-6 space-y-6">
            <div><h2 className="font-playfair text-lg font-bold text-[#0b1c30]">Format</h2><p className="text-xs text-[#5f5e5b] mt-1">Un seul format est réellement disponible pour le moment.</p></div>
            <div className="space-y-2">
              {formats.map((format) => {
                const available = format.id === "markdown";
                const selected = exportFormat === format.id;
                return <button key={format.id} type="button" disabled={!available} onClick={() => setExportFormat(format.id)} className={`w-full text-left p-3 rounded-lg border transition-colors ${selected ? "bg-[#0b1c30] text-white border-[#0b1c30]" : available ? "bg-white border-[#c6c6cd]/40 text-[#0b1c30] hover:bg-[#eff4ff]" : "bg-[#f8f5f0] border-[#c6c6cd]/30 text-[#8a8985] cursor-not-allowed"}`}><div className="flex items-center justify-between gap-3"><span className="text-sm font-semibold">{format.label}</span><span className="text-[10px] font-mono">{format.extension}</span></div><div className={`text-[11px] mt-1 ${selected ? "text-[#d9dfec]" : "text-[#76777d]"}`}>{format.description}</div></button>;
              })}
            </div>
            <div className="border-t border-[#c6c6cd]/20 pt-5 space-y-3">
              <h2 className="font-playfair text-lg font-bold text-[#0b1c30]">Contenu</h2>
              <label className="flex items-center justify-between gap-3 p-3 bg-[#f8f5f0] rounded border border-[#c6c6cd]/20 text-xs cursor-pointer"><span>Ajouter les résumés de chapitres</span><input type="checkbox" checked={includeSummaries} onChange={(event) => setIncludeSummaries(event.target.checked)} /></label>
              <label className={`flex items-center justify-between gap-3 p-3 bg-[#f8f5f0] rounded border border-[#c6c6cd]/20 text-xs ${loreItems.length ? "cursor-pointer" : "opacity-50 cursor-not-allowed"}`}><span>Ajouter l’univers en annexe</span><input type="checkbox" checked={includeLoreAppendix} disabled={!loreItems.length} onChange={(event) => setIncludeLoreAppendix(event.target.checked)} /></label>
            </div>
          </div>

          <div className="lg:col-span-3 bg-[#f8f5f0] rounded-xl border border-[#c6c6cd]/30 p-5 sm:p-8 space-y-6">
            <div className="flex items-start gap-3"><CheckCircle2 className="w-5 h-5 text-[#b87500] shrink-0 mt-0.5" /><div><h2 className="font-playfair text-xl font-bold text-[#0b1c30]">Votre manuscrit</h2><p className="text-xs text-[#5f5e5b] mt-1">{project.title}</p></div></div>
            <div className="bg-white rounded-lg border border-[#c6c6cd]/30 p-5 font-merriweather text-sm leading-relaxed text-[#0f172a] max-h-[420px] overflow-auto">
              {chapters.length === 0 ? <p className="text-[#76777d] italic">Votre livre est encore vide. Le manuscrit apparaîtra ici quand vous aurez commencé à écrire.</p> : chapters.map((chapter) => <section key={chapter.id} className="mb-6 last:mb-0"><h3 className="font-playfair text-lg font-bold mb-2">Chapitre {chapter.number} : {chapter.title}</h3>{includeSummaries && chapter.summary && <p className="text-xs italic text-[#5f5e5b] mb-3">{chapter.summary}</p>}<p className="whitespace-pre-wrap">{(chapter.scenes || [])[0]?.content || "Aucun texte dans ce chapitre pour le moment."}</p></section>)}
            </div>
            <button type="button" onClick={handleDownload} disabled={downloading || exportFormat !== "markdown"} className="w-full py-3 rounded bg-[#0b1c30] text-[#ffddb8] font-bold text-xs flex items-center justify-center gap-2 disabled:opacity-50"><Download className="w-4 h-4" />{downloading ? "Préparation…" : "Exporter en Markdown"}</button>
            <p className="text-[11px] text-[#76777d] text-center">EPUB, PDF et Word seront ajoutés une fois leur génération finalisée.</p>
          </div>
        </section>
      </main>
    </StudioLayout>
  );
}
