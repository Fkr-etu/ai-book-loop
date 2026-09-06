import { LegalFooter } from "@/components/LegalFooter";
import { LEGAL_CONTENT_VERSION, legal } from "@/lib/legal";

export function LegalPage({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[#f8f5f0] text-[#0f172a] font-inter">
      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-12 md:py-16">
        <header className="mb-10">
          <p className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider mb-3">Book Loop · Informations légales</p>
          <h1 className="font-playfair text-4xl sm:text-5xl font-bold text-[#0b1c30] tracking-tight">{title}</h1>
          <p className="mt-4 text-sm text-[#5f5e5b] leading-relaxed">{description}</p>
        </header>
        <article className="bg-white border border-[#c6c6cd]/40 rounded-2xl p-6 sm:p-10 space-y-8 leading-relaxed text-sm">
          {children}
          <aside className="rounded-lg bg-[#fff8ed] border border-[#b87500]/20 p-4 text-xs text-[#5f5e5b]">
            <strong className="text-[#2a1700]">Version du contenu : {LEGAL_CONTENT_VERSION}</strong>
            <br />
            Ces informations constituent une base technique. Les données d'identification, conditions contractuelles et textes définitifs doivent être complétés et validés avant commercialisation.
          </aside>
        </article>
      </main>
      <LegalFooter />
    </div>
  );
}

export function Placeholder({ children }: { children: React.ReactNode }) {
  return <span className="font-mono text-[#9a5c00]">{children}</span>;
}

export { legal };
