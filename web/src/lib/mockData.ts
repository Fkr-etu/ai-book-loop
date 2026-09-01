export interface Character {
  id: string;
  name: string;
  role: string;
  archetype: string;
  psychology: string;
  goal: string;
  secret: string;
  avatarUrl?: string;
  status: "active" | "draft" | "archived";
}

export interface LoreItem {
  id: string;
  title: string;
  category: "faction" | "location" | "artifact" | "rule";
  description: string;
  importance: "high" | "medium" | "low";
  canonStatus: "canonical" | "proposed" | "deprecated";
}

export interface GraphNode {
  id: string;
  label: string;
  type: "character" | "location" | "faction" | "artifact";
  x?: number;
  y?: number;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relation: string;
}

export interface Scene {
  id: string;
  title: string;
  summary: string;
  status: "validated" | "in_review" | "draft" | "rejected";
  content?: string;
  scoreStyle?: number;
  scoreCoherence?: number;
}

export interface Chapter {
  id: string;
  number: number;
  title: string;
  summary: string;
  status: "approved" | "in_progress" | "pending";
  scenes: Scene[];
}

export interface CreativeConstraint {
  id: string;
  type: "forbidden_word" | "pacing" | "tone" | "pov";
  description: string;
  active: boolean;
}

export interface SceneReview {
  id: string;
  sceneId: string;
  scoreStyle: number;
  scoreCoherence: number;
  forbiddenPatternsFound: string[];
  critique: string;
  approved: boolean;
  timestamp: string;
}

export interface ProjectState {
  id: string;
  title: string;
  subtitle: string;
  genre: string;
  targetAudience: string;
  theme: string;
  loreSummary: string;
  styleTone: string;
  wordCountTarget: number;
  currentWordCount: number;
  characters: Character[];
  loreItems: LoreItem[];
  graphNodes: GraphNode[];
  graphEdges: GraphEdge[];
  chapters: Chapter[];
  constraints: CreativeConstraint[];
  reviews: SceneReview[];
}

export const initialProjectData: ProjectState = {
  id: "proj-001",
  title: "La Porte d'Obsidienne",
  subtitle: "Chronique des Chronomanciens - Tome I",
  genre: "Dark Fantasy / Sci-Fi",
  targetAudience: "Adulte / Fiction Littéraire",
  theme: "Le prix de l'immortalité et la décomposition de la mémoire collective au fil des siècles.",
  loreSummary: "Dans l'Empire de Cendres, les mages utilisent le minerai d'Obsidienne stellaire pour figer les souvenirs. Mais la Porte Centrale menace de céder sous la pression du Vide.",
  styleTone: "Scholastique, poétique, sombre, rythme soutenu mais descriptif.",
  wordCountTarget: 80000,
  currentWordCount: 24500,
  characters: [
    {
      id: "char-1",
      name: "Archiviste Valerius",
      role: "Protagoniste",
      archetype: "Le Savant Maudit",
      psychology: "Obsédé par la vérité historique. Souffre d'amnésie sélective causée par ses rituels.",
      goal: "Restaurer la mémoire originelle avant l'effondrement du Grand Codex.",
      secret: "A lui-même ordonné l'effacement de son propre passé il y a deux siècles.",
      status: "active"
    },
    {
      id: "char-2",
      name: "Lyra Vane",
      role: "Antagoniste tragique",
      archetype: "La Réformatrice fanatique",
      psychology: "Pragmatique, implacable, hantée par la disparition de sa maison.",
      goal: "Ouvrir la Porte d'Obsidienne pour purger les corrompus.",
      secret: "Elle est la descendante directe de l'Architecte de la Porte.",
      status: "active"
    },
    {
      id: "char-3",
      name: "Soren le Muet",
      role: "Allié",
      archetype: "Le Gardien mystique",
      psychology: "Loyal, stoïque, communique par signes d'éther.",
      goal: "Protéger Valerius contre les Inquisiteurs de l'Ombre.",
      secret: "Cache la dernière relique de la Porte sacrée.",
      status: "active"
    }
  ],
  loreItems: [
    {
      id: "lore-1",
      title: "L'Obsidienne Stellaire",
      category: "artifact",
      description: "Minerai noir cristallin capable de capturer l'éther mnésique des défunts.",
      importance: "high",
      canonStatus: "canonical"
    },
    {
      id: "lore-2",
      title: "Citadelle de Cendres",
      category: "location",
      description: "Siège du Collège des Archivistes, bâtie sur le gouffre de la Première Faille.",
      importance: "high",
      canonStatus: "canonical"
    },
    {
      id: "lore-3",
      title: "Ordre des Inquisiteurs du Vide",
      category: "faction",
      description: "Police religieuse chargée de brûler les textes non approuvés par le Haut Conseil.",
      importance: "medium",
      canonStatus: "canonical"
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
      summary: "Valerius découvre un manuscrit interdit gravé sur une lame d'Obsidienne.",
      status: "approved",
      scenes: [
        {
          id: "sc-101",
          title: "Dans la pénombre des scriptoriums",
          summary: "Valerius isole une résonance anormale dans le hall des archives.",
          status: "validated",
          scoreStyle: 9,
          scoreCoherence: 10,
          content: "L'encre fraîche n'a pas le même poids que l'oubli. Valerius glissa ses doigts calleux sur la surface glacée du Codex d'Obsidienne. Dans le silence oppressant de la voûte, seule la pulsation régulière des cristaux venait troubler le bruissement des parchemins. Il savait que le Conseil Inquisitorial avait interdit l'accès au neuvième rayon, mais la vérité exigeait ce sacrilège."
        },
        {
          id: "sc-102",
          title: "La confrontation avec l'Inquisiteur",
          summary: "Une patrouille surprend Valerius, Soren intervient.",
          status: "validated",
          scoreStyle: 8,
          scoreCoherence: 9,
          content: "L'ombre projetée sur le pilier d'éther ne trompait pas. Soren fit un geste discret, étouffant la lumière de sa lanterne avant même que le bruit des bottes ferrées ne résonne sous la voûte. L'Inquisiteur s'arrêta à trois pas, la main sur le pommeau de sa lame."
        }
      ]
    },
    {
      id: "chap-2",
      number: 2,
      title: "La Cité Suspendue",
      summary: "Voyage vers les Hauts de Cendres à la recherche du premier fragment.",
      status: "in_progress",
      scenes: [
        {
          id: "sc-201",
          title: "L'ascension des tours mnésiques",
          summary: "Traversée du pont de verre sous la brume éthérée.",
          status: "in_review",
          scoreStyle: 7,
          scoreCoherence: 8,
          content: "Le vent des cimes charriait une odeur d'ozone et de poussière sacrée. suspendus à trois cents mètres au-dessus du gouffre, Valerius et Lyra marchaient côte à côte sans se regarder. Chaque pas sur le pont suspendu faisait résonner une note cristalline."
        }
      ]
    }
  ],
  constraints: [
    { id: "c1", type: "forbidden_word", description: "Interdire les anachronismes modernes (ex: 'technologie', 'robot', 'ordinateur')", active: true },
    { id: "c2", type: "tone", description: "Conserver une voix narrative érudite et littéraire à la 3ème personne", active: true },
    { id: "c3", type: "pacing", description: "Maintenir des descriptions tactiles (matières, sons, odeurs)", active: true }
  ],
  reviews: [
    {
      id: "rev-1",
      sceneId: "sc-201",
      scoreStyle: 7,
      scoreCoherence: 8,
      forbiddenPatternsFound: [],
      critique: "Bonne immersion sensorielle. Attention au vocabulaire moderniste dans le second paragraphe. La tension dramatique entre Valerius et Lyra pourrait être intensifiée.",
      approved: false,
      timestamp: "Aujourd'hui à 14:32"
    }
  ]
};
