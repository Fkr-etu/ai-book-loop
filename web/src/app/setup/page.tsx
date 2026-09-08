"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Feather, Sparkles, ArrowRight, ArrowLeft, Check } from "lucide-react";
import { useProjectStore } from "@/lib/useProjectStore";

export default function SetupPage() {
  const router = useRouter();
  const { project, updateProjectInfo } = useProjectStore();
  const [step, setStep] = useState(1);

  const [title, setTitle] = useState(project.title || "");
  const [authorIdea, setAuthorIdea] = useState(project.authorIdea || "");
  const [theme, setTheme] = useState(project.theme || "");
  const [lore, setLore] = useState(project.lore || "");

  const handleFinishSetup = () => {
    updateProjectInfo({ title, authorIdea, theme, lore });
    router.push("/studio");
  };

  return (
    <div className="min-h-screen bg-[#f8f5f0] text-[#0f172a] flex flex-col justify-between font-inter selection:bg-[#ffddb8] selection:text-[#0f172a]">
      <header className="px-4 sm:px-8 py-4 bg-white/80 backdrop-blur border-b border-[#c6c6cd]/30 flex flex-col sm:flex-row justify-between items-center gap-2 sticky top-0 z-20">
        <Link href="/studio" className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-[#0b1c30] text-[#ffddb8] flex items-center justify-center"><Feather className="w-4 h-4" /></div>
          <span className="font-playfair font-bold text-lg text-[#0b1c30]">Manuscript Studio</span>
        </Link>
        <div className="text-xs font-mono text-[#76777d]">Assistant de Configuration de Récit • Étape {step} sur 3</div>
      </header>

      <div className="w-full bg-[#e5eeff] h-1.5"><div className="bg-[#0b1c30] h-1.5 transition-all duration-300" style={{ width: `${(step / 3) * 100}%` }} /></div>

      <main className="flex-1 max-w-3xl w-full mx-auto p-4 sm:p-6 md:p-10">
        <div className="bg-white rounded-xl border border-[#c6c6cd]/30 shadow-xs p-5 sm:p-8">
          {step === 1 && (
            <div className="space-y-6 animate-fadeIn">
              <div><span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider block mb-1">Étape 1 • Fondations Narratives</span><h1 className="font-playfair text-xl sm:text-2xl font-bold text-[#0b1c30]">Titre, intention & thème du livre</h1><p className="text-xs text-[#45464d] mt-1">Ces informations correspondent directement au contrat du livre utilisé par l'API.</p></div>
              <div><label className="block text-xs font-semibold text-[#0b1c30] mb-1">Titre du Livre</label><input type="text" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Ex: La Porte d'Obsidienne" className="w-full px-3 py-2 text-sm border-b border-[#c6c6cd] focus:border-[#b87500] focus:outline-none bg-[#f8f9ff] rounded-t" /></div>
              <div><label className="block text-xs font-semibold text-[#0b1c30] mb-1">Idée de l'auteur</label><textarea rows={3} value={authorIdea} onChange={(e) => setAuthorIdea(e.target.value)} placeholder="Décrivez l'idée, l'intrigue ou l'intention que vous souhaitez développer..." className="w-full p-3 text-sm border border-[#c6c6cd]/60 focus:border-[#b87500] focus:outline-none bg-[#f8f9ff] rounded font-merriweather leading-relaxed" /></div>
              <div><label className="block text-xs font-semibold text-[#0b1c30] mb-1">Thème Central & Intentions Narratives</label><textarea rows={4} value={theme} onChange={(e) => setTheme(e.target.value)} placeholder="Décrivez l'intention philosophique, les questions morales ou la dynamique principale du récit..." className="w-full p-3 text-sm border border-[#c6c6cd]/60 focus:border-[#b87500] focus:outline-none bg-[#f8f9ff] rounded font-merriweather leading-relaxed" /></div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6 animate-fadeIn">
              <div><span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider block mb-1">Étape 2 • Ancrage du Lore & Bible du Monde</span><h1 className="font-playfair text-xl sm:text-2xl font-bold text-[#0b1c30]">Lore et règles du monde</h1><p className="text-xs text-[#45464d] mt-1">Le lore global est persisté dans le champ <code>lore</code> du livre.</p></div>
              <div><label className="block text-xs font-semibold text-[#0b1c30] mb-1">Résumé Global du Lore / Contextualisation</label><textarea rows={5} value={lore} onChange={(e) => setLore(e.target.value)} placeholder="Ex: Dans l'Empire de Cendres, les mages utilisent l'Obsidienne pour capturer la mémoire..." className="w-full p-3 text-sm border border-[#c6c6cd]/60 focus:border-[#b87500] focus:outline-none bg-[#f8f9ff] rounded font-merriweather text-xs leading-relaxed" /></div>
              <div className="p-4 bg-[#eff4ff] rounded-lg border border-[#c6c6cd]/30"><p className="text-xs text-[#45464d]">La gestion des personnages et des éléments de lore structurés sera ajoutée ultérieurement lorsqu'elle sera prise en charge par l'API.</p></div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6 animate-fadeIn">
              <div><span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider block mb-1">Étape 3 • Contraintes de Rédaction</span><h1 className="font-playfair text-xl sm:text-2xl font-bold text-[#0b1c30]">Contraintes du livre</h1><p className="text-xs text-[#45464d] mt-1">Les contraintes déjà présentes sont celles que l'API associe au livre.</p></div>
              <div className="p-4 bg-[#f8f5f0] rounded-lg border border-[#b87500]/30 space-y-3"><div className="flex items-center gap-2 text-xs font-bold text-[#2a1700]"><Sparkles className="w-4 h-4 text-[#b87500]" />Contraintes du livre</div><div className="space-y-2">{(project.constraints || []).length > 0 ? project.constraints.map((constraint, idx) => (<div key={`constraint-${idx}`} className="flex items-center justify-between text-xs bg-white p-2.5 rounded border border-[#c6c6cd]/30"><span className="text-[#0b1c30]">{constraint}</span><span className="text-[10px] font-mono text-[#b87500] font-bold shrink-0 ml-2">VERROUILLÉ</span></div>)) : <p className="text-xs text-[#76777d]">Aucune contrainte configurée.</p>}</div></div>
              <div className="p-4 bg-[#eff4ff] rounded border border-[#c6c6cd]/30 text-xs text-[#0b1c30]"><strong>Félicitations !</strong> Le socle de votre roman est prêt. Vous allez être redirigé vers l'Atelier de Rédaction.</div>
            </div>
          )}

          <div className="mt-8 pt-6 border-t border-[#c6c6cd]/30 flex justify-between items-center">
            {step > 1 ? <button type="button" onClick={() => setStep((s) => s - 1)} className="px-4 py-2 text-xs font-semibold text-[#0b1c30] border border-[#c6c6cd] rounded hover:bg-[#eff4ff] flex items-center gap-1.5 cursor-pointer"><ArrowLeft className="w-3.5 h-3.5" /> Précédent</button> : <div />}
            {step < 3 ? <button type="button" data-testid="next-step-btn" onClick={() => setStep((s) => s + 1)} className="px-5 py-2.5 text-xs font-semibold bg-[#0b1c30] text-white rounded hover:bg-[#131b2e] flex items-center gap-1.5 shadow-xs cursor-pointer"><span>Suivant</span><ArrowRight className="w-3.5 h-3.5 text-[#ffddb8]" /></button> : <button type="button" onClick={handleFinishSetup} className="px-6 py-2.5 text-xs font-bold bg-[#0b1c30] text-[#ffddb8] rounded hover:bg-[#131b2e] flex items-center gap-2 shadow-xs cursor-pointer"><Check className="w-4 h-4" /><span>Ouvrir l'Atelier de Rédaction</span></button>}
          </div>
        </div>
      </main>
    </div>
  );
}
