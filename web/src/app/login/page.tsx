"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Mail, Lock, Eye, EyeOff, ArrowRight, BookOpen, Feather } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("auteur@manuscript.studio");
  const [password, setPassword] = useState("••••••••");
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    router.push("/studio");
  };

  return (
    <div className="min-h-screen bg-[#f8f5f0] text-[#0f172a] flex flex-col justify-between font-inter selection:bg-[#ffddb8] selection:text-[#0f172a] relative overflow-hidden">
      {/* Background glow */}
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
          href="/pricing"
          className="text-xs font-semibold text-[#45464d] hover:text-[#0b1c30]"
        >
          Tarification
        </Link>
      </header>

      <main className="flex-1 flex items-center justify-center p-6 relative z-10">
        <div className="w-full max-w-md bg-white rounded-xl shadow-sm border border-[#c6c6cd]/30 p-8 flex flex-col">
          <div className="text-center mb-8">
            <h1 className="font-playfair text-2xl font-bold text-[#0f172a] mb-2">
              Manuscript Studio
            </h1>
            <p className="font-courier text-xs text-[#45464d]">
              Connexion à votre espace d'écriture
            </p>
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-5">
            <div>
              <label className="block text-xs font-semibold text-[#45464d] mb-1.5">
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
                  className="w-full pl-10 pr-3 py-2.5 text-sm border-b border-[#c6c6cd] focus:border-[#b87500] focus:outline-none bg-transparent transition-colors"
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="block text-xs font-semibold text-[#45464d]">
                  Mot de passe
                </label>
                <a
                  href="#"
                  className="text-xs text-[#45464d] hover:text-[#0f172a] underline decoration-dotted"
                >
                  Mot de passe oublié ?
                </a>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#76777d]" />
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full pl-10 pr-10 py-2.5 text-sm border-b border-[#c6c6cd] focus:border-[#b87500] focus:outline-none bg-transparent transition-colors"
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
              className="mt-2 w-full bg-[#0f172a] text-[#f8f5f0] font-semibold text-sm py-3 rounded hover:bg-[#213145] transition-colors flex items-center justify-center gap-2 group shadow-sm"
            >
              <span>Connexion</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform text-[#ffddb8]" />
            </button>
          </form>

          <div className="mt-6 text-center text-xs text-[#45464d]">
            Pas encore de compte ?{" "}
            <Link
              href="/register"
              className="font-semibold text-[#0f172a] hover:underline decoration-[#ffddb8] underline-offset-2"
            >
              Créer un compte
            </Link>
          </div>

          <div className="mt-8 pt-6 border-t border-[#c6c6cd]/30">
            <p className="text-[10px] font-mono text-[#76777d] uppercase tracking-wider text-center mb-3">
              Reprendre le travail
            </p>
            <button
              onClick={() => router.push("/studio")}
              className="w-full flex items-center justify-between p-3 rounded-lg border border-[#c6c6cd]/30 hover:border-[#ffddb8] hover:bg-[#f8f5f0] transition-all group text-left"
            >
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-[#f8f5f0] border border-[#c6c6cd]/30 flex items-center justify-center shrink-0">
                  <BookOpen className="w-4 h-4 text-[#0f172a]" />
                </div>
                <div>
                  <h3 className="text-xs font-semibold text-[#0f172a]">
                    La Porte d'Obsidienne
                  </h3>
                  <p className="text-[11px] text-[#76777d]">Modifié il y a 2h</p>
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-[#b87500] opacity-0 group-hover:opacity-100 transition-all transform group-hover:translate-x-1" />
            </button>
          </div>
        </div>
      </main>

      <footer className="p-6 text-center text-xs text-[#76777d] border-t border-[#c6c6cd]/20 max-w-5xl mx-auto w-full flex flex-col md:flex-row justify-between items-center gap-2 relative z-10">
        <div>© 2025 Manuscript Studio - Tous droits réservés.</div>
        <div className="flex gap-4">
          <a href="#" className="hover:text-[#0f172a]">Conditions</a>
          <a href="#" className="hover:text-[#0f172a]">Confidentialité</a>
          <a href="#" className="hover:text-[#0f172a]">Support Auteur</a>
        </div>
      </footer>
    </div>
  );
}
