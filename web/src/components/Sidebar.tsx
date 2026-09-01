"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Feather,
  ListOrdered,
  Users,
  Compass,
  GitFork,
  Sliders,
  CheckCircle2,
  Bookmark,
  Download,
  LayoutDashboard
} from "lucide-react";
import { useProjectStore } from "@/lib/useProjectStore";

export function Sidebar() {
  const pathname = usePathname();
  const { project } = useProjectStore();

  const navItems = [
    {
      name: "Atelier de Rédaction",
      href: "/studio",
      icon: Feather,
      description: "Desk principal & Canvas"
    },
    {
      name: "Plan & Structure",
      href: "/studio/outline",
      icon: ListOrdered,
      description: "Chapitres et Scènes"
    },
    {
      name: "Personnages Profonds",
      href: "/studio/characters",
      icon: Users,
      description: "Psychologie & Fiches",
      badge: project.characters.length
    },
    {
      name: "Bible du Monde",
      href: "/studio/lore",
      icon: Compass,
      description: "Lore, Factions, Reliques",
      badge: project.loreItems.length
    },
    {
      name: "Graphe de Relations",
      href: "/studio/lore-graph",
      icon: GitFork,
      description: "Cartographie interactive"
    },
    {
      name: "Laboratoire d'Intention",
      href: "/studio/intention-lab",
      icon: Sliders,
      description: "Pilotage IA & Contraintes"
    },
    {
      name: "Boucle de Validation",
      href: "/studio/validation-loop",
      icon: CheckCircle2,
      description: "Linter & Feedback IA"
    },
    {
      name: "Studio d'Exportation",
      href: "/studio/export",
      icon: Download,
      description: "Compilation & Formats"
    }
  ];

  return (
    <aside className="w-[280px] shrink-0 bg-[#eff4ff]/60 border-r border-[#c6c6cd]/30 h-[calc(100vh-61px)] sticky top-[61px] flex flex-col justify-between p-4 overflow-y-auto">
      <div className="space-y-6">
        {/* Active Project Banner */}
        <div className="p-3 bg-[#ffffff] rounded border border-[#c6c6cd]/40 shadow-xs">
          <div className="flex items-center justify-between text-[10px] font-mono uppercase text-[#45464d] mb-1">
            <span>Projet en cours</span>
            <Bookmark className="w-3 h-3 text-[#b87500]" />
          </div>
          <h2 className="font-playfair text-sm font-bold text-[#0b1c30] truncate">
            {project.title}
          </h2>
          <p className="text-[11px] text-[#45464d] truncate mt-0.5">
            {project.genre}
          </p>
          <div className="mt-2 pt-2 border-t border-[#c6c6cd]/20 flex items-center justify-between text-[11px] font-mono text-[#45464d]">
            <span>Mots: {project.currentWordCount.toLocaleString()}</span>
            <span className="text-[#b87500] font-semibold">
              {Math.round((project.currentWordCount / project.wordCountTarget) * 100)}%
            </span>
          </div>
        </div>

        {/* Navigation Section */}
        <div>
          <div className="flex items-center justify-between text-[10px] font-mono uppercase tracking-wider text-[#76777d] px-2 mb-2">
            <span>Espaces de Travail</span>
            <Link href="/dashboard" className="text-[#0b1c30] hover:underline flex items-center gap-0.5">
              <LayoutDashboard className="w-3 h-3" /> Mes livres
            </Link>
          </div>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-start gap-3 p-2.5 rounded transition-all text-left ${
                    isActive
                      ? "bg-[#0b1c30] text-[#ffffff] shadow-sm"
                      : "text-[#0b1c30] hover:bg-[#e5eeff] text-[#45464d]"
                  }`}
                >
                  <Icon
                    className={`w-4 h-4 mt-0.5 shrink-0 ${
                      isActive ? "text-[#ffddb8]" : "text-[#5f5e5b]"
                    }`}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold leading-none block truncate">
                        {item.name}
                      </span>
                      {item.badge !== undefined && (
                        <span
                          className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono ${
                            isActive
                              ? "bg-[#ffddb8] text-[#2a1700]"
                              : "bg-[#d3e4fe] text-[#0b1c30]"
                          }`}
                        >
                          {item.badge}
                        </span>
                      )}
                    </div>
                    <span
                      className={`text-[10px] block truncate mt-1 ${
                        isActive ? "text-[#7c839b]" : "text-[#76777d]"
                      }`}
                    >
                      {item.description}
                    </span>
                  </div>
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Footer Info */}
      <div className="pt-4 border-t border-[#c6c6cd]/30 text-[11px] font-mono text-[#76777d] flex items-center justify-between">
        <span>Manuscript v1.0</span>
        <span className="inline-flex items-center gap-1 text-[#b87500]">
          ● Mode Studio
        </span>
      </div>
    </aside>
  );
}
