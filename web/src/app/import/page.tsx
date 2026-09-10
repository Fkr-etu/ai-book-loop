"use client";

import { ChangeEvent, FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/Navbar";
import { realApiClient, RealApiError } from "@/services/realApiClient";
import { getApiErrorMessage } from "@/services/apiErrorMessages";
import { track } from "@/lib/analytics";
import { ArrowRight, BookOpen, FileText, Upload } from "lucide-react";
import type { BackendAnalysisJob } from "@/types/api";

function errorMessage(error: unknown): string {
  if (error instanceof RealApiError) return getApiErrorMessage(error, error.message);
  return "Impossible d’importer le manuscrit.";
}

function titleFromFileName(name: string): string {
  return name.replace(/\.[^.]+$/, "").replace(/[_-]+/g, " ").trim();
}

export default function ImportManuscriptPage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [content, setContent] = useState("");
  const [sourceType, setSourceType] = useState("markdown");
  const [importing, setImporting] = useState(false);
  const [job, setJob] = useState<BackendAnalysisJob | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!job || (job.status !== "queued" && job.status !== "running")) return;
    const timer = window.setInterval(async () => {
      try {
        const next = await realApiClient.getIngestionJob(job.book_id, job.job_id);
        setJob(next);
        if (next.status === "succeeded") {
          track("document_ingested");
          router.push(`/studio/lore?bookId=${encodeURIComponent(next.book_id)}`);
        } else if (next.status === "failed" || next.status === "cancelled") {
          setError(next.error_message || "L’import du manuscrit n’a pas pu être terminé.");
          setImporting(false);
        }
      } catch (err) {
        setError(errorMessage(err));
        setImporting(false);
      }
    }, 1500);
    return () => window.clearInterval(timer);
  }, [job, router]);

  const handleFile = async (event: ChangeEvent<HTMLInputElement>) => {
    const selected = event.target.files?.[0];
    if (!selected) return;
    setError(null);
    setFile(selected);
    setTitle((current) => current || titleFromFileName(selected.name));
    const extension = selected.name.split(".").pop()?.toLowerCase();
    setSourceType(extension === "md" || extension === "markdown" ? "markdown" : "text");
    try {
      setContent(await selected.text());
    } catch {
      setContent("");
      setError("Ce fichier ne peut pas être lu dans le navigateur.");
    }
  };

  const handleImport = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file || !content.trim() || !title.trim()) return;
    setImporting(true);
    setError(null);
    try {
      const book = await realApiClient.createBook({
        title: title.trim(),
        theme: "Manuscrit importé",
        author_idea: "À préciser à partir du manuscrit importé.",
      });
      const nextJob = await realApiClient.ingestDocument(book.id, file.name, content, sourceType);
      setJob(nextJob);
      track("book_created");
    } catch (err) {
      setError(errorMessage(err));
      setImporting(false);
    }
  };

  const progress = job?.progress ?? 0;
  const step = job?.current_step;
  const isWaiting = importing && (!job || job.status === "queued" || job.status === "running");

  return (
    <div className="min-h-screen bg-[#f8f5f0] text-[#0f172a] font-inter">
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-8 md:py-14">
        <div className="mb-8">
          <span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider flex items-center gap-1.5"><BookOpen className="w-4 h-4" /> Manuscrit existant</span>
          <h1 className="font-playfair text-3xl md:text-4xl font-bold text-[#0b1c30] mt-2">Importez votre livre</h1>
          <p className="text-sm text-[#5f5e5b] mt-2 max-w-2xl">Vous avez déjà écrit votre manuscrit ? Donnez-le à Book Loop. Son contenu sera préparé puis analysé en arrière-plan avant de passer à l’Atelier.</p>
        </div>

        <form onSubmit={handleImport} className="bg-white rounded-xl border border-[#c6c6cd]/50 shadow-xs p-5 sm:p-7 space-y-6">
          <div>
            <label htmlFor="import-title" className="block text-xs font-semibold text-[#0b1c30] mb-1">Titre du livre</label>
            <input id="import-title" value={title} onChange={(event) => setTitle(event.target.value)} required disabled={isWaiting} className="w-full px-3 py-2.5 text-sm border border-[#c6c6cd] rounded bg-[#f8f9ff] disabled:opacity-60" placeholder="Le titre de votre manuscrit" />
          </div>

          {!isWaiting ? <div>
            <label htmlFor="manuscript" className="block text-xs font-semibold text-[#0b1c30] mb-2">Manuscrit</label>
            <label htmlFor="manuscript" className="flex flex-col items-center justify-center gap-3 min-h-44 rounded-xl border-2 border-dashed border-[#c6c6cd] hover:border-[#b87500]/60 bg-[#faf9f6] cursor-pointer px-5 text-center transition-colors">
              {file ? <><FileText className="w-8 h-8 text-[#b87500]" /><span className="text-sm font-semibold text-[#0b1c30]">{file.name}</span><span className="text-[11px] text-[#76777d]">{Math.round(file.size / 1024)} Ko · fichier prêt à être importé</span></> : <><Upload className="w-8 h-8 text-[#b87500]" /><span className="text-sm font-semibold text-[#0b1c30]">Choisir un fichier</span><span className="text-[11px] text-[#76777d]">TXT ou Markdown pour cette première version</span></>}
              <input id="manuscript" type="file" accept=".txt,.md,.markdown,text/plain,text/markdown" onChange={handleFile} className="sr-only" />
            </label>
          </div> : <div className="rounded-xl bg-[#faf9f6] border border-[#c6c6cd]/50 p-5 space-y-4">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-semibold text-[#0b1c30]">Votre manuscrit est en cours de préparation</p>
                <p className="text-xs text-[#76777d] mt-1">Vous pouvez rester sur cette page pendant l’analyse.</p>
              </div>
              <span className="text-sm font-semibold text-[#b87500]">{progress}%</span>
            </div>
            <div className="h-2 rounded-full bg-[#e7e4de] overflow-hidden"><div className="h-full bg-[#b87500] transition-all duration-500" style={{ width: `${Math.max(3, progress)}%` }} /></div>
            <p className="text-xs text-[#5f5e5b]">{step ? `Étape en cours : ${step}` : "En attente de traitement…"}</p>
          </div>}

          {!isWaiting && <div className="rounded-lg bg-[#f8f5f0] border border-[#c6c6cd]/40 p-4 text-xs text-[#5f5e5b] space-y-1">
            <p className="font-semibold text-[#0b1c30]">Ce qui se passe ensuite</p>
            <p>1. Votre manuscrit devient la source de référence du projet.</p>
            <p>2. Book Loop prépare son contenu et lance l’analyse en arrière-plan.</p>
            <p>3. Vous pourrez examiner les premières connaissances dans le Lore avant de les utiliser comme Canon.</p>
          </div>}

          {error && <p role="alert" className="text-xs text-red-700">{error}</p>}
          {!isWaiting && <div className="flex flex-col-reverse sm:flex-row sm:items-center justify-between gap-3">
            <button type="button" onClick={() => router.push("/dashboard")} className="text-xs text-[#76777d] hover:text-[#0b1c30]">Annuler</button>
            <button type="submit" disabled={importing || !file || !content.trim() || !title.trim()} className="px-5 py-2.5 bg-[#0b1c30] text-white rounded text-xs font-semibold disabled:opacity-50 flex items-center justify-center gap-2">{importing ? "Préparation…" : "Importer le manuscrit"}<ArrowRight className="w-3.5 h-3.5" /></button>
          </div>}
        </form>
      </main>
    </div>
  );
}
