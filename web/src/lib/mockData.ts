import { BookState } from "@/types";

export const initialProjectData: BookState = {
  id: "proj-001",
  title: "La Porte d'Obsidienne",
  subtitle: "Chronique des Chronomanciens - Tome I",
  genre: "Dark Fantasy / Sci-Fi",
  targetAudience: "Adulte / Fiction Littéraire",
  theme: "Le prix de l'immortalité et la décomposition de la mémoire collective au fil des siècles.",
  authorIdea: "Un archiviste amnésique découvre un manuscrit interdit gravé dans l'obsidienne qui révèle que le passé de son empire est une illusion réécrite tous les siècles.",
  lore: "Dans l'Empire de Cendres, les mages utilisent l'Obsidienne stellaire pour figer les souvenirs. Mais la Porte Centrale menace de céder sous la pression du Vide.",
  loreSummary: "Dans l'Empire de Cendres, les mages utilisent l'Obsidienne stellaire pour figer les souvenirs. Mais la Porte Centrale menace de céder sous la pression du Vide.",
  styleTone: "Scholastique, poétique, sombre, rythme soutenu mais descriptif.",
  outline: "1. Le Murmure du Parchemin\n2. La Cité Suspendue\n3. L'Éclipse du Codex",
  outlineApproved: true,
  constraints: [
    "Interdire les anachronismes modernes (ex: 'technologie', 'robot', 'ordinateur')",
    "Conserver une voix narrative érudite et littéraire à la 3ème personne",
    "Maintenir des descriptions tactiles (matières, sons, odeurs)"
  ],
  wordCountTarget: 80000,
  currentWordCount: 24500,
  authorIntent: {
    originalIdea: "Un archiviste amnésique découvre un manuscrit interdit gravé dans l'obsidienne qui révèle que le passé de son empire est une illusion réécrite tous les siècles.",
    theme: "Le prix de l'immortalité et la décomposition de la mémoire collective au fil des siècles.",
    constraints: [
      "Interdire les anachronismes modernes",
      "Voix narrative érudite à la 3ème personne",
      "Descriptions tactiles"
    ],
    styleTone: "Scholastique, poétique, sombre"
  },
  characters: [
    {
      id: "char-1",
      name: "Archiviste Valerius",
      role: "Protagoniste",
      archetype: "Le Savant Maudit",
      psychology: "Obsédé par la vérité historique. Souffre d'amnésie sélective causée par ses rituels.",
      goal: "Restaurer la mémoire originelle avant l'effondrement du Grand Codex.",
      secret: "A lui-même ordonné l'effacement de son propre passé il y a deux siècles.",
      status: "canonical",
      traits: ["Erudit", "Obsessionnel", "Amnésique"],
      motivations: "Retrouver la vérité sur le Premier Rituel",
      canonicalFacts: ["Garde de la Grande Bibliothèque", "Maîtrise le chant éthéré"],
      source: "Auteur"
    },
    {
      id: "char-2",
      name: "Lyra Vane",
      role: "Antagoniste tragique",
      archetype: "La Réformatrice fanatique",
      psychology: "Pragmatique, implacable, hantée par la disparition de sa maison.",
      goal: "Ouvrir la Porte d'Obsidienne pour purger les corrompus.",
      secret: "Elle est la descendante directe de l'Architecte de la Porte.",
      status: "canonical",
      traits: ["Implacable", "Noble", "Déterminée"],
      motivations: "Restaurer la Maison Vane",
      canonicalFacts: ["Dernière héritière de la Faille", "Commande aux Inquisiteurs"],
      source: "Auteur"
    },
    {
      id: "char-3",
      name: "Soren le Muet",
      role: "Allié",
      archetype: "Le Gardien mystique",
      psychology: "Loyal, stoïque, communique par signes d'éther.",
      goal: "Protéger Valerius contre les Inquisiteurs de l'Ombre.",
      secret: "Cache la dernière relique de la Porte sacrée.",
      status: "canonical",
      traits: ["Stoïque", "Silencieux", "Fidèle"],
      motivations: "Vœu d'allégeance à Valerius",
      canonicalFacts: ["A perdu la voix lors de la purge de la Faille"],
      source: "Auteur"
    }
  ],
  loreItems: [
    {
      id: "lore-1",
      title: "L'Obsidienne Stellaire",
      category: "artifact",
      description: "Minerai noir cristallin capable de capturer l'éther mnésique des défunts.",
      importance: "high",
      canonStatus: "canonical",
      source: "Auteur"
    },
    {
      id: "lore-2",
      title: "Citadelle de Cendres",
      category: "location",
      description: "Siège du Collège des Archivistes, bâtie sur le gouffre de la Première Faille.",
      importance: "high",
      canonStatus: "canonical",
      source: "Auteur"
    },
    {
      id: "lore-3",
      title: "Ordre des Inquisiteurs du Vide",
      category: "faction",
      description: "Police religieuse chargée de brûler les textes non approuvés par le Haut Conseil.",
      importance: "medium",
      canonStatus: "canonical",
      source: "Auteur"
    }
  ],
  graphNodes: [
    { id: "char-1", label: "Archiviste Valerius", type: "character" },
    { id: "char-2", label: "Lyra Vane", type: "character" },
    { id: "char-3", label: "Soren le Muet", type: "character" },
    { id: "lore-1", label: "Obsidienne Stellaire", type: "artifact" },
    { id: "lore-2", label: "Citadelle de Cendres", type: "location" },
    { id: "lore-3", label: "Ordre des Inquisiteurs", type: "faction" }
  ],
  graphEdges: [
    { id: "e1", source: "char-1", target: "char-2", relation: "Rivalité ancienne" },
    { id: "e2", source: "char-1", target: "char-3", relation: "Protecteur" },
    { id: "e3", source: "char-1", target: "lore-1", relation: "Étudie" },
    { id: "e4", source: "char-2", target: "lore-3", relation: "Dirige secrètement" },
    { id: "e5", source: "char-1", target: "lore-2", relation: "Réside à" }
  ],
  chapters: [
    {
      id: "chap-1",
      number: 1,
      title: "Le Murmure du Parchemin",
      objective: "Découvrir la tablette d'obsidienne dans les archives scellées de la Citadelle.",
      summary: "Valerius découvre un manuscrit interdit gravé sur une lame d'Obsidienne dans la pénombre des scriptoriums.",
      status: "approved",
      currentVersion: 1,
      versions: [
        {
          id: "chap-1-v1",
          versionNumber: 1,
          content: "L'encre fraîche n'a pas le même poids que l'oubli. Valerius glissa ses doigts calleux sur la surface glacée du Codex d'Obsidienne. Dans le silence oppressant de la voûte, seule la pulsation régulière des cristaux venait troubler le bruissement des parchemins.",
          createdAt: "2025-01-15T10:00:00Z",
          source: "author",
          status: "approved",
          review: {
            score: 9,
            approved: true,
            issues: [],
            suggestions: ["Excellente ambiance atmosphérique."],
            scoreStyle: 9,
            scoreCoherence: 10
          }
        }
      ],
      scenes: [
        {
          id: "sc-101",
          title: "Dans la pénombre des scriptoriums",
          summary: "Valerius isole une résonance anormale dans le hall des archives.",
          status: "validated",
          scoreStyle: 9,
          scoreCoherence: 10,
          content: "L'encre fraîche n'a pas le même poids que l'oubli. Valerius glissa ses doigts calleux sur la surface glacée du Codex d'Obsidienne."
        }
      ]
    },
    {
      id: "chap-2",
      number: 2,
      title: "La Cité Suspendue",
      objective: "Mener l'ascension des tours mnésiques jusqu'au pont de verre sous la brume éthérée.",
      summary: "Voyage vers les Hauts de Cendres à la recherche du premier fragment.",
      status: "needs_review",
      currentVersion: 1,
      versions: [
        {
          id: "chap-2-v1",
          versionNumber: 1,
          content: "Le vent des cimes charriait une odeur d'ozone et de poussière sacrée. Suspendus à trois cents mètres au-dessus du gouffre, Valerius et Lyra marchaient côte à côte sans se regarder.",
          createdAt: "2025-01-16T14:30:00Z",
          source: "ai",
          status: "needs_review",
          review: {
            score: 7,
            approved: false,
            issues: ["Attention au vocabulaire moderniste dans le second paragraphe.", "Tension dramatique à intensifier."],
            suggestions: ["Accentuer le contraste entre les deux personnages sur le pont."],
            scoreStyle: 7,
            scoreCoherence: 8
          }
        }
      ],
      scenes: [
        {
          id: "sc-201",
          title: "L'ascension des tours mnésiques",
          summary: "Traversée du pont de verre sous la brume éthérée.",
          status: "in_review",
          scoreStyle: 7,
          scoreCoherence: 8,
          content: "Le vent des cimes charriait une odeur d'ozone et de poussière sacrée."
        }
      ]
    }
  ],
  creativeConstraints: [
    { id: "c1", type: "forbidden_word", description: "Interdire les anachronismes modernes (ex: 'technologie', 'robot', 'ordinateur')", active: true },
    { id: "c2", type: "tone", description: "Conserver une voix narrative érudite et littéraire à la 3ème personne", active: true },
    { id: "c3", type: "pacing", description: "Maintenir des descriptions tactiles (matières, sons, odeurs)", active: true }
  ],
  reviews: [
    {
      id: "rev-1",
      sceneId: "sc-201",
      score: 7,
      approved: false,
      issues: ["Vocabulaire moderniste dans le second paragraphe"],
      suggestions: ["Accentuer la tension dramatique entre Valerius et Lyra"],
      scoreStyle: 7,
      scoreCoherence: 8,
      forbiddenPatternsFound: [],
      critique: "Bonne immersion sensorielle. Attention au vocabulaire moderniste.",
      timestamp: "Aujourd'hui à 14:32"
    }
  ]
};
