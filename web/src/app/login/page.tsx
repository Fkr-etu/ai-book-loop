"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Mail, Lock, Eye, EyeOff, ArrowRight, Feather } from "lucide-react";
import { getApiClient } from "@/services/api";
import { getLoginError } from "@/services/authErrors";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const api = getApiClient();
      await api.loginUser(email.trim(), password);
      router.push("/studio");
    } catch (err: unknown) {
      setError(getLoginError(err));
    } finally {
      setLoading(false);
    }
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
          <span className="font-playfair font-bold text-lg text-[#0b1c30]">AI Book Loop</span>
        </Link>
        <Link href="/pricing" className="text-xs font-semibold text-[#45464d] hover:text-[#0b1c30]">Tarification</Link>
      </header>

      <main className="flex-1 flex items-center justify-center p-6 relative z-10">
        <div className="w-full max-w-md bg-white rounded-xl shadow-sm border border-[#c6c6cd]/30 p-8 flex flex-col">
          <div className="text-center mb-8">
            <h1 className="font-playfair text-2xl font-bold text-[#0f172a] mb-2">AI Book Loop</h1>
            <p className="font-courier text-xs text-[#45464d]">Connexion à votre espace d'écriture</p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded" role="alert" aria-live="polite">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-5" noValidate={false}>
            <div>
              <label htmlFor="login-email" className="block text-xs font-semibold text-[#45464d] mb-1.5">Adresse e-mail</label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#76777d]" />
                <input
                  id="login-email"
                  name="email"
                  type="email"
                  value={email}
                  onChange={(e) => { setEmail(e.target.value); setError(null); }}
                  placeholder="votre@email.com"
                  autoComplete="email"
                  required
                  aria-invalid={Boolean(error)}
                  className="w-full pl-10 pr-3 py-2.5 text-sm border-b border-[#c6c6cd] focus:border-[#b87500] focus:outline-none bg-transparent transition-colors"
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label htmlFor="login-password" className="block text-xs font-semibold text-[#45464d]">Mot de passe</label>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#76777d]" />
                <input
                  id="login-password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setError(null); }}
                  placeholder="Votre mot de passe"
                  autoComplete="current-password"
                  required
                  aria-invalid={Boolean(error)}
                  className="w-full pl-10 pr-10 py-2.5 text-sm border-b border-[#c6c6cd] focus:border-[#b87500] focus:outline-none bg-transparent transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#76777d] hover:text-[#0f172a]"
                  aria-label={showPassword ? "Masquer le mot de passe" : "Afficher le mot de passe"}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || !email.trim() || !password}
              className="mt-2 w-full bg-[#0f172a] text-[#f8f5f0] font-semibold text-sm py-3 rounded hover:bg-[#213145] transition-colors flex items-center justify-center gap-2 group shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>{loading ? "Connexion en cours..." : "Connexion"}</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform text-[#ffddb8]" />
            </button>
          </form>

          <div className="mt-6 text-center text-xs text-[#45464d]">
            Pas encore de compte?{" "}
            <Link href="/register" className="font-semibold text-[#0f172a] hover:underline decoration-[#ffddb8] underline-offset-2">Créer un compte</Link>
          </div>
        </div>
      </main>

      <footer className="p-6 text-center text-xs text-[#76777d] border-t border-[#c6c6cd]/20 max-w-5xl mx-auto w-full flex flex-col md:flex-row justify-between items-center gap-2 relative z-10">
        <div>© 2026 AI Book Loop - Tous droits réservés.</div>
        <div className="flex gap-4"><span>Conditions</span><span>Confidentialité</span><span>Support Auteur</span></div>
      </footer>
    </div>
  );
}
