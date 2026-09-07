"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Mail, Lock, User, Eye, EyeOff, ArrowRight, Feather, Check } from "lucide-react";
import { getApiClient } from "@/services/api";
import { getRegisterError } from "@/services/authErrors";

const PASSWORD_MIN_LENGTH = 12;
type SelectedPlan = "free" | "creator" | "pro";

function getPasswordChecks(password: string) {
  return [
    { label: `${PASSWORD_MIN_LENGTH} caractères minimum`, valid: password.length >= PASSWORD_MIN_LENGTH },
    { label: "Une lettre majuscule", valid: /[A-Z]/.test(password) },
    { label: "Une lettre minuscule", valid: /[a-z]/.test(password) },
    { label: "Un chiffre", valid: /\d/.test(password) },
    { label: "Un caractère spécial", valid: /[^A-Za-z0-9]/.test(password) },
  ];
}

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [plan, setPlan] = useState<SelectedPlan>("free");
  const [billingCycle, setBillingCycle] = useState<"monthly" | "yearly">("monthly");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const requestedPlan = params.get("plan");
    const requestedCycle = params.get("billing");
    if (requestedPlan === "creator" || requestedPlan === "pro") setPlan(requestedPlan);
    if (requestedCycle === "monthly" || requestedCycle === "yearly") setBillingCycle(requestedCycle);
  }, []);

  const passwordChecks = getPasswordChecks(password);
  const passwordIsValid = passwordChecks.every((check) => check.valid);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!passwordIsValid) {
      setError("Votre mot de passe ne respecte pas encore toutes les exigences indiquées ci-dessous.");
      return;
    }
    setLoading(true);
    try {
      const api = getApiClient();
      await api.registerUser(email.trim(), password, name.trim());
      if (plan === "creator" || plan === "pro") {
        const checkoutUrl = await api.createCheckout(plan, billingCycle);
        window.location.assign(checkoutUrl);
        return;
      }
      router.push("/setup");
    } catch (err: unknown) {
      setError(getRegisterError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f8f5f0] text-[#0f172a] flex flex-col justify-between font-inter selection:bg-[#ffddb8] selection:text-[#0f172a] relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none opacity-40" style={{ backgroundImage: "radial-gradient(circle at 50% 10%, #ffddb8 0%, transparent 60%)" }} />
      <header className="p-6 relative z-10 flex justify-between items-center max-w-5xl mx-auto w-full">
        <Link href="/studio" className="flex items-center gap-2"><div className="w-8 h-8 rounded bg-[#0b1c30] text-[#ffddb8] flex items-center justify-center"><Feather className="w-4 h-4" /></div><span className="font-playfair font-bold text-lg text-[#0b1c30]">AI Book Loop</span></Link>
        <Link href="/login" className="text-xs font-semibold text-[#45464d] hover:text-[#0b1c30]">Déjà inscrit ? Connexion</Link>
      </header>

      <main className="flex-1 flex items-center justify-center p-6 relative z-10 my-6">
        <div className="w-full max-w-lg bg-white rounded-xl shadow-sm border border-[#c6c6cd]/30 p-8 flex flex-col">
          <div className="text-center mb-6"><h1 className="font-playfair text-2xl font-bold text-[#0f172a] mb-2">Créer votre espace d'écrivain</h1><p className="font-courier text-xs text-[#45464d]">Votre abonnement sera géré par Stripe après la création du compte.</p></div>
          {error && <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded" role="alert" aria-live="polite">{error}</div>}

          <div className="grid grid-cols-3 gap-2 mb-6 p-1 bg-[#eff4ff] rounded-lg border border-[#c6c6cd]/20">
            {(["free", "creator", "pro"] as SelectedPlan[]).map((value) => (
              <button key={value} type="button" onClick={() => setPlan(value)} className={`p-3 rounded-md text-left transition-all ${plan === value ? "bg-[#0b1c30] text-white shadow-xs" : "text-[#45464d] hover:text-[#0b1c30]"}`}>
                <div className="text-xs font-bold capitalize">{value === "free" ? "Free" : value === "creator" ? "Creator" : "Pro"}</div>
                <div className="text-[10px] mt-1 opacity-70">{value === "free" ? "0 €" : value === "creator" ? "19 €/mois" : "39 €/mois"}</div>
              </button>
            ))}
          </div>

          {plan !== "free" && (
            <div className="flex gap-2 mb-6 text-xs"><button type="button" onClick={() => setBillingCycle("monthly")} className={`px-3 py-2 rounded ${billingCycle === "monthly" ? "bg-[#ffddb8] text-[#2a1700]" : "bg-[#f8f5f0]"}`}>Mensuel</button><button type="button" onClick={() => setBillingCycle("yearly")} className={`px-3 py-2 rounded ${billingCycle === "yearly" ? "bg-[#ffddb8] text-[#2a1700]" : "bg-[#f8f5f0]"}`}>Annuel</button></div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div><label htmlFor="register-name" className="block text-xs font-semibold text-[#45464d] mb-1">Nom complet / Pseudonyme d'auteur</label><div className="relative"><User className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#76777d]" /><input id="register-name" name="name" type="text" value={name} onChange={(e) => { setName(e.target.value); setError(null); }} placeholder="Votre nom ou pseudonyme" autoComplete="name" required className="w-full pl-10 pr-3 py-2 text-sm border-b border-[#c6c6cd] focus:border-[#b87500] focus:outline-none bg-transparent" /></div></div>
            <div><label htmlFor="register-email" className="block text-xs font-semibold text-[#45464d] mb-1">Adresse e-mail</label><div className="relative"><Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#76777d]" /><input id="register-email" name="email" type="email" value={email} onChange={(e) => { setEmail(e.target.value); setError(null); }} placeholder="votre@email.com" autoComplete="email" required className="w-full pl-10 pr-3 py-2 text-sm border-b border-[#c6c6cd] focus:border-[#b87500] focus:outline-none bg-transparent" /></div></div>
            <div><label htmlFor="password" className="block text-xs font-semibold text-[#45464d] mb-1">Mot de passe</label><div className="relative"><Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#76777d]" /><input id="password" name="password" type={showPassword ? "text" : "password"} value={password} onChange={(e) => { setPassword(e.target.value); setError(null); }} placeholder="Créez un mot de passe robuste" required minLength={PASSWORD_MIN_LENGTH} autoComplete="new-password" className="w-full pl-10 pr-10 py-2 text-sm border-b border-[#c6c6cd] focus:border-[#b87500] focus:outline-none bg-transparent" /><button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-[#76777d]" aria-label={showPassword ? "Masquer le mot de passe" : "Afficher le mot de passe"}>{showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}</button></div><div className="mt-3 rounded-md bg-[#f8f5f0] p-3"><ul className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-[11px] text-[#76777d]">{passwordChecks.map((check) => <li key={check.label} className={`flex items-center gap-1.5 ${check.valid ? "text-emerald-700" : ""}`}><Check className={`w-3 h-3 ${check.valid ? "opacity-100" : "opacity-30"}`} /><span>{check.label}</span></li>)}</ul></div></div>
            <button type="submit" disabled={loading || !name.trim() || !email.trim() || !passwordIsValid} className="mt-4 w-full bg-[#0f172a] text-[#f8f5f0] font-semibold text-sm py-3 rounded hover:bg-[#213145] transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"><span>{loading ? "Création du compte..." : plan === "free" ? "Créer mon compte" : "Créer mon compte et payer"}</span><ArrowRight className="w-4 h-4 text-[#ffddb8]" /></button>
          </form>
          <p className="mt-4 text-[11px] text-[#76777d] text-center">En vous inscrivant, vous acceptez nos <a href="#" className="underline">Conditions d'utilisation</a> et notre <a href="#" className="underline">Politique de confidentialité</a>.</p>
        </div>
      </main>
      <footer className="p-6 text-center text-xs text-[#76777d] border-t border-[#c6c6cd]/20 max-w-5xl mx-auto w-full flex flex-col md:flex-row justify-between items-center gap-2 relative z-10"><div>© 2026 AI Book Loop</div><div className="flex gap-4"><Link href="/login" className="hover:text-[#0f172a]">Connexion</Link><Link href="/pricing" className="hover:text-[#0f172a]">Tarification</Link></div></footer>
    </div>
  );
}
