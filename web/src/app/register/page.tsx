"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Mail, Lock, User, Eye, EyeOff, ArrowRight, Feather, Sparkles } from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [plan, setPlan] = useState<"standard" | "pro">("pro");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    router.push("/setup");
  };

  return (
    <div className="min-h-screen bg-[#f8f5f0] text-[#0f172a] flex flex-col justify-between font-inter selection:bg-[#ffddb8] selection:text-[#0f172a] relative overflow-hidden">
      <div
        className="absolute inset-0 pointer-events-none opacity-40"
        style={{
          backgroundImage:
            "radial-gradient(circle at 50% 10%, #ffddb8 0%, transparent 60%)",
        }}
      />

      <header className="p-6 relative z-10 flex justify-between items-center max-w-5xl mx-auto w-full">
        <Link href="/studio" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-[#0b1c30] text-[#ffddb8] flex items-center justify-center">
            <Feather className="w-4 h-4" />
          </div>
          <span className="font-playfair font-bold text-lg text-[#0b1c30]">
            Manuscript Studio
          </span>
        </Link>
        <Link
          href="/login"
          className="text-xs font-semibold text-[#45464d] hover:text-[#0b1c30]"
        >
          Déjà inscrit ? Connexion
        </Link>
      </header>

      <main className="flex-1 flex items-center justify-center p-6 relative z-10 my-6">
        <div className="w-full max-w-lg bg-white rounded-xl shadow-sm border border-[#c6c6cd]/30 p-8 flex flex-col">
          <div className="text-center mb-6">
            <h1 className="font-playfair text-2xl font-bold text-[#0f172a] mb-2">
              Créer votre espace d'écrivain
            </h1>
            <p className="font-courier text-xs text-[#45464d]">
              Rejoignez les auteurs qui façonnent leurs récits avec l'IA
            </p>
          </div>

          {/* Plan Selector Toggle */}
          <div className="grid grid-cols-2 gap-3 mb-6 p-1 bg-[#eff4ff] rounded-lg border border-[#c6c6cd]/20">
            <button
              type="button"
              onClick={() => setPlan("standard")}
              className={`p-3 rounded-md text-left transition-all ${
                plan === "standard"
                  ? "bg-white text-[#0b1c30] shadow-xs border border-[#c6c6cd]/30"
                  : "text-[#45464d] hover:text-[#0b1c30]"
              }`}
            >
              <div className="text-xs font-bold">Standard</div>
              <div className="text-[11px] text-[#76777d]">Essai gratuit 14 jours</div>
            </button>
            <button
              type="button"
              onClick={() => setPlan("pro")}
              className={`p-3 rounded-md text-left transition-all relative ${
                plan === "pro"
                  ? "bg-[#0b1c30] text-white shadow-xs"
                  : "text-[#45464d] hover:text-[#0b1c30]"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold flex items-center gap-1">
                  Pro Studio <Sparkles className="w-3 h-3 text-[#ffddb8]" />
                </span>
                <span className="text-[10px] bg-[#ffddb8] text-[#2a1700] px-1.5 py-0.5 rounded font-mono font-bold">
                  29€/mois
                </span>
              </div>
              <div className="text-[11px] text-[#7c839b] mt-0.5">
                Accès illimité aux agents IA
              </div>
            </button>
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
              <label className="block text-xs font-semibold text-[#45464d] mb-1">
                Nom complet / Pseudonyme d'auteur
              </label>
              <div className="relative">
                <User className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#76777d]" />
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Valerius de Cendres"
                  required
                  className="w-full pl-10 pr-3 py-2 text-sm border-b border-[#c6c6cd] focus:border-[#b87500] focus:outline-none bg-transparent transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#45464d] mb-1">
                Adresse e-mail
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#76777d]" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="auteur@manuscript.studio"
                  required
                  className="w-full pl-10 pr-3 py-2 text-sm border-b border-[#c6c6cd] focus:border-[#b87500] focus:outline-none bg-transparent transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#45464d] mb-1">
                Mot de passe
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#76777d]" />
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="8 caractères minimum"
                  required
                  className="w-full pl-10 pr-10 py-2 text-sm border-b border-[#c6c6cd] focus:border-[#b87500] focus:outline-none bg-transparent transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#76777d] hover:text-[#0f172a]"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="mt-4 w-full bg-[#0f172a] text-[#f8f5f0] font-semibold text-sm py-3 rounded hover:bg-[#213145] transition-colors flex items-center justify-center gap-2 group shadow-sm"
            >
              <span>Démarrer le Setup du Premier Projet</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform text-[#ffddb8]" />
            </button>
          </form>

          <p className="mt-4 text-[11px] text-[#76777d] text-center">
            En vous inscrivant, vous acceptez nos{" "}
            <a href="#" className="underline">Conditions d'utilisation</a> et notre{" "}
            <a href="#" className="underline">Politique de confidentialité</a>.
          </p>
        </div>
      </main>

      <footer className="p-6 text-center text-xs text-[#76777d] border-t border-[#c6c6cd]/20 max-w-5xl mx-auto w-full flex flex-col md:flex-row justify-between items-center gap-2 relative z-10">
        <div>© 2025 Manuscript Studio</div>
        <div className="flex gap-4">
          <Link href="/login" className="hover:text-[#0f172a]">Connexion</Link>
          <Link href="/pricing" className="hover:text-[#0f172a]">Tarification</Link>
        </div>
      </footer>
    </div>
  );
}
